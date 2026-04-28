/**
 * github-api.js — Commit files to GitHub repo via the REST API.
 *
 * Used by admin pages (review.html, add.html) to push changes
 * directly from the browser, removing the need for a local server.
 *
 * Auth: GitHub personal access token stored in localStorage.
 */

const GitHubAPI = (() => {
  const OWNER = 'sibowker-oss';
  const REPO = 'ai-token-tracker';
  const BRANCH = 'main';
  const TOKEN_KEY = 'ai-ledger-github-token';
  const API = 'https://api.github.com';

  function getToken() {
    return localStorage.getItem(TOKEN_KEY) || '';
  }

  function setToken(token) {
    localStorage.setItem(TOKEN_KEY, token.trim());
  }

  function clearToken() {
    localStorage.removeItem(TOKEN_KEY);
  }

  function hasToken() {
    return !!getToken();
  }

  async function _headers() {
    const token = getToken();
    if (!token) throw new Error('GitHub token not configured. Go to Settings tab to add one.');
    return {
      'Authorization': 'token ' + token,
      'Accept': 'application/vnd.github.v3+json',
      'Content-Type': 'application/json'
    };
  }

  /** Get the SHA of the latest commit on the branch */
  async function _getLatestCommitSha() {
    const headers = await _headers();
    const resp = await fetch(`${API}/repos/${OWNER}/${REPO}/git/ref/heads/${BRANCH}`, { headers });
    if (!resp.ok) throw new Error('Failed to get branch ref: ' + resp.status);
    const data = await resp.json();
    return data.object.sha;
  }

  /** Get the tree SHA from a commit */
  async function _getTreeSha(commitSha) {
    const headers = await _headers();
    const resp = await fetch(`${API}/repos/${OWNER}/${REPO}/git/commits/${commitSha}`, { headers });
    if (!resp.ok) throw new Error('Failed to get commit: ' + resp.status);
    const data = await resp.json();
    return data.tree.sha;
  }

  /** Encode a JS string as base64 of its UTF-8 bytes (round-trip-safe). */
  function _encodeBase64Utf8(str) {
    const bytes = new TextEncoder().encode(str);
    let bin = '';
    for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
    return btoa(bin);
  }

  // wq-029: post the blob as base64 of UTF-8 bytes rather than a raw JS string
  // tagged encoding:utf-8. Stale browsers running the pre-14e256a readFile()
  // returned a raw-byte string (each UTF-8 byte → a Latin-1 codepoint); when
  // that round-tripped through fetch's USVString body it re-encoded as UTF-8
  // and produced the c3 a2 c2 80 c2 94 mojibake observed at 249cffe.
  // TextEncoder + btoa freezes whatever bytes the JS string represents, so
  // this path is byte-clean regardless of how the string was decoded upstream.
  async function _createBlob(content) {
    const headers = await _headers();
    const resp = await fetch(`${API}/repos/${OWNER}/${REPO}/git/blobs`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ content: _encodeBase64Utf8(content), encoding: 'base64' })
    });
    if (!resp.ok) throw new Error('Failed to create blob: ' + resp.status);
    const data = await resp.json();
    return data.sha;
  }

  /** Create a tree with the given file changes */
  async function _createTree(baseTreeSha, files) {
    const headers = await _headers();
    const tree = [];
    for (const f of files) {
      const blobSha = await _createBlob(typeof f.content === 'string' ? f.content : JSON.stringify(f.content, null, 2));
      tree.push({ path: f.path, mode: '100644', type: 'blob', sha: blobSha });
    }
    const resp = await fetch(`${API}/repos/${OWNER}/${REPO}/git/trees`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ base_tree: baseTreeSha, tree })
    });
    if (!resp.ok) throw new Error('Failed to create tree: ' + resp.status);
    const data = await resp.json();
    return data.sha;
  }

  /** Create a commit */
  async function _createCommit(treeSha, parentSha, message) {
    const headers = await _headers();
    const resp = await fetch(`${API}/repos/${OWNER}/${REPO}/git/commits`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ message, tree: treeSha, parents: [parentSha] })
    });
    if (!resp.ok) throw new Error('Failed to create commit: ' + resp.status);
    const data = await resp.json();
    return data.sha;
  }

  /** Update branch ref to point to new commit */
  async function _updateRef(commitSha) {
    const headers = await _headers();
    const resp = await fetch(`${API}/repos/${OWNER}/${REPO}/git/refs/heads/${BRANCH}`, {
      method: 'PATCH',
      headers,
      body: JSON.stringify({ sha: commitSha })
    });
    if (!resp.ok) throw new Error('Failed to update ref: ' + resp.status);
    return resp.json();
  }

  /**
   * Commit one or more files to the repo.
   *
   * @param {Array<{path: string, content: string|object}>} files
   *   Each file needs `path` (repo-relative, e.g. "beta/data-updates/decisions.json")
   *   and `content` (string or object — objects are JSON-stringified).
   * @param {string} message — commit message
   * @returns {Promise<{sha: string, url: string}>} — the new commit
   */
  async function commitFiles(files, message) {
    for (let attempt = 0; attempt < 3; attempt++) {
      const latestSha = await _getLatestCommitSha();
      const baseTreeSha = await _getTreeSha(latestSha);
      const newTreeSha = await _createTree(baseTreeSha, files);
      const newCommitSha = await _createCommit(newTreeSha, latestSha, message);
      try {
        await _updateRef(newCommitSha);
        return { sha: newCommitSha, url: `https://github.com/${OWNER}/${REPO}/commit/${newCommitSha}` };
      } catch (e) {
        if (attempt < 2 && e.message.includes('422')) continue; // ref moved, retry
        throw e;
      }
    }
  }

  /**
   * Read a file from the repo (for read-modify-write patterns).
   *
   * @param {string} path — repo-relative path
   * @returns {Promise<{content: string, sha: string}>}
   */
  function _decodeBase64Utf8(b64) {
    const binary = atob((b64 || '').replace(/\n/g, ''));
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    return new TextDecoder('utf-8').decode(bytes);
  }

  async function readFile(path) {
    const headers = await _headers();
    const resp = await fetch(`${API}/repos/${OWNER}/${REPO}/contents/${path}?ref=${BRANCH}`, { headers });
    if (!resp.ok) throw new Error('Failed to read ' + path + ': ' + resp.status);
    const data = await resp.json();
    // GitHub Contents API returns empty content for files > 1 MB. When that
    // happens fall back to the Git Blobs API which handles up to 100 MB.
    if (!data.content && data.sha) {
      const blobResp = await fetch(`${API}/repos/${OWNER}/${REPO}/git/blobs/${data.sha}`, { headers });
      if (!blobResp.ok) throw new Error('Failed to read blob for ' + path + ': ' + blobResp.status);
      const blob = await blobResp.json();
      return { content: _decodeBase64Utf8(blob.content), sha: data.sha };
    }
    // GitHub sends base64 of UTF-8 bytes. atob() returns a raw-byte string, so
    // non-ASCII chars (Chinese, curly quotes, emoji) come back as mojibake and
    // break JSON.parse. Decode properly via TextDecoder.
    return { content: _decodeBase64Utf8(data.content), sha: data.sha };
  }

  /**
   * Validate the token by fetching repo info.
   * @returns {Promise<{valid: boolean, scopes: string, message: string}>}
   */
  async function validateToken() {
    try {
      const headers = await _headers();
      const resp = await fetch(`${API}/repos/${OWNER}/${REPO}`, { headers });
      const scopes = resp.headers.get('x-oauth-scopes') || '';
      if (resp.ok) {
        return { valid: true, scopes, message: 'Token valid — access to ' + OWNER + '/' + REPO };
      }
      return { valid: false, scopes, message: 'Token rejected: ' + resp.status };
    } catch (e) {
      return { valid: false, scopes: '', message: 'Error: ' + e.message };
    }
  }

  // wq-029 defensive guard. When stale pre-14e256a JS decodes UTF-8 bytes
  // as a raw byte-string (atob without TextDecoder), multi-byte codepoints
  // land in JS memory as a sequence of Latin-1-range codepoints. Canonical
  // signatures: U+00E2 + U+0080 + U+009X (broken em/en-dash, curly quotes,
  // ellipsis) and U+00C2 + U+00A0 (broken nbsp). U+00E2 alone is legitimate
  // (French/Portuguese vowels) so the discriminator is U+00E2 followed by
  // a C1 control U+0080-U+009F or U+00A6 (ellipsis trailer) - impossible
  // in normal text. ASCII-only escape sequences below to keep this source
  // file robust against editors that strip C1 controls.
  const MOJIBAKE_RE = /\u00e2\u0080[\u0093-\u009d\u00a6]|\u00c2\u00a0/;

  /**
   * Count canonical mojibake markers in a JS object (deep walk over strings).
   * Used by the defensive guard to compare a page-load baseline vs pre-commit
   * value — if the count went *up* without the user touching strings, abort.
   */
  function countMojibakeMarkers(value) {
    let n = 0;
    const walk = (v) => {
      if (v == null) return;
      if (typeof v === 'string') {
        const m = v.match(new RegExp(MOJIBAKE_RE.source, 'g'));
        if (m) n += m.length;
      } else if (Array.isArray(v)) {
        for (let i = 0; i < v.length; i++) walk(v[i]);
      } else if (typeof v === 'object') {
        for (const k in v) walk(v[k]);
      }
    };
    walk(value);
    return n;
  }

  /**
   * Trigger a workflow via workflow_dispatch.
   * @param {string} workflowFile — e.g. "apply-decisions.yml"
   * @returns {Promise<boolean>} — true if triggered
   */
  async function triggerWorkflow(workflowFile) {
    const headers = await _headers();
    const resp = await fetch(`${API}/repos/${OWNER}/${REPO}/actions/workflows/${workflowFile}/dispatches`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ ref: BRANCH })
    });
    return resp.status === 204;
  }

  return { getToken, setToken, clearToken, hasToken, commitFiles, readFile, validateToken, triggerWorkflow, countMojibakeMarkers, OWNER, REPO };
})();

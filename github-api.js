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

  /** Create a blob for file content */
  async function _createBlob(content) {
    const headers = await _headers();
    const resp = await fetch(`${API}/repos/${OWNER}/${REPO}/git/blobs`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ content, encoding: 'utf-8' })
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
    const latestSha = await _getLatestCommitSha();
    const baseTreeSha = await _getTreeSha(latestSha);
    const newTreeSha = await _createTree(baseTreeSha, files);
    const newCommitSha = await _createCommit(newTreeSha, latestSha, message);
    await _updateRef(newCommitSha);
    return { sha: newCommitSha, url: `https://github.com/${OWNER}/${REPO}/commit/${newCommitSha}` };
  }

  /**
   * Read a file from the repo (for read-modify-write patterns).
   *
   * @param {string} path — repo-relative path
   * @returns {Promise<{content: string, sha: string}>}
   */
  async function readFile(path) {
    const headers = await _headers();
    const resp = await fetch(`${API}/repos/${OWNER}/${REPO}/contents/${path}?ref=${BRANCH}`, { headers });
    if (!resp.ok) throw new Error('Failed to read ' + path + ': ' + resp.status);
    const data = await resp.json();
    return { content: atob(data.content), sha: data.sha };
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

  return { getToken, setToken, clearToken, hasToken, commitFiles, readFile, validateToken, triggerWorkflow, OWNER, REPO };
})();

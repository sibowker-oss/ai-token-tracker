# Brief: take In-Dev page off the public surface (footer + indexing)

> **Handoff metadata (per GUIDELINES §9.3)**
> - **Source draft:** Cowork session 2026-05-04
> - **Handoff date:** 2026-05-04
> - **Work queue:** wq-NNN (assign on Notion)
> - **Parent:** Simon spotted "In development" in the public site footer; the page is internal-only and should only be reachable via the Command Centre.

**Status:** Scoped
**Budget:** $0 — markup + manifest only
**Estimated effort:** ~30 min

---

## 1. Goal

`in-development.html` should stop being a public, discoverable page. After this brief:

- No public page links to `/in-development.html` (footer link gone everywhere).
- Search engines are told not to index it (`noindex,nofollow` meta + `robots.txt` Disallow).
- `data/page-registry.json` reflects the new lifecycle: `live` → `admin`.
- The Command Centre (`admin.html`) still loads it via the existing `dev` iframe tab — no admin behaviour changes.

The page file stays at `/in-development.html` so the admin iframe (`TAB_PAGES.dev = 'in-development.html'`) keeps working without code changes. Anyone who knows the URL can still load it directly — that's accepted scope for this brief. If we later want hard auth, that's a separate piece of work (would need to either move the file or gate it via the `hepburn-decap-auth` worker).

---

## 2. Pre-flight

- `git status` clean / on `main`. Pull before starting.
- Confirm `scripts/sync_ideas.py` hasn't run between now and the start of work — it edits `in-development.html` and would race the markup edit. If it ran, just rebase the meta tag onto whatever it produced.

---

## 3. Files to change

### 3.1 Footer link removal (11 files)

Remove this exact line from each file:

```html
        <li><a href="/in-development.html">In development</a></li>
```

| File | Line (approx) |
|---|---|
| `index.html` | 479 |
| `about.html` | 257 |
| `capital.html` | 996 |
| `revenue.html` | 792 |
| `usage.html` | 869 |
| `power.html` | 197 |
| `methodology.html` | 362 |
| `openrouter.html` | 810 |
| `timeline.html` | 442 |
| `changelog.html` | 241 |
| `in-development.html` | 463 |

(The page itself loses the link too — clean and avoids self-reference inside the admin iframe.)

Use a single `sed`/multi-file find-replace; surrounding `<li>` items in the footer (Timeline / Live pricing / Changelog) stay untouched.

### 3.2 In-Dev page meta (1 file)

In `in-development.html`, inside `<head>`, add **directly under the existing `<meta charset>` line** (or wherever the meta block lives):

```html
<meta name="robots" content="noindex,nofollow">
```

### 3.3 robots.txt (new file at repo root)

There is no existing `robots.txt`. Create one at the repo root (`/robots.txt` once deployed by Cloudflare Pages):

```
User-agent: *
Disallow: /in-development.html
```

If a `robots.txt` shows up between now and shipping, just add the `Disallow` line; don't overwrite.

### 3.4 page-registry.json (1 entry)

In `data/page-registry.json`, find the `in-development.html` entry and update three fields:

```json
{
  "path": "in-development.html",
  "status": "admin",
  "title": "In Development — Global AI Dash",
  "purpose": "Admin-only index of in-flight prototypes and specs. Loaded into Command Centre via the 'dev' iframe tab. Removed from public footer + deindexed (wq-NNN, 2026-05-04).",
  ...
  "lastReviewed": "2026-05-04"
}
```

Bump `last_updated` at the top of the file to `"2026-05-04-wq-NNN"`.

`"admin"` is the right value per `metric-schema.json :: page_lifecycle_statuses` ("Tooling page … Not in public nav. Schema-checked but skipped on dataReferences"). Don't invent a new status.

### 3.5 Changelog entry

Add a one-line entry to `changelog.html` recording the deindex (date 2026-05-04). Format-match the surrounding entries.

---

## 4. Things NOT to change (guard rails)

- **Don't move or rename `in-development.html`.** `admin.html` line 126 (`dev: 'in-development.html'`) and `scripts/sync_ideas.py` (`INDEV_PAGE = ... 'in-development.html'`) both hardcode the path.
- **Don't touch `scripts/validate-no-hardcoded-constants.mjs`.** The wq-073 rule requiring `in-development.html` to fetch `data/methodology_constants.json` still applies — admin status doesn't exempt it from that specific check, only from the `dataReferences` lint. Verify it still passes (§5).
- **Don't touch the beta tree.** `beta/in-development.html` stays as-is.
- **Don't add a sitemap entry.** No sitemap exists; don't introduce one in this brief.

---

## 5. Acceptance / verification

Run from repo root:

```bash
# 1. Confirm zero footer links remain to in-development.html
rg -n 'href="/in-development\.html"' --glob '!beta/**' --glob '!archive/**' --glob '!briefs/**' --glob '!audits/**' --glob '!scripts/**' --glob '!data/**'
# Expected: no matches.

# 2. Confirm meta tag is in place
rg -n 'name="robots"' in-development.html
# Expected: one line, content="noindex,nofollow".

# 3. Confirm robots.txt
cat robots.txt
# Expected: Disallow: /in-development.html present.

# 4. Page registry validates
python scripts/validate_page_registry.py
# Expected: passes.

# 5. wq-073 hardcoded-constants still passes for in-development.html
node scripts/validate-no-hardcoded-constants.mjs
# Expected: in-development.html rule reports as required + present.

# 6. Full release-check
node scripts/release-check.mjs
# Expected: all 9 steps green (or no new failures vs. main).
```

**Manual check (the one that actually matters per `feedback_validate_rendered_output`):**

1. Open the deployed site. Scroll the footer of any public page. Confirm "In development" is gone.
2. Open `/admin.html#dev`. Confirm the In Dev tab still loads.
3. Hit `/in-development.html` directly — page should still render (this is intentional; we only removed discoverability), and view-source should show the `noindex` meta.
4. Hit `/robots.txt` — should serve the Disallow line.

---

## 6. Commit + PR

- Branch: `wq-NNN-indev-deindex`
- One commit, message: `wq-NNN: take in-development.html off the public surface (footer + noindex + registry)`
- PR description: link this brief; paste the §5 verification output.

---

## 7. Out of scope (follow-ups)

- Real auth-gating of `/in-development.html` (move behind hepburn-decap-auth worker or relocate to `/admin/`). Not doing now — accepted risk that a known URL is still reachable.
- Removing the `dev` tab from `admin.html` if Simon decides In Dev should live elsewhere in the Command Centre. Not in scope.
- Cleaning up the `_provenance` history field on the registry entry. Not needed.

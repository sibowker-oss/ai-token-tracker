/* design-system/components/admin-nav.js
   wq-088 — fetches admin-nav.html, injects it into <div id="admin-nav-mount">,
   highlights the [data-tab] matching <body data-active-tab="…">, and wires
   the Inbox pending-pill from /vault-inbox.json (count of items with
   status === 'pending'). No build step; static-site fetch only. */
(function () {
  'use strict';

  const PARTIAL_URL = '/design-system/components/admin-nav.html';
  const STYLE_ID = 'admin-nav-styles';

  function injectStyles() {
    if (document.getElementById(STYLE_ID)) return;
    const css = `
      .admin-secondary-nav {
        background: rgba(15, 23, 42, 0.92);
        border-bottom: 1px solid var(--border-dark, #1e293b);
        position: sticky;
        top: 0;
        z-index: 49;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
      }
      .admin-secondary-nav__inner {
        display: flex;
        align-items: stretch;
        gap: 8px;
        padding: 6px 16px;
        overflow-x: auto;
        scrollbar-width: none;
        white-space: nowrap;
      }
      .admin-secondary-nav__inner::-webkit-scrollbar { display: none; }
      .admin-nav-group {
        display: flex;
        align-items: center;
        gap: 2px;
        padding: 0 10px 0 0;
        border-right: 1px solid rgba(148, 163, 184, 0.15);
      }
      .admin-nav-group:last-child { border-right: none; }
      .admin-nav-group--end { margin-left: auto; padding-left: 10px; border-left: 1px solid rgba(148, 163, 184, 0.15); border-right: none; }
      .admin-nav-group__label {
        font: 600 9px/1 'Inter', -apple-system, sans-serif;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #64748b;
        margin-right: 6px;
        flex-shrink: 0;
      }
      .admin-nav-link {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 7px 12px;
        border-radius: 6px;
        font: 500 12px/1 'Inter', -apple-system, sans-serif;
        color: #cbd5e1;
        text-decoration: none;
        border: 1px solid transparent;
        transition: background 120ms ease, color 120ms ease, border-color 120ms ease;
        flex-shrink: 0;
      }
      .admin-nav-link:hover { background: rgba(255,255,255,0.05); color: #f8fafc; }
      .admin-nav-link.is-active {
        background: rgba(59, 130, 246, 0.18);
        color: #60a5fa;
        border-color: rgba(59, 130, 246, 0.4);
        font-weight: 600;
      }
      .admin-nav-pill {
        display: inline-block;
        min-width: 18px;
        padding: 1px 6px;
        background: #ef4444;
        color: #fff;
        font-size: 10px;
        font-weight: 700;
        border-radius: 9px;
        text-align: center;
      }
      .admin-nav-pill[hidden] { display: none; }
      @media (max-width: 768px) {
        .admin-secondary-nav__inner { padding: 6px 10px; gap: 4px; }
        .admin-nav-group { padding-right: 6px; }
        .admin-nav-group__label { display: none; }
        .admin-nav-link { font-size: 11px; padding: 6px 9px; }
        .admin-nav-group--end { margin-left: 8px; }
      }
    `;
    const style = document.createElement('style');
    style.id = STYLE_ID;
    style.textContent = css;
    document.head.appendChild(style);
  }

  function activate(root) {
    const tab = document.body.getAttribute('data-active-tab');
    if (!tab) return;
    const link = root.querySelector(`[data-tab="${tab}"]`);
    if (link) link.classList.add('is-active');
  }

  async function loadPendingPill(root) {
    try {
      const res = await fetch('/vault-inbox.json?v=' + Date.now(), { cache: 'no-store' });
      if (!res.ok) return;
      const inbox = await res.json();
      const items = Array.isArray(inbox.items) ? inbox.items : [];
      const pending = items.filter(i => i && i.status === 'pending').length;
      const pill = root.querySelector('[data-role="pending-pill"]');
      if (!pill) return;
      if (pending > 0) {
        pill.textContent = String(pending);
        pill.hidden = false;
      } else {
        pill.hidden = true;
      }
    } catch (_) {
      /* silent — admin nav still works without the badge */
    }
  }

  async function init() {
    const mount = document.getElementById('admin-nav-mount');
    if (!mount) return;
    injectStyles();
    try {
      const res = await fetch(PARTIAL_URL, { cache: 'no-cache' });
      if (!res.ok) {
        mount.innerHTML = `<div style="padding:12px 16px;color:#ef4444;font:500 12px sans-serif;">Failed to load admin nav (HTTP ${res.status}).</div>`;
        return;
      }
      const html = await res.text();
      mount.innerHTML = html;
      activate(mount);
      loadPendingPill(mount);
    } catch (err) {
      mount.innerHTML = `<div style="padding:12px 16px;color:#ef4444;font:500 12px sans-serif;">Admin nav unavailable: ${err && err.message ? err.message : 'fetch failed'}.</div>`;
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

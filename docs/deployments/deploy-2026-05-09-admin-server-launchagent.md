# Deployment: admin_server.py auto-start via macOS LaunchAgent

**Date:** 2026-05-09
**WQ:** none (operational fix, surfaced during a claims.html review session)
**Branch/Commit:** main (uncommitted at time of writing)

## What shipped

Set up a macOS LaunchAgent so `scripts/admin_server.py` starts automatically on
login and stays alive in the background. Closes the operational gap that hit
during a 2026-05-09 claims.html review session: the wq-100 fail-loud banner
fired because the helper wasn't running, and Simon (non-technical day-to-day)
had no way to know the helper needed to be started before submitting decisions.

Files changed:

- `scripts/admin_server.py`
  - Added `SSL_CERT_FILE` self-heal at import time (resolves via `certifi.where()`
    if the env var isn't already set). This makes pipeline subprocesses spawned
    by `/api/decision` (apply_pipeline.py etc.) survive HTTPS calls under launchd,
    where the user's shell exports don't apply. Same fix is harmless for manual
    runs.
  - Added `--no-browser` flag. Skips the `webbrowser.open()` call so the LaunchAgent
    doesn't pop a browser tab on every login. Manual `python3 scripts/admin_server.py`
    behaviour unchanged.

- `~/Library/LaunchAgents/com.tail.admin-server.plist` (new, outside repo)
  - `RunAtLoad: true`, `KeepAlive: true`, `ThrottleInterval: 10` — auto-start
    on login, auto-restart on crash, throttle restart loops.
  - Logs to `~/Library/Logs/tail-admin-server.log` and `.error.log`.
  - WorkingDirectory set to repo root so `SCRIPT_DIR`-relative paths inside
    admin_server.py resolve identically to manual runs.
  - Hardcoded Python 3.14 framework path (`/Library/Frameworks/Python.framework/...`)
    to avoid PATH ambiguity under launchd.

## Decisions made during implementation

- **LaunchAgent over double-clickable Automator app.** Asked Simon directly;
  he picked auto-start. Rationale: he's a non-technical user who shouldn't have
  to remember "is the helper running?" before editorial work. The cost
  (~30 MB RAM idle, plist file outside repo) is trivial vs. the recurrence
  risk of another silent failure during a review session.

- **SSL_CERT_FILE handled inside admin_server.py, not the plist.** The macos-ssl-certifi
  memory says "don't hardcode — re-resolve via certifi each time." Putting it in
  the plist would hardcode a path that breaks if Python is reinstalled. Self-heal
  inside the script means manual runs, the LaunchAgent, and any future invocation
  paths all work without coordination.

- **`--no-browser` as a positional sys.argv check, not argparse.** One flag, used
  in exactly one place. Argparse would be three lines for no benefit.

- **Did NOT auto-start `decision_watcher.py`.** The script's own docstring says
  it's "belt-and-braces for cases where decision files arrive by other paths"
  and apply_pipeline runs inline via /api/decision. For the current single-author
  manual-review workflow it's pure overhead. Documented this in the chat reply
  so Simon knows to revisit if/when batch decision flows appear.

- **Did NOT touch the existing kill-existing-on-port logic in `main()`.** It's
  fine under launchd: KeepAlive will respawn after Simon manually runs the script,
  and one of the two will eventually win port 8080. In practice Simon shouldn't
  manually run it anymore — the LaunchAgent always has it running.

## Open items

- **Plist not in version control.** Lives at `~/Library/LaunchAgents/com.tail.admin-server.plist`
  — outside the repo. If Simon switches Macs the plist needs to be recreated.
  Possible follow-up: commit a copy at `scripts/launchagent/com.tail.admin-server.plist`
  with a setup helper. Defer until it actually matters.

- **Hardcoded Python path in plist.** If Python 3.14 is upgraded or removed,
  the LaunchAgent will fail silently and Simon will hit the same wq-100 banner
  as before. Mitigation: error log will show the failure clearly. Proper fix
  would be a small wrapper shell script that resolves `python3` from PATH and
  execs the server. Defer until first occurrence.

- **No health-check.** If admin_server.py wedges (process alive but not serving),
  KeepAlive won't notice. Could add a periodic `curl localhost:8080/admin.html`
  check with auto-restart on failure. Defer — wedging hasn't been observed.

## Acceptance criteria status

- [x] LaunchAgent loads without error (`launchctl load` returns clean)
- [x] Server starts on agent load (PID 43753 listening on :8080 verified via lsof)
- [x] HTTP smoke tests pass (`/admin.html` 200, `/claims.html` 200, POST `/api/decision` 200)
- [x] No browser window opens when launched via LaunchAgent (`--no-browser` flag honoured)
- [x] Manual `python3 scripts/admin_server.py` still opens the browser (regression check)
- [ ] Survives a real reboot/login cycle (untested — Simon will confirm next time he restarts)

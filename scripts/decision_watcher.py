#!/usr/bin/env python3
"""decision_watcher.py — wq-100 belt-and-braces watcher for data-updates/decisions/.

The primary apply path runs inline inside admin_server.py /api/decision.
This watcher exists for cases where decision files arrive by other paths —
a future cron, a scripted batch decision, a sibling tool — so the 5-minute
apply-latency target (D6) holds even when admin_server isn't the writer.

Polling-based (not fsevents/inotify) so it works identically on macOS and
Linux without optional dependencies. Default 60-second poll interval.

USAGE
    # foreground (logs to stdout)
    python3 scripts/decision_watcher.py

    # custom interval
    python3 scripts/decision_watcher.py --interval 30

    # one-shot (process pending files once, then exit — handy for tests)
    python3 scripts/decision_watcher.py --once

The watcher tracks processed files in data/.decision_watcher_state.json
so re-running it doesn't reprocess history. apply_pipeline.py is
idempotent so a duplicate run is safe regardless.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)

DECISIONS_DIR = os.path.join(ROOT_DIR, "data-updates", "decisions")
STATE_PATH = os.path.join(ROOT_DIR, "data", ".decision_watcher_state.json")
APPLY_PIPELINE = os.path.join(SCRIPT_DIR, "apply_pipeline.py")


def load_state():
    if not os.path.exists(STATE_PATH):
        return {"processed": []}
    try:
        with open(STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {"processed": []}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def list_decision_files():
    if not os.path.isdir(DECISIONS_DIR):
        return []
    return sorted(
        f for f in os.listdir(DECISIONS_DIR)
        if f.endswith(".json") and not f.startswith(".")
    )


def run_apply():
    """Invoke apply_pipeline.py. Returns (returncode, output_tail)."""
    res = subprocess.run(
        [sys.executable, APPLY_PIPELINE],
        capture_output=True, text=True, cwd=ROOT_DIR, timeout=180,
    )
    return res.returncode, (res.stdout + res.stderr)[-2000:]


def tick():
    """One poll cycle. Returns the count of new decision files processed."""
    state = load_state()
    processed = set(state.get("processed", []))
    pending = [f for f in list_decision_files() if f not in processed]
    if not pending:
        return 0

    print(f"[{datetime.now().isoformat(timespec='seconds')}] "
          f"{len(pending)} new decision file(s) — running apply_pipeline.py")
    rc, tail = run_apply()
    if rc == 0:
        print("  apply_pipeline: OK")
    else:
        print(f"  apply_pipeline: FAILED rc={rc}")
        print("  --- output tail ---")
        print(tail)

    # Mark processed regardless of returncode — the operator should fix
    # the apply error and re-run manually rather than have the watcher
    # spin on a permanently-failing batch.
    processed.update(pending)
    state["processed"] = sorted(processed)[-500:]  # keep a rolling tail
    state["lastRun"] = datetime.now().isoformat(timespec="seconds")
    state["lastReturnCode"] = rc
    save_state(state)
    return len(pending)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--interval", type=int, default=60,
                   help="seconds between polls (default 60)")
    p.add_argument("--once", action="store_true",
                   help="process pending files once then exit")
    args = p.parse_args(argv)

    if args.once:
        tick()
        return 0

    print(f"decision_watcher: polling {DECISIONS_DIR} every {args.interval}s")
    print("  (Ctrl+C to stop)")
    try:
        while True:
            tick()
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\ndecision_watcher: stopped.")
        return 0


if __name__ == "__main__":
    sys.exit(main())

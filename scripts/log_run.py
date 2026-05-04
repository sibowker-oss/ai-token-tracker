"""wq-043 — append-only run log writer.

Every run-producing script wraps its main() with `with logged_run(name): ...`
so status.html can render a single source-of-truth view of automation health.

Two records get written per run:
  1. on enter: status="running", with started_at timestamp
  2. on exit:  status="success" or "failure", with ended_at + duration

The status page reads the latest record per run_id. Append-only is safe under
normal sequential-per-workflow GHA execution; the brief's §4 documents the
locking trade-off if it ever becomes a contention issue.

Usage:
    from log_run import logged_run

    def main():
        with logged_run("monitor_sources.py") as outputs:
            # ... existing logic ...
            outputs["claims_added"] = added
"""
import contextlib
import json
import os
import socket
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path

RUNS_FILE = Path(__file__).resolve().parent.parent / "data" / "runs.jsonl"


def _resolve_trigger():
    if os.environ.get("GITHUB_ACTIONS") == "true":
        return "github_action"
    return os.environ.get("RUN_TRIGGER", "local")


def _resolve_host():
    if os.environ.get("GITHUB_ACTIONS") == "true":
        return os.environ.get("GITHUB_WORKFLOW", "github-actions")
    return os.environ.get("HOSTNAME") or socket.gethostname() or "unknown"


def _resolve_git_sha():
    return (
        os.environ.get("GIT_SHA")
        or os.environ.get("GITHUB_SHA")
        or None
    )


def _append(run):
    RUNS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RUNS_FILE, "a") as f:
        f.write(json.dumps(run) + "\n")


@contextlib.contextmanager
def logged_run(script_name, trigger=None):
    started_at = datetime.now(timezone.utc)
    run_id = str(uuid.uuid4())
    outputs = {}

    start_record = {
        "run_id": run_id,
        "script": script_name,
        "trigger": trigger or _resolve_trigger(),
        "started_at": started_at.isoformat(),
        "status": "running",
        "outputs": {},
        "git_sha": _resolve_git_sha(),
        "host": _resolve_host(),
    }
    _append(start_record)

    status = "success"
    error = None
    try:
        yield outputs
    except BaseException as exc:
        # wq-043 fix: SystemExit(0) is a clean exit (the script asked Python to
        # quit with rc=0). Without this guard, scripts that call sys.exit(0)
        # *inside* a `with logged_run(...)` block — e.g. derive_market_aggregates.py
        # — got stamped status=failure even though they ran perfectly. The
        # giveaway in runs.jsonl was outputs.return_code=0 alongside an error
        # traceback ending in `SystemExit: 0`. Treat that case as success.
        if not (isinstance(exc, SystemExit) and (exc.code is None or exc.code == 0)):
            status = "failure"
            error = traceback.format_exc()[-500:]
        raise
    finally:
        ended_at = datetime.now(timezone.utc)
        end_record = dict(start_record)
        end_record["status"] = status
        end_record["outputs"] = outputs
        end_record["ended_at"] = ended_at.isoformat()
        end_record["duration_s"] = (ended_at - started_at).total_seconds()
        if error:
            end_record["error"] = error
        _append(end_record)

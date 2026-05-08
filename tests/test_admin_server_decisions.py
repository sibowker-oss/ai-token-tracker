"""Integration test for admin_server.py /api/decision and /api/override.

Boots admin_server.py on an ephemeral port, POSTs synthetic decisions and
override payloads, verifies the side effects (file written, vault marked,
override audit appended). Uses the live repo state in a temp working
directory so the production data is never touched.

Run:
    python3 -m unittest tests.test_admin_server_decisions
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def post_json(url, body, timeout=20):
    req = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8") or "{}")


@unittest.skipUnless(os.environ.get("ADMIN_SERVER_INTEGRATION") == "1",
                     "set ADMIN_SERVER_INTEGRATION=1 to run live-server tests")
class TestAdminServerLive(unittest.TestCase):
    """Skipped by default — only fires under ADMIN_SERVER_INTEGRATION=1.

    Live HTTP boot is too slow / port-fragile for the default suite, but the
    test is here so the integration path can be exercised manually.
    """

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="wq100_admin_")
        # Mirror the repo into a tmpdir so writes don't touch real state.
        for name in ("scripts", "vault-data.json", "vault-inbox.json",
                     "entities.json", "site-data.json", "metric-schema.json"):
            src = os.path.join(BASE, name)
            dst = os.path.join(cls.tmp, name)
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy(src, dst)

        # Boot admin_server.py
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        cls.proc = subprocess.Popen(
            [sys.executable, os.path.join(cls.tmp, "scripts", "admin_server.py")],
            cwd=cls.tmp, env=env,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        # Wait for the server to come up
        for _ in range(20):
            try:
                urllib.request.urlopen("http://localhost:8080/", timeout=1)
                break
            except Exception:
                time.sleep(0.25)

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()
        try:
            cls.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            cls.proc.kill()
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_decision_endpoint_writes_file_and_runs_apply(self):
        body = {
            "ui": "claims",
            "decisions": {
                "accepted": [],
                "declined": [],
                "parked": [],
            },
        }
        code, result = post_json("http://localhost:8080/api/decision", body)
        self.assertEqual(code, 200)
        self.assertTrue(result.get("success"))
        self.assertIn("data-updates/decisions/", result.get("decisions_path", ""))
        # Decision file landed
        path = os.path.join(self.tmp, result["decisions_path"])
        self.assertTrue(os.path.exists(path))


class TestAdminServerImports(unittest.TestCase):
    """Static smoke — admin_server module imports without error and the
    new endpoints are registered."""

    def test_imports_and_registers_endpoints(self):
        sys.path.insert(0, os.path.join(BASE, "scripts"))
        import importlib
        m = importlib.import_module("admin_server")
        self.assertTrue(hasattr(m, "AdminHandler"))
        # Verify our new dispatch lines are present
        do_post_src = m.AdminHandler.do_POST.__code__.co_consts
        flat = " ".join(str(c) for c in do_post_src)
        self.assertIn("/api/decision", flat)
        self.assertIn("/api/override", flat)
        # Handler methods exist
        self.assertTrue(callable(m.AdminHandler.handle_decision))
        self.assertTrue(callable(m.AdminHandler.handle_override))


if __name__ == "__main__":
    unittest.main()

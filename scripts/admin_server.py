#!/usr/bin/env python3
"""
admin_server.py — Local server for the AI Ledger admin interface.

Serves beta/ static files AND handles API endpoints:
  POST /api/submit-decisions  — apply review decisions directly
  POST /api/add-source        — add a source to sources-registry.json
  POST /api/add-company       — add a company to entities.json

Start: python3 scripts/admin_server.py
Opens: http://localhost:8080/admin.html

All writes go to beta/ files. No manual file moving needed.
"""

import json, os, sys, subprocess, webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
BETA_DIR = os.path.join(ROOT_DIR, "beta")
PORT = 8080


def load_json(path):
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


class AdminHandler(SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BETA_DIR, **kwargs)

    def do_POST(self):
        if self.path == "/api/submit-decisions":
            self.handle_submit_decisions()
        elif self.path == "/api/add-source":
            self.handle_add_source()
        elif self.path == "/api/add-company":
            self.handle_add_company()
        else:
            self.send_error(404, "Unknown API endpoint")

    def read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length)) if length > 0 else {}

    def send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    # ── Submit Decisions ──

    def handle_submit_decisions(self):
        try:
            decisions = self.read_body()

            # 1. Save decisions file
            date = datetime.now().strftime("%Y-%m-%d")
            os.makedirs(os.path.join(BETA_DIR, "data-updates"), exist_ok=True)
            decisions_path = os.path.join(BETA_DIR, "data-updates", f"review-decisions-{date}.json")
            save_json(decisions_path, decisions)

            # 2. Run apply_decisions.py
            result = subprocess.run(
                [sys.executable, os.path.join(SCRIPT_DIR, "apply_decisions.py"), decisions_path],
                capture_output=True, text=True, cwd=ROOT_DIR, timeout=30
            )

            output = result.stdout + result.stderr
            success = result.returncode == 0

            accepted_count = len(decisions.get("accepted", []))
            declined_count = len(decisions.get("declined", []))
            parked_count = len(decisions.get("parked", []))
            new_fields_count = len(decisions.get("new_fields_approved", []))

            self.send_json({
                "success": success,
                "message": f"Applied: {accepted_count} accepted, {declined_count} declined, {parked_count} parked, {new_fields_count} new fields",
                "details": output,
                "accepted": accepted_count,
                "declined": declined_count,
                "parked": parked_count,
                "new_fields": new_fields_count
            })

        except Exception as e:
            self.send_json({"success": False, "message": str(e)}, 500)

    # ── Add Source ──

    def handle_add_source(self):
        try:
            data = self.read_body()
            url = data.get("url", "").strip()
            title = data.get("title", "").strip()
            if not url:
                self.send_json({"success": False, "message": "URL required"}, 400)
                return

            registry_path = os.path.join(BETA_DIR, "sources-registry.json")
            registry = load_json(registry_path)

            # Auto-classify
            source_type = "web_page"
            extraction = "web_extract"
            freq = "one_time"
            if "docs.google.com/presentation" in url: source_type, extraction, freq = "slide_deck", "pdf_export", "annual"
            elif url.endswith(".pdf"): source_type, extraction = "pdf", "pdf_export"
            elif "substack.com" in url: source_type, freq = "newsletter", "weekly"
            elif "youtube.com/watch" in url: source_type, extraction = "video", "youtube_captions"
            elif "/feed" in url or "/rss" in url or "feeds." in url: source_type, extraction, freq = "rss_feed", "podcast_scraper", "weekly"
            elif "github.com" in url and url.count("/") >= 4: source_type, extraction, freq = "github_repo", "api", "weekly"

            new_id = f"src-{len(registry['sources']) + 1:03d}"
            if not title:
                try:
                    from urllib.parse import urlparse
                    title = urlparse(url).hostname.replace("www.", "")
                except:
                    title = url[:50]

            new_source = {
                "id": new_id, "url": url, "title": title,
                "type": source_type, "author": "", "organization": "",
                "added": datetime.now().strftime("%Y-%m-%d"),
                "tags": [],
                "extraction_method": extraction, "frequency": freq,
                "next_check": datetime.now().strftime("%Y-%m-%d"),
                "last_checked": None, "last_claims_count": 0,
                "status": "pending_first_extraction"
            }

            registry["sources"].append(new_source)
            save_json(registry_path, registry)

            self.send_json({
                "success": True,
                "message": f"Added: {title} (type: {source_type}, freq: {freq})",
                "source": new_source
            })

        except Exception as e:
            self.send_json({"success": False, "message": str(e)}, 500)

    # ── Add Company ──

    def handle_add_company(self):
        try:
            data = self.read_body()
            name = data.get("name", "").strip()
            if not name:
                self.send_json({"success": False, "message": "Company name required"}, 400)
                return

            entities_path = os.path.join(BETA_DIR, "entities.json")
            entities = load_json(entities_path)

            slug = name.lower().replace(" ", "-").replace(".", "")
            # Check for duplicate
            if any(c["slug"] == slug for c in entities["companies"]):
                self.send_json({"success": False, "message": f"Company '{name}' already exists"}, 400)
                return

            new_company = {
                "slug": slug,
                "name": name,
                "roles": [data.get("role", "ai_app")],
                "region": data.get("region", ""),
                "website": data.get("url", ""),
                "products": [],
                "financials": {},
                "current": {},
            }

            entities["companies"].append(new_company)
            save_json(entities_path, entities)

            self.send_json({
                "success": True,
                "message": f"Added: {name} ({data.get('role', 'ai_app')})",
                "company": new_company
            })

        except Exception as e:
            self.send_json({"success": False, "message": str(e)}, 500)

    # Suppress noisy logs
    def log_message(self, format, *args):
        if "/api/" in (args[0] if args else ""):
            print(f"  API: {args[0]}")
        # Suppress static file logs


def main():
    # Kill any existing server on the port
    try:
        import signal
        subprocess.run(["lsof", "-ti", f":{PORT}"], capture_output=True, text=True)
        result = subprocess.run(["lsof", "-ti", f":{PORT}"], capture_output=True, text=True)
        if result.stdout.strip():
            for pid in result.stdout.strip().split("\n"):
                os.kill(int(pid), signal.SIGTERM)
                print(f"  Killed existing server (PID {pid})")
    except:
        pass

    server = HTTPServer(("", PORT), AdminHandler)
    print(f"AI Ledger Command Centre")
    print(f"  Serving: {BETA_DIR}")
    print(f"  URL:     http://localhost:{PORT}/admin.html")
    print(f"  API:     POST /api/submit-decisions")
    print(f"           POST /api/add-source")
    print(f"           POST /api/add-company")
    print(f"  Press Ctrl+C to stop\n")

    # Open browser
    webbrowser.open(f"http://localhost:{PORT}/admin.html")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
        server.shutdown()


if __name__ == "__main__":
    main()

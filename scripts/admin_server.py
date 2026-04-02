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

            # ── Extract claims from the URL immediately ──
            pasted_text = data.get("content", "").strip()
            claims_extracted = 0
            extract_error = None
            try:
                claims_extracted = self.extract_claims_from_url(url, new_id, title, pasted_text)
                new_source["status"] = "active"
                new_source["last_checked"] = datetime.now().strftime("%Y-%m-%d")
                new_source["last_claims_count"] = claims_extracted
                save_json(registry_path, registry)
            except Exception as e:
                extract_error = str(e)

            msg = f"Added: {title}"
            if claims_extracted > 0:
                msg += f" — {claims_extracted} claim(s) extracted and ready for review"
            elif extract_error:
                msg += f" — extraction failed: {extract_error}"
            else:
                msg += " — no claims found"

            self.send_json({
                "success": True,
                "message": msg,
                "source": new_source,
                "claims_extracted": claims_extracted,
                "extract_error": extract_error
            })

        except Exception as e:
            self.send_json({"success": False, "message": str(e)}, 500)

    def extract_claims_from_url(self, url, source_id, source_title, pasted_text=None):
        """Fetch a URL (or use pasted text), send to Claude, extract structured claims, add to vault-inbox."""
        import re as _re
        import urllib.request as _urllib_request

        text = None

        if pasted_text and len(pasted_text.strip()) > 50:
            text = pasted_text.strip()[:8000]
        else:
            # Strategy 1: subprocess curl
            try:
                result = subprocess.run(
                    ["curl", "-sL", "-m", "15",
                     "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                     "-H", "Accept: text/html",
                     url],
                    capture_output=True, text=True, timeout=20
                )
                if result.returncode == 0 and len(result.stdout) > 200 and "Just a moment" not in result.stdout[:500]:
                    html = result.stdout
                    text = _re.sub(r'<script[^>]*>.*?</script>', '', html, flags=_re.DOTALL)
                    text = _re.sub(r'<style[^>]*>.*?</style>', '', text, flags=_re.DOTALL)
                    text = _re.sub(r'<[^>]+>', ' ', text)
                    text = _re.sub(r'\s+', ' ', text).strip()[:8000]
            except Exception:
                pass

            # Strategy 2: urllib
            if not text:
                try:
                    req = _urllib_request.Request(url, headers={
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                        "Accept": "text/html,application/xhtml+xml",
                    })
                    with _urllib_request.urlopen(req, timeout=15) as resp:
                        html = resp.read().decode("utf-8", errors="replace")
                    text = _re.sub(r'<script[^>]*>.*?</script>', '', html, flags=_re.DOTALL)
                    text = _re.sub(r'<style[^>]*>.*?</style>', '', text, flags=_re.DOTALL)
                    text = _re.sub(r'<[^>]+>', ' ', text)
                    text = _re.sub(r'\s+', ' ', text).strip()[:8000]
                except Exception:
                    pass

            if not text or len(text) < 100:
                raise Exception(
                    "Could not fetch page (site may block automated access). "
                    "Paste the article text into the content field and try again."
                )

        # 2. Get API key
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            for key_file in [os.path.expanduser("~/.anthropic_api_key"), os.path.join(ROOT_DIR, ".env")]:
                if os.path.exists(key_file):
                    with open(key_file) as f:
                        content = f.read().strip()
                        if content.startswith("sk-ant-"):
                            api_key = content
                        elif "ANTHROPIC_API_KEY" in content:
                            for line in content.split("\n"):
                                if line.startswith("ANTHROPIC_API_KEY="):
                                    api_key = line.split("=", 1)[1].strip().strip("\"'")
                    break
        if not api_key:
            raise Exception("No API key found. Set ANTHROPIC_API_KEY or save key in Settings.")

        # 3. Call Claude to extract claims
        prompt = f"""Extract ALL specific quantitative claims from this web page. Focus on:
- Revenue figures (ARR, annual revenue, monthly revenue, collected revenue)
- User/customer counts
- Growth rates
- Financial projections, targets, or guidance
- Token volumes, API usage stats
- Funding, valuation
- Cost figures, margins, losses
- Employee counts

For each claim, return a JSON array. Each item:
{{
  "claim": "ALWAYS start with the company name, e.g. 'OpenAI ended 2024 with $3.4B revenue' not 'We ended 2024...'",
  "entity": "company name this is about",
  "value": <numeric value — use billions for $B, millions for $M, raw number for counts>,
  "unit": "unit — e.g. $B, $B ARR, %, count, T tokens/day",
  "confidence": "verified|estimated|speculative",
  "dateOfClaim": "YYYY-MM-DD or best guess",
  "tags": ["relevant", "tags"]
}}

Return ONLY a valid JSON array. No markdown, no explanation. If no claims found, return [].

PAGE CONTENT:
{text}"""

        body = json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": prompt}]
        }).encode()

        req = _urllib_request.Request(
            "https://api.anthropic.com/v1/messages",
            data=body,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            }
        )

        with _urllib_request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())

        response_text = result["content"][0]["text"].strip()
        # Parse JSON (handle markdown wrapping)
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        claims = json.loads(response_text.strip())

        if not isinstance(claims, list) or len(claims) == 0:
            return 0

        # 4. Add claims to vault-inbox.json
        inbox_path = os.path.join(BETA_DIR, "vault-inbox.json")
        inbox = load_json(inbox_path)
        date_str = datetime.now().strftime("%Y%m%d")
        added = 0

        for i, claim in enumerate(claims):
            claim_id = f"extract-{date_str}-{source_id}-{i+1}"

            # Skip if already exists
            if any(item["id"] == claim_id for item in inbox["items"]):
                continue

            inbox["items"].append({
                "id": claim_id,
                "claim": claim.get("claim", ""),
                "value": claim.get("value"),
                "unit": claim.get("unit", ""),
                "sourceUrl": claim.get("sourceUrl", "") or self.path,
                "sourceType": "official" if "openai.com" in (claim.get("sourceUrl", "") or self.path) else "reporting",
                "sourceAuthor": claim.get("entity", source_title),
                "confidence": claim.get("confidence", "estimated"),
                "dateOfClaim": claim.get("dateOfClaim", datetime.now().strftime("%Y-%m-%d")),
                "dateAdded": datetime.now().strftime("%Y-%m-%d"),
                "usedOn": [],
                "tags": claim.get("tags", []),
                "notes": f"Auto-extracted from {source_title}",
                "status": "pending",
                "replaces": None,
                "source_id": source_id,
                "metricKey": None
            })
            added += 1

        inbox["lastProcessed"] = datetime.now().strftime("%Y-%m-%d")
        save_json(inbox_path, inbox)
        return added

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
        try:
            msg = str(args[0]) if args else ""
            if "/api/" in msg:
                print(f"  API: {msg}")
        except Exception:
            pass


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

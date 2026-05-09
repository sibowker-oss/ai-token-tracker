#!/usr/bin/env python3
"""
admin_server.py — Local server for the AI Ledger admin interface.

Serves admin static files AND handles API endpoints:
  POST /api/decision          — server-side decision write (claims.html / review.html)
                                 wq-100: writes data-updates/decisions/{date}-{ui}-{ts}.json,
                                 updates vault-inbox.json, triggers apply_pipeline.py
  POST /api/override          — wq-100: revert an auto-applied entity write and
                                 re-queue the source claim for human review.
  POST /api/submit-decisions  — legacy alias for /api/decision (kept for backward
                                 compatibility with older claims.html builds)
  POST /api/add-source        — add a source to sources-registry.json
  POST /api/add-company       — add a company to entities.json

Start: python3 scripts/admin_server.py
Opens: http://localhost:8080/admin.html

All writes go to repo files; no manual file moving needed. The review UIs require
this server to be running — they fail loudly rather than fall back to the
browser-download path that wq-100 eliminated.
"""

import json, os, sys, subprocess, webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from datetime import datetime

# macOS framework Python ships without root certs; pipeline subprocesses (scrape_*, monitor_*)
# fall over on HTTPS without this. Self-heal so the LaunchAgent and manual runs both work.
if not os.environ.get("SSL_CERT_FILE"):
    try:
        import certifi
        os.environ["SSL_CERT_FILE"] = certifi.where()
    except ImportError:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
SITE_DIR = ROOT_DIR
PORT = 8080


def load_json(path):
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


class AdminHandler(SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SITE_DIR, **kwargs)

    def do_POST(self):
        if self.path == "/api/decision":
            self.handle_decision()
        elif self.path == "/api/override":
            self.handle_override()
        elif self.path == "/api/submit-decisions":
            # Legacy alias — older claims.html / review.html builds POST here.
            # Route through the new wq-100 path so behaviour stays consistent.
            self.handle_decision()
        elif self.path == "/api/add-source":
            self.handle_add_source()
        elif self.path == "/api/add-company":
            self.handle_add_company()
        elif self.path == "/api/run-reconcile":
            self.handle_run_reconcile()
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

    # ── Decision (wq-100 server-side write) ──

    def handle_decision(self):
        """POST /api/decision — receives decisions from claims.html or review.html.

        Body shape:
          {
            "ui": "claims" | "review",
            "decisions": {
              "accepted": [...claim items...],
              "declined": [...],
              "parked":   [...],
              "raw_pool": [...],            # review.html only
              "new_fields_approved": [...], # review.html only
              "new_fields_rejected": [...]  # review.html only
            }
          }

        Writes the decision payload to data-updates/decisions/{date}-{ui}-{ts}.json,
        updates vault-inbox.json item statuses to match, then triggers
        apply_pipeline.py inline so the auto-apply / review-route gate runs
        immediately. The 5-minute apply latency target (D6) is satisfied
        because this runs synchronously in the POST handler.
        """
        try:
            body = self.read_body()
            # Tolerate both wrapped {ui, decisions} and bare-decision payloads
            # (the latter is what older claims.html builds POST to /api/submit-decisions).
            if isinstance(body, dict) and "decisions" in body:
                ui = (body.get("ui") or "unknown")[:32]
                decisions = body.get("decisions") or {}
            else:
                ui = "claims"
                decisions = body or {}

            now = datetime.now()
            date = now.strftime("%Y-%m-%d")
            ts = now.strftime("%H%M%S")
            decisions_dir = os.path.join(SITE_DIR, "data-updates", "decisions")
            os.makedirs(decisions_dir, exist_ok=True)
            decisions_path = os.path.join(decisions_dir, f"{date}-{ui}-{ts}.json")
            payload = {
                "ui": ui,
                "submitted_at": now.isoformat(timespec="seconds"),
                **decisions,
            }
            save_json(decisions_path, payload)

            # Append fingerprints to data-updates/decided-signatures.json so
            # claims.html / review.html stop resurfacing the same items on
            # subsequent loads. Done before apply_pipeline so the index is
            # ready by the time the user reloads the page.
            try:
                from _decided_signatures import record_decisions
                record_decisions(decisions, decided_at=now.isoformat(timespec="seconds"))
            except Exception as _sig_err:
                # Non-fatal: failing to write the suppress-list shouldn't block
                # the decision itself. Log to stderr for visibility.
                print(f"  WARN: decided-signatures append failed: {_sig_err}", file=sys.stderr)

            # Update vault-inbox.json statuses so the inbox reflects the human
            # decision before apply runs. Both review surfaces operate on
            # vault-inbox.json items — accepted/declined/parked/raw_pool all
            # change inbox state regardless of whether apply_pipeline.py
            # subsequently auto-applies or routes-to-review.
            inbox_updated = self._sync_inbox_status(decisions)

            # Run apply_pipeline.py to flow accepted claims through the gate.
            # Timeout is generous — full apply on a 200-claim vault runs in
            # <30s; 120s is comfortable headroom.
            result = subprocess.run(
                [sys.executable, os.path.join(SCRIPT_DIR, "apply_pipeline.py")],
                capture_output=True, text=True, cwd=ROOT_DIR, timeout=120
            )

            output = result.stdout + result.stderr
            success = result.returncode == 0

            accepted_count = len(decisions.get("accepted") or [])
            declined_count = len(decisions.get("declined") or [])
            parked_count = len(decisions.get("parked") or [])
            raw_pool_count = len(decisions.get("raw_pool") or [])
            new_fields_count = len(decisions.get("new_fields_approved") or [])

            # Best-effort: read the most recent apply_log.json entry so the
            # caller can show "X auto-applied, Y routed to review, Z anomalies".
            apply_summary = self._read_latest_apply_summary()

            msg_parts = []
            if accepted_count: msg_parts.append(f"{accepted_count} accepted")
            if declined_count: msg_parts.append(f"{declined_count} declined")
            if parked_count: msg_parts.append(f"{parked_count} parked")
            if raw_pool_count: msg_parts.append(f"{raw_pool_count} raw_pool")
            if new_fields_count: msg_parts.append(f"{new_fields_count} new fields")

            self.send_json({
                "success": success,
                "message": "Decisions applied: " + (", ".join(msg_parts) or "no changes"),
                "decisions_path": os.path.relpath(decisions_path, SITE_DIR),
                "inbox_updated": inbox_updated,
                "apply_returncode": result.returncode,
                "apply_summary": apply_summary,
                "details": output[-4000:],  # last 4KB of pipeline output
                "accepted": accepted_count,
                "declined": declined_count,
                "parked": parked_count,
                "raw_pool": raw_pool_count,
                "new_fields": new_fields_count,
            })

        except subprocess.TimeoutExpired:
            self.send_json({
                "success": False,
                "message": "apply_pipeline.py timed out (>120s). Decisions were saved but not applied.",
            }, 500)
        except Exception as e:
            self.send_json({"success": False, "message": str(e)}, 500)

    def _sync_inbox_status(self, decisions):
        """Update vault-inbox.json items based on the decision payload.

        accepted → status='accepted', declined → 'declined',
        parked → 'parked', raw_pool → 'raw_pool'. Items not in any decision
        bucket are left untouched. Returns the count of inbox items updated.
        """
        inbox_path = os.path.join(SITE_DIR, "vault-inbox.json")
        if not os.path.exists(inbox_path):
            return 0
        inbox = load_json(inbox_path)
        now_iso = datetime.now().isoformat(timespec="seconds")

        def _ids(bucket):
            return {(d.get("id") if isinstance(d, dict) else d)
                    for d in (decisions.get(bucket) or [])}

        accepted_ids = _ids("accepted")
        declined_ids = _ids("declined")
        parked_ids = _ids("parked")
        raw_pool_ids = _ids("raw_pool")

        updated = 0
        for item in inbox.get("items", []):
            iid = item.get("id")
            new_status = None
            if iid in accepted_ids:   new_status = "accepted"
            elif iid in declined_ids: new_status = "declined"
            elif iid in parked_ids:   new_status = "parked"
            elif iid in raw_pool_ids: new_status = "raw_pool"
            if new_status and item.get("status") != new_status:
                item["status"] = new_status
                item["decidedAt"] = now_iso
                item["decidedBy"] = "admin_server@wq-100"
                updated += 1

        if updated:
            inbox["lastProcessed"] = now_iso.split("T")[0]
            save_json(inbox_path, inbox)
        return updated

    def _read_latest_apply_summary(self):
        """Return the most-recent apply_pipeline run summary if available."""
        log_path = os.path.join(SITE_DIR, "data", "apply_log.json")
        if not os.path.exists(log_path):
            return None
        try:
            log = load_json(log_path)
            runs = log.get("runs") or []
            if not runs:
                return None
            last = runs[-1]
            return {
                "ts": last.get("ts"),
                "auto_applied": last.get("auto_applied", 0),
                "routed_to_review": last.get("routed_to_review", 0),
                "anomalies": last.get("anomalies", 0),
            }
        except Exception:
            return None

    # ── Override (wq-100 D9) ──

    def handle_override(self):
        """POST /api/override — revert an auto-applied entityDirectory write.

        Body shape:
          {
            "entity_slug": "cursor-(anysphere)",
            "year_key":    "2026" | "current",
            "field_key":   "arr",
            "revert_to_value": <number or null to clear>,
            "claim_id":    "dp-148",         # optional — re-queues this claim for review
            "reason":      "wrong attribution"
          }

        Reverts the value in entities.json, appends an override record to
        data/audits/wq-100-overrides.md, and (if claim_id given) flips the
        vault-data.json claim to pending_review=true so the next review
        session surfaces it. After revert, regenerates site-data.json so the
        public render reflects the rollback immediately.
        """
        try:
            body = self.read_body()
            entity_slug = (body.get("entity_slug") or "").strip().lower()
            year_key = (body.get("year_key") or "").strip()
            field_key = (body.get("field_key") or "").strip()
            revert_to = body.get("revert_to_value", None)
            claim_id = body.get("claim_id") or ""
            reason = (body.get("reason") or "").strip() or "no reason provided"

            if not entity_slug or not year_key or not field_key:
                self.send_json({
                    "success": False,
                    "message": "entity_slug, year_key, and field_key are required",
                }, 400)
                return

            entities_path = os.path.join(SITE_DIR, "entities.json")
            entities = load_json(entities_path)
            ent = next((c for c in entities.get("companies", [])
                        if c.get("slug", "").lower() == entity_slug), None)
            if not ent:
                self.send_json({
                    "success": False,
                    "message": f"entity '{entity_slug}' not found",
                }, 404)
                return

            if year_key == "current":
                container = ent.setdefault("current", {})
            else:
                container = ent.setdefault("financials", {}).setdefault(year_key, {})
            prior = container.get(field_key)

            if revert_to is None:
                container.pop(field_key, None)
            else:
                container[field_key] = revert_to

            # Provenance trail — drop the matching claim entry if present so
            # the next apply pass doesn't re-write the same value.
            prov_key = f"current.{field_key}" if year_key == "current" \
                else f"{year_key}.{field_key}"
            prov = ent.get("provenance", {}).get(prov_key)
            removed_prov = 0
            if prov and claim_id:
                before = len(prov.get("claims", []))
                prov["claims"] = [c for c in prov.get("claims", [])
                                  if c.get("id") != claim_id]
                removed_prov = before - len(prov["claims"])
                prov["claim_count"] = len(prov["claims"])

            save_json(entities_path, entities)

            # Re-queue the source claim for human review
            requeued = False
            if claim_id:
                vault_path = os.path.join(SITE_DIR, "vault-data.json")
                if os.path.exists(vault_path):
                    vault = load_json(vault_path)
                    for dp in vault.get("dataPoints", []):
                        if dp.get("id") == claim_id:
                            dp["pending_review"] = True
                            dp["pending_review_reason"] = (
                                f"override: {reason}"
                            )
                            # Drop the auto-apply usedOn marker so the
                            # orphan validator surfaces the claim again.
                            used = [k for k in (dp.get("usedOn") or [])
                                    if not k.endswith(":auto")]
                            dp["usedOn"] = used
                            requeued = True
                            break
                    if requeued:
                        save_json(vault_path, vault)

            # Log the override
            now = datetime.now()
            log_path = os.path.join(SITE_DIR, "data", "audits",
                                    "wq-100-overrides.md")
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            new_log = not os.path.exists(log_path)
            with open(log_path, "a", encoding="utf-8") as f:
                if new_log:
                    f.write("# wq-100 — Override log\n\n")
                    f.write("Reversion records from `POST /api/override`.\n\n")
                    f.write("| ts | entity | period | field | from | to | claim | reason |\n")
                    f.write("|---|---|---|---|---|---|---|---|\n")
                f.write(
                    f"| {now.isoformat(timespec='seconds')} "
                    f"| {entity_slug} | {year_key} | {field_key} "
                    f"| {prior!r} | {revert_to!r} | {claim_id} "
                    f"| {reason.replace('|', '/')} |\n"
                )

            # Regenerate site-data so the rollback surfaces immediately
            regen = subprocess.run(
                [sys.executable, os.path.join(SCRIPT_DIR, "generate_site_data.py")],
                capture_output=True, text=True, cwd=ROOT_DIR, timeout=120
            )

            self.send_json({
                "success": True,
                "message": (f"Reverted {entity_slug}.{year_key}.{field_key}: "
                            f"{prior!r} → {revert_to!r}"),
                "prior_value": prior,
                "new_value": revert_to,
                "claim_requeued": requeued,
                "provenance_dropped": removed_prov,
                "site_data_regenerated": regen.returncode == 0,
                "site_data_stderr": regen.stderr[-1000:] if regen.returncode else "",
            })

        except subprocess.TimeoutExpired:
            self.send_json({
                "success": False,
                "message": "site-data regeneration timed out (>120s); revert was saved.",
            }, 500)
        except Exception as e:
            self.send_json({"success": False, "message": str(e)}, 500)

    # ── Run reconciliation (wq-099) ──

    def handle_run_reconcile(self):
        """Manual trigger for scripts/reconcile_pipeline.py.

        Called from status.html#pipeline's "Run reconciliation now" button so
        the operator can refresh the snapshot without waiting for the next
        nightly auto_update.py run.
        """
        try:
            result = subprocess.run(
                [sys.executable, os.path.join(SCRIPT_DIR, "reconcile_pipeline.py")],
                capture_output=True, text=True, cwd=ROOT_DIR, timeout=60,
            )
            output = (result.stdout or "") + (result.stderr or "")
            success = result.returncode == 0

            health_path = os.path.join(SITE_DIR, "data", "pipeline-health-latest.json")
            health = None
            if os.path.exists(health_path):
                try:
                    health = load_json(health_path)
                except Exception:
                    health = None

            self.send_json({
                "success": success,
                "message": "Reconciliation complete" if success else "Reconciliation failed",
                "details": output[-2000:],
                "asOf": (health or {}).get("asOf"),
                "alertCount": (health or {}).get("alertCount"),
            })
        except subprocess.TimeoutExpired:
            self.send_json({
                "success": False,
                "message": "reconcile_pipeline.py timed out (>60s)",
            }, 500)
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

            registry_path = os.path.join(SITE_DIR, "sources-registry.json")
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
        inbox_path = os.path.join(SITE_DIR, "vault-inbox.json")
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

            entities_path = os.path.join(SITE_DIR, "entities.json")
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
    print(f"  Serving: {SITE_DIR}")
    print(f"  URL:     http://localhost:{PORT}/admin.html")
    print(f"  API:     POST /api/decision         (claims.html / review.html — wq-100)")
    print(f"           POST /api/override         (revert auto-apply — wq-100)")
    print(f"           POST /api/submit-decisions (legacy alias)")
    print(f"           POST /api/run-reconcile    (status.html#pipeline — wq-099)")
    print(f"           POST /api/add-source")
    print(f"           POST /api/add-company")
    print(f"  Press Ctrl+C to stop\n")

    # Open browser unless --no-browser (used by the LaunchAgent to run headless on login).
    if "--no-browser" not in sys.argv:
        webbrowser.open(f"http://localhost:{PORT}/admin.html")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
        server.shutdown()


if __name__ == "__main__":
    main()

"""
FastAPI web server for Cold Email Automation Dashboard.
Run with: python api.py
"""
import asyncio
import base64
import json
import os
import queue
import sys
import threading
from pathlib import Path
from typing import List, Optional

import urllib.parse
import requests as _requests

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel

from database import (
    init_db, create_user_email, login_email, upsert_google_user,
    get_user_by_id, create_session, get_session_user, delete_session,
    list_campaigns, get_campaign, get_active_campaign,
    create_campaign, update_campaign, activate_campaign,
    delete_campaign, update_campaign_stats,
)

# ---------------------------------------------------------------------------
# Credential bootstrapping (for cloud deployment)
# Set these env vars to base64-encoded file contents:
#   GOOGLE_CREDENTIALS_B64  -> credentials.json
#   GMAIL_CREDENTIALS_B64   -> gmail_credentials.json
#   GMAIL_TOKEN_B64         -> gmail_token.json
# ---------------------------------------------------------------------------
def _write_cred_from_env(env_var: str, filename: str) -> None:
    val = os.getenv(env_var)
    if val and not Path(filename).exists():
        try:
            Path(filename).write_bytes(base64.b64decode(val))
            print(f"[startup] Wrote {filename} from env var {env_var}")
        except Exception as e:
            print(f"[startup] Failed to write {filename}: {e}")

_write_cred_from_env("GOOGLE_CREDENTIALS_B64", "credentials.json")
_write_cred_from_env("GMAIL_CREDENTIALS_B64", "gmail_credentials.json")
_write_cred_from_env("GMAIL_TOKEN_B64", "gmail_token.json")

# ---------------------------------------------------------------------------
# Import project config (must happen after credentials are written)
# ---------------------------------------------------------------------------
from config import TARGET, EMAIL, AI, SHEETS, SCRAPING  # noqa: E402

# ---------------------------------------------------------------------------
# Log capture — tee stdout into a thread-safe queue for SSE streaming
# ---------------------------------------------------------------------------
_log_queue: queue.Queue = queue.Queue(maxsize=2000)


class _LogTee:
    def __init__(self, original):
        self.original = original

    def write(self, text: str):
        self.original.write(text)
        if text.strip():
            try:
                _log_queue.put_nowait(text.strip())
            except queue.Full:
                pass

    def flush(self):
        self.original.flush()

    def isatty(self):
        return self.original.isatty()

    def fileno(self):
        return self.original.fileno()


sys.stdout = _LogTee(sys.stdout)

# ---------------------------------------------------------------------------
# Pipeline state
# ---------------------------------------------------------------------------
_state: dict = {"running": False, "step": "", "error": "", "stop_requested": False}


def _guard():
    if _state["running"]:
        raise HTTPException(409, "A pipeline step is already running: " + _state["step"])


def _run_sync(fn, step: str):
    _guard()

    def _wrap():
        _state.update(running=True, step=step, error="", stop_requested=False)
        try:
            import pg_database as _pgdb
            _pgdb._stop_requested = False
            _pgdb._pipeline_notice = ""
        except Exception:
            pass
        try:
            fn()
        except Exception as e:
            if not _state.get("stop_requested"):
                _state["error"] = str(e)
                _log_queue.put_nowait(f"ERROR: {step} failed: {e}")
        finally:
            if not _state.get("stop_requested"):
                _state.update(running=False, step="")

    threading.Thread(target=_wrap, daemon=True).start()


def _run_async(coro_fn, step: str):
    _guard()

    def _wrap():
        _state.update(running=True, step=step, error="", stop_requested=False)
        try:
            import pg_database as _pgdb
            _pgdb._stop_requested = False
            _pgdb._pipeline_notice = ""
        except Exception:
            pass
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(coro_fn())
            loop.close()
        except Exception as e:
            if not _state.get("stop_requested"):
                _state["error"] = str(e)
                _log_queue.put_nowait(f"ERROR: {step} failed: {e}")
        finally:
            if not _state.get("stop_requested"):
                _state.update(running=False, step="")

    threading.Thread(target=_wrap, daemon=True).start()


# ---------------------------------------------------------------------------
# DB init + restore active campaign config
# ---------------------------------------------------------------------------
init_db()

_active_camp = get_active_campaign()
if _active_camp and _active_camp.get("config"):
    TARGET.update(_active_camp["config"])
    print(f"[startup] Loaded active campaign: {_active_camp['name']}")
    try:
        from pg_database import PostgresDatabase
        PostgresDatabase().claim_unassigned(_active_camp["id"])
    except Exception:
        pass

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(title="LeadFlow")

# ---------------------------------------------------------------------------
# Auth middleware — protect /dashboard and all /api/* except /api/auth/*
# ---------------------------------------------------------------------------
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    path = request.url.path
    public = (
        path in ("/", "/auth")
        or path.startswith("/static")
        or path.startswith("/api/auth")
        or path.startswith("/api/track")
    )
    if public:
        return await call_next(request)

    token = request.cookies.get("session") or \
            request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    user = get_session_user(token) if token else None

    if not user:
        if path.startswith("/api/"):
            return JSONResponse({"detail": "Not authenticated"}, status_code=401)
        return RedirectResponse("/auth")

    return await call_next(request)


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------
GOOGLE_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
APP_URL              = os.getenv("APP_URL", "http://localhost:8000")
COOKIE_SECURE        = APP_URL.startswith("https")


def _set_session(response: Response, token: str) -> None:
    response.set_cookie(
        "session", token,
        httponly=True, secure=COOKIE_SECURE, samesite="lax",
        max_age=86400 * 30,
    )


def _get_user(request: Request) -> dict:
    """Extract the authenticated user from the session cookie. Raises 401 if missing."""
    token = request.cookies.get("session") or \
            request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    user = get_session_user(token) if token else None
    if not user:
        raise HTTPException(401, "Not authenticated")
    return user


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------
class TargetConfig(BaseModel):
    city: str
    state: str = ""
    country: str
    localities: List[str]
    niche: str
    niche_plural: str
    industry: str
    your_service: str
    your_service_benefit: str
    pain_point: str


class EmailConfig(BaseModel):
    your_name: str
    your_email: str
    smtp_host: str = ""
    smtp_port: int = 465
    smtp_user: str = ""
    smtp_password: str = ""   # only written if non-empty
    imap_host: str = ""
    max_per_day: int = 1000
    batch_size: int = 20
    delay_between_sends: int = 30


class EmailCreativeConfig(BaseModel):
    email_mode:             str = "ai"
    ai_tone:                str = "casual_professional"
    ai_guidelines:          str = ""
    ai_sample_email:        str = ""
    email_template_subject: str = ""
    email_template_body:    str = ""


class ScrapeRequest(BaseModel):
    max_results: int = 20
    priority: str = "HIGH"
    campaign_id: Optional[int] = None


class SendRequest(BaseModel):
    batch_size: int = 20
    campaign_id: Optional[int] = None


class CampaignOnlyRequest(BaseModel):
    campaign_id: Optional[int] = None


# ---------------------------------------------------------------------------
# Auth endpoints
# ---------------------------------------------------------------------------
class SignupRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/api/auth/signup")
def signup(req: SignupRequest, response: Response):
    if len(req.password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters")
    user = create_user_email(req.email, req.name, req.password)
    if not user:
        raise HTTPException(409, "An account with that email already exists")
    token = create_session(user["id"])
    _set_session(response, token)
    return {"ok": True, "name": user["name"], "email": user["email"]}


@app.post("/api/auth/login")
def login(req: LoginRequest, response: Response):
    user = login_email(req.email, req.password)
    if not user:
        raise HTTPException(401, "Invalid email or password")
    token = create_session(user["id"])
    _set_session(response, token)
    return {"ok": True, "name": user["name"], "email": user["email"]}


@app.post("/api/auth/logout")
def logout(request: Request, response: Response):
    token = request.cookies.get("session", "")
    if token:
        delete_session(token)
    response.delete_cookie("session")
    return {"ok": True}


@app.get("/api/auth/me")
def get_me(request: Request):
    token = request.cookies.get("session", "")
    user = get_session_user(token)
    if not user:
        raise HTTPException(401, "Not authenticated")
    return {"id": user["id"], "name": user["name"], "email": user["email"], "plan": user["plan"]}


@app.get("/api/auth/google")
def google_oauth_start():
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(501, "Google OAuth is not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET env vars.")
    params = urllib.parse.urlencode({
        "client_id":     GOOGLE_CLIENT_ID,
        "redirect_uri":  f"{APP_URL}/api/auth/google/callback",
        "response_type": "code",
        "scope":         "openid email profile",
        "access_type":   "online",
    })
    return RedirectResponse(f"https://accounts.google.com/o/oauth2/v2/auth?{params}")


@app.get("/api/auth/google/callback")
def google_oauth_callback(code: str = "", error: str = ""):
    if error or not code:
        return RedirectResponse("/auth?error=google_cancelled")
    try:
        # Exchange code for tokens
        token_resp = _requests.post("https://oauth2.googleapis.com/token", data={
            "code":          code,
            "client_id":     GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri":  f"{APP_URL}/api/auth/google/callback",
            "grant_type":    "authorization_code",
        }, timeout=10)
        token_data = token_resp.json()
        access_token = token_data.get("access_token")
        if not access_token:
            return RedirectResponse("/auth?error=google_failed")

        # Get user info
        info = _requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        ).json()

        user = upsert_google_user(info["id"], info["email"], info.get("name", info["email"]))
        token = create_session(user["id"])

        resp = RedirectResponse("/dashboard")
        _set_session(resp, token)
        return resp
    except Exception as e:
        print(f"Google OAuth error: {e}")
        return RedirectResponse("/auth?error=google_failed")


# ---------------------------------------------------------------------------
# Stats / data endpoints
# ---------------------------------------------------------------------------
@app.get("/api/stats")
def get_stats(request: Request):
    try:
        user = _get_user(request)
        camps = list_campaigns(user["id"])
        camp_ids = [c["id"] for c in camps]
        from pg_database import PostgresDatabase
        return PostgresDatabase().get_stats_by_campaigns(camp_ids)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/config")
def get_config():
    return {
        "target": dict(TARGET),
        "email": dict(EMAIL),
        "scraping": dict(SCRAPING),
    }


@app.post("/api/config/target")
def update_target(cfg: TargetConfig):
    TARGET.update(cfg.model_dump())
    SHEETS["spreadsheet_name"] = f"{TARGET['niche'].title()} - {TARGET['city']}"
    return {"ok": True}


@app.post("/api/config/email")
def update_email_config(cfg: EmailConfig):
    data = cfg.model_dump()
    # Don't overwrite saved password with blank if user left the field empty
    if not data.get("smtp_password"):
        data.pop("smtp_password", None)
    EMAIL.update(data)
    return {"ok": True}


# ---------------------------------------------------------------------------
# Campaign endpoints
# ---------------------------------------------------------------------------
@app.get("/api/campaigns")
def get_campaigns(request: Request):
    user = _get_user(request)
    uid = user["id"]
    camps = list_campaigns(uid)
    # Enrich each campaign with live stats from pg_database
    try:
        from pg_database import PostgresDatabase
        pg = PostgresDatabase()
        for camp in camps:
            try:
                bizes = pg.get_businesses_by_campaign(camp["id"])
                sent  = sum(1 for b in bizes if b.get("Email Sent") in ("Yes", True))
                update_campaign_stats(camp["id"], len(bizes), sent)
            except Exception:
                pass
        camps = list_campaigns(uid)
    except Exception:
        pass
    return camps


class SuggestAreasRequest(BaseModel):
    city: str
    country: str

@app.post("/api/campaigns/suggest-areas")
def suggest_areas(req: SuggestAreasRequest):
    """Use OpenRouter AI to suggest searchable areas/neighbourhoods for a given city."""
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    if not api_key:
        raise HTTPException(500, "OPENROUTER_API_KEY not set")
    prompt = (
        f"List 15 specific, searchable neighbourhoods, districts, or suburbs of {req.city}, {req.country}. "
        "Return ONLY a plain list — one neighbourhood per line, no numbering, no bullet points, no extra text. "
        "Make sure every entry is a real, well-known area that would return results on Google Maps."
    )
    try:
        resp = _requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "arcee-ai/trinity-large-preview:free",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 512,
                "temperature": 0.7,
            },
            timeout=30,
        )
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"].strip()
        areas = [l.strip() for l in text.splitlines() if l.strip()]
        return {"areas": areas}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/campaigns")
def create_campaign_endpoint(request: Request, cfg: TargetConfig):
    user = _get_user(request)
    camp = create_campaign(cfg.model_dump(), user_id=user["id"])
    return camp


@app.put("/api/campaigns/{campaign_id}")
def update_campaign_endpoint(request: Request, campaign_id: int, cfg: TargetConfig):
    user = _get_user(request)
    camp = get_campaign(campaign_id)
    if not camp:
        raise HTTPException(404, "Campaign not found")
    if camp.get("user_id", 0) not in (0, user["id"]):
        raise HTTPException(403, "Not your campaign")
    camp = update_campaign(campaign_id, cfg.model_dump())
    # If this was the active campaign, sync TARGET in memory
    if camp["is_active"]:
        TARGET.update(camp["config"])
        SHEETS["spreadsheet_name"] = f"{TARGET['niche'].title()} - {TARGET['city']}"
    return camp


@app.post("/api/campaigns/{campaign_id}/activate")
def activate_campaign_endpoint(request: Request, campaign_id: int):
    user = _get_user(request)
    camp = get_campaign(campaign_id)
    if not camp:
        raise HTTPException(404, "Campaign not found")
    if camp.get("user_id", 0) not in (0, user["id"]):
        raise HTTPException(403, "Not your campaign")
    camp = activate_campaign(campaign_id, user_id=user["id"])
    TARGET.update(camp["config"])
    SHEETS["spreadsheet_name"] = f"{TARGET['niche'].title()} - {TARGET['city']}"
    try:
        from pg_database import PostgresDatabase
        PostgresDatabase().claim_unassigned(campaign_id)
    except Exception:
        pass
    print(f"[campaign] Activated: {camp['name']}")
    return camp


@app.delete("/api/campaigns/{campaign_id}")
def delete_campaign_endpoint(request: Request, campaign_id: int):
    user = _get_user(request)
    camp = get_campaign(campaign_id)
    if not camp:
        raise HTTPException(404, "Campaign not found")
    if camp.get("user_id", 0) not in (0, user["id"]):
        raise HTTPException(403, "Not your campaign")
    if camp["is_active"]:
        raise HTTPException(400, "Cannot delete the active campaign. Activate another campaign first.")
    delete_campaign(campaign_id)
    return {"ok": True}


@app.get("/api/email/creative")
def get_email_creative():
    return {
        "email_mode":             EMAIL.get("email_mode", "ai"),
        "ai_tone":                EMAIL.get("ai_tone", "casual_professional"),
        "ai_guidelines":          EMAIL.get("ai_guidelines", ""),
        "ai_sample_email":        EMAIL.get("ai_sample_email", ""),
        "email_template_subject": EMAIL.get("email_template_subject", ""),
        "email_template_body":    EMAIL.get("email_template_body", ""),
    }


@app.post("/api/email/creative")
def update_email_creative(cfg: EmailCreativeConfig):
    EMAIL.update(cfg.model_dump())
    return {"ok": True}


@app.get("/api/email/preview-generated")
def preview_generated_email():
    """Generate a live AI/template preview using the first available lead."""
    try:
        from email_generator import EmailGenerator
        gen = EmailGenerator()
        from pg_database import PostgresDatabase
        db = PostgresDatabase()
        businesses = db.get_high_priority_businesses() or list(db.get_all_businesses())[:1]
        if not businesses:
            return {"subject": "No leads yet", "body": "Run the pipeline first to scrape some businesses."}
        result = gen.generate_email(businesses[0])
        if result:
            result["business_name"] = businesses[0].get("Name", "")
        return result or {"subject": "Preview failed", "body": "Could not generate preview."}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/leads")
def get_leads(limit: int = 100, offset: int = 0, filter: str = "all"):
    try:
        from pg_database import PostgresDatabase
        db = PostgresDatabase()
        if filter == "high_priority":
            items = db.get_high_priority_businesses()
        elif filter == "with_emails":
            items = [b for b in db.get_all_businesses() if b.get("Email")]
        else:
            items = list(db.get_all_businesses())
        return {"total": len(items), "items": items[offset: offset + limit]}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/campaigns/{campaign_id}/leads")
def get_campaign_leads(request: Request, campaign_id: int, limit: int = 100, offset: int = 0, filter: str = "all"):
    user = _get_user(request)
    camp = get_campaign(campaign_id)
    if not camp:
        raise HTTPException(404, "Campaign not found")
    if camp.get("user_id", 0) not in (0, user["id"]):
        raise HTTPException(403, "Not your campaign")
    try:
        from pg_database import PostgresDatabase
        items = PostgresDatabase().get_businesses_by_campaign(campaign_id, filter=filter)
        return {"total": len(items), "items": items[offset: offset + limit]}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/campaigns/{campaign_id}/emails")
def get_campaign_emails(request: Request, campaign_id: int):
    """Return generated emails for a campaign, keyed by Agency ID."""
    user = _get_user(request)
    camp = get_campaign(campaign_id)
    if not camp:
        raise HTTPException(404, "Campaign not found")
    if camp.get("user_id", 0) not in (0, user["id"]):
        raise HTTPException(403, "Not your campaign")
    try:
        from pg_database import PostgresDatabase
        emails = PostgresDatabase().get_all_emails_by_campaign(campaign_id)
        return {e["Agency ID"]: e for e in emails if e}
    except Exception as e:
        raise HTTPException(500, str(e))


class ManualSendRequest(BaseModel):
    business_id: str


@app.post("/api/businesses/send-manual")
def send_manual_email(req: ManualSendRequest):
    """Manually send the generated email for a single business."""
    try:
        from pg_database import PostgresDatabase
        db = PostgresDatabase()
        email_data = db.get_generated_email_by_agency(req.business_id)
        if not email_data:
            raise HTTPException(404, "No generated email found for this business")
        from email_sender import GmailSender
        sender = GmailSender()
        ok = sender.send_email(
            email_data["To Email"],
            email_data["Subject"],
            email_data["Body"],
            email_id=email_data["Email ID"],
        )
        if ok:
            db.mark_email_sent(req.business_id)
            return {"ok": True}
        raise HTTPException(500, "SMTP send failed")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


# ---------------------------------------------------------------------------
# Pipeline status
# ---------------------------------------------------------------------------
@app.get("/api/pipeline/status")
def pipeline_status():
    try:
        import pg_database as _pgdb
        notice = _pgdb._pipeline_notice or ""
        camp_name = ""
        if notice:
            active = get_active_campaign()
            camp_name = active["name"] if active else ""
        return {**_state, "notice": notice, "notice_campaign": camp_name}
    except Exception:
        return _state


@app.post("/api/pipeline/stop")
def stop_pipeline():
    if not _state["running"]:
        return {"ok": False, "message": "No pipeline is running"}
    _state.update(running=False, step="", stop_requested=True)
    try:
        import pg_database as _pgdb
        _pgdb._stop_requested = True
        _pgdb._pipeline_notice = "Pipeline was stopped manually."
    except Exception:
        pass
    try:
        _log_queue.put_nowait("Pipeline stopped by user")
    except Exception:
        pass
    return {"ok": True}


# ---------------------------------------------------------------------------
# Pipeline action endpoints
# ---------------------------------------------------------------------------
def _resolve_campaign(user: dict, campaign_id: int = None) -> tuple:
    """
    Return (campaign, camp_id_str) for the pipeline step.

    Priority:
      1. Explicit campaign_id in the request — verify it belongs to this user, use it.
      2. User's currently-active campaign — fallback when no explicit id given.
    Raises HTTP 400 if neither resolves to a valid campaign.
    """
    if campaign_id:
        camp = get_campaign(campaign_id)
        if not camp:
            raise HTTPException(404, "Campaign not found")
        if camp.get("user_id", 0) not in (0, user["id"]):
            raise HTTPException(403, "Not your campaign")
        # Auto-activate so TARGET config reflects this campaign
        if not camp["is_active"]:
            camp = activate_campaign(campaign_id, user_id=user["id"])
        # Always sync TARGET to this campaign's config
        TARGET.update(camp["config"])
        SHEETS["spreadsheet_name"] = f"{TARGET['niche'].title()} - {TARGET['city']}"
        return camp, str(camp["id"])

    # Fallback: use whatever campaign the user last activated
    active = get_active_campaign(user["id"])
    if not active:
        raise HTTPException(
            400,
            "No active campaign. Go to Campaigns and activate one first."
        )
    return active, str(active["id"])


@app.post("/api/pipeline/scrape")
def start_scrape(request: Request, req: ScrapeRequest):
    user = _get_user(request)
    _, camp_id = _resolve_campaign(user, req.campaign_id)

    async def _do():
        import pg_database as _pgdb
        _pgdb._current_campaign_id = camp_id
        from scraper import GoogleMapsScraper
        await GoogleMapsScraper().scrape_all_localities(max_per_locality=req.max_results)

    _run_async(_do, "Scraping Google Maps")
    return {"ok": True}


@app.post("/api/pipeline/analyze")
def start_analyze(request: Request, req: CampaignOnlyRequest = CampaignOnlyRequest()):
    user = _get_user(request)
    _, camp_id = _resolve_campaign(user, req.campaign_id)

    def _do():
        import pg_database as _pgdb
        _pgdb._current_campaign_id = camp_id
        from analyzer import WebsiteAnalyzer
        WebsiteAnalyzer().analyze_all_businesses()

    _run_sync(_do, "Analyzing Websites")
    return {"ok": True}


@app.post("/api/pipeline/find-emails")
def start_find_emails(request: Request, req: ScrapeRequest):
    user = _get_user(request)
    _, camp_id = _resolve_campaign(user, req.campaign_id)

    def _do():
        import pg_database as _pgdb
        _pgdb._current_campaign_id = camp_id
        from email_finder import EmailFinder
        EmailFinder().find_emails_for_businesses(priority=req.priority)

    _run_sync(_do, "Finding Emails")
    return {"ok": True}


@app.post("/api/pipeline/generate-emails")
def start_generate(request: Request, req: CampaignOnlyRequest = CampaignOnlyRequest()):
    user = _get_user(request)
    _, camp_id = _resolve_campaign(user, req.campaign_id)

    def _do():
        import pg_database as _pgdb
        _pgdb._current_campaign_id = camp_id
        from email_generator import EmailGenerator
        EmailGenerator().generate_for_all_high_priority()

    _run_sync(_do, "Generating Emails")
    return {"ok": True}


@app.post("/api/pipeline/send-emails")
def start_send(request: Request, req: SendRequest):
    user = _get_user(request)
    _, camp_id = _resolve_campaign(user, req.campaign_id)

    def _do():
        import pg_database as _pgdb
        _pgdb._current_campaign_id = camp_id
        from email_sender import GmailSender
        sender = GmailSender()
        result = sender.test_connection()
        if not result.get("ok"):
            raise Exception(
                result.get("error") or
                f"Email mismatch: token is for '{result.get('authenticated_as')}' "
                f"but config says '{result.get('configured_as')}'. "
                "Reset the token from the dashboard and re-authenticate."
            )
        sender.send_batch(batch_size=req.batch_size)

    _run_sync(_do, f"Sending Emails (batch={req.batch_size})")
    return {"ok": True}


@app.post("/api/pipeline/full")
def start_full(request: Request, req: ScrapeRequest):
    user = _get_user(request)
    _, camp_id = _resolve_campaign(user, req.campaign_id)

    async def _do():
        import pg_database as _pgdb
        _pgdb._current_campaign_id = camp_id
        from scraper import GoogleMapsScraper
        from analyzer import WebsiteAnalyzer
        from email_finder import EmailFinder
        from email_generator import EmailGenerator

        print("Starting full pipeline...")

        print("Step 1/4: Scraping Google Maps...")
        await GoogleMapsScraper().scrape_all_localities(max_per_locality=req.max_results)

        print("Step 2/4: Analyzing websites...")
        WebsiteAnalyzer().analyze_all_businesses()

        print("Step 3/4: Finding emails...")
        EmailFinder().find_emails_for_businesses(priority=req.priority)

        print("Step 4/4: Generating personalized emails...")
        EmailGenerator().generate_for_all_high_priority()

        print("Full pipeline complete!")

    _run_async(_do, "Full Pipeline")
    return {"ok": True}


# ---------------------------------------------------------------------------
# Email connection check (SMTP)
# ---------------------------------------------------------------------------
@app.get("/api/email/check")
def check_email():
    """Test SMTP connection with current config and return status."""
    try:
        from email_sender import GmailSender
        sender = GmailSender()
        result = sender.test_connection()
        result["status"] = "ok" if result.get("ok") else "error"
        result["message"] = (
            f"Connected — sending as {result.get('authenticated_as')} "
            f"via {result.get('host')}:{result.get('port')}"
            if result.get("ok")
            else result.get("error", "Connection failed")
        )
        return result
    except Exception as e:
        return {
            "ok":      False,
            "status":  "error",
            "message": str(e),
            "host":    EMAIL.get("smtp_host", ""),
            "port":    EMAIL.get("smtp_port", 587),
        }


# ---------------------------------------------------------------------------
# SSE log stream
# ---------------------------------------------------------------------------
@app.get("/api/logs/stream")
async def stream_logs():
    async def _gen():
        yield f"data: {json.dumps({'msg': 'Connected to live logs'})}\n\n"
        while True:
            msgs = []
            try:
                while True:
                    msgs.append(_log_queue.get_nowait())
            except queue.Empty:
                pass
            for m in msgs:
                yield f"data: {json.dumps({'msg': m})}\n\n"
            if not msgs:
                yield f"data: {json.dumps({'ping': 1})}\n\n"
            await asyncio.sleep(0.25)

    return StreamingResponse(
        _gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ---------------------------------------------------------------------------
# Open-tracking pixel (public — no auth required)
# ---------------------------------------------------------------------------
_PIXEL = bytes.fromhex(
    "47494638396101000100800000ffffff00000021f90400000000002c"
    "00000000010001000002024401003b"
)

@app.get("/api/track/open/{email_id}")
async def track_open(email_id: str):
    """1×1 GIF pixel. Records an open when an email client loads it."""
    try:
        from pg_database import PostgresDatabase
        PostgresDatabase().record_email_open(email_id)
    except Exception:
        pass
    from fastapi.responses import Response
    return Response(content=_PIXEL, media_type="image/gif",
                    headers={"Cache-Control": "no-cache, no-store"})


# ---------------------------------------------------------------------------
# Inbox endpoints
# ---------------------------------------------------------------------------
class ComposeRequest(BaseModel):
    to: str
    subject: str
    body: str
    business_id: str = ""


@app.post("/api/inbox/sync")
def inbox_sync():
    try:
        from inbox_sync import sync_inbox
        result = sync_inbox()
        return result
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/inbox/messages")
def inbox_messages(unread_only: bool = False, limit: int = 100):
    try:
        from pg_database import PostgresDatabase
        msgs = PostgresDatabase().get_inbox_messages(unread_only=unread_only, limit=limit)
        return msgs
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/inbox/messages/{msg_id}/read")
def mark_read(msg_id: int):
    try:
        from pg_database import PostgresDatabase
        PostgresDatabase().mark_inbox_read(msg_id)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/inbox/sent")
def inbox_sent(campaign_id: int = None):
    try:
        from pg_database import PostgresDatabase
        rows = PostgresDatabase().get_sent_with_tracking(campaign_id=campaign_id)
        return rows
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/inbox/stats")
def inbox_stats():
    try:
        from pg_database import PostgresDatabase
        return PostgresDatabase().get_inbox_stats()
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/inbox/compose")
def inbox_compose(req: ComposeRequest):
    try:
        from email_sender import GmailSender
        from pg_database import PostgresDatabase
        sender = GmailSender()
        ok = sender.send_email(req.to, req.subject, req.body)
        if not ok:
            raise HTTPException(500, "SMTP send failed")
        if req.business_id:
            PostgresDatabase()._log("compose_send", "business", req.business_id,
                                    {"to": req.to, "subject": req.subject})
        return {"ok": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


# ---------------------------------------------------------------------------
# Serve pages
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def serve_landing():
    return HTMLResponse(Path("static/landing.html").read_text(encoding="utf-8"))

@app.get("/auth", response_class=HTMLResponse)
async def serve_auth():
    return HTMLResponse(Path("static/auth.html").read_text(encoding="utf-8"))

@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    return HTMLResponse(Path("static/index.html").read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"Starting web server on http://0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False, use_colors=False)

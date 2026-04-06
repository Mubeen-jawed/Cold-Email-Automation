"""
User accounts, session management, and campaigns — SQLite, no external deps.
"""
import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import time

DB_PATH = os.getenv("DB_PATH", "app.db")


def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with _conn() as c:
        c.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                email         TEXT    UNIQUE NOT NULL,
                name          TEXT    NOT NULL DEFAULT '',
                password_hash TEXT,
                google_id     TEXT    UNIQUE,
                plan          TEXT    NOT NULL DEFAULT 'free',
                created_at    INTEGER NOT NULL DEFAULT (unixepoch())
            );
            CREATE TABLE IF NOT EXISTS sessions (
                token      TEXT    PRIMARY KEY,
                user_id    INTEGER NOT NULL,
                expires_at INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS campaigns (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id      INTEGER NOT NULL DEFAULT 0,
                name         TEXT    NOT NULL,
                config_json  TEXT    NOT NULL DEFAULT '{}',
                is_active    INTEGER NOT NULL DEFAULT 0,
                status       TEXT    NOT NULL DEFAULT 'idle',
                leads_found  INTEGER NOT NULL DEFAULT 0,
                emails_sent  INTEGER NOT NULL DEFAULT 0,
                created_at   TEXT    NOT NULL DEFAULT (datetime('now'))
            );
        """)
        # Add user_id column to existing campaigns tables that predate this migration
        try:
            c.execute("ALTER TABLE campaigns ADD COLUMN user_id INTEGER NOT NULL DEFAULT 0")
        except Exception:
            pass  # Column already exists


# ── Password helpers ──────────────────────────────────────────────────────────

def _hash_pw(password: str) -> str:
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 260_000)
    return salt.hex() + ":" + key.hex()


def _verify_pw(password: str, stored: str) -> bool:
    try:
        salt_hex, key_hex = stored.split(":", 1)
        salt = bytes.fromhex(salt_hex)
        key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 260_000)
        return hmac.compare_digest(key.hex(), key_hex)
    except Exception:
        return False


# ── User CRUD ─────────────────────────────────────────────────────────────────

def create_user_email(email: str, name: str, password: str) -> dict | None:
    """Returns user dict on success, None if email already taken."""
    with _conn() as c:
        try:
            c.execute(
                "INSERT INTO users (email, name, password_hash) VALUES (?, ?, ?)",
                (email.lower().strip(), name.strip(), _hash_pw(password)),
            )
            return dict(c.execute("SELECT * FROM users WHERE email = ?", (email.lower(),)).fetchone())
        except sqlite3.IntegrityError:
            return None


def login_email(email: str, password: str) -> dict | None:
    user = get_user_by_email(email)
    if not user or not user.get("password_hash"):
        return None
    return user if _verify_pw(password, user["password_hash"]) else None


def upsert_google_user(google_id: str, email: str, name: str) -> dict:
    with _conn() as c:
        row = c.execute("SELECT * FROM users WHERE google_id = ?", (google_id,)).fetchone()
        if row:
            return dict(row)
        existing = c.execute("SELECT * FROM users WHERE email = ?", (email.lower(),)).fetchone()
        if existing:
            c.execute("UPDATE users SET google_id = ? WHERE email = ?", (google_id, email.lower()))
        else:
            c.execute(
                "INSERT INTO users (email, name, google_id) VALUES (?, ?, ?)",
                (email.lower(), name, google_id),
            )
        return dict(c.execute("SELECT * FROM users WHERE email = ?", (email.lower(),)).fetchone())


def get_user_by_email(email: str) -> dict | None:
    with _conn() as c:
        row = c.execute("SELECT * FROM users WHERE email = ?", (email.lower().strip(),)).fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id: int) -> dict | None:
    with _conn() as c:
        row = c.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None


# ── Sessions ──────────────────────────────────────────────────────────────────

def create_session(user_id: int) -> str:
    token = secrets.token_urlsafe(40)
    expires = int(time.time()) + 86400 * 30  # 30 days
    with _conn() as c:
        c.execute(
            "INSERT INTO sessions (token, user_id, expires_at) VALUES (?, ?, ?)",
            (token, user_id, expires),
        )
    return token


def get_session_user(token: str) -> dict | None:
    if not token:
        return None
    with _conn() as c:
        row = c.execute(
            "SELECT u.* FROM users u "
            "JOIN sessions s ON s.user_id = u.id "
            "WHERE s.token = ? AND s.expires_at > ?",
            (token, int(time.time())),
        ).fetchone()
        return dict(row) if row else None


def delete_session(token: str) -> None:
    with _conn() as c:
        c.execute("DELETE FROM sessions WHERE token = ?", (token,))


# ── Campaigns ──────────────────────────────────────────────────────────────────

def _campaign_row(row) -> dict:
    return {
        "id":          row["id"],
        "user_id":     row["user_id"] if "user_id" in row.keys() else 0,
        "name":        row["name"],
        "config":      json.loads(row["config_json"]),
        "is_active":   bool(row["is_active"]),
        "status":      row["status"],
        "leads_found": row["leads_found"],
        "emails_sent": row["emails_sent"],
        "created_at":  row["created_at"],
    }


def _campaign_name(config: dict) -> str:
    niche = config.get("niche_plural") or config.get("niche") or "Businesses"
    city  = config.get("city") or "Unknown"
    return f"{niche.title()} in {city}"


def list_campaigns(user_id: int = None) -> list:
    with _conn() as c:
        if user_id is not None:
            rows = c.execute(
                "SELECT * FROM campaigns WHERE user_id = ? ORDER BY created_at ASC",
                (user_id,),
            ).fetchall()
        else:
            rows = c.execute("SELECT * FROM campaigns ORDER BY created_at ASC").fetchall()
        return [_campaign_row(r) for r in rows]


def get_campaign(campaign_id: int) -> dict | None:
    with _conn() as c:
        row = c.execute("SELECT * FROM campaigns WHERE id = ?", (campaign_id,)).fetchone()
        return _campaign_row(row) if row else None


def get_active_campaign(user_id: int = None) -> dict | None:
    with _conn() as c:
        if user_id is not None:
            row = c.execute(
                "SELECT * FROM campaigns WHERE is_active = 1 AND user_id = ?", (user_id,)
            ).fetchone()
        else:
            row = c.execute("SELECT * FROM campaigns WHERE is_active = 1").fetchone()
        return _campaign_row(row) if row else None


def create_campaign(config: dict, user_id: int = 0) -> dict:
    name = _campaign_name(config)
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO campaigns (user_id, name, config_json) VALUES (?, ?, ?)",
            (user_id, name, json.dumps(config)),
        )
        return get_campaign(cur.lastrowid)


def update_campaign(campaign_id: int, config: dict) -> dict | None:
    name = _campaign_name(config)
    with _conn() as c:
        c.execute(
            "UPDATE campaigns SET name = ?, config_json = ? WHERE id = ?",
            (name, json.dumps(config), campaign_id),
        )
    return get_campaign(campaign_id)


def activate_campaign(campaign_id: int, user_id: int = None) -> dict | None:
    with _conn() as c:
        if user_id is not None:
            # Only deactivate this user's campaigns, leave other users' campaigns untouched
            c.execute("UPDATE campaigns SET is_active = 0 WHERE user_id = ?", (user_id,))
        else:
            c.execute("UPDATE campaigns SET is_active = 0")
        c.execute("UPDATE campaigns SET is_active = 1 WHERE id = ?", (campaign_id,))
    return get_campaign(campaign_id)


def delete_campaign(campaign_id: int) -> None:
    with _conn() as c:
        c.execute("DELETE FROM campaigns WHERE id = ?", (campaign_id,))


def update_campaign_stats(campaign_id: int, leads_found: int, emails_sent: int) -> None:
    with _conn() as c:
        c.execute(
            "UPDATE campaigns SET leads_found = ?, emails_sent = ? WHERE id = ?",
            (leads_found, emails_sent, campaign_id),
        )

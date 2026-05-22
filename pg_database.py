"""
PostgreSQL Database - replaces Google Sheets
Tables: businesses, generated_emails, sent_emails, activity_logs, accounts
"""
import json
import os
from datetime import datetime

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

# Set this before running a scrape to tag all saved businesses with the active campaign.
_current_campaign_id: str = ""
# Set to True by the API stop endpoint; checked during inter-locality delays.
_stop_requested: bool = False
# Human-readable reason the last pipeline run ended (empty = completed normally).
_pipeline_notice: str = ""


class _EmailsSheet:
    """Duck-typed wrapper so legacy callers can use db.emails_sheet.get_all_records()."""

    def __init__(self, db):
        self._db = db

    def get_all_records(self):
        return self._db.get_all_emails()


class PostgresDatabase:

    def __init__(self):
        self._connect()
        self._create_tables()
        self.emails_sheet = _EmailsSheet(self)

    # ── Connection ───────────────────────────────────────────────────────────

    def _connect(self):
        url = os.getenv("DATABASE_URL")
        if not url:
            raise ValueError(
                "DATABASE_URL not set. Add to .env:\n"
                "  DATABASE_URL=postgresql://user:password@localhost:5432/cold_email"
            )
        self.conn = psycopg2.connect(url)
        self.conn.autocommit = True
        print("Connected to PostgreSQL")

    def _cursor(self):
        """Return a RealDictCursor, reconnecting if the connection was lost."""
        try:
            if self.conn.closed:
                self._connect()
        except Exception:
            self._connect()
        return self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # ── Schema ───────────────────────────────────────────────────────────────

    def _create_tables(self):
        ddl = """
        CREATE TABLE IF NOT EXISTS businesses (
            id                  VARCHAR(512)  PRIMARY KEY,
            name                VARCHAR(500),
            locality            VARCHAR(255),
            city                VARCHAR(255),
            country             VARCHAR(255),
            address             TEXT,
            phone               VARCHAR(100),
            website             VARCHAR(1000),
            rating              DECIMAL(4,2),
            reviews_count       INTEGER,
            source              VARCHAR(100)  DEFAULT 'google_maps',
            has_website         BOOLEAN       DEFAULT FALSE,
            performance_score   INTEGER,
            seo_score           INTEGER,
            quality             VARCHAR(50),
            priority            VARCHAR(50),
            qualification_score INTEGER,
            reasons             TEXT,
            email               VARCHAR(255),
            email_source        VARCHAR(255),
            qualified           BOOLEAN       DEFAULT FALSE,
            email_sent          BOOLEAN       DEFAULT FALSE,
            campaign_id         VARCHAR(50),
            created_at          TIMESTAMP     DEFAULT NOW(),
            updated_at          TIMESTAMP     DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS generated_emails (
            id           VARCHAR(512) PRIMARY KEY,
            agency_id    VARCHAR(512) REFERENCES businesses(id) ON DELETE CASCADE,
            agency_name  VARCHAR(500),
            to_email     VARCHAR(255),
            subject      TEXT,
            body         TEXT,
            generated_at TIMESTAMP    DEFAULT NOW(),
            sent         VARCHAR(50)  DEFAULT 'No',
            sent_at      TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS sent_emails (
            id          SERIAL PRIMARY KEY,
            agency_id   VARCHAR(512),
            agency_name VARCHAR(500),
            email       VARCHAR(255),
            sent_at     TIMESTAMP    DEFAULT NOW(),
            status      VARCHAR(50),
            opened      BOOLEAN      DEFAULT FALSE,
            replied     BOOLEAN      DEFAULT FALSE,
            notes       TEXT
        );

        CREATE TABLE IF NOT EXISTS activity_logs (
            id          SERIAL PRIMARY KEY,
            action      VARCHAR(100),
            entity_type VARCHAR(50),
            entity_id   VARCHAR(512),
            details     JSONB,
            created_at  TIMESTAMP    DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS accounts (
            id                SERIAL PRIMARY KEY,
            name              VARCHAR(255),
            email             VARCHAR(255) UNIQUE,
            smtp_host         VARCHAR(255),
            smtp_port         INTEGER,
            smtp_user         VARCHAR(255),
            daily_limit       INTEGER      DEFAULT 50,
            emails_sent_today INTEGER      DEFAULT 0,
            last_reset_date   DATE,
            is_active         BOOLEAN      DEFAULT TRUE,
            created_at        TIMESTAMP    DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS inbox_messages (
            id            SERIAL PRIMARY KEY,
            message_uid   VARCHAR(512) UNIQUE,
            from_email    VARCHAR(255),
            from_name     VARCHAR(255),
            subject       TEXT,
            body_text     TEXT,
            received_at   TIMESTAMP DEFAULT NOW(),
            business_id   VARCHAR(512),
            sent_email_id VARCHAR(512),
            is_read       BOOLEAN DEFAULT FALSE,
            is_reply      BOOLEAN DEFAULT FALSE
        );

        CREATE TABLE IF NOT EXISTS email_opens (
            id        SERIAL PRIMARY KEY,
            email_id  VARCHAR(512),
            opened_at TIMESTAMP DEFAULT NOW()
        );
        """
        with self._cursor() as cur:
            cur.execute(ddl)
        print("Database tables ready")

    # ── Logging helper ───────────────────────────────────────────────────────

    def _log(self, action, entity_type=None, entity_id=None, details=None):
        try:
            with self._cursor() as cur:
                cur.execute(
                    "INSERT INTO activity_logs (action, entity_type, entity_id, details) "
                    "VALUES (%s, %s, %s, %s)",
                    (action, entity_type, entity_id,
                     json.dumps(details) if details else None),
                )
        except Exception:
            pass

    # ── Row converters ───────────────────────────────────────────────────────

    @staticmethod
    def _row_to_business(row):
        if row is None:
            return None
        r = dict(row)
        return {
            "ID":                  r.get("id", ""),
            "Name":                r.get("name", ""),
            "Locality":            r.get("locality", ""),
            "City":                r.get("city", ""),
            "Country":             r.get("country", ""),
            "Address":             r.get("address", ""),
            "Phone":               r.get("phone", ""),
            "Website":             r.get("website", ""),
            "Rating":              str(r["rating"]) if r.get("rating") is not None else "",
            "Reviews":             str(r["reviews_count"]) if r.get("reviews_count") is not None else "",
            "Source":              r.get("source", ""),
            "Has Website":         "Yes" if r.get("has_website") else "No",
            "Performance Score":   str(r["performance_score"]) if r.get("performance_score") is not None else "",
            "SEO Score":           str(r["seo_score"]) if r.get("seo_score") is not None else "",
            "Quality":             r.get("quality", ""),
            "Priority":            r.get("priority", ""),
            "Qualification Score": str(r["qualification_score"]) if r.get("qualification_score") is not None else "",
            "Reasons":             r.get("reasons", ""),
            "Email":               r.get("email") or "",
            "Email Source":        r.get("email_source") or "",
            "Qualified":           "Yes" if r.get("qualified") else "No",
            "Email Sent":          "Yes" if r.get("email_sent") else "No",
            "Created At":          str(r.get("created_at", "")),
        }

    @staticmethod
    def _row_to_email(row):
        if row is None:
            return None
        r = dict(row)
        return {
            "Email ID":    r.get("id", ""),
            "Agency ID":   r.get("agency_id", ""),
            "Agency Name": r.get("agency_name", ""),
            "To Email":    r.get("to_email") or "",
            "Subject":     r.get("subject") or "",
            "Body":        r.get("body") or "",
            "Generated At": str(r.get("generated_at", "")),
            "Sent":        r.get("sent", "No"),
            "Sent At":     str(r["sent_at"]) if r.get("sent_at") else "",
        }

    # ── Business CRUD ────────────────────────────────────────────────────────

    def save_business(self, business_data):
        business_id = (
            f"{business_data['name']}_{business_data.get('locality', 'unknown')}"
            .replace(" ", "_")
        )
        try:
            rating = business_data.get("rating")
            try:
                rating = float(rating) if rating else None
            except (ValueError, TypeError):
                rating = None

            reviews = business_data.get("reviews_count")
            try:
                reviews = int(reviews) if reviews else None
            except (ValueError, TypeError):
                reviews = None

            camp_id = str(business_data.get("_campaign_id") or _current_campaign_id or "")
            with self._cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO businesses
                        (id, name, locality, city, country, address, phone, website,
                         rating, reviews_count, source, has_website, campaign_id)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (id) DO UPDATE SET
                        name          = EXCLUDED.name,
                        phone         = EXCLUDED.phone,
                        website       = EXCLUDED.website,
                        rating        = EXCLUDED.rating,
                        reviews_count = EXCLUDED.reviews_count,
                        has_website   = EXCLUDED.has_website,
                        campaign_id   = COALESCE(businesses.campaign_id, EXCLUDED.campaign_id),
                        updated_at    = NOW()
                    """,
                    (
                        business_id,
                        business_data.get("name", ""),
                        business_data.get("locality", ""),
                        business_data.get("city", ""),
                        business_data.get("country", ""),
                        business_data.get("address", ""),
                        business_data.get("phone", ""),
                        business_data.get("website", ""),
                        rating,
                        reviews,
                        business_data.get("source", "google_maps"),
                        bool(business_data.get("website")),
                        camp_id or None,
                    ),
                )
            print(f"  Saved: {business_data['name']}")
            self._log("save_business", "business", business_id,
                      {"name": business_data.get("name")})
            return business_id
        except Exception as e:
            print(f"  Error saving business: {e}")
            return None

    def get_all_businesses(self):
        with self._cursor() as cur:
            cur.execute("SELECT * FROM businesses ORDER BY created_at DESC")
            return [self._row_to_business(r) for r in cur.fetchall()]

    # Alias
    def get_all_agencies(self):
        return self.get_all_businesses()

    def get_unqualified_businesses(self):
        with self._cursor() as cur:
            cur.execute(
                "SELECT * FROM businesses WHERE qualified = FALSE ORDER BY created_at"
            )
            return [self._row_to_business(r) for r in cur.fetchall()]

    # Alias
    def get_unqualified_agencies(self):
        return self.get_unqualified_businesses()

    def get_high_priority_businesses(self):
        with self._cursor() as cur:
            cur.execute(
                "SELECT * FROM businesses "
                "WHERE priority = 'HIGH' AND email_sent = FALSE "
                "ORDER BY qualification_score DESC NULLS LAST"
            )
            return [self._row_to_business(r) for r in cur.fetchall()]

    # Alias
    def get_high_priority_agencies(self):
        return self.get_high_priority_businesses()

    def claim_unassigned(self, campaign_id):
        """Assign all businesses with no campaign_id to the given campaign."""
        cid = str(campaign_id)
        try:
            with self._cursor() as cur:
                cur.execute(
                    "UPDATE businesses SET campaign_id = %s WHERE campaign_id IS NULL OR campaign_id = ''",
                    (cid,),
                )
            print(f"[db] Claimed unassigned leads for campaign {cid}")
        except Exception as e:
            print(f"  Error claiming unassigned leads: {e}")

    def get_businesses_by_campaign(self, campaign_id, filter: str = "all"):
        cid = str(campaign_id)
        with self._cursor() as cur:
            if filter == "high_priority":
                cur.execute(
                    "SELECT * FROM businesses WHERE campaign_id = %s AND priority = 'HIGH' ORDER BY qualification_score DESC NULLS LAST",
                    (cid,),
                )
            elif filter == "with_emails":
                cur.execute(
                    "SELECT * FROM businesses WHERE campaign_id = %s AND email IS NOT NULL AND email <> '' ORDER BY created_at DESC",
                    (cid,),
                )
            else:
                cur.execute(
                    "SELECT * FROM businesses WHERE campaign_id = %s ORDER BY created_at DESC",
                    (cid,),
                )
            return [self._row_to_business(r) for r in cur.fetchall()]

    def get_unqualified_businesses_by_campaign(self, campaign_id):
        cid = str(campaign_id)
        with self._cursor() as cur:
            cur.execute(
                "SELECT * FROM businesses WHERE campaign_id = %s AND qualified = FALSE ORDER BY created_at",
                (cid,),
            )
            return [self._row_to_business(r) for r in cur.fetchall()]

    def get_all_emails_by_campaign(self, campaign_id):
        cid = str(campaign_id)
        with self._cursor() as cur:
            cur.execute(
                """SELECT ge.* FROM generated_emails ge
                   JOIN businesses b ON b.id = ge.agency_id
                   WHERE b.campaign_id = %s
                   ORDER BY ge.generated_at""",
                (cid,),
            )
            return [self._row_to_email(r) for r in cur.fetchall()]

    def update_qualification(self, agency_id, qual_data):
        wq = qual_data.get("website_quality", {})
        try:
            perf = wq.get("performance_score")
            seo  = wq.get("seo_score")
            score = qual_data.get("score")
            try:
                perf  = int(perf)  if perf  else None
                seo   = int(seo)   if seo   else None
                score = int(score) if score else None
            except (ValueError, TypeError):
                pass

            with self._cursor() as cur:
                cur.execute(
                    """
                    UPDATE businesses SET
                        performance_score   = %s,
                        seo_score           = %s,
                        quality             = %s,
                        priority            = %s,
                        qualification_score = %s,
                        reasons             = %s,
                        qualified           = TRUE,
                        updated_at          = NOW()
                    WHERE id = %s
                    """,
                    (
                        perf,
                        seo,
                        wq.get("quality", ""),
                        qual_data.get("priority", ""),
                        score,
                        ", ".join(qual_data.get("reasons", [])),
                        agency_id,
                    ),
                )
            self._log("qualify_business", "business", agency_id,
                      {"priority": qual_data.get("priority")})
            return True
        except Exception as e:
            print(f"  Error updating qualification: {e}")
            return False

    def update_email(self, agency_id, email, email_source):
        try:
            with self._cursor() as cur:
                cur.execute(
                    "UPDATE businesses SET email = %s, email_source = %s, "
                    "updated_at = NOW() WHERE id = %s",
                    (email, email_source, agency_id),
                )
            self._log("update_email", "business", agency_id, {"email": email})
            return True
        except Exception as e:
            print(f"  Error updating email: {e}")
            return False

    # ── Email CRUD ───────────────────────────────────────────────────────────

    def save_generated_email(self, agency_id, agency_name, email_content):
        email_id = f"email_{agency_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        try:
            with self._cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO generated_emails
                        (id, agency_id, agency_name, to_email, subject, body, sent)
                    VALUES (%s, %s, %s, %s, %s, %s, 'No')
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (
                        email_id,
                        agency_id,
                        agency_name,
                        email_content.get("to", ""),
                        email_content.get("subject", ""),
                        email_content.get("body", ""),
                    ),
                )
            self._log("generate_email", "email", email_id,
                      {"agency_id": agency_id})
            return email_id
        except Exception as e:
            print(f"  Error saving generated email: {e}")
            return None

    def get_all_emails(self):
        with self._cursor() as cur:
            cur.execute("SELECT * FROM generated_emails ORDER BY generated_at")
            return [self._row_to_email(r) for r in cur.fetchall()]

    def get_generated_email_by_agency(self, agency_id):
        with self._cursor() as cur:
            cur.execute(
                "SELECT * FROM generated_emails WHERE agency_id = %s ORDER BY generated_at DESC LIMIT 1",
                (agency_id,),
            )
            row = cur.fetchone()
        return self._row_to_email(row) if row else None

    def mark_email_sent(self, agency_id):
        try:
            agency_name = ""
            email = ""
            with self._cursor() as cur:
                cur.execute(
                    "UPDATE businesses SET email_sent = TRUE, updated_at = NOW() "
                    "WHERE id = %s",
                    (agency_id,),
                )
                cur.execute(
                    "UPDATE generated_emails SET sent = 'Yes', sent_at = NOW() "
                    "WHERE agency_id = %s AND sent = 'No'",
                    (agency_id,),
                )
                cur.execute(
                    "SELECT name, email FROM businesses WHERE id = %s", (agency_id,)
                )
                row = cur.fetchone()
                if row:
                    agency_name = row["name"]
                    email = row["email"] or ""
                cur.execute(
                    "INSERT INTO sent_emails (agency_id, agency_name, email, status) "
                    "VALUES (%s, %s, %s, 'Sent')",
                    (agency_id, agency_name, email),
                )
            self._log("send_email", "business", agency_id)
            return True
        except Exception as e:
            print(f"  Error marking sent: {e}")
            return False

    def mark_email_skipped(self, agency_id):
        try:
            with self._cursor() as cur:
                cur.execute(
                    "UPDATE generated_emails SET sent = 'Skipped', sent_at = NOW() "
                    "WHERE agency_id = %s AND sent = 'No'",
                    (agency_id,),
                )
            self._log("skip_email", "business", agency_id)
            return True
        except Exception as e:
            print(f"  Error marking skipped: {e}")
            return False

    # ── Stats ────────────────────────────────────────────────────────────────

    def get_stats(self):
        with self._cursor() as cur:
            cur.execute(
                """
                SELECT
                    COUNT(*)                                                    AS total_agencies,
                    COUNT(*) FILTER (WHERE qualified = TRUE)                    AS qualified,
                    COUNT(*) FILTER (WHERE priority = 'HIGH')                   AS high_priority,
                    COUNT(*) FILTER (WHERE email IS NOT NULL AND email <> '')    AS with_email,
                    COUNT(*) FILTER (WHERE email_sent = TRUE)                   AS emails_sent,
                    COUNT(*) FILTER (
                        WHERE priority = 'HIGH'
                          AND email IS NOT NULL AND email <> ''
                          AND email_sent = FALSE
                    )                                                           AS pending_outreach
                FROM businesses
                """
            )
            row = cur.fetchone()
        return {k: int(v) for k, v in dict(row).items()}

    def get_stats_by_campaigns(self, campaign_ids: list):
        """Stats scoped to a list of campaign IDs (for per-user dashboard)."""
        if not campaign_ids:
            return {
                "total_agencies": 0, "qualified": 0, "high_priority": 0,
                "with_email": 0, "emails_sent": 0, "pending_outreach": 0,
            }
        ids = [str(i) for i in campaign_ids]
        placeholders = ",".join(["%s"] * len(ids))
        with self._cursor() as cur:
            cur.execute(
                f"""
                SELECT
                    COUNT(*)                                                    AS total_agencies,
                    COUNT(*) FILTER (WHERE qualified = TRUE)                    AS qualified,
                    COUNT(*) FILTER (WHERE priority = 'HIGH')                   AS high_priority,
                    COUNT(*) FILTER (WHERE email IS NOT NULL AND email <> '')    AS with_email,
                    COUNT(*) FILTER (WHERE email_sent = TRUE)                   AS emails_sent,
                    COUNT(*) FILTER (
                        WHERE priority = 'HIGH'
                          AND email IS NOT NULL AND email <> ''
                          AND email_sent = FALSE
                    )                                                           AS pending_outreach
                FROM businesses
                WHERE campaign_id IN ({placeholders})
                """,
                ids,
            )
            row = cur.fetchone()
        return {k: int(v) for k, v in dict(row).items()}

    # ── Inbox / tracking ─────────────────────────────────────────────────────

    def record_email_open(self, email_id: str):
        with self._cursor() as cur:
            cur.execute("INSERT INTO email_opens (email_id) VALUES (%s)", (email_id,))

    def save_inbox_message(self, msg: dict):
        with self._cursor() as cur:
            cur.execute(
                """
                INSERT INTO inbox_messages
                    (message_uid, from_email, from_name, subject, body_text,
                     business_id, sent_email_id, is_reply)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (message_uid) DO NOTHING
                """,
                (
                    msg.get("message_uid"), msg.get("from_email"), msg.get("from_name"),
                    msg.get("subject"), msg.get("body_text"), msg.get("business_id"),
                    msg.get("sent_email_id"), bool(msg.get("is_reply", False)),
                ),
            )

    def get_inbox_messages(self, unread_only: bool = False, limit: int = 100):
        with self._cursor() as cur:
            if unread_only:
                cur.execute(
                    "SELECT * FROM inbox_messages WHERE is_read = FALSE ORDER BY received_at DESC LIMIT %s",
                    (limit,),
                )
            else:
                cur.execute(
                    "SELECT * FROM inbox_messages ORDER BY received_at DESC LIMIT %s",
                    (limit,),
                )
            return [dict(r) for r in cur.fetchall()]

    def mark_inbox_read(self, msg_id: int):
        with self._cursor() as cur:
            cur.execute("UPDATE inbox_messages SET is_read = TRUE WHERE id = %s", (msg_id,))

    def get_sent_with_tracking(self, campaign_id=None):
        """Return generated emails with open count and reply flag."""
        with self._cursor() as cur:
            if campaign_id:
                cur.execute(
                    """
                    SELECT ge.*,
                           COUNT(DISTINCT eo.id)  AS open_count,
                           MAX(eo.opened_at)       AS last_opened,
                           COUNT(DISTINCT im.id)   AS reply_count
                    FROM generated_emails ge
                    JOIN businesses b ON b.id = ge.agency_id
                    LEFT JOIN email_opens eo ON eo.email_id = ge.id
                    LEFT JOIN inbox_messages im ON im.sent_email_id = ge.id
                    WHERE b.campaign_id = %s
                    GROUP BY ge.id
                    ORDER BY ge.generated_at DESC
                    """,
                    (str(campaign_id),),
                )
            else:
                cur.execute(
                    """
                    SELECT ge.*,
                           COUNT(DISTINCT eo.id)  AS open_count,
                           MAX(eo.opened_at)       AS last_opened,
                           COUNT(DISTINCT im.id)   AS reply_count
                    FROM generated_emails ge
                    LEFT JOIN email_opens eo ON eo.email_id = ge.id
                    LEFT JOIN inbox_messages im ON im.sent_email_id = ge.id
                    GROUP BY ge.id
                    ORDER BY ge.generated_at DESC
                    """,
                )
            return [dict(r) for r in cur.fetchall()]

    def get_inbox_stats(self):
        with self._cursor() as cur:
            cur.execute(
                """
                SELECT
                    COUNT(*) FILTER (WHERE is_read = FALSE)  AS unread,
                    COUNT(*) FILTER (WHERE is_reply = TRUE)  AS replies,
                    COUNT(*)                                  AS total
                FROM inbox_messages
                """
            )
            row = cur.fetchone()
        stats = dict(row)
        # open rate
        with self._cursor() as cur:
            cur.execute("SELECT COUNT(DISTINCT email_id) AS opened FROM email_opens")
            stats["emails_opened"] = cur.fetchone()["opened"] or 0
        return stats

    def get_spreadsheet_url(self):
        """Kept for API compatibility."""
        url = os.getenv("DATABASE_URL", "postgresql://localhost/cold_email")
        # Strip credentials from display
        try:
            from urllib.parse import urlparse
            p = urlparse(url)
            return f"[PostgreSQL] {p.hostname}:{p.port or 5432}/{p.path.lstrip('/')}"
        except Exception:
            return "[PostgreSQL] connected"

    # ── Account helpers (new) ────────────────────────────────────────────────

    def upsert_account(self, name, email, smtp_host, smtp_port, smtp_user,
                       daily_limit=50):
        try:
            with self._cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO accounts
                        (name, email, smtp_host, smtp_port, smtp_user, daily_limit)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (email) DO UPDATE SET
                        name        = EXCLUDED.name,
                        smtp_host   = EXCLUDED.smtp_host,
                        smtp_port   = EXCLUDED.smtp_port,
                        smtp_user   = EXCLUDED.smtp_user,
                        daily_limit = EXCLUDED.daily_limit
                    """,
                    (name, email, smtp_host, smtp_port, smtp_user, daily_limit),
                )
            return True
        except Exception as e:
            print(f"  Error upserting account: {e}")
            return False

    def get_activity_logs(self, limit=100):
        with self._cursor() as cur:
            cur.execute(
                "SELECT * FROM activity_logs ORDER BY created_at DESC LIMIT %s",
                (limit,),
            )
            return [dict(r) for r in cur.fetchall()]


# ── CLI test ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    db = PostgresDatabase()
    stats = db.get_stats()
    print("\nStats:")
    for k, v in stats.items():
        print(f"  {k}: {v}")

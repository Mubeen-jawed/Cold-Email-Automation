"""
IMAP Inbox Sync — pull inbox messages from your mail server and store them
in the database so they appear in the in-app Inbox.
"""
import email as email_lib
import imaplib
import os
from email.header import decode_header

from config import EMAIL
from pg_database import PostgresDatabase


def _decode_str(raw):
    """Decode an RFC-2047 encoded header value to a plain Python string."""
    if not raw:
        return ""
    parts = decode_header(raw)
    result = ""
    for fragment, charset in parts:
        if isinstance(fragment, bytes):
            result += fragment.decode(charset or "utf-8", errors="replace")
        else:
            result += str(fragment)
    return result


def _extract_body(msg):
    """Extract the plain-text body from an email.Message object."""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            disp = str(part.get("Content-Disposition", ""))
            if ctype == "text/plain" and "attachment" not in disp:
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    return payload.decode(charset, errors="replace")
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            return payload.decode(charset, errors="replace")
    return ""


def sync_inbox():
    """Fetch up to 200 recent messages from IMAP and upsert into inbox_messages."""
    imap_host = (EMAIL.get("imap_host") or "").strip() or (EMAIL.get("smtp_host") or "").strip()
    imap_user = (EMAIL.get("smtp_user") or EMAIL.get("your_email") or "").strip()
    imap_pass = os.getenv("SMTP_PASSWORD", EMAIL.get("smtp_password", "")).strip()

    if not imap_host or not imap_user or not imap_pass:
        return {"error": "IMAP credentials not configured", "synced": 0}

    db = PostgresDatabase()

    # Build fast lookup: business email → business_id
    biz_by_email = {
        b["Email"].lower().strip(): b["ID"]
        for b in db.get_all_businesses()
        if b.get("Email")
    }

    # Build lookup: (to_email_lower, subject_lower) → email_id  for reply matching
    sent_lookup = {}
    for se in db.get_all_emails():
        key = (
            se.get("To Email", "").lower().strip(),
            se.get("Subject", "").lower().strip(),
        )
        sent_lookup[key] = se.get("Email ID")

    try:
        imap = imaplib.IMAP4_SSL(imap_host, 993)
        imap.login(imap_user, imap_pass)
        imap.select("INBOX")

        _, data = imap.search(None, "ALL")
        uids = data[0].split() if data[0] else []
        uids = uids[-200:]  # last 200 to keep it fast

        synced = 0
        for uid in uids:
            try:
                _, msg_data = imap.fetch(uid, "(RFC822)")
                raw = msg_data[0][1]
                msg = email_lib.message_from_bytes(raw)

                message_uid = f"uid_{uid.decode()}"
                subject   = _decode_str(msg.get("Subject", ""))
                from_raw  = _decode_str(msg.get("From", ""))
                body      = _extract_body(msg)[:8000]

                # Parse from_email / from_name
                if "<" in from_raw:
                    from_name  = from_raw.split("<")[0].strip().strip("\"'")
                    from_email = from_raw.split("<")[1].rstrip(">").strip().lower()
                else:
                    from_name  = ""
                    from_email = from_raw.strip().lower()

                business_id   = biz_by_email.get(from_email)
                is_reply      = subject.lower().startswith("re:")
                sent_email_id = None
                if is_reply:
                    orig = subject[2:].strip().lower()
                    sent_email_id = sent_lookup.get((from_email, orig))

                db.save_inbox_message({
                    "message_uid":   message_uid,
                    "from_email":    from_email,
                    "from_name":     from_name,
                    "subject":       subject,
                    "body_text":     body,
                    "business_id":   business_id,
                    "sent_email_id": sent_email_id,
                    "is_reply":      is_reply,
                })
                synced += 1
            except Exception:
                pass

        imap.logout()
        return {"synced": synced}

    except Exception as e:
        return {"error": str(e), "synced": 0}

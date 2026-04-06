"""
Email Sender — SMTP + IMAP
Works with any email provider: custom domain, Outlook, Zoho, Yahoo, cPanel, etc.
No OAuth required — just SMTP host, port, and password.
Sent emails are automatically saved to the IMAP Sent folder so they appear in webmail.
"""
import imaplib
import os
import smtplib
import ssl
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv

from pg_database import PostgresDatabase as SheetsDatabase
from config import EMAIL

load_dotenv()


class GmailSender:
    """SMTP-based email sender (name kept for compatibility)."""

    def __init__(self):
        self.db = SheetsDatabase()
        self.host     = EMAIL.get('smtp_host', '').strip()
        self.port     = int(EMAIL.get('smtp_port', 587))
        self.username = (EMAIL.get('smtp_user') or EMAIL.get('your_email', '')).strip()
        self.password = os.getenv('SMTP_PASSWORD', EMAIL.get('smtp_password', '')).strip()
        self.from_name  = EMAIL.get('your_name', '')
        self.from_email = EMAIL.get('your_email', '')

        self._validate_config()
        self._verify_connection()

    # ── Config validation ─────────────────────────────────────────────────────

    def _validate_config(self):
        missing = []
        if not self.host:
            missing.append("smtp_host (e.g. mail.revenuelyft.com)")
        if not self.username:
            missing.append("smtp_user / your_email")
        if not self.password:
            missing.append("SMTP_PASSWORD env var")
        if missing:
            raise ValueError(
                "SMTP not configured. Set the following:\n  " + "\n  ".join(missing)
            )

    # ── Connection ────────────────────────────────────────────────────────────

    def _connect(self) -> smtplib.SMTP:
        """Open and return an authenticated SMTP connection."""
        context = ssl.create_default_context()
        if self.port == 465:
            # Implicit SSL
            smtp = smtplib.SMTP_SSL(self.host, self.port, context=context, timeout=15)
        else:
            # STARTTLS (587) or plain 25
            smtp = smtplib.SMTP(self.host, self.port, timeout=15)
            smtp.ehlo()
            smtp.starttls(context=context)
            smtp.ehlo()
        smtp.login(self.username, self.password)
        return smtp

    def _verify_connection(self):
        """Test the connection at startup so errors surface immediately."""
        try:
            smtp = self._connect()
            smtp.quit()
            print(f"✅ SMTP connected: {self.username} via {self.host}:{self.port}")
        except Exception as e:
            raise ConnectionError(f"SMTP connection failed: {e}")

    # ── IMAP (save to Sent folder) ────────────────────────────────────────────

    # Common Sent folder names across providers
    _SENT_FOLDER_CANDIDATES = ["Sent", "Sent Items", "Sent Messages", "[Gmail]/Sent Mail", "INBOX.Sent"]

    def _imap_connect(self) -> imaplib.IMAP4_SSL:
        """Open an authenticated IMAP SSL connection."""
        imap_host = EMAIL.get('imap_host', self.host).strip() or self.host
        imap = imaplib.IMAP4_SSL(imap_host, 993)
        imap.login(self.username, self.password)
        return imap

    def _find_sent_folder(self, imap: imaplib.IMAP4_SSL) -> str | None:
        """Return the name of the Sent folder, or None if not found."""
        _, folders = imap.list()
        folder_names = []
        for f in folders:
            if not f:
                continue
            parts = f.decode(errors="ignore").split('"')
            folder_names.append(parts[-1].strip().strip('"'))

        for candidate in self._SENT_FOLDER_CANDIDATES:
            if candidate in folder_names:
                return candidate
        # Case-insensitive fallback
        lower = {n.lower(): n for n in folder_names}
        for candidate in self._SENT_FOLDER_CANDIDATES:
            if candidate.lower() in lower:
                return lower[candidate.lower()]
        return None

    def _save_to_sent(self, raw_message: bytes) -> None:
        """Append a raw message to the IMAP Sent folder (best-effort)."""
        try:
            imap = self._imap_connect()
            folder = self._find_sent_folder(imap)
            if not folder:
                print("    ⚠️  Could not find Sent folder — skipping IMAP save")
                imap.logout()
                return
            imap.append(folder, r"\Seen", imaplib.Time2Internaldate(time.time()), raw_message)
            imap.logout()
        except Exception as e:
            # Non-fatal — email was still sent; just log the warning
            print(f"    ⚠️  Could not save to Sent folder: {e}")

    # ── Send a single email ───────────────────────────────────────────────────

    def send_email(self, to: str, subject: str, body: str, email_id: str = None) -> bool:
        """Send one email and save a copy to the IMAP Sent folder. Returns True on success."""
        from email.utils import make_msgid
        msg = MIMEMultipart('alternative')
        msg['Subject']  = subject
        msg['From']     = f"{self.from_name} <{self.from_email}>" if self.from_name else self.from_email
        msg['To']       = to
        msg['Reply-To'] = self.from_email
        msg['Message-ID'] = make_msgid()
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        # HTML part with open-tracking pixel (best-effort)
        if email_id:
            try:
                app_url = os.getenv('APP_URL', 'http://localhost:8000').rstrip('/')
                pixel = f'<img src="{app_url}/api/track/open/{email_id}" width="1" height="1" style="display:none">'
                html_body = (
                    '<div style="font-family:Arial,sans-serif;font-size:14px;'
                    'line-height:1.6;white-space:pre-wrap">'
                    + body.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    + f'</div>{pixel}'
                )
                msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            except Exception:
                pass

        raw = msg.as_bytes()

        try:
            smtp = self._connect()
            smtp.sendmail(self.from_email, to, raw)
            smtp.quit()
        except Exception as e:
            print(f"    ❌ Send error: {e}")
            return False

        # Save to Sent folder so it appears in webmail
        self._save_to_sent(raw)
        return True

    # ── Send a batch ──────────────────────────────────────────────────────────

    def send_batch(self, batch_size=None):
        import pg_database as _pgdb
        if not _pgdb._current_campaign_id:
            raise RuntimeError(
                "No active campaign set. Activate a campaign before sending emails."
            )

        if batch_size is None:
            batch_size = EMAIL['batch_size']

        cid = _pgdb._current_campaign_id
        print(f"\n🚀 Sending batch of up to {batch_size} emails for campaign {cid}...\n")
        all_emails = self.db.get_all_emails_by_campaign(cid)

        # Addresses already sent or previously skipped
        already_contacted = {
            e['To Email'].lower().strip()
            for e in all_emails
            if e.get('Sent') in ('Yes', 'Skipped') and e.get('To Email')
        }

        pending = [e for e in all_emails if e.get('Sent') == 'No' and e.get('To Email')]

        # Deduplicate within batch AND against history
        seen = set(already_contacted)
        unique_emails, duplicates = [], []
        for e in pending:
            addr = e['To Email'].lower().strip()
            if addr in seen:
                duplicates.append(e)
            else:
                seen.add(addr)
                unique_emails.append(e)

        if duplicates:
            print(f"⚠️  Skipping {len(duplicates)} duplicate address(es):")
            for dup in duplicates:
                print(f"   - {dup.get('Agency Name', '?')} → {dup['To Email']}")
                self.db.mark_email_skipped(dup['Agency ID'])
            print()

        ready_emails = unique_emails[:batch_size]

        if not ready_emails:
            print("❌ No emails ready to send")
            print("💡 Generate emails first (Step 4 in the pipeline)")
            return

        print(f"📧 Sending to {len(ready_emails)} unique address(es)\n")

        sent = failed = 0

        for idx, email in enumerate(ready_emails, 1):
            try:
                print(f"[{idx}/{len(ready_emails)}] {email.get('Agency Name', '?')}")
                print(f"  To: {email['To Email']}")
                print(f"  Subject: {email['Subject']}")

                ok = self.send_email(
                    email['To Email'],
                    email['Subject'],
                    email['Body'],
                    email_id=email.get('Email ID'),
                )

                if ok:
                    self.db.mark_email_sent(email['Agency ID'])
                    sent += 1
                    print(f"  ✅ Sent!")
                else:
                    failed += 1

                if idx < len(ready_emails):
                    delay = EMAIL.get('delay_between_sends', 30)
                    print(f"  ⏳ Waiting {delay}s...")
                    time.sleep(delay)

            except Exception as e:
                print(f"  ❌ Error: {e}")
                failed += 1

        print(f"\n{'='*60}")
        print(f"Batch complete — Sent: {sent}  Failed: {failed}  "
              f"Rate: {sent/len(ready_emails)*100:.1f}%")

        remaining = sum(
            1 for e in all_emails
            if e.get('Sent') == 'No' and e.get('To Email')
        ) - len(ready_emails)
        if remaining > 0:
            print(f"\n💡 {remaining} emails still pending for next batch")

    # ── Connection check (used by API) ────────────────────────────────────────

    def test_connection(self) -> dict:
        try:
            smtp = self._connect()
            smtp.quit()
            return {
                "ok":               True,
                "authenticated_as": self.username,
                "configured_as":    self.from_email,
                "host":             self.host,
                "port":             self.port,
                "matched":          True,
            }
        except Exception as e:
            return {
                "ok":    False,
                "error": str(e),
                "host":  self.host,
                "port":  self.port,
            }


# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        sender = GmailSender()
        result = sender.test_connection()
        if not result["ok"]:
            print(f"❌ Connection failed: {result.get('error')}")
        else:
            print(f"\n{'='*60}")
            batch_size = input(f"\nHow many emails to send? (default {EMAIL['batch_size']}): ").strip()
            batch_size = int(batch_size) if batch_size else EMAIL['batch_size']
            print(f"\n⚠️  About to send {batch_size} emails from {EMAIL['your_email']}")
            if input("Continue? (yes/no): ").strip().lower() == 'yes':
                sender.send_batch(batch_size)
            else:
                print("Cancelled")
    except Exception as e:
        print(f"❌ {e}")

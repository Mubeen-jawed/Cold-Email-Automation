"""
Email Sender - 100% FREE
Uses Gmail API (500 emails/day FREE!)
"""
import os
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import time
from sheets_database import SheetsDatabase
from config import EMAIL

SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]
class GmailSender:
    def __init__(self):
        self.db = SheetsDatabase()
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Gmail API"""
        creds = None
        
        # Token.json stores user's access and refresh tokens
        if os.path.exists('gmail_token.json'):
            creds = Credentials.from_authorized_user_file('gmail_token.json', SCOPES)
        
        # If no valid credentials, let user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists('gmail_credentials.json'):
                    print("❌ gmail_credentials.json not found!")
                    print("📝 Follow setup instructions to create this file")
                    raise FileNotFoundError("gmail_credentials.json required")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    'gmail_credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open('gmail_token.json', 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('gmail', 'v1', credentials=creds)
        print("✅ Connected to Gmail")
    
    def create_message(self, to, subject, body):
        """Create email message"""
        message = MIMEText(body)
        message['to'] = to
        message['from'] = EMAIL['your_email']
        message['subject'] = subject
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return {'raw': raw}
    
    def send_email(self, to, subject, body):
        """Send email via Gmail API"""
        try:
            message = self.create_message(to, subject, body)
            result = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            
            return result.get('id')
        except Exception as e:
            print(f"    ❌ Send error: {e}")
            return None
    
    def send_batch(self, batch_size=None):
        """Send batch of emails"""
        if batch_size is None:
            batch_size = EMAIL['batch_size']
        
        print(f"\n🚀 Sending batch of {batch_size} emails...\n")
        
        # Get emails ready to send
        all_emails = self.db.emails_sheet.get_all_records()
        ready_emails = [e for e in all_emails if e.get('Sent') == 'No' and e.get('To Email')][:batch_size]
        
        if not ready_emails:
            print("❌ No emails ready to send")
            print("💡 Generate emails first using email_generator.py")
            return
        
        print(f"📧 Found {len(ready_emails)} emails to send\n")
        
        sent = failed = 0
        
        for idx, email in enumerate(ready_emails, 1):
            try:
                print(f"[{idx}/{len(ready_emails)}] {email['Agency Name']}")
                print(f"  To: {email['To Email']}")
                print(f"  Subject: {email['Subject']}")
                
                message_id = self.send_email(
                    email['To Email'],
                    email['Subject'],
                    email['Body']
                )
                
                if message_id:
                    self.db.mark_email_sent(email['Agency ID'])
                    sent += 1
                    print(f"  ✅ Sent!")
                else:
                    failed += 1
                
                # Rate limiting
                if idx < len(ready_emails):
                    print(f"  ⏳ Waiting {EMAIL['delay_between_sends']}s...")
                    time.sleep(EMAIL['delay_between_sends'])
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                failed += 1
                continue
        
        print(f"\n{'='*60}")
        print(f"🎉 Batch sending complete!")
        print(f"\n📊 Results:")
        print(f"  ✅ Sent: {sent}")
        print(f"  ❌ Failed: {failed}")
        print(f"  📈 Success rate: {(sent/len(ready_emails)*100):.1f}%")
        
        remaining = len([e for e in all_emails if e.get('Sent') == 'No' and e.get('To Email')]) - len(ready_emails)
        if remaining > 0:
            print(f"\n💡 {remaining} emails still pending")
            print(f"   Run again tomorrow to send next batch")
    
    def test_connection(self):
        """Test Gmail connection"""
        try:
            profile = self.service.users().getProfile(userId='me').execute()
            email = profile.get('emailAddress')
            print(f"✅ Gmail connected: {email}")
            
            # Check daily quota
            print(f"📊 Gmail allows 500 emails/day")
            print(f"   Current batch size: {EMAIL['batch_size']}")
            
            return True
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False

if __name__ == "__main__":
    sender = GmailSender()
    
    if sender.test_connection():
        print(f"\n{'='*60}")
        
        batch_size = input(f"\nHow many emails to send? (max {EMAIL['batch_size']}): ").strip()
        if batch_size:
            batch_size = int(batch_size)
        else:
            batch_size = EMAIL['batch_size']
        
        print(f"\n⚠️  You're about to send {batch_size} emails from {EMAIL['your_email']}")
        confirm = input("Continue? (yes/no): ").strip().lower()
        
        if confirm == 'yes':
            sender.send_batch(batch_size)
        else:
            print("❌ Cancelled")
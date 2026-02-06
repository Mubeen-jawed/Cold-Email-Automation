"""
Google Sheets Database - Free cloud storage
No MongoDB needed!
"""
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json
from config import SHEETS, TARGET

class SheetsDatabase:
    def __init__(self):
        """Initialize Google Sheets connection"""
        self.setup_credentials()
        self.setup_sheets()
    
    def setup_credentials(self):
        """Setup Google Sheets API credentials"""
        # Define the scope
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        try:
            # Load credentials from service account file
            self.creds = Credentials.from_service_account_file(
                'credentials.json',
                scopes=scopes
            )
            self.client = gspread.authorize(self.creds)
            print("✅ Connected to Google Sheets")
        except FileNotFoundError:
            print("❌ credentials.json not found!")
            print("📝 Follow setup instructions to create this file")
            raise
    
    def setup_sheets(self):
        """Create or open spreadsheet with all required sheets"""
        spreadsheet_name = SHEETS['spreadsheet_name']
        
        # Check if user provided a spreadsheet URL in config
        spreadsheet_url = SHEETS.get('spreadsheet_url', None)
        
        try:
            if spreadsheet_url:
                # Open by URL if provided
                self.spreadsheet = self.client.open_by_url(spreadsheet_url)
                print(f"📊 Opened spreadsheet from URL")
            else:
                # Try to open existing spreadsheet by name
                self.spreadsheet = self.client.open(spreadsheet_name)
                print(f"📊 Opened existing spreadsheet: {spreadsheet_name}")
        except gspread.SpreadsheetNotFound:
            # Can't create - user must create and share
            print(f"\n❌ Spreadsheet not found!")
            print(f"\n📝 Please do this:")
            print(f"1. Go to https://sheets.google.com")
            print(f"2. Create a new spreadsheet named: {spreadsheet_name}")
            print(f"3. Click 'Share' button")
            print(f"4. Add this email as Editor: {self.creds.service_account_email}")
            print(f"5. Copy the spreadsheet URL")
            print(f"6. Add to config.py: SHEETS['spreadsheet_url'] = 'your-url-here'")
            print(f"\nOr run: python setup_sheets.py")
            raise Exception("Spreadsheet not found. Please create and share it first.")
        except Exception as e:
            if "storageQuotaExceeded" in str(e):
                print(f"\n❌ Service account storage is full!")
                print(f"\n📝 SOLUTION - Create spreadsheet manually:")
                print(f"1. Go to https://sheets.google.com")
                print(f"2. Create new spreadsheet: {spreadsheet_name}")
                print(f"3. Click 'Share' → Add as Editor:")
                
                # Show service account email
                try:
                    print(f"   {self.creds.service_account_email}")
                except:
                    print(f"   (Check credentials.json for 'client_email')")
                
                print(f"4. Copy the spreadsheet URL")
                print(f"5. Update config.py:")
                print(f"   SHEETS['spreadsheet_url'] = 'paste-url-here'")
                print(f"\nThen run this script again!")
                raise Exception("Storage quota exceeded")
            raise
        
        # Setup individual sheets
        self._setup_agencies_sheet()
        self._setup_emails_sheet()
        self._setup_sent_sheet()
        self._setup_stats_sheet()
    
    def _setup_agencies_sheet(self):
        """Setup agencies sheet with headers"""
        sheet_name = SHEETS['sheets']['agencies'] if isinstance(SHEETS.get('sheets'), dict) else 'Agencies'
        
        try:
            self.agencies_sheet = self.spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            self.agencies_sheet = self.spreadsheet.add_worksheet(
                title=sheet_name,
                rows=1000,
                cols=20
            )
            
            # Add headers
            headers = [
                'ID', 'Name', 'Locality', 'City', 'Country', 'Address', 'Phone',
                'Website', 'Rating', 'Reviews', 'Source', 
                'Has Website', 'Performance Score', 'SEO Score', 'Quality',
                'Priority', 'Qualification Score', 'Reasons',
                'Email', 'Email Source', 'Qualified', 'Email Sent', 'Created At'
            ]
            self.agencies_sheet.update('A1:W1', [headers])
            print(f"  ✅ Created {sheet_name} sheet")
    
    def _setup_emails_sheet(self):
        """Setup generated emails sheet"""
        sheet_name = SHEETS['sheets']['emails'] if isinstance(SHEETS.get('sheets'), dict) else 'Generated Emails'
        
        try:
            self.emails_sheet = self.spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            self.emails_sheet = self.spreadsheet.add_worksheet(
                title=sheet_name,
                rows=1000,
                cols=10
            )
            
            headers = [
                'Email ID', 'Agency ID', 'Agency Name', 'To Email',
                'Subject', 'Body', 'Generated At', 'Sent', 'Sent At'
            ]
            self.emails_sheet.update('A1:I1', [headers])
            print(f"  ✅ Created {sheet_name} sheet")
    
    def _setup_sent_sheet(self):
        """Setup sent emails tracking sheet"""
        sheet_name = SHEETS['sheets']['sent'] if isinstance(SHEETS.get('sheets'), dict) else 'Sent Emails'
        
        try:
            self.sent_sheet = self.spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            self.sent_sheet = self.spreadsheet.add_worksheet(
                title=sheet_name,
                rows=1000,
                cols=8
            )
            
            headers = [
                'Agency ID', 'Agency Name', 'Email', 'Sent At',
                'Status', 'Opened', 'Replied', 'Notes'
            ]
            self.sent_sheet.update('A1:H1', [headers])
            print(f"  ✅ Created {sheet_name} sheet")
    
    def _setup_stats_sheet(self):
        """Setup statistics sheet"""
        sheet_name = SHEETS['sheets']['stats'] if isinstance(SHEETS.get('sheets'), dict) else 'Statistics'
        
        try:
            self.stats_sheet = self.spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            self.stats_sheet = self.spreadsheet.add_worksheet(
                title=sheet_name,
                rows=100,
                cols=5
            )
            
            headers = ['Metric', 'Value', 'Updated At']
            self.stats_sheet.update('A1:C1', [headers])
            print(f"  ✅ Created {sheet_name} sheet")
    
    def save_business(self, business_data):
        """Save or update business"""
        try:
            # Generate unique ID
            business_id = f"{business_data['name']}_{business_data.get('locality', 'unknown')}".replace(' ', '_')
            
            # Check if exists
            cell = self.agencies_sheet.find(business_id, in_column=1)
            
            row_data = [
                business_id,
                business_data.get('name', ''),
                business_data.get('locality', ''),
                business_data.get('city', ''),
                business_data.get('country', ''),
                business_data.get('address', ''),
                business_data.get('phone', ''),
                business_data.get('website', ''),
                business_data.get('rating', ''),
                business_data.get('reviews_count', ''),
                business_data.get('source', 'google_maps'),
                'Yes' if business_data.get('website') else 'No',
                '', '', '',  # Performance, SEO, Quality (filled during qualification)
                '', '', '',  # Priority, Score, Reasons (filled during qualification)
                '', '',      # Email, Email Source (filled during email finding)
                'No',        # Qualified
                'No',        # Email Sent
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
            
            if cell:
                # Update existing
                row_number = cell.row
                self.agencies_sheet.update(f'A{row_number}:W{row_number}', [row_data])
                print(f"  ✅ Updated: {business_data['name']}")
            else:
                # Add new
                self.agencies_sheet.append_row(row_data)
                print(f"  ✨ Added: {business_data['name']}")
            
            return business_id
            
        except Exception as e:
            print(f"  ❌ Error saving agency: {e}")
            return None
    
    def get_unqualified_businesses(self):
        """Get businesses that haven't been qualified"""
        all_businesses = self.get_all_businesses()
        return [b for b in all_businesses if b.get('Qualified') == 'No' and b.get('ID')]
    
    def get_all_businesses(self):
        """Get all businesses as list of dicts"""
        try:
            records = self.agencies_sheet.get_all_records()
            return records
        except Exception as e:
            print(f"❌ Error getting businesses: {e}")
            return []
    
    def get_all_agencies(self):
        """Get all agencies as list of dicts"""
        try:
            records = self.agencies_sheet.get_all_records()
            return records
        except Exception as e:
            print(f"❌ Error getting agencies: {e}")
            return []
    
    def get_unqualified_agencies(self):
        """Get agencies that haven't been qualified"""
        all_agencies = self.get_all_agencies()
        return [a for a in all_agencies if a.get('Qualified') == 'No' and a.get('ID')]
    
    def update_qualification(self, agency_id, qual_data):
        """Update agency with qualification data"""
        try:
            cell = self.agencies_sheet.find(agency_id, in_column=1)
            if cell:
                row = cell.row
                
                # Update qualification columns
                updates = [
                    (f'M{row}', qual_data.get('website_quality', {}).get('performance_score', '')),
                    (f'N{row}', qual_data.get('website_quality', {}).get('seo_score', '')),
                    (f'O{row}', qual_data.get('website_quality', {}).get('quality', '')),
                    (f'P{row}', qual_data.get('priority', '')),
                    (f'Q{row}', qual_data.get('score', '')),
                    (f'R{row}', ', '.join(qual_data.get('reasons', []))),
                    (f'U{row}', 'Yes')  # Qualified = Yes
                ]
                
                for cell_ref, value in updates:
                    self.agencies_sheet.update(cell_ref, [[value]])
                
                return True
        except Exception as e:
            print(f"  ❌ Error updating qualification: {e}")
            return False
    
    def get_all_businesses(self):
        """Get all businesses as list of dicts"""
        try:
            # Check if sheet has data first
            all_values = self.agencies_sheet.get_all_values()
            if len(all_values) <= 1:  # Only headers or empty
                return []
            records = self.agencies_sheet.get_all_records()
            return records
        except Exception as e:
            print(f"❌ Error getting businesses: {e}")
            return []
    
    def get_high_priority_agencies(self):
        """Get high priority agencies without emails sent"""
        all_agencies = self.get_all_agencies()
        return [a for a in all_agencies 
                if a.get('Priority') == 'HIGH' 
                and a.get('Email Sent') == 'No'
                and a.get('ID')]
    
    def update_email(self, agency_id, email, email_source):
        """Update agency with found email"""
        try:
            cell = self.agencies_sheet.find(agency_id, in_column=1)
            if cell:
                row = cell.row
                self.agencies_sheet.update(f'S{row}', [[email]])
                self.agencies_sheet.update(f'T{row}', [[email_source]])
                return True
        except Exception as e:
            print(f"  ❌ Error updating email: {e}")
            return False
    
    def save_generated_email(self, agency_id, agency_name, email_content):
        """Save generated email"""
        try:
            email_id = f"email_{agency_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            row_data = [
                email_id,
                agency_id,
                agency_name,
                email_content.get('to', ''),
                email_content.get('subject', ''),
                email_content.get('body', ''),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'No',  # Sent
                ''     # Sent At
            ]
            
            self.emails_sheet.append_row(row_data)
            return email_id
            
        except Exception as e:
            print(f"  ❌ Error saving email: {e}")
            return None
    
    def mark_email_sent(self, agency_id):
        """Mark email as sent"""
        try:
            # Update agencies sheet
            cell = self.agencies_sheet.find(agency_id, in_column=1)
            if cell:
                row = cell.row
                self.agencies_sheet.update(f'V{row}', [['Yes']])
            
            # Update emails sheet
            emails = self.emails_sheet.get_all_records()
            for idx, email in enumerate(emails, start=2):
                if email.get('Agency ID') == agency_id and email.get('Sent') == 'No':
                    self.emails_sheet.update(f'H{idx}', [['Yes']])
                    self.emails_sheet.update(f'I{idx}', [[datetime.now().strftime('%Y-%m-%d %H:%M:%S')]])
                    break
            
            # Log to sent sheet
            sent_data = [
                agency_id,
                '',  # Will be filled with agency name
                '',  # Will be filled with email
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Sent',
                'No',  # Opened
                'No',  # Replied
                ''     # Notes
            ]
            self.sent_sheet.append_row(sent_data)
            
            return True
        except Exception as e:
            print(f"  ❌ Error marking sent: {e}")
            return False
    
    def get_stats(self):
        """Get current statistics"""
        agencies = self.get_all_agencies()
        
        stats = {
            'total_agencies': len(agencies),
            'qualified': len([a for a in agencies if a.get('Qualified') == 'Yes']),
            'high_priority': len([a for a in agencies if a.get('Priority') == 'HIGH']),
            'with_email': len([a for a in agencies if a.get('Email')]),
            'emails_sent': len([a for a in agencies if a.get('Email Sent') == 'Yes']),
            'pending_outreach': len([a for a in agencies 
                                   if a.get('Priority') == 'HIGH' 
                                   and a.get('Email') 
                                   and a.get('Email Sent') == 'No'])
        }
        
        # Update stats sheet
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        stats_rows = [[k.replace('_', ' ').title(), v, timestamp] for k, v in stats.items()]
        self.stats_sheet.update('A2:C7', stats_rows)
        
        return stats
    
    def get_spreadsheet_url(self):
        """Get the URL to view the spreadsheet"""
        return self.spreadsheet.url

# Test connection
if __name__ == "__main__":
    print("🔌 Testing Google Sheets connection...")
    try:
        db = SheetsDatabase()
        print(f"\n✅ Connected successfully!")
        print(f"📊 Spreadsheet URL: {db.get_spreadsheet_url()}")
        print(f"\n💡 Open this URL to view your data")
        
        # Show stats
        stats = db.get_stats()
        print(f"\n📈 Current Stats:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print("\n📝 Make sure you've created credentials.json")
        print("   See SETUP_GUIDE.md for instructions")
"""
Google Sheets Setup Helper
Use this when you get "storageQuotaExceeded" error
"""

print("\n" + "="*70)
print("📊 GOOGLE SHEETS MANUAL SETUP")
print("="*70)

# Get service account email
try:
    from google.oauth2.service_account import Credentials
    creds = Credentials.from_service_account_file('credentials.json')
    service_account_email = creds.service_account_email
    print(f"\n✅ Found service account email:")
    print(f"   {service_account_email}")
except Exception as e:
    print(f"\n❌ Error reading credentials.json: {e}")
    print(f"\nMake sure credentials.json exists in this folder!")
    exit(1)

# Get spreadsheet name from config
try:
    from config import SHEETS, TARGET
    spreadsheet_name = SHEETS['spreadsheet_name']
    print(f"\n✅ Spreadsheet name from config:")
    print(f"   {spreadsheet_name}")
except Exception as e:
    print(f"\n⚠️  Using default name: Business Automation")
    spreadsheet_name = "Business Automation"

print("\n" + "="*70)
print("📝 FOLLOW THESE STEPS:")
print("="*70)

print("""
1️⃣  CREATE SPREADSHEET
   • Go to: https://sheets.google.com
   • Click: "+ Blank" to create new spreadsheet
   • Name it: {}

2️⃣  SHARE WITH SERVICE ACCOUNT
   • Click the "Share" button (top right)
   • In "Add people and groups" field, paste:
     {}
   • Make sure role is set to "Editor"
   • Click "Send" (you may see a warning - ignore it)

3️⃣  GET THE URL
   • Copy the full URL from your browser address bar
   • It looks like:
     https://docs.google.com/spreadsheets/d/LONG_ID_HERE/edit
   • Copy everything!

4️⃣  UPDATE CONFIG
   • Open: config.py
   • Find the SHEETS = {{ ... }} section
   • Add this line inside:
     "spreadsheet_url": "paste-your-url-here",
   
   Example:
   SHEETS = {{
       "spreadsheet_name": "...",
       "spreadsheet_url": "https://docs.google.com/spreadsheets/d/1234.../edit",  # ADD THIS
       "sheets": {{ ... }}
   }}

5️⃣  TEST IT
   • Run: python sheets_database.py
   • Should connect successfully!

""".format(spreadsheet_name, service_account_email))

print("="*70)
print("💡 WHY THIS HAPPENS")
print("="*70)
print("""
Service accounts have their own 15GB Google Drive storage,
separate from your personal account. When the service account's
storage fills up, it can't create new files.

Solution: YOU create the spreadsheet in YOUR Google Drive,
then share it with the service account. This way it uses YOUR
storage, not the service account's!
""")

print("="*70)
print("🔄 ALTERNATIVE: CREATE NEW SERVICE ACCOUNT")
print("="*70)
print("""
If you want to start fresh:

1. Go to: https://console.cloud.google.com
2. Create a NEW project (don't use the old one)
3. Enable Google Sheets API
4. Enable Google Drive API
5. Create NEW service account
6. Download NEW credentials.json
7. Replace your old credentials.json

This new service account will have empty 15GB storage.
""")

print("="*70)
print("\nCopy the service account email above and follow the steps!")
print("="*70 + "\n")

# Ask if user wants to test now
input("Press Enter when you've completed the steps above...")

print("\n🧪 Testing connection...")
try:
    from sheets_database import SheetsDatabase
    db = SheetsDatabase()
    print("\n✅ SUCCESS! Connected to Google Sheets")
    print(f"📊 Spreadsheet URL: {db.get_spreadsheet_url()}")
except Exception as e:
    print(f"\n❌ Connection failed: {e}")
    print("\nDouble-check:")
    print("1. Did you share the spreadsheet with the service account email?")
    print("2. Did you set it as 'Editor' (not 'Viewer')?")
    print("3. Did you add the 'spreadsheet_url' to config.py?")
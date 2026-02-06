# 🚀 Complete Setup Guide - 100% FREE Automation System

## 💰 Cost Breakdown

| Service                  | Free Limit          | Cost | What We Use         |
| ------------------------ | ------------------- | ---- | ------------------- |
| **Google Gemini API**    | 1,500 requests/day  | FREE | AI email generation |
| **Google PageSpeed API** | 25,000 requests/day | FREE | Website analysis    |
| **Gmail API**            | 500 emails/day      | FREE | Send emails         |
| **Google Sheets API**    | Unlimited           | FREE | Database            |
| **Playwright**           | Unlimited           | FREE | Scraping            |

**Total Monthly Cost: $0** 🎉

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [API Keys Setup](#api-keys-setup)
4. [Configuration](#configuration)
5. [Running the Automation](#running)
6. [Troubleshooting](#troubleshooting)

---

## 📋 Prerequisites

### What You Need:

- Computer (Windows/Mac/Linux)
- Gmail account
- Google account
- Internet connection
- 2 hours for setup

---

## 🔧 Installation

### Step 1: Install Python

#### Windows:

1. Go to https://python.org/downloads
2. Download Python 3.11+
3. Run installer
4. ⚠️ **CHECK "Add Python to PATH"**
5. Click "Install Now"

Verify:

```bash
python --version
```

#### Mac:

```bash
brew install python@3.11
python3 --version
```

#### Linux:

```bash
sudo apt update
sudo apt install python3.11 python3-pip
```

### Step 2: Create Project Folder

```bash
# Create folder
mkdir business-automation
cd business-automation

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### Step 3: Download Files

Download all these files to your `business-automation` folder:

- `config.py`
- `sheets_database.py`
- `scraper.py`
- `analyzer.py`
- `email_finder.py`
- `email_generator.py`
- `email_sender.py`
- `main.py`
- `requirements.txt`

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

---

## 🔐 API Keys Setup

### 1. Google Gemini API (FREE - Email Generation)

**Step-by-step:**

1. Go to https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Select or create a Google Cloud project
5. Click "Create API Key in New Project"
6. **Copy the API key** (starts with `AIza...`)

**Store it:**
Create a file called `.env` in your project folder:

```bash
GEMINI_API_KEY=AIzaSy...your-key-here
```

**Limits:** 1,500 requests/day FREE (enough for 1,500 emails!)

---

### 2. Google Sheets API (FREE - Database)

**Step-by-step:**

1. Go to https://console.cloud.google.com
2. Create a new project or select existing
3. Click "Enable APIs and Services"
4. Search for "Google Sheets API"
5. Click "Enable"
6. Search for "Google Drive API"
7. Click "Enable"

**Create Service Account:**

1. Go to "Credentials" (left menu)
2. Click "Create Credentials" → "Service Account"
3. Name: "Business Automation"
4. Click "Create and Continue"
5. Role: "Editor"
6. Click "Done"

**Download Credentials:**

1. Click on the service account you just created
2. Go to "Keys" tab
3. Click "Add Key" → "Create New Key"
4. Choose "JSON"
5. Click "Create"
6. A file downloads: `project-name-xxxxx.json`
7. **Rename it to `credentials.json`**
8. Move it to your project folder

**Install gspread:**

```bash
pip install gspread google-auth
```

---

### 3. Gmail API (FREE - Send Emails)

**Step-by-step:**

1. Go to https://console.cloud.google.com
2. Same project as above
3. Click "Enable APIs and Services"
4. Search for "Gmail API"
5. Click "Enable"

**Create OAuth Credentials:**

1. Go to "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure consent screen:
   - User Type: "External"
   - App name: "Business Automation"
   - User support email: Your email
   - Developer contact: Your email
   - Click "Save and Continue" through all steps
   - Add yourself as test user

4. Back to Create OAuth client ID:
   - Application type: "Desktop app"
   - Name: "Gmail Sender"
   - Click "Create"

5. **Download the credentials:**
   - Click "Download JSON"
   - **Rename to `gmail_credentials.json`**
   - Move to project folder

**Limits:** 500 emails/day FREE

---

### 4. Google PageSpeed API (FREE - Website Analysis)

**No key needed!** The API works without authentication.

Just works out of the box! 🎉

---

## ⚙️ Configuration

### Update config.py

Open `config.py` and update these settings:

```python
# Line 9-18: Change to your target
TARGET = {
    "city": "Dubai",              # Your target city
    "country": "UAE",             # Country
    "localities": [               # Neighborhoods/areas
        "Dubai Marina",
        "Business Bay",
        # Add more areas...
    ],
    "niche": "real estate agency",  # Business type
    "niche_plural": "real estate agencies",
    "industry": "real estate",

    # What you're selling
    "your_service": "websites and digital presence",
    "your_service_benefit": "get more leads online",
    "pain_point": "limited online presence",
}

# Line 103: Update your email
EMAIL = {
    # ... other settings ...
    "your_name": "Hassan",        # Your name
    "your_email": "your-email@gmail.com",  # ⚠️ UPDATE THIS!
}
```

**Examples for other cities/niches:**

```python
# New York Restaurants
TARGET = {
    "city": "New York",
    "country": "USA",
    "localities": ["Manhattan", "Brooklyn", "Queens"],
    "niche": "restaurant",
    "niche_plural": "restaurants",
    "industry": "food & beverage",
    "your_service": "online ordering systems",
    "your_service_benefit": "increase takeout orders",
    "pain_point": "no online ordering",
}

# London Fitness Centers
TARGET = {
    "city": "London",
    "country": "UK",
    "localities": ["Shoreditch", "Camden", "Soho"],
    "niche": "fitness center",
    "niche_plural": "fitness centers",
    "industry": "health & fitness",
    "your_service": "member management software",
    "your_service_benefit": "automate bookings",
    "pain_point": "manual booking process",
}
```

---

## 🚀 Running the Automation

### First Time Setup

1. Test database connection:

```bash
python sheets_database.py
```

Should output:

```
✅ Connected to Google Sheets
📊 Spreadsheet URL: https://docs.google.com/spreadsheets/...
```

2. Open the spreadsheet URL in browser
3. You'll see 4 sheets created automatically!

### Run Main Program

```bash
python main.py
```

You'll see a menu with all options!

---

## 📊 Step-by-Step Workflow

### Day 1: Collect Data (1 hour)

```
1. Run option 1: Scrape businesses from Google Maps
2. Run option 3: Analyze & qualify
3. Run option 12: Check statistics
```

### Day 2: Find Contacts (30 min)

```
1. Run option 5: Find emails (HIGH priority)
2. Run option 6: View businesses with emails
```

### Day 3: Generate Emails (30 min)

```
1. Run option 8: Preview email (check quality)
2. Run option 7: Generate all emails
```

### Day 4: Start Outreach

```
1. Run option 9: Send batch (start with 10)
2. Next day: Send another 10
3. Continue daily until all sent
```

---

## 🎯 Features Explained

### 1. Scraping (Option 1)

**What it does:**

- Opens Google Maps automatically
- Searches for your target businesses
- Collects: name, address, phone, website, rating
- Saves everything to Google Sheets

**Time:** ~2-3 min per locality

**Output:** 150-300 businesses in Google Sheet

---

### 2. Analysis (Option 3)

**What it does:**

- Checks each website automatically
- Scores performance, SEO, mobile-friendliness
- Assigns priority (HIGH/MEDIUM/LOW)

**Qualification Logic:**

```
HIGH PRIORITY:
✅ No website
✅ Website performance < 55/100
✅ No SSL certificate
✅ Poor SEO < 60/100

MEDIUM PRIORITY:
⚡ Website has issues but not critical

LOW PRIORITY:
💤 Website is modern and optimized
```

**Time:** ~5 sec per business

---

### 3. Email Finding (Option 5)

**Methods used (FREE):**

1. Scrape contact pages
2. Try common patterns (info@, contact@)
3. Hunter.io free tier if available

**Success rate:** 60-70%

---

### 4. Email Generation (Option 7)

**Uses Gemini AI to create:**

- Personalized subject lines
- Natural, human-sounding emails
- Specific observations about their business
- Casual tone that gets replies

**Example output:**

```
Subject: quick question about your dubai marina presence

Hey ABC Properties,

I was checking out real estate agencies in Dubai Marina
and noticed you have solid reviews (4.7★) but your website
is loading pretty slow on mobile.

I help agencies build faster, lead-generating websites.
Working with a few other agencies in JVC right now.

Would you be open to a quick chat?

Mubeen
```

**Cost:** FREE (1,500 emails/day limit)

---

### 5. Sending (Option 9)

**Uses Gmail API:**

- Sends through your Gmail account
- Respects rate limits (500/day max)
- Adds delays between sends
- Tracks who was sent

**Best practice:** Send 10-20/day

---

## 🐛 Troubleshooting

### Error: "credentials.json not found"

**Solution:**

1. Make sure you downloaded the service account JSON
2. Renamed it to exactly `credentials.json`
3. Put it in the same folder as your Python files

---

### Error: "GEMINI_API_KEY not found"

**Solution:**

1. Create a `.env` file (not .env.txt!)
2. Add: `GEMINI_API_KEY=your-key-here`
3. Make sure it's in the project folder

---

### Error: "gmail_credentials.json not found"

**Solution:**

1. Create OAuth credentials (not service account)
2. Download as `gmail_credentials.json`
3. Put in project folder
4. First run will open browser to authorize

---

### Browser closes immediately

**Solution:**
In `scraper.py`, line ~27:

```python
# Change this:
browser = await p.chromium.launch(headless=False)  # See browser
# Instead of:
browser = await p.chromium.launch(headless=True)   # Invisible
```

---

### Quota exceeded errors

**Google Gemini:**

- Limit: 1,500 requests/day
- Reset: Every 24 hours
- Solution: Wait or generate fewer emails

**Gmail API:**

- Limit: 500 emails/day
- Solution: Send in batches over multiple days

**PageSpeed API:**

- Limit: 25,000 requests/day
- Solution: You won't hit this!

---

### Sheets not updating

**Solution:**

1. Share the Google Sheet with service account email:
   - Open your Google Sheet
   - Click "Share"
   - Add the service account email (find in credentials.json: `client_email`)
   - Give "Editor" access

---

## ✅ Best Practices

### Scraping:

- ✅ Run during business hours
- ✅ Add 2-3 sec delays
- ✅ Don't scrape same area repeatedly
- ❌ Don't run 24/7

### Email Sending:

- ✅ Send 10-20 per day
- ✅ Wait 24 hours between batches
- ✅ Personalize emails
- ✅ Reply quickly to responses
- ❌ Don't send 100+ at once
- ❌ Don't use personal email

### Deliverability:

- ✅ Use Gmail (best deliverability)
- ✅ Warm up new accounts (send 5-10/day first week)
- ✅ Keep bounce rate < 5%
- ✅ Monitor spam reports

---

## 📈 Expected Results

### Week 1:

- Scrape: 200-300 businesses
- Qualify: 60-80 HIGH priority
- Find emails: 40-50 contacts
- Send: 50-70 emails

### Response Rates:

- Open rate: 40-70%
- Reply rate: 10-25%
- Meetings: 3-6 per week
- Deals: 1-2 per month

---

## 🔄 Switching Cities/Niches

### Option 1: Edit config.py directly

```python
TARGET = {
    "city": "London",              # Change city
    "niche": "restaurant",         # Change niche
    # ... update all fields ...
}
```

### Option 2: Use menu (Option 11)

Run the program and choose option 11 to change target interactively!

### Option 3: Quick switch functions

In Python console:

```python
from config import switch_to_restaurants_nyc
switch_to_restaurants_nyc()
```

**Changes apply immediately to all modules!**

---

## 💡 Pro Tips

### 1. Start Small

- Test with 10 businesses first
- Verify everything works
- Then scale up

### 2. Monitor Quality

- Check generated emails regularly
- Adjust AI prompts if needed
- Test different approaches

### 3. A/B Testing

- Try different subject lines
- Test email lengths
- Track what works

### 4. Follow Up

- Reply within 24 hours
- Have a clear next step
- Be helpful, not pushy

---

## 🎓 Advanced Features

### Change niche MID-campaign:

```python
# In config.py
TARGET["niche"] = "dental clinic"
TARGET["niche_plural"] = "dental clinics"
TARGET["your_service"] = "appointment systems"
# ... etc
```

All future operations use new niche!

### Multiple cities:

Create different project folders:

```
dubai-real-estate/
london-restaurants/
nyc-gyms/
```

Each with own config.py and credentials.

---

## 📞 Support

If you get stuck:

1. Check error message carefully
2. Read this guide section again
3. Check official docs:
   - Google Gemini: https://ai.google.dev
   - Gmail API: https://developers.google.com/gmail
   - Sheets API: https://developers.google.com/sheets

---

## 🎉 You're Ready!

Your complete FREE automation system:

✅ Scrapes ANY business in ANY city
✅ Analyzes websites automatically
✅ Finds email addresses
✅ Generates personalized AI emails
✅ Sends via Gmail API
✅ Tracks everything in Google Sheets

**Total cost: $0/month**

**Start with:**

```bash
cd business-automation
source venv/bin/activate  # or venv\Scripts\activate on Windows
python main.py
```

**Choose Option 13** to run the full pipeline!

Good luck! 🚀

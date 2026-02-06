# ✅ Quick Start Checklist

## 📦 Before You Start

### Files Needed

- [ ] All Python files in project folder
- [ ] `requirements.txt` file
- [ ] `.env` file created
- [ ] `credentials.json` (Google Sheets)
- [ ] `gmail_credentials.json` (Gmail API)

### Software

- [ ] Python 3.11+ installed
- [ ] Virtual environment created & activated
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Playwright browser installed (`playwright install chromium`)

---

## 🔐 API Keys Checklist

### 1. Gemini API (AI Emails)

- [ ] Got API key from https://makersuite.google.com/app/apikey
- [ ] Added to `.env` file: `GEMINI_API_KEY=AIza...`

### 2. Google Sheets (Database)

- [ ] Enabled Google Sheets API
- [ ] Enabled Google Drive API
- [ ] Created service account
- [ ] Downloaded `credentials.json`
- [ ] Tested connection: `python sheets_database.py`

### 3. Gmail API (Send Emails)

- [ ] Enabled Gmail API
- [ ] Created OAuth credentials
- [ ] Downloaded `gmail_credentials.json`
- [ ] Configured consent screen
- [ ] Added yourself as test user

---

## ⚙️ Configuration Checklist

### config.py

- [ ] Updated `TARGET['city']` to your target city
- [ ] Updated `TARGET['localities']` with neighborhoods
- [ ] Updated `TARGET['niche']` to your business type
- [ ] Updated `TARGET['niche_plural']`
- [ ] Updated `TARGET['your_service']`
- [ ] Updated `TARGET['your_service_benefit']`
- [ ] Updated `EMAIL['your_name']`
- [ ] Updated `EMAIL['your_email']` ⚠️ IMPORTANT!

---

## 🧪 Test Everything

### 1. Test Database

```bash
python sheets_database.py
```

✅ Should show: "Connected to Google Sheets"

### 2. Test Configuration

```bash
python config.py
```

✅ Should show your current configuration

### 3. Test Scraper (dry run)

```bash
python scraper.py
```

✅ Should open browser and start scraping

### 4. Test Gmail

```bash
python email_sender.py
```

✅ Should connect to Gmail (will open browser first time)

---

## 🚀 Ready to Run!

### Option 1: Full Pipeline

```bash
python main.py
# Choose option 13
```

### Option 2: Step by Step

```bash
python main.py
# Choose options 1 → 3 → 5 → 7 → 9
```

---

## 📊 Monitor Progress

### Check Google Sheet

- URL shown when you run `sheets_database.py`
- Should have 4 tabs: Agencies, Generated Emails, Sent Emails, Statistics

### Check Stats

```bash
python main.py
# Choose option 12
```

---

## ⚠️ Common Issues

### "credentials.json not found"

→ Make sure file is in project folder, not in Downloads

### "GEMINI_API_KEY not found"

→ Create `.env` file (not .env.txt)

### "Gmail auth failed"

→ Make sure you added yourself as test user in OAuth consent screen

### Browser closes immediately

→ Change `headless=True` to `headless=False` in scraper.py

---

## 💰 Cost Verification

- Gemini API: FREE ✅
- PageSpeed API: FREE ✅
- Gmail API: FREE ✅
- Google Sheets: FREE ✅
- Playwright: FREE ✅

**Total: $0/month** 🎉

---

## 📈 Success Metrics

After running full pipeline once:

- [ ] Businesses scraped: 100+
- [ ] HIGH priority: 20-30
- [ ] Emails found: 15-25
- [ ] Emails generated: 15-25
- [ ] Ready to send: ✅

Now send 10-20 per day!

---

## 🔄 Daily Routine

**Morning:**

```bash
python main.py
# Option 9: Send 10-20 emails
```

**Evening:**

- Check Google Sheet for replies
- Respond to any replies promptly
- Update notes

**Weekly:**

- Review what's working
- Adjust email templates if needed
- Try new localities

---

## 🎯 What Makes This System Special

✅ **100% FREE** - No monthly costs
✅ **Flexible** - Change city/niche anytime
✅ **Automated** - Runs on autopilot
✅ **Scalable** - Handle 1000s of businesses
✅ **Smart** - AI personalizes every email
✅ **Safe** - Respects rate limits
✅ **Trackable** - Everything in Google Sheets

---

## 💡 Quick Tips

1. **Start small**: Test with 10 businesses first
2. **Be patient**: Cold outreach takes time
3. **Stay consistent**: Send emails daily
4. **Reply fast**: Respond within 24 hours
5. **Track results**: See what works

---

## 🆘 Need Help?

1. Check SETUP_GUIDE.md (detailed instructions)
2. Read error messages carefully
3. Google the specific error
4. Check official API docs

---

## ✨ You're All Set!

Run this to start:

```bash
cd business-automation
source venv/bin/activate  # Windows: venv\Scripts\activate
python main.py
```

Good luck! 🚀

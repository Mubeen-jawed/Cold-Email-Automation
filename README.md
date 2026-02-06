# 🚀 100% FREE Multi-City Multi-Niche Business Outreach Automation

**Automate your B2B outreach for ANY business type in ANY city - completely FREE!**

Target real estate agents in Dubai, restaurants in New York, fitness centers in London, or ANY niche in ANY location - just change one config file!

## ✨ What This Does

1. **Scrapes** businesses from Google Maps (any city, any niche)
2. **Analyzes** their websites automatically (performance, SEO, quality)
3. **Qualifies** them based on your criteria
4. **Finds** email addresses (scraping + Hunter.io free tier)
5. **Generates** personalized AI emails for each business
6. **Sends** emails via Gmail API (500/day free)
7. **Tracks** everything in Google Sheets

## 💰 Cost: $0/Month

| Service              | Free Limit          | What We Use It For   |
| -------------------- | ------------------- | -------------------- |
| Google Gemini API    | 1,500 requests/day  | AI email generation  |
| Gmail API            | 500 emails/day      | Sending emails       |
| Google Sheets API    | Unlimited           | Database             |
| Google PageSpeed API | 25,000 requests/day | Website analysis     |
| Playwright           | Unlimited           | Google Maps scraping |

**No credit card needed. No paid subscriptions. 100% FREE.**

## 🎯 Perfect For

- **Freelancers**: Get clients by offering websites, SEO, design
- **Agencies**: Automate lead generation for any niche
- **Startups**: Build your client base without ads
- **Consultants**: Reach potential clients at scale

## 🌍 Works For ANY City + ANY Niche

Just edit `config.py`:

```python
# Dubai Real Estate
TARGET = {
    "city": "Dubai",
    "niche": "real estate agency",
    "your_service": "modern websites",
}

# New York Restaurants
TARGET = {
    "city": "New York",
    "niche": "restaurant",
    "your_service": "online ordering systems",
}

# London Gyms
TARGET = {
    "city": "London",
    "niche": "fitness center",
    "your_service": "member management",
}
```

**Everything updates automatically!** Emails, search queries, qualification logic - all adapt to your target.

## 🚀 Quick Start

### 1. Install Python

```bash
# Verify Python 3.11+
python --version
```

### 2. Setup Project

```bash
# Create folder
mkdir business-automation
cd business-automation

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
playwright install chromium
```

### 3. Get API Keys (All FREE)

**Gemini API** (AI emails):

- Get it: https://makersuite.google.com/app/apikey
- Add to `.env`: `GEMINI_API_KEY=your-key`

**Google Sheets** (database):

- Enable Google Sheets API
- Create service account
- Download `credentials.json`

**Gmail API** (sending):

- Enable Gmail API
- Create OAuth credentials
- Download `gmail_credentials.json`

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed instructions!

### 4. Configure Target

```bash
# Edit config.py
nano config.py  # or use any text editor
```

Update:

- City & localities
- Business niche
- Your service offering
- Your email

### 5. Run!

```bash
python main.py
```

Choose option 13 for full automation or run steps individually!

## 📊 Features

### 🤖 Smart Qualification

Automatically identifies high-value leads:

- No website = HIGH priority
- Slow website (<55/100) = HIGH priority
- Poor SEO (<60/100) = HIGH priority
- No SSL = HIGH priority

### 🧠 AI Personalization

Each email is unique and personalized:

- Mentions specific business observations
- Natural, human tone
- Adapted to your niche/city
- No marketing jargon

### 📧 Safe Sending

- Respects Gmail limits (500/day)
- Adds delays between sends
- Tracks delivery status
- Prevents spam

### 📈 Complete Tracking

Everything stored in Google Sheets:

- All businesses found
- Qualification scores
- Email addresses
- Generated emails
- Send status

## 📁 Project Structure

```
business-automation/
├── config.py              # ⚠️ EDIT THIS - Target configuration
├── sheets_database.py     # Google Sheets database
├── scraper.py            # Google Maps scraper
├── analyzer.py           # Website analyzer
├── email_finder.py       # Email discovery
├── email_generator.py    # AI email generation
├── email_sender.py       # Gmail sender
├── main.py              # Control panel
├── requirements.txt      # Dependencies
├── .env                 # API keys
├── credentials.json     # Google Sheets (you create)
├── gmail_credentials.json  # Gmail API (you create)
├── SETUP_GUIDE.md       # Detailed setup instructions
└── CHECKLIST.md         # Quick start checklist
```

## 🎯 Usage Examples

### Scrape Businesses

```bash
python main.py
# Option 1: Scrape businesses
# Collects name, phone, website, rating, reviews
```

### Analyze Websites

```bash
# Option 3: Analyze & qualify
# Checks performance, SEO, mobile, SSL
# Assigns priority levels
```

### Generate Emails

```bash
# Option 7: Generate emails
# AI creates personalized email for each business
```

### Send Batch

```bash
# Option 9: Send batch
# Sends via Gmail API
# Recommendation: 10-20 per day
```

## 📈 Expected Results

### Week 1

- **Scrape**: 200-300 businesses
- **Qualify**: 60-80 HIGH priority
- **Find emails**: 40-50 contacts
- **Send**: 50-70 emails
- **Replies**: 5-15 (10-20% rate)
- **Meetings**: 2-4

### Month 1

- **Total outreach**: 200-400 emails
- **Reply rate**: 10-25%
- **Meetings booked**: 8-20
- **Deals closed**: 2-5

## 🔧 Customization

### Change City

```python
# In config.py
TARGET["city"] = "London"
TARGET["localities"] = ["Westminster", "Chelsea", "Mayfair"]
```

### Change Niche

```python
TARGET["niche"] = "dental clinic"
TARGET["niche_plural"] = "dental clinics"
TARGET["your_service"] = "appointment booking systems"
TARGET["your_service_benefit"] = "reduce no-shows"
```

**All modules update automatically!**

### Adjust Qualification

```python
# In config.py
QUALIFICATION = {
    "min_performance_score": 60,  # Stricter
    "min_seo_score": 70,          # Stricter
    "min_rating": 4.0,            # Higher threshold
}
```

### Email Settings

```python
EMAIL = {
    "max_per_day": 50,      # Gmail allows 500
    "batch_size": 20,       # Per batch
    "delay_between_sends": 30,  # Seconds
}
```

## 🐛 Troubleshooting

### Common Issues

**"credentials.json not found"**

- Download service account JSON from Google Cloud
- Rename to `credentials.json`
- Place in project folder

**"GEMINI_API_KEY not found"**

- Create `.env` file (not .env.txt)
- Add: `GEMINI_API_KEY=your-key`

**"Gmail auth failed"**

- Make sure you created OAuth credentials (not service account)
- Add yourself as test user in consent screen

**Browser closes immediately**

- Set `headless=False` in scraper.py to see browser

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for more solutions!

## ✅ Best Practices

### Scraping

✅ Run during business hours
✅ Add 2-3 sec delays
✅ Don't scrape same area daily
❌ Don't run 24/7

### Email Sending

✅ Send 10-20 per day
✅ Wait 24 hours between batches
✅ Personalize subject lines
✅ Reply within 24 hours
❌ Don't send 100+ at once
❌ Don't use personal email

### Deliverability

✅ Use Gmail account
✅ Warm up new accounts (5-10/day first week)
✅ Keep bounce rate < 5%
✅ Monitor spam reports

## 🎓 Advanced Usage

### Multiple Cities/Niches

Create separate folders:

```
dubai-real-estate/
london-restaurants/
nyc-fitness/
```

Each with own config.py and credentials!

### A/B Testing

Change email generation prompts in `email_generator.py` to test different styles.

### Custom Qualification

Edit `analyzer.py` to add your own qualification logic.

## 📚 Documentation

- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detailed setup instructions
- [CHECKLIST.md](CHECKLIST.md) - Quick start checklist
- config.py - All configuration options (heavily commented)

## 🤝 Contributing

This is a complete, working system. Feel free to:

- Fork and customize
- Add new features
- Improve qualification logic
- Share your results!

## ⚠️ Disclaimer

- Respect rate limits
- Follow email best practices
- Check local regulations
- Use responsibly
- Don't spam

## 📄 License

MIT License - Use freely for personal or commercial projects!

## 🎉 Why This Is Better Than Alternatives

| Feature               | This System     | Instantly.ai | Apollo    | Hunter.io   |
| --------------------- | --------------- | ------------ | --------- | ----------- |
| **Cost**              | FREE            | $37/mo       | $49/mo    | $49/mo      |
| **Email Generation**  | AI personalized | Templates    | Templates | N/A         |
| **City Targeting**    | ANY city        | Manual       | Manual    | N/A         |
| **Niche Flexibility** | ANY niche       | Manual       | Manual    | N/A         |
| **Website Analysis**  | Automatic       | Manual       | N/A       | N/A         |
| **Qualification**     | AI-powered      | Manual       | Manual    | N/A         |
| **Daily Limit**       | 500             | Unlimited\*  | 500       | 25 searches |
| **Setup Time**        | 2 hours         | 30 min       | 30 min    | 5 min       |
| **Customizable**      | 100%            | Limited      | Limited   | No          |

\*Unlimited but charges per email

## 🚀 Get Started Now!

1. Clone/download this repository
2. Follow [SETUP_GUIDE.md](SETUP_GUIDE.md)
3. Run `python main.py`
4. Start getting clients!

**Total cost: $0. Total time: 2 hours setup.**

---

Made with ❤️ for entrepreneurs who want to grow without expensive tools.

Questions? Check [SETUP_GUIDE.md](SETUP_GUIDE.md) or open an issue!

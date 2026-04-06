# Quick Start Checklist

## Before You Start

### Software
- [ ] Python 3.11+ installed
- [ ] Virtual environment created and activated
- [ ] `pip install -r requirements.txt -r requirements_api.txt` completed
- [ ] `playwright install chromium` completed

### Services
- [ ] PostgreSQL database created (local or hosted)
- [ ] OpenRouter account and API key (https://openrouter.ai)
- [ ] SMTP email account ready (cPanel, Outlook, Zoho, etc.)

---

## Environment Variables (`.env`)

- [ ] `DATABASE_URL=postgresql://...` set
- [ ] `OPENROUTER_API_KEY=sk-or-...` set
- [ ] `SMTP_PASSWORD=...` set

Optional:
- [ ] `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` (for Google OAuth)
- [ ] `APP_URL` (for deployments — default is `http://localhost:8000`)

---

## `config.py` Settings

- [ ] `TARGET['city']` updated
- [ ] `TARGET['state']` and `TARGET['country']` updated
- [ ] `TARGET['localities']` filled with real area names
- [ ] `TARGET['niche']` set to your business type
- [ ] `TARGET['niche_plural']` set
- [ ] `TARGET['your_service']` set
- [ ] `TARGET['your_service_benefit']` set
- [ ] `EMAIL['your_name']` set to your name
- [ ] `EMAIL['your_email']` set to your sending address
- [ ] `EMAIL['smtp_host']`, `smtp_port`, `smtp_user` configured

---

## First Run

```bash
# Activate venv first
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

python api.py
```

Open http://localhost:8000

- [ ] Landing page loads
- [ ] Sign up for an account at `/auth`
- [ ] Dashboard loads at `/dashboard`

---

## Dashboard Workflow

- [ ] Create a campaign (Campaigns tab → New Campaign)
- [ ] Activate the campaign
- [ ] Run **Scrape** (try 10–20 results per area first)
- [ ] Run **Analyze** (scores websites)
- [ ] Run **Find Emails**
- [ ] Run **Generate Emails**
- [ ] Check email preview looks good
- [ ] Run **Send** (start with a small batch: 10–20)

---

## Verify Each Step

| Step | What to check |
|---|---|
| Scrape | Leads appear in the Leads tab |
| Analyze | Leads have priority (HIGH/MEDIUM/LOW) |
| Find Emails | Leads have email addresses |
| Generate | Emails tab shows subject + body |
| Send | Sent count increases in stats |
| Inbox sync | Replies appear in Inbox tab |

---

## Common Issues

| Error | Fix |
|---|---|
| `DATABASE_URL not set` | Add to `.env` |
| `OPENROUTER_API_KEY not set` | Add to `.env` |
| SMTP connection failed | Check `smtp_host`/`smtp_port`/`SMTP_PASSWORD` |
| "No active campaign" | Campaigns tab → activate a campaign |
| Browser closes (scraper) | Set `visible_browser: True` in `config.py` |
| Playwright not found | Run `playwright install chromium` |

---

## Daily Routine

**Morning:**
- Send a batch of 10–20 emails from the dashboard

**Evening:**
- Sync inbox (Inbox tab → Sync)
- Reply to any leads within 24 hours

**Weekly:**
- Check open/reply rates in stats
- Add new localities or niches if needed
- Adjust AI tone/guidelines if response rate is low

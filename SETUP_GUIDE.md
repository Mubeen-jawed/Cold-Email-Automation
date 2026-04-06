# Setup Guide

## Prerequisites

- Python 3.11+
- PostgreSQL database (local or a hosted service like Supabase, Railway, Render, etc.)
- An SMTP email account (cPanel, Outlook, Zoho, Yahoo, etc.)
- An [OpenRouter](https://openrouter.ai) account (free tier)

---

## 1. Install Python

### Windows

1. Download from https://python.org/downloads
2. Run the installer — check **"Add Python to PATH"**
3. Verify: `python --version`

### Mac

```bash
brew install python@3.11
python3 --version
```

### Linux

```bash
sudo apt update && sudo apt install python3.11 python3-pip
```

---

## 2. Project Setup

```bash
# Clone / download the project, then:
cd cold-email-automation

python -m venv venv

# Activate:
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt -r requirements_api.txt
playwright install chromium
```

---

## 3. PostgreSQL Database

You need a PostgreSQL database. The app creates all tables automatically on first run.

### Option A — Local PostgreSQL

```bash
# Install PostgreSQL, then:
createdb cold_email
# Connection string:
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/cold_email
```

### Option B — Hosted (Supabase free tier)

1. Create a project at https://supabase.com
2. Go to **Settings → Database → Connection string**
3. Copy the URI (starts with `postgresql://...`)

### Option C — Railway / Render

Create a PostgreSQL service and copy the provided `DATABASE_URL`.

---

## 4. OpenRouter API Key (AI Emails)

1. Sign up at https://openrouter.ai
2. Go to **Keys** and create a new key
3. The free model `arcee-ai/trinity-large-preview:free` requires no credits

---

## 5. SMTP Email Account

You need an SMTP-enabled email account to send emails.

### cPanel / Namecheap (recommended)

- `smtp_host`: `mail.yourdomain.com`
- `smtp_port`: `465`
- User: your full email address

### Outlook / Office 365

- `smtp_host`: `smtp.office365.com`
- `smtp_port`: `587`

### Zoho Mail

- `smtp_host`: `smtp.zoho.com`
- `smtp_port`: `465`

### Yahoo Mail

- `smtp_host`: `smtp.mail.yahoo.com`
- `smtp_port`: `465`

---

## 6. Create Your `.env` File

Create a file named `.env` in the project root:

```env
# Required
DATABASE_URL=postgresql://user:password@localhost:5432/cold_email
OPENROUTER_API_KEY=sk-or-...
SMTP_PASSWORD=your-email-password

# Optional — Google OAuth login button
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...

# Optional — set to your public URL when deploying
APP_URL=http://localhost:8000
```

Never commit `.env` to git.

---

## 7. Configure `config.py`

Open `config.py` and update the defaults (these are also editable from the dashboard):

```python
TARGET = {
    "city": "Your City",
    "state": "Your State",
    "country": "USA",
    "localities": ["Downtown", "Suburb A", "Suburb B"],
    "niche": "home service business",
    "niche_plural": "home service businesses",
    "industry": "home services",
    "your_service": "website conversion optimization",
    "your_service_benefit": "get more leads online",
    "pain_point": "limited online visibility",
}

EMAIL = {
    "your_name":  "Your Name",
    "your_email": "you@yourdomain.com",
    "smtp_host":  "mail.yourdomain.com",
    "smtp_port":  465,
    "smtp_user":  "you@yourdomain.com",
    # smtp_password is read from SMTP_PASSWORD env var
}
```

---

## 8. Run the App

```bash
python api.py
```

Open `http://localhost:8000`.

You'll see the landing page. Click **Get Started** to create an account, then log in.

---

## 9. First-Time Dashboard Flow

1. **Create a campaign** — click "New Campaign", fill in city/niche/areas
2. **Activate the campaign**
3. **Scrape** — click Scrape in the pipeline panel (pick how many results per area)
4. **Analyze** — scores every scraped website
5. **Find Emails** — discovers contact emails
6. **Generate Emails** — AI writes a personalized email for each HIGH-priority lead
7. **Send** — sends the batch via SMTP

The live log panel streams all output in real time.

---

## 10. Google OAuth Login (Optional)

If you want a "Sign in with Google" button:

1. Go to https://console.cloud.google.com
2. Create a project → **APIs & Services → Credentials**
3. Create **OAuth 2.0 Client ID** (type: Web application)
4. Add authorized redirect URI: `http://localhost:8000/api/auth/google/callback`
5. Copy **Client ID** and **Client Secret** into `.env`:

```env
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

---

## 11. IMAP Inbox Sync (Optional)

To pull replies from your inbox into the dashboard:

- `imap_host` in `config.py` (leave blank to use the same host as `smtp_host`)
- The IMAP server must support SSL on port 993 (most do)
- Uses the same credentials as SMTP

Click **Sync Inbox** in the dashboard Inbox tab.

---

## Troubleshooting

### `DATABASE_URL not set`

Add it to `.env`. Make sure the database exists and the user has access.

### `OPENROUTER_API_KEY not set`

Add it to `.env`. Get a free key at openrouter.ai.

### SMTP connection failed

- Double-check `smtp_host`, `smtp_port`, `smtp_user` in `config.py`
- Make sure `SMTP_PASSWORD` is in `.env`
- Try port `587` (STARTTLS) if `465` (SSL) doesn't work
- Some providers require "App Passwords" when 2FA is on

### Browser closes immediately (scraper)

Set `"visible_browser": True` in `SCRAPING` in `config.py` to watch the browser and see errors.

### "No active campaign"

Go to Campaigns → create and activate one before running any pipeline step.

### Playwright not found

```bash
playwright install chromium
```

---

## Docker

```bash
docker build -t leadflow .
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e OPENROUTER_API_KEY=sk-or-... \
  -e SMTP_PASSWORD=... \
  leadflow
```

See `deploy/` for full VPS + nginx instructions.

# LeadFlow — Automated Cold Email Outreach

LeadFlow finds local businesses that need your service, writes them a personalized email using AI, and sends it — all automatically, from a simple web dashboard you open in your browser.

No coding required to use it. This guide covers how to set it up the first time.

---

## What It Does (Plain English)

1. You tell it what kind of business to target (e.g. "HVAC companies in Miami")
2. It searches Google Maps and collects a list of matching businesses
3. It checks each business's website — is it slow? Bad SEO? No website at all?
4. It finds the email address for each business
5. It uses AI to write a unique, personalized email for each one — mentioning their specific website issues
6. It sends the emails through your email account
7. You can see who opened your email and who replied, right in the dashboard

---

## What You Need Before Starting

You need four things set up before you can run this. All of them have free options.

### 1. Python (the programming language that runs this app)
Just needs to be installed once. Download it from **https://python.org/downloads** — get version 3.11 or newer.

> **Windows tip:** When installing, check the box that says "Add Python to PATH" before clicking Install.

### 2. A Database (where your leads and emails are stored)
This app stores all your leads in a PostgreSQL database. The easiest free option is **Supabase**:
- Go to https://supabase.com and create a free account
- Create a new project
- Go to **Settings → Database** and copy the "Connection string" — it looks like: `postgresql://postgres:yourpassword@...`

### 3. An OpenRouter API Key (powers the AI email writing)
- Go to https://openrouter.ai and create a free account
- Click your profile → **Keys** → create a new key
- The default AI model used is free — no credit card needed

### 4. An Email Account to Send From
Any business email works (cPanel, Outlook, Zoho, Yahoo, etc.). You just need to know:
- Your email address
- Your email password
- Your email server's SMTP address (your hosting provider can tell you this)

---

## Setup (One Time Only)

### Step 1 — Download the project

Download or clone this project to your computer. Open a terminal (Command Prompt on Windows, Terminal on Mac) and navigate to the project folder.

### Step 2 — Install the required software

Copy and paste these commands one at a time:

```
python -m venv venv
```
```
venv\Scripts\activate
```
*(On Mac/Linux, use: `source venv/bin/activate` instead)*

```
pip install -r requirements.txt -r requirements_api.txt
```
```
playwright install chromium
```

This installs everything the app needs. It only takes a few minutes.

### Step 3 — Create your secrets file

In the project folder, create a new text file called `.env` (exactly that — a dot, then "env", no other extension).

Paste this into it and fill in your own values:

```
DATABASE_URL=postgresql://your-database-url-here
OPENROUTER_API_KEY=your-openrouter-key-here
SMTP_PASSWORD=your-email-password-here
```

That's it. Three lines. Save the file.

> Your email password lives only in this file on your computer. It is never shared anywhere.

### Step 4 — Enter your email settings

Open the file `config.py` in any text editor (Notepad works fine) and find this section:

```python
EMAIL = {
    "your_name":  "Mubeen",
    "your_email": "mubeen@revenuelyft.com",
    "smtp_host":  "mail.revenuelyft.com",
    "smtp_port":  465,
    "smtp_user":  "mubeen@revenuelyft.com",
    ...
}
```

Replace with your own name, email address, and SMTP server. If you're not sure what your SMTP server address is, ask your email hosting provider or look it up below:

| Email provider | SMTP server address | Port |
|---|---|---|
| cPanel / Namecheap | `mail.yourdomain.com` | 465 |
| Outlook / Office 365 | `smtp.office365.com` | 587 |
| Zoho Mail | `smtp.zoho.com` | 465 |
| Yahoo Mail | `smtp.mail.yahoo.com` | 465 |

### Step 5 — Start the app

In your terminal, run:

```
python api.py
```

Then open your browser and go to: **http://localhost:8000**

You'll see the LeadFlow landing page. Click **Get Started** to create your account.

---

## Using the Dashboard

Once you're logged in, here's what to do:

### 1. Create a Campaign
A campaign is one targeting goal — for example "HVAC companies in Miami".

- Click **Campaigns** → **New Campaign**
- Enter the city, the type of business you're targeting, the areas/neighborhoods to search, and what service you're offering
- Click **Activate** on the campaign to make it the active one

### 2. Run the Pipeline
The pipeline runs in steps. You can run them one at a time or all at once.

| Step | What it does |
|---|---|
| **Scrape** | Searches Google Maps and collects businesses |
| **Analyze** | Checks each business's website for problems |
| **Find Emails** | Finds email addresses for each business |
| **Generate Emails** | AI writes a personalized email for each business |
| **Send** | Sends the emails through your email account |

You'll see live updates in the log panel at the bottom of the screen as each step runs.

### 3. Review Your Leads
Click **Leads** to see every business that was found. Each one shows:
- Their name, location, rating, and website
- Priority level (HIGH / MEDIUM / LOW)
- Whether an email was found and sent

**Priority levels explained:**
- **HIGH** — best leads to contact. Either no website at all, or their website is slow / bad for SEO
- **MEDIUM** — some issues, worth reaching out
- **LOW** — their website looks fine, probably not a great prospect

### 4. Check Your Inbox
Click **Inbox** → **Sync** to pull in any replies from your email account. You can read and reply to messages directly in the dashboard.

---

## Adjusting What the AI Writes

In the dashboard, go to **Settings → Email Creative** to control how the AI writes your emails:

- **Tone** — casual, professional, or casual-professional (default)
- **Custom guidelines** — add specific instructions like "always mention we're a local company"
- **Sample email** — paste an example of how you like to write, and the AI will match your style
- **Template mode** — if you'd prefer to write the email yourself with no AI, switch to Template and type your own subject and body

---

## Fixing Common Problems

**"DATABASE_URL not set"**
Your `.env` file is missing or in the wrong folder. Make sure it's in the same folder as `api.py`.

**"OPENROUTER_API_KEY not set"**
Same as above — check your `.env` file has the right key.

**Email sending fails**
- Double-check the `smtp_host`, `smtp_port`, and `smtp_user` in `config.py`
- Make sure `SMTP_PASSWORD` is in your `.env` file
- If port 465 doesn't work, try 587

**"No active campaign"**
Go to the Campaigns tab, create a campaign, and click Activate on it.

**The scraper opens a browser window and then immediately closes**
Open `config.py` and change `"visible_browser": False` to `"visible_browser": True`. This lets you see what's happening in the browser window and spot any errors.

---

## Tips for Getting Replies

- **Send 10–20 emails per day** — sending hundreds at once is the fastest way to get flagged as spam
- **In your first week**, send only 5–10 per day while your account warms up
- **Reply quickly** — if someone responds, reply within a few hours while you're fresh in their mind
- **Watch your open rates** — if nobody is opening your emails, the subject line probably needs work. Try the AI tone settings or write your own subject lines

---

## For Developers

The app is a Python FastAPI server (`api.py`) that serves three HTML pages from the `static/` folder and exposes a REST API. User accounts and campaigns are stored in SQLite (`app.db`). All lead/email data is stored in PostgreSQL. The scraper uses Playwright (headless Chromium). AI emails are generated via OpenRouter's API.

To run with Docker:

```bash
docker build -t leadflow .
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e OPENROUTER_API_KEY=sk-or-... \
  -e SMTP_PASSWORD=... \
  leadflow
```

See `SETUP_GUIDE.md` for full technical details and `deploy/` for server deployment scripts.

---

## License

MIT — free to use for personal or commercial projects.

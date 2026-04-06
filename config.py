"""
🌍 MASTER CONFIGURATION FILE
Change city, niche, and all settings from here!
"""

# ============================================
# 🎯 BUSINESS TARGET CONFIGURATION
# ============================================
# Change these to target ANY city and ANY niche!

TARGET = {
    # City & Location
    "city": "Seattle & Eastside suburbs",
    "state": "Washington",
    "country": "USA",

  "localities": [
    "Miami Beach",
    "Coral Gables",
    "Kendall (Miami)",
    "Doral",
    "Hialeah",
    "Hollywood (Florida)",
    "Pembroke Pines",
    "Fort Lauderdale Downtown",
    "Boca Raton",
    "Delray Beach",
    "West Palm Beach",
    "Sarasota",
    "Naples (Florida)",
    "Cape Coral",
    "Port St. Lucie",

    "Scottsdale",
    "Chandler (Arizona)",
    "Tempe",
    "Gilbert (Arizona)",
    "Glendale (Arizona)",
    "Peoria (Arizona)",
    "Mesa (Arizona)",
    "Paradise Valley (Arizona)",

    "Dallas Downtown",
    "Plano (Texas)",
    "Frisco (Texas)",
    "McKinney (Texas)",
    "Arlington (Texas)",
    "Irving (Texas)",
    "Katy (Texas)",
    "Sugar Land",
    "The Woodlands",
    "Spring (Texas)",
    "Pearland",
    "Round Rock",
    "Cedar Park",
    "San Antonio Northside",

    "Pasadena (California)",
    "Glendale (California)",
    "Burbank",
    "Long Beach",
    "Santa Ana",
    "Anaheim",
    "Irvine",
    "Fremont (California)",
    "Oakland",
    "Sunnyvale",
    "Mountain View",
    "Santa Clara",
    "Riverside (California)",
    "San Bernardino",

    "Charlotte Uptown",
    "Ballantyne (Charlotte)",
    "Huntersville",
    "Matthews (North Carolina)",
    "Concord (North Carolina)",
    "Raleigh North Hills",
    "Cary (North Carolina)",
    "Apex (North Carolina)",
    "Durham",

    "Denver Downtown",
    "Aurora (Colorado)",
    "Lakewood (Colorado)",
    "Arvada",
    "Westminster (Colorado)",
    "Littleton (Colorado)",
    "Boulder",

    "Chicago Loop",
    "Naperville",
    "Schaumburg",
    "Evanston",
    "Oak Park (Illinois)",
    "Joliet",

    "Nashville Downtown",
    "Franklin (Tennessee)",
    "Brentwood (Tennessee)",
    "Murfreesboro",

    "Kansas City Downtown",
    "Overland Park",
    "Olathe",
    "Lees Summit",

    "Columbus Downtown",
    "Dublin (Ohio)",
    "Westerville",
    "Cleveland Heights",
    "Lakewood (Ohio)",

    "Brooklyn",
    "Queens",
    "Staten Island",
    "Yonkers",
    "Jersey City",
    "Newark (New Jersey)"
  ],
  
    # Business Niche
    "niche": "home service business",
    "niche_plural": "home service businesses",
    "industry": "home services ( HVAC, Plumbing only)",

    # What you're selling
    "your_service": "website conversion optimization",
    "your_service_benefit": "get more leads online and increase revenue",
    "pain_point": "limited online visibility and lead generation"
}

SCRAPING = {
    "results_per_locality": 20,
    "scroll_times": 3,
    "delay_between_businesses": 2,
    "delay_between_localities": 40,
    "visible_browser": False,  # True = see browser, False = invisible
}

QUALIFICATION = {
    "min_performance_score": 55,
    "min_seo_score": 60,
    "min_rating": 3.5,
    "min_reviews": 10,
    "high_priority_threshold": 40,
    "medium_priority_threshold": 20,
}

EMAIL = {
    # ── Who you are ───────────────────────────────────────────────────────────
    "your_name":  "Mubeen",
    "your_email": "mubeen@revenuelyft.com",

    # ── SMTP settings (works with any provider) ───────────────────────────────
    # Common examples:
    #   cPanel / Namecheap  → smtp_host: mail.yourdomain.com   port: 465 or 587
    #   Outlook / Office365 → smtp_host: smtp.office365.com    port: 587
    #   Zoho Mail           → smtp_host: smtp.zoho.com         port: 465 or 587
    #   Yahoo Mail          → smtp_host: smtp.mail.yahoo.com   port: 465
    "smtp_host":     "mail.revenuelyft.com",   # ← your SMTP server
    "smtp_port":     465,                       # ← 465 (SSL) or 587 (STARTTLS)
    "smtp_user":     "mubeen@revenuelyft.com", # ← usually same as your_email
    "smtp_password": "",                        # ← set SMTP_PASSWORD env var instead
    # IMAP (for saving sent emails to webmail Sent folder)
    # Leave blank to use the same host as smtp_host (works for most cPanel/Namecheap servers)
    "imap_host":     "",                        # ← e.g. mail.revenuelyft.com (blank = same as smtp_host)

    # ── Sending limits ────────────────────────────────────────────────────────
    "max_per_day":          1000,
    "batch_size":           20,
    "delay_between_sends":  30,
    "signature":            "Mubeen",

    # ── Email content ─────────────────────────────────────────────────────────
    # "ai" = AI writes each email individually  |  "template" = fixed template
    "email_mode":             "ai",
    "ai_tone":                "casual_professional",
    "ai_guidelines":          "",
    "ai_sample_email":        "",
    "email_template_subject": "",
    "email_template_body":    "",
}

AI = {
    "model": "arcee-ai/trinity-large-preview:free",  # or "openai/gpt-4o-mini"
    "temperature": 0.9,
    "max_tokens": 2048,
    "api_url": "https://openrouter.ai/api/v1/chat/completions"
    
}

SHEETS = {
    "spreadsheet_name": f"{TARGET['niche'].title()} - {TARGET['city']}",
    # If you get "storageQuotaExceeded" error, create spreadsheet manually:
    # 1. Go to sheets.google.com and create new spreadsheet
    # 2. Share it with service account email (from credentials.json)
    # 3. Add URL here:
    "spreadsheet_url": "https://docs.google.com/spreadsheets/d/1IVU4_k2C5s3sZu5u5l0rAdzKrkda5qBd7LA8SX6ryRw/edit?usp=sharing",  # Paste URL here if needed
    "sheets": {
        "agencies": "Agencies",
        "emails": "Generated Emails",
        "sent": "Sent Emails",
        "stats": "Statistics"
    }
}

# ============================================
# 🤖 DYNAMIC FUNCTIONS
# ============================================

def get_search_query(locality):
    """Generate Google Maps search query"""
    return f"{TARGET['niche']} {locality} {TARGET['city']}"

def get_email_context():
    """Get context for AI email generation"""
    return {
        "city": TARGET['city'],
        "niche": TARGET['niche'],
        "niche_plural": TARGET['niche_plural'],
        "industry": TARGET['industry'],
        "service": TARGET['your_service'],
        "benefit": TARGET['your_service_benefit'],
        "pain_point": TARGET['pain_point'],
        "sender_name": EMAIL['your_name'],
    }

def get_qualification_context():
    """Get context for website analysis"""
    return {
        "niche": TARGET['niche'],
        "city": TARGET['city'],
        "typical_website_needs": f"{TARGET['niche_plural']} need websites to showcase properties and capture leads"
    }

# ============================================
# 🔄 QUICK SWITCH FUNCTIONS
# ============================================

def switch_to_real_estate_dubai():
    """Quick switch to Dubai real estate"""
    TARGET.update({
        "city": "Dubai",
        "country": "UAE",
        "localities": ["Dubai Marina", "Business Bay", "Downtown Dubai", "JVC", "Palm Jumeirah"],
        "niche": "real estate agency",
        "niche_plural": "real estate agencies",
        "industry": "real estate",
        "your_service": "modern websites",
        "your_service_benefit": "get more property leads online",
        "pain_point": "outdated or no website",
    })
    SHEETS["spreadsheet_name"] = f"{TARGET['niche'].title()} - {TARGET['city']}"
    print(f"✅ Switched to: {TARGET['niche_plural']} in {TARGET['city']}")

def switch_to_restaurants_nyc():
    """Quick switch to NYC restaurants"""
    TARGET.update({
        "city": "New York",
        "country": "USA",
        "localities": ["Manhattan", "Brooklyn", "Queens"],
        "niche": "restaurant",
        "niche_plural": "restaurants",
        "industry": "food & beverage",
        "your_service": "online ordering systems",
        "your_service_benefit": "boost takeout revenue",
        "pain_point": "no online ordering",
    })
    SHEETS["spreadsheet_name"] = f"{TARGET['niche'].title()} - {TARGET['city']}"
    print(f"✅ Switched to: {TARGET['niche_plural']} in {TARGET['city']}")

def switch_to_custom(city, country, localities, niche, niche_plural, industry, service, benefit, pain):
    """Switch to any custom configuration"""
    TARGET.update({
        "city": city,
        "country": country,
        "localities": localities,
        "niche": niche,
        "niche_plural": niche_plural,
        "industry": industry,
        "your_service": service,
        "your_service_benefit": benefit,
        "pain_point": pain,
    })
    SHEETS["spreadsheet_name"] = f"{niche.title()} - {city}"
    print(f"✅ Switched to: {niche_plural} in {city}")

# ============================================
# 📊 DISPLAY CURRENT CONFIG
# ============================================

def show_current_config():
    """Display current configuration"""
    print("\n" + "="*60)
    print("📋 CURRENT TARGET CONFIGURATION")
    print("="*60)
    print(f"\n🌍 Location:")
    print(f"   City: {TARGET['city']}, {TARGET['country']}")
    print(f"   Areas: {len(TARGET['localities'])} localities")
    
    print(f"\n🎯 Target Business:")
    print(f"   Niche: {TARGET['niche']}")
    print(f"   Industry: {TARGET['industry']}")
    
    print(f"\n💼 Your Offering:")
    print(f"   Service: {TARGET['your_service']}")
    print(f"   Benefit: {TARGET['your_service_benefit']}")
    print(f"   Pain Point: {TARGET['pain_point']}")
    
    print(f"\n📧 Email Settings:")
    print(f"   From: {EMAIL['your_name']}")
    print(f"   Reply-to: {EMAIL['your_email']}")
    print(f"   Daily limit: {EMAIL['max_per_day']}")
    
    print(f"\n📊 Google Sheet:")
    print(f"   Name: {SHEETS['spreadsheet_name']}")
    
    print("\n" + "="*60)
    
    if EMAIL['your_email'] == "your-email@gmail.com":
        print("\n⚠️  WARNING: Update EMAIL['your_email'] with your actual email!")
    
    print()

# Run on import
if __name__ == "__main__":
    show_current_config()
    
    print("\n💡 TO CHANGE CONFIGURATION:")
    print("   1. Edit the TARGET dictionary in this file")
    print("   2. Or use quick switch functions:")
    print("      - switch_to_real_estate_dubai()")
    print("      - switch_to_restaurants_nyc()")
    print("      - switch_to_custom(...)")
    print("\n   Changes apply immediately to all modules!")
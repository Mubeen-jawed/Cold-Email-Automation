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
    "city": "Dubai",
    "country": "UAE",
    "localities": [
        "Dubai Marina",
        "Business Bay", 
        "Downtown Dubai",
        "JVC",
        "Palm Jumeirah",
        "JLT",
        "DIFC"
    ],
    
    # Business Niche
    "niche": "real estate agency",
    "niche_plural": "real estate agencies",
    "industry": "real estate",
    
    # What you're selling
    "your_service": "websites and digital presence",
    "your_service_benefit": "get more leads online",
    "pain_point": "limited online presence",
}

# ============================================
# 📋 EXAMPLE CONFIGURATIONS FOR OTHER CITIES/NICHES
# ============================================

"""
# London Real Estate:
TARGET = {
    "city": "London",
    "country": "UK",
    "localities": ["Westminster", "Kensington", "Chelsea", "Mayfair", "Canary Wharf"],
    "niche": "estate agent",
    "niche_plural": "estate agents",
    "industry": "real estate",
    "your_service": "modern websites and CRM systems",
    "your_service_benefit": "automate lead management",
    "pain_point": "outdated systems",
}

# New York Restaurants:
TARGET = {
    "city": "New York",
    "country": "USA",
    "localities": ["Manhattan", "Brooklyn", "Queens", "Bronx"],
    "niche": "restaurant",
    "niche_plural": "restaurants",
    "industry": "food & beverage",
    "your_service": "online ordering systems",
    "your_service_benefit": "increase takeout orders",
    "pain_point": "no online ordering",
}

# Singapore Fitness Centers:
TARGET = {
    "city": "Singapore",
    "country": "Singapore",
    "localities": ["Central Area", "Marina Bay", "Orchard", "Jurong"],
    "niche": "fitness center",
    "niche_plural": "fitness centers",
    "industry": "health & fitness",
    "your_service": "member management software",
    "your_service_benefit": "automate bookings and payments",
    "pain_point": "manual booking process",
}

# Dubai Dental Clinics:
TARGET = {
    "city": "Dubai",
    "country": "UAE",
    "localities": ["Dubai Marina", "JBR", "Business Bay", "Downtown"],
    "niche": "dental clinic",
    "niche_plural": "dental clinics",
    "industry": "healthcare",
    "your_service": "appointment booking systems",
    "your_service_benefit": "reduce no-shows and manage appointments",
    "pain_point": "inefficient scheduling",
}

# London Coffee Shops:
TARGET = {
    "city": "London",
    "country": "UK",
    "localities": ["Shoreditch", "Camden", "Soho", "Notting Hill"],
    "niche": "coffee shop",
    "niche_plural": "coffee shops",
    "industry": "hospitality",
    "your_service": "loyalty apps and online ordering",
    "your_service_benefit": "build customer loyalty",
    "pain_point": "lack of customer retention",
}
"""

# ============================================
# 🔧 AUTOMATION SETTINGS
# ============================================

SCRAPING = {
    "results_per_locality": 20,
    "scroll_times": 3,
    "delay_between_businesses": 2,
    "delay_between_localities": 45,
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
    "max_per_day": 50,
    "batch_size": 20,
    "delay_between_sends": 30,
    "your_name": "Mubeen",
    "your_email": "jawedmubeen905@gmail.com",  # ⚠️ UPDATE THIS!
    "signature": "Mubeen",
}

AI = {
    "model": "google/gemini-flash-1.5",  # or "openai/gpt-4o-mini"
    "temperature": 0.9,
    "max_tokens": 2048,
}

SHEETS = {
    "spreadsheet_name": f"{TARGET['niche'].title()} - {TARGET['city']}",
    # If you get "storageQuotaExceeded" error, create spreadsheet manually:
    # 1. Go to sheets.google.com and create new spreadsheet
    # 2. Share it with service account email (from credentials.json)
    # 3. Add URL here:
    "spreadsheet_url": "https://docs.google.com/spreadsheets/d/1IVU4_k2C5s3sZu5u5l0rAdzKrkda5qBd7LA8SX6ryRw/edit?gid=0#gid=0",  # Paste URL here if needed
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
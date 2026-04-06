"""
Main Control Panel - 100% FREE Automation
Works for ANY city, ANY niche!
"""
import asyncio
from pg_database import PostgresDatabase as SheetsDatabase
from scraper import GoogleMapsScraper
from analyzer import WebsiteAnalyzer
from email_finder import EmailFinder
from email_generator import EmailGenerator
from email_sender import GmailSender
from config import TARGET, show_current_config, EMAIL

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def show_stats():
    """Show current statistics"""
    db = SheetsDatabase()
    stats = db.get_stats()
    
    print_header(f"📊 STATISTICS - {TARGET['niche_plural'].upper()} IN {TARGET['city'].upper()}")
    print(f"  Total Businesses: {stats['total_agencies']}")
    print(f"  Qualified: {stats['qualified']}")
    print(f"  High Priority: {stats['high_priority']}")
    print(f"  With Email: {stats['with_email']}")
    print(f"  Emails Sent: {stats['emails_sent']}")
    print(f"  Pending Outreach: {stats['pending_outreach']}")
    print()

def show_menu():
    """Display main menu"""
    print_header(f"🚀 AUTOMATED OUTREACH - {TARGET['niche_plural'].upper()}")
    
    print(f"🎯 Current Target: {TARGET['niche_plural']} in {TARGET['city']}, {TARGET['country']}")
    print(f"💼 Your Service: {TARGET['your_service']}")
    print()
    
    print("STEP 1 - DATA COLLECTION:")
    print("  1. Scrape businesses from Google Maps")
    print("  2. View collected businesses")
    
    print("\nSTEP 2 - QUALIFICATION:")
    print("  3. Analyze & qualify businesses")
    print("  4. View high priority leads")
    
    print("\nSTEP 3 - EMAIL DISCOVERY:")
    print("  5. Find email addresses")
    print("  6. View businesses with emails")
    
    print("\nSTEP 4 - EMAIL GENERATION:")
    print("  7. Generate personalized emails (AI)")
    print("  8. Preview sample email")
    
    print("\nSTEP 5 - OUTREACH:")
    print("  9. Send email batch")
    
    print("\nCONFIGURATION:")
    print("  10. Show current configuration")
    print("  11. Change target (city/niche)")
    print("  12. Show statistics")
    
    print("\nAUTOMATION:")
    print("  13. Run full pipeline")
    
    print("\n  0. Exit")
    print("\n" + "-"*60)

async def run_scraper():
    """Run Google Maps scraper"""
    print_header(f"STEP 1: SCRAPING {TARGET['niche_plural'].upper()}")
    
    scraper = GoogleMapsScraper()
    
    print(f"How many {TARGET['niche_plural']} per locality? (default: 20)")
    max_results = input("Enter number (or press Enter for 20): ").strip()
    max_results = int(max_results) if max_results else 20
    
    await scraper.scrape_all_localities(max_per_locality=max_results)

def run_analyzer():
    """Run website analyzer"""
    print_header(f"STEP 2: ANALYZING {TARGET['niche_plural'].upper()}")
    
    analyzer = WebsiteAnalyzer()
    analyzer.analyze_all_businesses()

def run_email_finder():
    """Run email finder"""
    print_header("STEP 3: FINDING EMAILS")
    
    finder = EmailFinder()
    
    print("Which priority level?")
    print("  1. HIGH priority only (recommended)")
    print("  2. All qualified businesses")
    choice = input("Choose (1 or 2): ").strip()
    
    if choice == "2":
        finder.find_emails_for_businesses(priority='ALL')
    else:
        finder.find_emails_for_businesses(priority='HIGH')

def run_email_generator():
    """Run email generator"""
    print_header("STEP 4: GENERATING EMAILS")
    
    generator = EmailGenerator()
    generator.generate_for_all_high_priority()

def preview_email():
    """Preview a sample email"""
    print_header("EMAIL PREVIEW")
    
    generator = EmailGenerator()
    generator.preview_email()

def send_emails():
    """Send email batch"""
    print_header("STEP 5: SENDING EMAILS")
    
    sender = GmailSender()

    result = sender.test_connection()
    if not result.get('ok'):
        print("\n❌ Gmail connection failed!")
        if result.get('error'):
            print(f"   Error: {result['error']}")
        if not result.get('matched', True):
            print(f"   Authenticated as : {result.get('authenticated_as')}")
            print(f"   Config email     : {result.get('configured_as')}")
            print("   Delete gmail_token.json and re-authenticate with the correct account.")
        return
    
    print(f"\nHow many emails to send? (max: {EMAIL['max_per_day']})")
    batch_size = input(f"Enter number (or press Enter for {EMAIL['batch_size']}): ").strip()
    batch_size = int(batch_size) if batch_size else EMAIL['batch_size']
    
    print(f"\n⚠️  You're about to send {batch_size} emails from {EMAIL['your_email']}")
    confirm = input("Continue? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        sender.send_batch(batch_size=batch_size)
    else:
        print("❌ Cancelled")

def view_businesses():
    """View collected businesses"""
    db = SheetsDatabase()
    businesses = list(db.get_all_businesses())[:10]
    
    print_header(f"RECENT {TARGET['niche_plural'].upper()}")
    
    if not businesses:
        print(f"❌ No {TARGET['niche_plural']} found. Run scraper first!")
        return
    
    for biz in businesses:
        print(f"\n📍 {biz['Name']}")
        print(f"   Location: {biz.get('Locality', 'Unknown')}, {biz.get('City', '')}")
        print(f"   Rating: {biz.get('Rating', 'N/A')}⭐")
        print(f"   Website: {biz.get('Website', 'None')}")
        print(f"   Phone: {biz.get('Phone', 'N/A')}")

def view_high_priority():
    """View high priority leads"""
    db = SheetsDatabase()
    businesses = db.get_high_priority_businesses()[:10]
    
    print_header(f"HIGH PRIORITY {TARGET['niche_plural'].upper()}")
    
    if not businesses:
        print(f"❌ No high priority {TARGET['niche_plural']} found. Run analyzer first!")
        return
    
    for biz in businesses:
        print(f"\n🔥 {biz['Name']}")
        print(f"   Score: {biz.get('Qualification Score', 'N/A')}")
        print(f"   Reasons: {biz.get('Reasons', 'N/A')}")
        print(f"   Email: {biz.get('Email', 'Not found')}")

def view_with_emails():
    """View businesses with emails"""
    db = SheetsDatabase()
    businesses = [b for b in db.get_all_businesses() if b.get('Email')][:10]
    
    print_header(f"{TARGET['niche_plural'].upper()} WITH EMAILS")
    
    if not businesses:
        print(f"❌ No emails found yet. Run email finder first!")
        return
    
    for biz in businesses:
        print(f"\n📧 {biz['Name']}")
        print(f"   Email: {biz.get('Email', 'N/A')}")
        print(f"   Source: {biz.get('Email Source', 'N/A')}")

def change_target():
    """Change target city/niche"""
    print_header("CHANGE TARGET")
    
    print("Quick options:")
    print("  1. Dubai Real Estate")
    print("  2. New York Restaurants")
    print("  3. Custom (enter your own)")
    
    choice = input("\nChoose option: ").strip()
    
    if choice == "1":
        from config import switch_to_real_estate_dubai
        switch_to_real_estate_dubai()
    elif choice == "2":
        from config import switch_to_restaurants_nyc
        switch_to_restaurants_nyc()
    elif choice == "3":
        print("\n📝 Custom Configuration:")
        city = input("City: ").strip()
        country = input("Country: ").strip()
        localities_input = input("Localities (comma-separated): ").strip()
        localities = [l.strip() for l in localities_input.split(',')]
        niche = input("Business type (singular, e.g. 'restaurant'): ").strip()
        niche_plural = input("Business type (plural, e.g. 'restaurants'): ").strip()
        industry = input("Industry (e.g. 'food & beverage'): ").strip()
        service = input("Your service (e.g. 'websites'): ").strip()
        benefit = input("Main benefit (e.g. 'get more leads'): ").strip()
        pain = input("Their pain point (e.g. 'no online presence'): ").strip()
        
        from config import switch_to_custom
        switch_to_custom(city, country, localities, niche, niche_plural, industry, service, benefit, pain)
    
    print("\n✅ Configuration updated!")
    print("💡 This will affect all future scraping, analysis, and emails")

async def run_full_pipeline():
    """Run complete automation"""
    print_header(f"🤖 FULL AUTOMATION - {TARGET['niche_plural'].upper()}")
    
    print(f"""
This will run all steps for {TARGET['niche_plural']} in {TARGET['city']}:
1. Scrape businesses (20 per locality)
2. Analyze & qualify
3. Find emails (high priority)
4. Generate personalized emails
5. Review (don't send automatically)

This may take 1-2 hours.
""")
    
    confirm = input("Start full pipeline? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("❌ Cancelled")
        return
    
    try:
        # Step 1
        print("\n🔄 STEP 1/5: Scraping...")
        scraper = GoogleMapsScraper()
        await scraper.scrape_all_localities(max_per_locality=20)
        
        # Step 2
        print("\n🔄 STEP 2/5: Analyzing...")
        analyzer = WebsiteAnalyzer()
        analyzer.analyze_all_businesses()
        
        # Step 3
        print("\n🔄 STEP 3/5: Finding emails...")
        finder = EmailFinder()
        finder.find_emails_for_businesses(priority='HIGH')
        
        # Step 4
        print("\n🔄 STEP 4/5: Generating emails...")
        generator = EmailGenerator()
        generator.generate_for_all_high_priority()
        
        # Step 5
        print("\n🔄 STEP 5/5: Complete!")
        print("\n✅ Pipeline finished!")
        print("\nYou can now:")
        print("  - Preview emails (option 8)")
        print("  - Send batch (option 9)")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted")
    except Exception as e:
        print(f"\n\n❌ Pipeline error: {e}")

async def main():
    """Main control loop"""
    
    while True:
        show_menu()
        choice = input("Choose option: ").strip()
        
        try:
            if choice == '0':
                print("\n👋 Goodbye!")
                break
            
            elif choice == '1':
                await run_scraper()
            
            elif choice == '2':
                view_businesses()
            
            elif choice == '3':
                run_analyzer()
            
            elif choice == '4':
                view_high_priority()
            
            elif choice == '5':
                run_email_finder()
            
            elif choice == '6':
                view_with_emails()
            
            elif choice == '7':
                run_email_generator()
            
            elif choice == '8':
                preview_email()
            
            elif choice == '9':
                send_emails()
            
            elif choice == '10':
                show_current_config()
            
            elif choice == '11':
                change_target()
            
            elif choice == '12':
                show_stats()
            
            elif choice == '13':
                await run_full_pipeline()
            
            else:
                print("❌ Invalid choice")
            
            input("\n\nPress Enter to continue...")
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted")
            input("Press Enter to continue...")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   🚀  100% FREE BUSINESS OUTREACH AUTOMATION             ║
    ║                                                           ║
    ║   Works for ANY city, ANY niche!                         ║
    ║   Powered by: Gemini AI + Gmail + Google Sheets          ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    asyncio.run(main())
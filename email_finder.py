"""
Email Finder - 100% FREE Methods
1. Scrape contact pages
2. Common patterns (info@, contact@)
3. Hunter.io free tier (25/month)
"""
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import time
from sheets_database import SheetsDatabase
from config import TARGET
import os

class EmailFinder:
    def __init__(self):
        self.db = SheetsDatabase()
        self.niche = TARGET['niche']
        # Hunter.io free tier (optional - set in .env if you have it)
        self.hunter_key = os.getenv('HUNTER_API_KEY', '')
    
    def extract_domain(self, url):
        """Extract clean domain from URL"""
        if not url:
            return None
        try:
            if not url.startswith('http'):
                url = 'https://' + url
            parsed = urlparse(url)
            return parsed.netloc.replace('www.', '')
        except:
            return None
    
    def scrape_emails_from_website(self, url):
        """Scrape emails from website (FREE method)"""
        if not url:
            return []
        
        print(f"  🔍 Scraping: {url}")
        
        emails = []
        pages_to_check = [
            url,
            urljoin(url, '/contact'),
            urljoin(url, '/contact-us'),
            urljoin(url, '/about'),
            urljoin(url, '/about-us'),
        ]
        
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        
        for page_url in pages_to_check:
            try:
                response = requests.get(
                    page_url,
                    headers={'User-Agent': 'Mozilla/5.0'},
                    timeout=10
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    text = soup.get_text()
                    
                    # Find all emails
                    found_emails = re.findall(email_pattern, text)
                    
                    for email in found_emails:
                        email = email.lower()
                        # Skip common fake emails
                        if not any(skip in email for skip in ['example.com', 'domain.com', 'email.com', 'test.com', '@placeholder']):
                            if email not in emails:
                                emails.append(email)
                
                time.sleep(0.5)  # Be respectful
                
            except:
                continue
        
        return emails
    
    def generate_common_emails(self, domain, business_name):
        """Generate common email patterns (FREE method)"""
        if not domain:
            return []
        
        common_patterns = [
            f'info@{domain}',
            f'contact@{domain}',
            f'hello@{domain}',
            f'admin@{domain}',
            f'sales@{domain}',
        ]
        
        # Add business name based patterns
        if business_name:
            clean_name = business_name.lower().replace(' ', '').replace('-', '')[:15]
            common_patterns.append(f'{clean_name}@{domain}')
        
        return common_patterns
    
    def try_hunter_free(self, domain):
        """Try Hunter.io free tier if API key available"""
        if not self.hunter_key or not domain:
            return None
        
        try:
            url = 'https://api.hunter.io/v2/domain-search'
            params = {
                'domain': domain,
                'api_key': self.hunter_key,
                'limit': 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                emails = data.get('data', {}).get('emails', [])
                if emails:
                    return emails[0].get('value')
            
            return None
        except:
            return None
    
    def find_best_email(self, url, business_name):
        """Find the best email using all FREE methods"""
        domain = self.extract_domain(url)
        
        # Method 1: Scrape website
        scraped_emails = self.scrape_emails_from_website(url)
        
        if scraped_emails:
            # Prioritize info@, contact@, etc.
            priority_prefixes = ['info', 'contact', 'hello', 'sales']
            for email in scraped_emails:
                prefix = email.split('@')[0]
                if any(p in prefix for p in priority_prefixes):
                    print(f"    ✅ Found (scraped): {email}")
                    return {
                        'email': email,
                        'source': 'website_scrape',
                        'confidence': 'high'
                    }
            
            # Return first found email
            print(f"    ✅ Found (scraped): {scraped_emails[0]}")
            return {
                'email': scraped_emails[0],
                'source': 'website_scrape',
                'confidence': 'medium'
            }
        
        # Method 2: Try Hunter.io free (if available)
        if self.hunter_key:
            hunter_email = self.try_hunter_free(domain)
            if hunter_email:
                print(f"    ✅ Found (Hunter): {hunter_email}")
                return {
                    'email': hunter_email,
                    'source': 'hunter_free',
                    'confidence': 'high'
                }
        
        # Method 3: Generate common patterns (verify later)
        common_emails = self.generate_common_emails(domain, business_name)
        if common_emails:
            email = common_emails[0]  # Start with info@
            print(f"    💡 Suggested: {email} (verify manually)")
            return {
                'email': email,
                'source': 'common_pattern',
                'confidence': 'low'
            }
        
        print("    ⚠️ No email found")
        return None
    
    def find_emails_for_businesses(self, priority='HIGH'):
        """Find emails for all qualified businesses"""
        print(f"\n🚀 Finding emails for {priority} priority {self.niche}s...\n")
        
        
        if priority == 'HIGH':
            all_businesses = self.db.get_all_businesses()
            businesses = [b for b in all_businesses if b.get('Priority') == 'HIGH']
        else:
            businesses = self.db.get_all_businesses()

        businesses = [b for b in businesses if not b.get('Email') and b.get('Website')]
        
        total = len(businesses)
        
        if total == 0:
            print(f"❌ No {self.niche}s need email finding")
            return
        
        print(f"📋 Found {total} {self.niche}s with websites\n")
        
        found = not_found = 0
        
        for idx, business in enumerate(businesses, 1):
            print(f"[{idx}/{total}] {business['Name']}")
            
            try:
                email_data = self.find_best_email(business['Website'], business['Name'])
                
                if email_data:
                    self.db.update_email(
                        business['ID'],
                        email_data['email'],
                        f"{email_data['source']} ({email_data['confidence']})"
                    )
                    found += 1
                else:
                    not_found += 1
                
                time.sleep(1)
                
            except Exception as e:
                print(f"    ❌ Error: {e}")
                not_found += 1
                continue
        
        print(f"\n{'='*60}")
        print(f"🎉 Email discovery complete!")
        print(f"\n📊 Results:")
        print(f"  ✅ Found: {found}")
        print(f"  ❌ Not found: {not_found}")
        print(f"  📈 Success rate: {(found/total*100):.1f}%")
        
        if not_found > 0:
            print(f"\n💡 TIP: For businesses without emails:")
            print(f"   1. Call them directly (phone in sheet)")
            print(f"   2. Try LinkedIn")
            print(f"   3. Check their social media")

if __name__ == "__main__":
    finder = EmailFinder()
    finder.find_emails_for_businesses(priority='HIGH')
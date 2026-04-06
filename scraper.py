"""
Google Maps Scraper - 100% FREE
Works for ANY city and ANY niche
"""
import asyncio
from playwright.async_api import async_playwright
import time
import random
from pg_database import PostgresDatabase as SheetsDatabase
from config import TARGET, SCRAPING, get_search_query

class GoogleMapsScraper:
    def __init__(self):
        self.db = SheetsDatabase()
        self.city = TARGET['city']
        self.country = TARGET['country']
        self.niche = TARGET['niche']
        self.localities = TARGET['localities']
    
    async def scrape_locality(self, locality, max_results=None):
        """Scrape businesses from a specific locality"""
        if max_results is None:
            max_results = SCRAPING['results_per_locality']
        
        print(f"\n🔍 Searching: {self.niche} in {locality}, {self.city}")
        
        search_query = get_search_query(locality)
        print(f"   Query: '{search_query}'")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=not SCRAPING['visible_browser'])
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            try:
                print("   Opening Google Maps...")
                await page.goto('https://www.google.com/maps', timeout=30000)
                await asyncio.sleep(3)
                
                # Search
                # Search - try multiple selectors
                print("   Entering search query...")
                search_box = None
                selectors_to_try = [
                    'input#searchboxinput',
                    'input[aria-label="Search Google Maps"]',
                    'input[name="q"]',
                    'input.searchboxinput'
                ]

                for selector in selectors_to_try:
                    try:
                        search_box = await page.wait_for_selector(selector, timeout=3000)
                        if search_box:
                            print(f"   Found search box: {selector}")
                            break
                    except:
                        continue

                if not search_box:
                    print("   ❌ Could not find search box")
                    await browser.close()
                    return 0

                await search_box.click()
                await asyncio.sleep(1)
                await search_box.fill('')  # Clear first
                await asyncio.sleep(0.5)
                await search_box.type(search_query, delay=100)  # Type slower
                await asyncio.sleep(2)
                await page.keyboard.press('Enter')
                
                # Wait for results - try multiple approaches
                print("   Waiting for results...")
                try:
                    # Wait for the results container
                    await page.wait_for_selector('div.m6QErb[aria-label]', timeout=15000)
                    print("   ✅ Results loaded!")
                except:
                    # Alternative: wait for any result link
                    try:
                        await page.wait_for_selector('a[href*="/maps/place/"]', timeout=10000)
                        print("   ✅ Results found!")
                    except:
                        print("   ❌ No results appeared - try different search terms")
                        await browser.close()
                        return 0
                
                await asyncio.sleep(3)
                
                # Scroll to load more results
                print("   Loading more results...")
                for i in range(SCRAPING['scroll_times']):
                    try:
                        await page.evaluate('''
                            const scrollable = document.querySelector('div.m6QErb[aria-label]')
                                           || document.querySelector('div[role="feed"]');
                            if (scrollable) scrollable.scrollBy(0, 1500);
                        ''')
                        await asyncio.sleep(3)
                    except:
                        pass
                
                # Get all result links — try multiple selectors (Google Maps changes class names)
                result_links = await page.query_selector_all('a.hfpxzc')
                if not result_links:
                    result_links = await page.query_selector_all('div[role="feed"] a[href*="/maps/place/"]')
                if not result_links:
                    result_links = await page.query_selector_all('a[href*="/maps/place/"]')

                if not result_links:
                    print("   ⚠️ No business links found")
                    await browser.close()
                    return 0
                
                print(f"   Found {len(result_links)} results, processing {min(max_results, len(result_links))}...")
                
                found_count = 0
                
                for idx, link in enumerate(result_links[:max_results]):
                    try:
                        print(f"  [{idx + 1}/{min(max_results, len(result_links))}] ", end="")
                        
                        await link.click()
                        await asyncio.sleep(4)  # Wait for details to load
                        
                        business_data = await self._extract_data(page, locality)
                        
                        if business_data:
                            self.db.save_business(business_data)
                            found_count += 1
                        else:
                            print("⚠️ No data")
                        
                        await asyncio.sleep(random.uniform(
                            SCRAPING['delay_between_businesses'] - 0.5,
                            SCRAPING['delay_between_businesses'] + 0.5
                        ))
                        
                    except Exception as e:
                        print(f"⚠️ Error: {str(e)[:50]}")
                        continue
                
                print(f"\n✅ Found {found_count} {self.niche}s in {locality}")
                return found_count
                
            except Exception as e:
                print(f"\n❌ Error: {e}")
                return 0
            finally:
                await browser.close()
    
    async def _extract_data(self, page, locality):
        """Extract business data from Google Maps"""
        try:
            data = {
                'locality': locality,
                'city': self.city,
                'country': self.country,
                'niche': self.niche,
                'source': 'google_maps'
            }
            
            # Wait for content to load
            await asyncio.sleep(2)
            
            # Name - try multiple selectors
            try:
                name_elem = await page.wait_for_selector('h1.DUwDvf', timeout=5000)
                if name_elem:
                    data['name'] = await name_elem.inner_text()
                else:
                    # Try alternative selector
                    name_elem = await page.query_selector('h1')
                    if name_elem:
                        data['name'] = await name_elem.inner_text()
                    else:
                        print("⚠️ No name found")
                        return None
            except:
                print("⚠️ No name element")
                return None
            
            # Rating
            try:
                rating_elem = await page.query_selector('div.F7nice span[aria-hidden="true"]')
                if rating_elem:
                    data['rating'] = await rating_elem.inner_text()
                else:
                    data['rating'] = None
            except:
                data['rating'] = None
            
            # Reviews count
            try:
                reviews_elem = await page.query_selector('div.F7nice span[aria-label*="reviews"]')
                if reviews_elem:
                    reviews_text = await reviews_elem.get_attribute('aria-label')
                    if reviews_text:
                        reviews_num = ''.join(filter(str.isdigit, reviews_text.split()[0].replace(',', '')))
                        data['reviews_count'] = int(reviews_num) if reviews_num else 0
                    else:
                        data['reviews_count'] = 0
                else:
                    data['reviews_count'] = 0
            except:
                data['reviews_count'] = 0
            
            # Address
            try:
                address_elem = await page.query_selector('button[data-item-id="address"]')
                if address_elem:
                    addr_text = await address_elem.inner_text()
                    data['address'] = addr_text.replace('Address: ', '').strip()
                else:
                    data['address'] = None
            except:
                data['address'] = None
            
            # Phone
            try:
                phone_elem = await page.query_selector('button[data-item-id^="phone"]')
                if phone_elem:
                    phone_text = await phone_elem.inner_text()
                    data['phone'] = phone_text.replace('Phone: ', '').strip()
                else:
                    data['phone'] = None
            except:
                data['phone'] = None
            
            # Website
            try:
                website_elem = await page.query_selector('a[data-item-id="authority"]')
                if website_elem:
                    href = await website_elem.get_attribute('href') or ''
                    # Google Maps wraps URLs in a redirect: /url?q=https://...&...
                    if '/url?q=' in href or href.startswith('/url?'):
                        from urllib.parse import urlparse, parse_qs
                        qs = parse_qs(urlparse(href).query)
                        href = qs.get('q', [href])[0]
                    # Strip trailing tracking params that survived
                    if href and '&' in href:
                        href = href.split('&')[0]
                    data['website'] = href.rstrip('/') if href else None
                else:
                    data['website'] = None
            except:
                data['website'] = None
            
            return data
            
        except Exception as e:
            print(f"⚠️ Error extracting: {str(e)[:50]}")
            return None
    
    async def scrape_all_localities(self, max_per_locality=None):
        """Scrape all configured localities"""
        import pg_database as _pgdb
        print(f"\n🚀 Starting {self.niche} scraping in {self.city}")
        print(f"📋 Will scrape {len(self.localities)} localities\n")

        total_found = 0

        for idx, locality in enumerate(self.localities, 1):
            print(f"\n{'='*60}")
            print(f"Locality {idx}/{len(self.localities)}")
            found = await self.scrape_locality(locality, max_per_locality)
            total_found += found

            if found == 0:
                print(f"   ⚡ No businesses found in {locality} — skipping delay")
                _pgdb._pipeline_notice = f"No businesses found in \"{locality}\" — check the area name or try a different search term."

            if idx < len(self.localities) and found > 0:
                wait_time = random.uniform(
                    SCRAPING['delay_between_localities'] - 10,
                    SCRAPING['delay_between_localities'] + 10
                )
                print(f"\n⏳ Waiting {wait_time:.0f}s before next locality...")
                # Sleep in 1-second chunks so Stop button is responsive
                elapsed = 0
                while elapsed < wait_time:
                    if getattr(_pgdb, '_stop_requested', False):
                        print("   🛑 Stop requested — halting scrape")
                        return total_found
                    await asyncio.sleep(1)
                    elapsed += 1

        print(f"\n{'='*60}")
        print(f"🎉 Scraping complete!")
        print(f"📊 Total {self.niche}s found: {total_found}")

async def main():
    scraper = GoogleMapsScraper()
    await scraper.scrape_all_localities()

if __name__ == "__main__":
    asyncio.run(main())
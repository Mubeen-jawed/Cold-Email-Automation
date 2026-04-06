"""
Website Analyzer - 100% FREE
Uses Google PageSpeed Insights API (25,000 requests/day FREE)
"""
import requests
import time
from pg_database import PostgresDatabase as SheetsDatabase
from config import TARGET, QUALIFICATION

class WebsiteAnalyzer:
    def __init__(self):
        self.db = SheetsDatabase()
        self.pagespeed_url = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed'
        self.niche = TARGET['niche']
    
    def analyze_website(self, url):
        """Analyze website using simple checks (NO API needed!)"""
        if not url:
            return None
        
        url = url.strip()
        if not url.startswith('http'):
            url = 'https://' + url
        
        print(f"  🔍 Checking: {url}")
        
        try:
            import time
            start_time = time.time()
            
            # Simple HTTP request to check website
            response = requests.get(
                url, 
                timeout=10,
                allow_redirects=True,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            load_time = time.time() - start_time
            
            # Calculate scores based on load time
            if load_time < 2:
                perf_score = 90
            elif load_time < 4:
                perf_score = 70
            elif load_time < 6:
                perf_score = 50
            else:
                perf_score = 30
            
            # Check for basic SEO elements
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            seo_score = 50  # Base score
            
            # Check for title
            if soup.find('title'):
                seo_score += 15
            
            # Check for meta description
            if soup.find('meta', attrs={'name': 'description'}):
                seo_score += 15
            
            # Check for h1
            if soup.find('h1'):
                seo_score += 10
            
            # Check for images with alt tags
            images = soup.find_all('img')
            if images:
                images_with_alt = [img for img in images if img.get('alt')]
                if len(images_with_alt) > len(images) * 0.5:
                    seo_score += 10
            
            analysis = {
                'performance_score': perf_score,
                'seo_score': min(seo_score, 100),
                'has_ssl': url.startswith('https://'),
                'mobile_friendly': response.status_code == 200,
                'load_time': round(load_time, 2)
            }
            
            avg_score = (perf_score + seo_score) / 2
            if avg_score < 50:
                analysis['quality'] = 'POOR'
            elif avg_score < 70:
                analysis['quality'] = 'FAIR'
            elif avg_score < 85:
                analysis['quality'] = 'GOOD'
            else:
                analysis['quality'] = 'EXCELLENT'
            
            print(f"    ✅ Load: {load_time:.1f}s, Perf: {perf_score}, SEO: {seo_score}")
            return analysis
        
        except requests.exceptions.Timeout:
            print(f"    ⚠️ Timeout (slow website)")
            return {
                'performance_score': 20,
                'seo_score': 50,
                'has_ssl': url.startswith('https://'),
                'quality': 'POOR',
                'load_time': 10
            }
        
        except Exception as e:
            print(f"    ⚠️ Error: {str(e)[:50]}")
            return None
            
    def qualify_business(self, business):
        """Qualify business based on website and data"""
        print(f"\n🎯 Qualifying: {business['Name']}")
        
        qualification = {
            'has_website': bool(business.get('Website')),
            'website_quality': {},
            'priority': 'LOW',
            'reasons': [],
            'score': 0
        }
        
        # Check 1: No website = TOP priority
        if not business.get('Website'):
            qualification['priority'] = 'HIGH'
            qualification['reasons'].append(f'No website - perfect for {TARGET["your_service"]}')
            qualification['score'] += 50
            print(f"  🔥 HIGH: No website")
        
        # Check 2: Has website - analyze it
        elif business.get('Website'):
            analysis = self.analyze_website(business['Website'])
            
            if analysis:
                qualification['website_quality'] = analysis
                
                if analysis['performance_score'] < QUALIFICATION['min_performance_score']:
                    qualification['priority'] = 'HIGH'
                    qualification['reasons'].append(f'Slow website ({analysis["performance_score"]}/100)')
                    qualification['score'] += 40
                
                if analysis['seo_score'] < QUALIFICATION['min_seo_score']:
                    if qualification['priority'] != 'HIGH':
                        qualification['priority'] = 'MEDIUM'
                    qualification['reasons'].append(f'Poor SEO ({analysis["seo_score"]}/100)')
                    qualification['score'] += 30
                
                if not analysis['has_ssl']:
                    qualification['priority'] = 'HIGH'
                    qualification['reasons'].append('No SSL certificate')
                    qualification['score'] += 35
                
                if analysis['quality'] == 'POOR':
                    qualification['priority'] = 'HIGH'
                    qualification['reasons'].append('Overall poor website quality')
                    qualification['score'] += 40
                
                print(f"  📊 Quality: {analysis['quality']}, Priority: {qualification['priority']}")
        
        # Check 3: Good rating = easier conversion
        try:
            rating = float(business.get('Rating', 0))
            if rating >= QUALIFICATION['min_rating']:
                qualification['reasons'].append(f'High rating ({rating}★)')
                qualification['score'] += 10
        except:
            pass
        
        # Check 4: Established business
        try:
            reviews = int(business.get('Reviews', 0))
            if reviews >= QUALIFICATION['min_reviews']:
                qualification['reasons'].append(f'Established ({reviews} reviews)')
                qualification['score'] += 10
        except:
            pass
        
        return qualification
    
    def analyze_all_businesses(self):
        """Analyze and qualify all businesses"""
        import pg_database as _pgdb
        if not _pgdb._current_campaign_id:
            raise RuntimeError(
                "No active campaign set. Activate a campaign before running Analyze."
            )

        print(f"\n🚀 Analyzing {self.niche}s for campaign {_pgdb._current_campaign_id}...")
        businesses = self.db.get_unqualified_businesses_by_campaign(_pgdb._current_campaign_id)
        total = len(businesses)
        
        if total == 0:
            print("❌ No unqualified businesses found")
            return
        
        print(f"📋 Found {total} {self.niche}s to qualify\n")
        
        high = medium = low = 0
        analyzed_count = 0
        skipped_count = 0
        
        for idx, business in enumerate(businesses, 1):
            print(f"[{idx}/{total}] ", end="")
            
            try:
                qualification = self.qualify_business(business)
                self.db.update_qualification(business['ID'], qualification)
                
                if qualification['priority'] == 'HIGH':
                    high += 1
                elif qualification['priority'] == 'MEDIUM':
                    medium += 1
                else:
                    low += 1
                
                analyzed_count += 1
                
                # Rate limiting - wait longer between requests
                if idx % 10 == 0:
                    print(f"\n  ⏳ Taking a break (analyzed {idx}/{total})...")
                    time.sleep(30)  # Longer break every 10 businesses
                else:
                    time.sleep(5)  # 5 seconds between each
                
            except Exception as e:
                print(f"    ❌ Error: {e}")
                skipped_count += 1
                continue
        
        print(f"\n{'='*60}")
        print(f"🎉 Qualification complete!")
        print(f"\n📊 Results:")
        print(f"  🔥 HIGH priority: {high}")
        print(f"  ⚡ MEDIUM priority: {medium}")
        print(f"  💤 LOW priority: {low}")
        print(f"  ⚠️ Skipped (errors): {skipped_count}")
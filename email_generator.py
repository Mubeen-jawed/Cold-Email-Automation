"""
Email Generator - 100% FREE
Uses Google Gemini API (1,500 requests/day FREE!)
Fully dynamic - adapts to any niche/city from config
"""
import requests
import os
import json
from sheets_database import SheetsDatabase
from config import TARGET, EMAIL, AI, get_email_context
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class EmailGenerator:
    def __init__(self):
        self.db = SheetsDatabase()
        
        # Load environment variables
        load_dotenv()
        
        # Setup OpenRouter
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in .env file!")
        
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "arcee-ai/trinity-large-preview:free"  # or "openai/gpt-4o-mini"
        
        # Get dynamic context from config
        self.context = get_email_context()

    def generate_email(self, business):
        """Generate personalized email using OpenRouter"""
        
        # Build business-specific context
        business_context = self._build_business_context(business)
        
        # Create dynamic prompt
        prompt = self._create_dynamic_prompt(business_context)
        
        print(f"  🤖 Generating email for: {business['Name']}")
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/yourusername/automation",  # Optional
                "X-Title": "Business Outreach Automation"  # Optional
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": AI['temperature'],
                "max_tokens": AI['max_tokens']
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"    ❌ API Error: {response.status_code}")
                print(f"    Response: {response.text}")
                return None
            
            data = response.json()
            content = data['choices'][0]['message']['content'].strip()
            
            # Clean up markdown if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            try:
                email_data = json.loads(content)
                print(f"    ✅ Email generated!")
                return email_data
            except json.JSONDecodeError:
                # Fallback: extract manually
                import re
                subject_match = re.search(r'"subject"\s*:\s*"([^"]+)"', content)
                body_match = re.search(r'"body"\s*:\s*"(.*)"', content, re.DOTALL)
                
                if subject_match and body_match:
                    body_text = body_match.group(1).rstrip('",\n\r }')
                    email_data = {
                        "subject": subject_match.group(1).strip(),
                        "body": body_text.strip()
                    }
                    print(f"    ✅ Email generated!")
                    return email_data
                else:
                    print(f"    ❌ Could not parse response")
                    return None
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
            return None
        
    def _build_business_context(self, business):
        """Build context about specific business"""
        context_parts = []
        
        context_parts.append(f"Business Name: {business['Name']}")
        context_parts.append(f"Type: {self.context['niche']}")
        context_parts.append(f"Location: {business.get('Locality', 'Unknown')}, {self.context['city']}")
        
        if business.get('Rating'):
            context_parts.append(f"Rating: {business['Rating']} stars")
        
        if business.get('Reviews'):
            context_parts.append(f"Reviews: {business['Reviews']}")
        
        # Website status
        if not business.get('Website'):
            context_parts.append("Website: NO WEBSITE")
            context_parts.append(f"Key Issue: Missing online presence")
        else:
            context_parts.append(f"Website: {business['Website']}")
            
            # Website quality info
            perf = business.get('Performance Score')
            seo = business.get('SEO Score')
            
            if perf:
                context_parts.append(f"Performance: {perf}/100")
            if seo:
                context_parts.append(f"SEO: {seo}/100")
            
            if business.get('Quality'):
                context_parts.append(f"Quality: {business['Quality']}")
        
        # Qualification reasons
        reasons = business.get('Reasons', '')
        if reasons:
            context_parts.append(f"Issues Found: {reasons}")
        
        return "\n".join(context_parts)
    

    def _create_dynamic_prompt(self, business_context):
        """Create dynamic prompt that adapts based on website status"""
        
        # Determine the specific pitch based on website status
        has_website = "Website: NO WEBSITE" in business_context or "has_website: False" in business_context.lower()
        
        if has_website or "NO WEBSITE" in business_context:
            # No website - pitch website development
            pitch_focus = f"""
    SPECIFIC PITCH (NO WEBSITE SCENARIO):
    - They don't have a website at all
    - Emphasize: "I noticed you don't have a website" or "couldn't find your website online"
    - Pain point: Missing out on online leads, people can't find them, competitors are online
    - Solution: Build them a professional conversion focused website from scratch
    - Benefit: Get online presence, capture leads 24/7, look professional, increase revenue
    - Example: "Most clients search online first - without a website, you're invisible to them"
    """
        else:
            # Has website but poor quality - pitch optimization/redesign
            pitch_focus = f"""
    SPECIFIC PITCH (POOR WEBSITE SCENARIO):
    - They have a website but it's poorly optimized
    - Emphasize specific issues you found: slow loading, poor mobile experience, bad SEO
    - Pain point: Website exists but not generating leads, losing visitors due to poor UX
    - Solution: Redesign/optimize for high conversion and better SEO
    - Benefit: Turn visitors into actual leads, rank higher in Google, better user experience
    - Example: "Your site loads in 8 seconds - most people leave after 3. That's costing you leads"
    """
        
        return f"""You are writing a cold outreach email to a {self.context['niche']} in {self.context['city']}.

    BUSINESS INFO:
    {business_context}

    {pitch_focus}

    YOUR OFFERING:
    - You provide: {self.context['service']}
    - Main benefit: {self.context['benefit']}

    EMAIL STRUCTURE (Follow this EXACTLY):
    Line 1: Can I make you more money?
    Line 2: Greeting (use "Hi [BusinessName] team," or "Hey [BusinessName],")
    Line 3: Blank
    Line 4: Opening - mention specific observation about their online presence
    Line 5-6: Point out the specific problem (website missing OR website issues) - be specific
    Line 7: Blank
    Line 8: Brief mention of what you do and the benefit
    Line 9: Blank  
    Line 10: Simple question to engage them
    Line 11: Blank
    Line 12: My Linkedin: www.linkedin.com/in/mubeejaweddev"
    Line 13: Blank
    Line 14: Sign off as just "Best - {self.context['sender_name']}"
    CRITICAL RULES:
    1. NO em dashes (—) or en dashes (–) ANYWHERE
    2. Dont use hyphens
    3. Be SPECIFIC about what you noticed (slow site, no mobile version, missing website, etc.)
    4. Keep it under 120 words total
    5. Write in first person as {self.context['sender_name']}
    6. Sound like you genuinely checked out their business
    7. NO marketing jargon ("leverage", "synergy", "cutting-edge", "optimize", "streamline")
    8. NO multiple exclamation marks
    9. Use contractions (you're, I'm, it's)
    10. End with ONE simple question

    TONE:
    - Helpful, not salesy
    - Observational, not judgmental
    - Casual but professional
    - Like you're genuinely trying to help

    FORBIDDEN WORDS/PHRASES:
    - Leverage, synergy, cutting-edge, state-of-the-art, solutions
    - Optimize, streamline, revolutionize, transform
    - Game-changer, next-level, world-class
    - Em dashes (—), en dashes (–)

    EXAMPLES OF GOOD OPENINGS:

    For NO WEBSITE:
    "I was looking for real estate agencies in [area] and noticed you don't seem to have a website..."
    "Couldn't find your website when I searched - just your Google listing..."

    For POOR WEBSITE:
    "Your site took about 8 seconds to load on my phone..."
    "Noticed your website doesn't work well on mobile..."
    "Your site's performance score is pretty low (42/100)..."

    Return ONLY a valid JSON object on a SINGLE LINE:
    {{"subject": "casual subject line 5-7 words no dashes", "body": "email body with \\n for line breaks"}}

    CRITICAL: Put the ENTIRE JSON on ONE line. Use \\n for line breaks in the email body."""

    
    def generate_for_all_high_priority(self):
        """Generate emails for all high priority leads"""
        print(f"\n🚀 Generating emails for HIGH priority {self.context['niche_plural']}...\n")
        
        all_businesses = self.db.get_all_businesses()
        businesses = [b for b in all_businesses if b.get('Priority') == 'HIGH']
        
        total = len(businesses)
        
        if total == 0:
            print(f"❌ No {self.context['niche_plural']} ready for email generation")
            print("💡 Make sure you've:")
            print("   1. Scraped businesses")
            print("   2. Analyzed & qualified them")
            print("   3. Found email addresses")
            return
        
        print(f"📋 Generating {total} emails\n")
        
        success = failed = 0
        
        for idx, business in enumerate(businesses, 1):
            print(f"[{idx}/{total}] ", end="")
            
            try:
                email_content = self.generate_email(business)
                
                if email_content:
                    # Add recipient info
                    email_content['to'] = business['Email']
                    email_content['business_name'] = business['Name']
                    
                    # Save to sheets
                    self.db.save_generated_email(
                        business['ID'],
                        business['Name'],
                        email_content
                    )
                    success += 1
                else:
                    failed += 1
                    
            except Exception as e:
                print(f"    ❌ Error: {e}")
                failed += 1
        
        print(f"\n{'='*60}")
        print(f"🎉 Email generation complete!")
        print(f"\n📊 Results:")
        print(f"  ✅ Generated: {success}")
        print(f"  ❌ Failed: {failed}")
        print(f"  📈 Success rate: {(success/total*100) if total > 0 else 0:.1f}%")
    
    def preview_email(self):
        """Preview a sample email"""
        print("\n🎲 Generating preview email...\n")
        
        all_businesses = self.db.get_all_businesses()
        businesses = [b for b in all_businesses if b.get('Priority') == 'HIGH']        

        if not businesses:
            print(f"❌ No {self.context['niche_plural']} available for preview")
            return
        
        business = businesses[0]
        email = self.generate_email(business)
        
        if email:
            print(f"\n{'='*60}")
            print("📧 EMAIL PREVIEW")
            print("="*60)
            print(f"\nTo: {business.get('Email', 'example@business.com')}")
            print(f"Business: {business['Name']}")
            print(f"Subject: {email['subject']}\n")
            print(email['body'])
            print(f"\n{'='*60}\n")

if __name__ == "__main__":
    generator = EmailGenerator()
    
    print("Preview one email first...\n")
    generator.preview_email()
    
    input("\nPress Enter to generate all emails (or Ctrl+C to cancel)...")
    generator.generate_for_all_high_priority()
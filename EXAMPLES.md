# Example Outputs

What the automation actually produces.

---

## Example Lead: Home Services in Miami

### Scraped from Google Maps

```
Name:     Miami Pro Plumbing
Location: Coral Gables, Miami, USA
Rating:   4.6 stars
Reviews:  187 reviews
Website:  https://miamiroplumbing.com
Phone:    (305) 555-0142
```

### After Website Analysis

```
Priority:    HIGH
Score:       78

Website Issues:
- Performance:  44/100  (slow load time)
- SEO:          51/100  (poor search ranking)
- SSL:          Yes
- Mobile:       No
```

### Generated AI Email (casual_professional tone)

```
To:      info@miamiroplumbing.com
Subject: noticed something about your miami listings

Hey Miami Pro Plumbing,

I was looking at plumbers in Coral Gables and came across your site —
solid reviews (4.6★ from 187 people), you're clearly doing good work.

One thing I noticed: your website loads pretty slow on mobile and
doesn't rank well in Google. For a local plumber, that usually means
missing out on people searching "plumber near me" — which is basically
most of your potential customers.

I help home service businesses fix this. Working with a few other
companies in the Boca Raton area right now.

Worth a quick chat?

Mubeen
```

---

## Example Lead: No Website

### Scraped Data

```
Name:     Sunrise HVAC Services
Location: Doral, Miami, USA
Rating:   4.8 stars
Reviews:  312 reviews
Website:  None
```

### After Analysis

```
Priority: HIGH
Score:    95
Reasons:
- No website (perfect opportunity)
- Established business (4.8★, 312 reviews)
```

### Generated Email

```
Subject: quick question for sunrise hvac

Hey Sunrise HVAC,

Found you on Google Maps while looking at HVAC companies in Doral —
312 reviews and 4.8 stars is genuinely impressive.

I noticed you don't have a website though. A lot of people search
online before calling, so you're probably losing some of those leads
to competitors who show up in search.

I build websites for home service businesses that are set up to
actually convert visitors into calls. Simple, fast, no fluff.

Would you be open to seeing what it could look like for Sunrise?

Mubeen
```

---

## Email Tone Variations

The AI can be tuned via the **Email Creative** settings in the dashboard.

### Casual

```
Hey ABC Plumbing,

Quick thing — your website's super slow on mobile. That's probably
costing you calls tbh.

I fix this for home service companies. Usually takes about a week.

Want me to show you what I mean?

Mubeen
```

### Professional

```
Hello ABC Plumbing,

I came across your business while researching home service companies
in Coral Gables. Your customer reviews (4.6 stars) reflect the
quality of your work.

However, I noticed your website's performance score (44/100) may be
limiting your online lead generation, particularly on mobile devices.

I specialize in conversion-optimized websites for home service
businesses. Would you be open to a brief conversation about how this
could impact your lead volume?

Mubeen
```

### Problem-Focused

```
Hey ABC Plumbing,

Noticed a few things holding your website back:

- Load time is slow (especially on mobile)
- SEO score is below average — you're not showing up for local searches
- No contact form above the fold

These are fixable. I've helped other HVAC and plumbing companies in
the area improve their lead flow from search.

Worth a quick call?

Mubeen
```

---

## Dashboard Stats Example

After running the full pipeline on one campaign:

| Metric | Value |
|---|---|
| Businesses scraped | 240 |
| HIGH priority | 82 |
| MEDIUM priority | 94 |
| Emails found | 61 |
| Emails generated | 61 |
| Emails sent | 25 |
| Opens | 16 (64%) |
| Replies | 4 (16%) |

---

## Leads Table (Dashboard View)

| Name | City | Rating | Priority | Email | Sent |
|---|---|---|---|---|---|
| Miami Pro Plumbing | Coral Gables | 4.6 | HIGH | info@... | Yes |
| Sunrise HVAC | Doral | 4.8 | HIGH | contact@... | No |
| Quick Fix Electric | Miami Beach | 4.2 | MEDIUM | — | No |
| Best AC Repair | Hialeah | 4.9 | LOW | support@... | No |

Priority meanings:
- **HIGH** — major website issues or no website; best leads to contact
- **MEDIUM** — some issues; worth contacting
- **LOW** — good website; lower chance of interest

---

## Campaign Examples

### Home Services (HVAC, Plumbing)

```python
TARGET = {
    "city": "Miami",
    "country": "USA",
    "localities": ["Coral Gables", "Doral", "Hialeah", "Brickell"],
    "niche": "home service business",
    "niche_plural": "home service businesses",
    "industry": "home services (HVAC, Plumbing)",
    "your_service": "website conversion optimization",
    "your_service_benefit": "get more leads online",
    "pain_point": "limited online visibility",
}
```

### Real Estate (Dubai)

```python
TARGET = {
    "city": "Dubai",
    "country": "UAE",
    "localities": ["Dubai Marina", "Business Bay", "Downtown Dubai", "JVC"],
    "niche": "real estate agency",
    "niche_plural": "real estate agencies",
    "industry": "real estate",
    "your_service": "modern lead-generating websites",
    "your_service_benefit": "get more property enquiries online",
    "pain_point": "outdated or slow website",
}
```

### Restaurants (New York)

```python
TARGET = {
    "city": "New York",
    "country": "USA",
    "localities": ["Manhattan", "Brooklyn", "Queens"],
    "niche": "restaurant",
    "niche_plural": "restaurants",
    "industry": "food & beverage",
    "your_service": "online ordering systems",
    "your_service_benefit": "increase takeout revenue without app fees",
    "pain_point": "no direct online ordering",
}
```

---

## What Makes These Emails Work

**Good elements:**
1. Specific observation — "noticed your website loads slowly on mobile"
2. Real numbers — "4.6 stars from 187 reviews"
3. Local context — "plumber in Coral Gables"
4. Concrete benefit — "most customers search on their phones"
5. Social proof — "working with a few other companies in the area"
6. One simple CTA — "worth a quick chat?"

**What to avoid:**
1. Generic openers — "Dear Sir/Madam"
2. Buzzwords — "cutting-edge solution", "synergy", "leverage"
3. Too long — keep under 120 words
4. Multiple asks — one question only
5. Corporate tone — "We would like to explore a potential partnership"

# Caffrey Recreation Area — SEO + AEO Plan

**Goal:** Be the top answer, on Google and in AI assistants (ChatGPT, Perplexity, Google AI Overviews, Claude), for "camping on Lake Wallenpaupack" and "Lake Wallenpaupack boat launch".

## Where things stand on the current site
- 4 pages, almost no text. The homepage is hours plus a photo gallery, so there's little for Google or an AI to read or quote.
- No structured data (schema), no meta descriptions, and no FAQ.
- The address appears only on the Contact page. There's no map, directions or embedded hours schema.
- The "Capri Marina" link points to an external Chaparral page, so link value leaves the site.
- The footer says © 2020, which makes the site look abandoned to both people and crawlers.

## Target queries
| Intent | Queries |
|---|---|
| Core | lake wallenpaupack camping, campground lake wallenpaupack, lakeville pa campground |
| RV | rv camping lake wallenpaupack, rv park poconos lakefront, 30 amp campground poconos |
| Boating | lake wallenpaupack boat launch, boat launch with camping poconos, gas dock lake wallenpaupack |
| Tent | tent camping poconos lake, waterfront tent sites pennsylvania |
| Conversational (AEO) | "where can I camp right on Lake Wallenpaupack with my boat?", "cheapest lakefront camping in the Poconos", "Lake Wallenpaupack campground that has a gas dock" |

## Site structure (new)
- `/` Home
- `/camping/` Sites and amenities
- `/rates/` Rates, deposits and policies, all in HTML (no PDFs)
- `/boating/` Launch, slips, gas dock, plus a link to Capri Marina
- `/faq/` 15–25 Q&As with FAQPage schema
- `/lake-wallenpaupack-guide/` Things to do, fishing and nearby towns (Hawley, Lakeville). This is the topical-authority page.
- `/contact/` Map, directions from NYC, NJ and Philly, and hours

## Technical SEO checklist
- [x] `Campground` + `LocalBusiness` JSON-LD with address, phone, hours, amenities and price range (in the concepts)
- [x] `FAQPage` JSON-LD
- [x] Unique title and meta description per page, plus Open Graph tags
- [x] `robots.txt` that explicitly allows AI crawlers, plus `sitemap.xml`
- [x] `llms.txt`, a plain-text fact sheet for LLMs
- [ ] Self-host fonts, convert images to WebP, keep LCP under 2.5s
- [ ] HTTPS with www → apex redirects, and 301s from `/regular-camping-rates/` → `/rates/`
- [ ] Google Search Console and Bing Webmaster Tools, then submit the sitemap

## AEO (answer engine optimization)
1. **Answer-first copy.** Every section opens with a one-sentence factual answer (who, what, where, price) that an AI can quote verbatim.
2. **Consistent facts everywhere.** Use the exact same NAP (name, address, phone), rates and amenities on the site, Google Business Profile, DiscoverNEPA, PoconoGo, CamplinQ, Campendium and Yelp. LLMs trust facts that agree across sources. *Note: some directories list ZIP 18348. Confirm 18438 and fix the listings.*
3. **Entity linking.** Name "Lake Wallenpaupack", "Wayne County", "Route 590", "Poconos" and "Lakeville, PA" explicitly in the copy.
4. **Reviews.** Ask campers for Google reviews at checkout (QR code at the camp store). Review count and recency drive both the map pack and AI recommendations.
5. **Fresh content.** Publish a dated "This season at Caffrey" update every spring and fall.

## Local SEO
- Claim and optimize the Google Business Profile: category "Campground", secondary "Boat ramp", 20+ photos, hours, booking link and Q&A.
- Apple Business Connect and Bing Places.
- Pursue backlinks from Pocono Mountains Visitors Bureau, Wallenpaupack Area Chamber, DiscoverNEPA and Brookfield Renewable (the lake operator).

## Measuring it
- Search Console impressions and clicks for the target queries
- Google Business Profile calls and direction requests
- Monthly manual check: ask ChatGPT, Perplexity and Google AI Mode "best campground on Lake Wallenpaupack with a boat launch" and log whether Caffrey is cited.

## Open questions for the client
- Exact season dates for this year
- Online booking: keep phone/email, or add a booking engine (Campspot, Firefly, Newbook)?
- Better photography? A drone shoot of the shoreline sites would upgrade concepts A and C a lot.
- Relationship with Capri Marina: one brand or two? (This affects the joint pitch.)

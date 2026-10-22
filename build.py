#!/usr/bin/env python3
"""Build the Caffrey Recreation static site.

Page bodies live in src/pages/*.html and FAQ content in src/faq.json.
This script wraps each body with the shared <head>, header and footer,
adds per-page SEO (title, description, canonical, Open Graph, JSON-LD)
and writes the result to <slug>/index.html. Run: python3 build.py
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
SITE = "https://caffreyrecreation.com"

BUSINESS = {
    "name": "Caffrey Recreation Area",
    "legal": "Caffrey Recreation LLC",
    "phone": "(570) 226-4608",
    "tel": "+15702264608",
    "email": "Reservations@caffreyrecreation.com",
    "street": "431 Lakeshore Drive",
    "city": "Lakeville",
    "region": "PA",
    "zip": "18438",
}

NAV = [
    ("camping", "Camping", "/camping/"),
    ("rates", "Rates", "/rates/"),
    ("boating", "Boating", "/boating/"),
    ("guide", "Lake Guide", "/lake-wallenpaupack-guide/"),
    ("faq", "FAQ", "/faq/"),
    ("contact", "Contact", "/contact/"),
]

PAGES = [
    dict(src="home", out="", nav=None, crumb=None,
         title="Lake Wallenpaupack Camping & Boat Launch | Caffrey Recreation Area",
         desc="Lakefront RV and tent camping on Lake Wallenpaupack's west shore in Lakeville, PA. 29 waterfront sites, boat launch, gas dock and camp store. Price your trip in seconds."),
    dict(src="camping", out="camping/", nav="camping", crumb="Camping",
         title="Lakefront RV & Tent Camping on Lake Wallenpaupack | Caffrey",
         desc="29 waterfront campsites with 30 amp electric, water, picnic tables and fire rings on Lake Wallenpaupack in the Poconos. RV, trailer and tent sites."),
    dict(src="rates", out="rates/", nav="rates", crumb="Rates & Policies",
         title="Camping Rates & Policies | Caffrey Recreation Area, Lakeville PA",
         desc="RV sites $52–$65, tent sites $40–$48 per night on Lake Wallenpaupack. Deposits, cancellation policy, guest limits and what's included."),
    dict(src="boating", out="boating/", nav="boating", crumb="Boating",
         title="Lake Wallenpaupack Boat Launch, Slips & Gas Dock | Caffrey",
         desc="Launch and store your boat for $10 per stay, fuel up at the on-site gas dock, and camp steps from the water on Lake Wallenpaupack."),
    dict(src="guide", out="lake-wallenpaupack-guide/", nav="guide", crumb="Lake Wallenpaupack Guide",
         title="Lake Wallenpaupack Guide: Fishing, Boating & Things to Do | Caffrey",
         desc="A camper's guide to Lake Wallenpaupack in the Poconos: fishing, boating, nearby towns, day trips and the best time to visit."),
    dict(src="faq", out="faq/", nav="faq", crumb="FAQ",
         title="Caffrey Recreation Area FAQ | Camping on Lake Wallenpaupack",
         desc="Answers about rates, reservations, boat launching, pets, hookups, check-in and getting to Caffrey Recreation Area on Lake Wallenpaupack."),
    dict(src="contact", out="contact/", nav="contact", crumb="Contact & Directions",
         title="Contact & Directions | Caffrey Recreation Area, Lakeville PA",
         desc="431 Lakeshore Drive, Lakeville, PA 18438. Call (570) 226-4608 or email to reserve. Directions from NYC, Philadelphia and Scranton."),
]

ICONS = {
    "tent": '<path d="M3 20 12 4l9 16H3Z"/><path d="M12 4v16M9 20l3-6 3 6"/>',
    "rv": '<rect x="2" y="6" width="16" height="11" rx="2"/><path d="M18 10h2.5L22 13v4h-4"/><circle cx="7" cy="18" r="2"/><circle cx="17" cy="18" r="2"/><path d="M5 9h5v3H5z"/>',
    "boat": '<path d="M2 17s2 2 5 2 4-2 5-2 2 2 5 2 5-2 5-2"/><path d="M4 14 3 10h18l-2 4"/><path d="M12 10V3l5 5"/>',
    "fuel": '<path d="M4 21V5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v16"/><path d="M3 21h12M6 9h6"/><path d="M14 11h2a2 2 0 0 1 2 2v3a1.5 1.5 0 0 0 3 0V8l-3-3"/>',
    "store": '<path d="M3 9 5 4h14l2 5"/><path d="M4 9v11h16V9"/><path d="M3 9a3 3 0 0 0 6 0 3 3 0 0 0 6 0 3 3 0 0 0 6 0"/><path d="M10 20v-6h4v6"/>',
    "plug": '<path d="M9 2v6M15 2v6"/><path d="M6 8h12v4a6 6 0 0 1-12 0V8Z"/><path d="M12 18v4"/>',
    "fire": '<path d="M12 22c4 0 7-3 7-7 0-5-5-8-6-13-2 3-3 5-3 7-1-1-2-2-2-4-2 2-3 5-3 8 0 5 3 9 7 9Z"/>',
    "shower": '<path d="M4 4h6a6 6 0 0 1 6 6"/><path d="M12 10h8"/><path d="M13 14v1M16 14v1M19 14v1M13 18v1M16 18v1M19 18v1"/>',
    "laundry": '<rect x="4" y="2" width="16" height="20" rx="2"/><circle cx="12" cy="13" r="5"/><path d="M8 6h.01M11 6h.01"/>',
    "table": '<path d="M3 9h18M6 9l-2 9M18 9l2 9M8 14h8"/>',
    "fish": '<path d="M2 12s4-6 11-6c4 0 7 3 7 6s-3 6-7 6C6 18 2 12 2 12Z"/><path d="M20 12l2-3v6l-2-3Z"/><circle cx="15" cy="11" r=".8"/>',
    "pin": '<path d="M12 22s7-6.5 7-12a7 7 0 1 0-14 0c0 5.5 7 12 7 12Z"/><circle cx="12" cy="10" r="2.5"/>',
    "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2Z"/>',
    "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 6-10 7L2 6"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    "anchor": '<circle cx="12" cy="5" r="3"/><path d="M12 8v14M5 12H2a10 10 0 0 0 20 0h-3"/>',
    "leaf": '<path d="M11 20A7 7 0 0 1 4 13c0-6 6-10 16-10 0 10-4 16-10 16"/><path d="M4 21c4-4 7-7 11-10"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
}


def icon(name):
    return (f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


LOGO = ('<svg viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="9" fill="#3cc6b4"/>'
        '<path d="M6 21 13 11l4 5 3-3 6 8Z" fill="#0d1b1e"/><path d="M5 24c3 0 3-1.5 5.5-1.5S13 24 16 24s3-1.5 5.5-1.5S24 24 27 24" '
        'stroke="#0d1b1e" stroke-width="2" fill="none" stroke-linecap="round"/></svg>')


def business_schema():
    b = BUSINESS
    return {
        "@context": "https://schema.org",
        "@type": ["Campground", "LocalBusiness"],
        "@id": f"{SITE}/#business",
        "name": b["name"],
        "legalName": b["legal"],
        "url": f"{SITE}/",
        "telephone": "+1-570-226-4608",
        "email": b["email"],
        "image": f"{SITE}/assets/img/photo3.jpg",
        "logo": f"{SITE}/assets/img/logo.svg",
        "description": "Family-run lakefront campground with 29 waterfront RV and tent sites, boat launch, gas dock and camp store on the west shore of Lake Wallenpaupack in the Pocono Mountains.",
        "priceRange": "$40–$65 per night",
        "currenciesAccepted": "USD",
        "petsAllowed": False,
        "address": {"@type": "PostalAddress", "streetAddress": b["street"], "addressLocality": b["city"],
                    "addressRegion": b["region"], "postalCode": b["zip"], "addressCountry": "US"},
        "areaServed": ["Pocono Mountains", "Wayne County, PA", "Lake Wallenpaupack"],
        "containedInPlace": {"@type": "LakeBodyOfWater", "name": "Lake Wallenpaupack",
                             "sameAs": "https://en.wikipedia.org/wiki/Lake_Wallenpaupack"},
        "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": n, "value": True} for n in [
            "Lakefront campsites", "30 amp electric hookups", "Water hookups", "RV dump station", "Boat launch",
            "Boat storage", "Gas dock", "Camp store", "Hot showers", "Laundry", "Waterfront picnic area",
            "Fire rings", "Picnic tables"]],
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Thursday", "Sunday"], "opens": "09:00", "closes": "17:00"},
            {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Friday", "Saturday"], "opens": "09:00", "closes": "18:00"},
        ],
        "makesOffer": [
            {"@type": "Offer", "name": "RV / Trailer site (regular night)", "price": "52", "priceCurrency": "USD"},
            {"@type": "Offer", "name": "Tent site (regular night)", "price": "40", "priceCurrency": "USD"},
            {"@type": "Offer", "name": "Boat storage & launch (per stay)", "price": "10", "priceCurrency": "USD"},
        ],
    }


def breadcrumb_schema(page):
    return {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": page["crumb"], "item": f"{SITE}/{page['out']}"},
        ],
    }


def faq_schema(groups, limit=None):
    qs = [q for g in groups for q in g["items"]]
    if limit:
        qs = [q for q in qs if q.get("home")]
    return {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q["q"],
                        "acceptedAnswer": {"@type": "Answer", "text": q["a"]}} for q in qs],
    }


def render_faq(groups, only_home=False):
    out = []
    for g in groups:
        items = [q for q in g["items"] if q.get("home")] if only_home else g["items"]
        if not items:
            continue
        if not only_home:
            out.append(f'<div class="faq-group" id="{g["id"]}"><h2>{html.escape(g["title"])}</h2>')
        for q in items:
            out.append(f'<details class="qa"><summary>{html.escape(q["q"])}</summary><p>{html.escape(q["a"])}</p></details>')
        if not only_home:
            out.append("</div>")
    return "\n".join(out)


def head(page, schemas):
    url = f"{SITE}/{page['out']}"
    ld = "\n".join(f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>' for s in schemas)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(page['title'])}</title>
<meta name="description" content="{html.escape(page['desc'])}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#0d1b1e">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Caffrey Recreation Area">
<meta property="og:title" content="{html.escape(page['title'])}">
<meta property="og:description" content="{html.escape(page['desc'])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/assets/img/photo3.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="geo.region" content="US-PA">
<meta name="geo.placename" content="Lakeville, Pennsylvania">
<link rel="icon" href="/assets/img/logo.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/site.css">
{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>"""


def header(page):
    current = ' aria-current="page"'
    links = "".join(
        f'<li><a href="{href}"{current if page["nav"] == key else ""}>{label}</a></li>'
        for key, label, href in NAV)
    return f"""
<header class="site-head">
  <div class="wrap">
    <a class="logo" href="/" aria-label="Caffrey Recreation Area home">{LOGO}Caffrey<span>.</span></a>
    <ul class="menu" id="menu">{links}</ul>
    <a class="status" href="/contact/" data-status><span class="dot"></span><span class="txt">Hours</span></a>
    <button class="burger" aria-label="Menu" aria-controls="menu" aria-expanded="false">☰</button>
  </div>
</header>
<main id="main">"""


def crumbs(page):
    if not page["crumb"]:
        return ""
    return f'<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / {html.escape(page["crumb"])}</nav>'


FOOTER = f"""</main>
<footer class="site-foot">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <a class="logo" href="/">{LOGO}Caffrey<span>.</span></a>
        <p class="muted" style="margin-top:12px;max-width:320px">Family-run lakefront camping on the west shore of Lake Wallenpaupack, in the Pocono Mountains of Pennsylvania.</p>
      </div>
      <div><h4>Stay</h4><ul><li><a href="/camping/">Campsites</a></li><li><a href="/rates/">Rates &amp; policies</a></li><li><a href="/boating/">Boat launch &amp; gas</a></li><li><a href="/faq/">FAQ</a></li></ul></div>
      <div><h4>Explore</h4><ul><li><a href="/lake-wallenpaupack-guide/">Lake Wallenpaupack guide</a></li><li><a href="/boating/#capri-marina">Capri Marina</a></li><li><a href="/contact/#directions">Directions</a></li></ul></div>
      <div><h4>Contact</h4><ul>
        <li><a href="tel:{BUSINESS['tel']}">{BUSINESS['phone']}</a></li>
        <li><a href="mailto:{BUSINESS['email']}">{BUSINESS['email']}</a></li>
        <li class="muted">{BUSINESS['street']}<br>{BUSINESS['city']}, {BUSINESS['region']} {BUSINESS['zip']}</li>
      </ul></div>
    </div>
    <div class="legal"><span>© <span data-year>2026</span> {BUSINESS['legal']}</span><span>No pets · Max 8 guests per site</span></div>
  </div>
</footer>
<div class="callbar"><a class="btn alt" href="tel:{BUSINESS['tel']}">Call</a><a class="btn" href="/#plan">Price my trip</a></div>
<script src="/assets/js/site.js" defer></script>
</body>
</html>
"""


def build():
    faq = json.loads((SRC / "faq.json").read_text())
    for page in PAGES:
        body = (SRC / "pages" / f"{page['src']}.html").read_text()
        body = re.sub(r"\{\{icon:(\w+)\}\}", lambda m: icon(m.group(1)), body)
        body = body.replace("{{crumbs}}", crumbs(page))
        body = body.replace("{{faq:home}}", render_faq(faq, only_home=True))
        body = body.replace("{{faq:all}}", render_faq(faq))
        for k, v in BUSINESS.items():
            body = body.replace("{{" + k + "}}", v)

        schemas = [business_schema()] if page["src"] in ("home", "contact", "camping") else []
        if page["crumb"]:
            schemas.append(breadcrumb_schema(page))
        if page["src"] == "faq":
            schemas.append(faq_schema(faq))
        elif page["src"] == "home":
            schemas.append(faq_schema(faq, limit=True))

        out = ROOT / page["out"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(head(page, schemas) + header(page) + body + FOOTER)
        print("built", out.relative_to(ROOT))

    urls = "\n".join(f"  <url><loc>{SITE}/{p['out']}</loc></url>" for p in PAGES)
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n')
    print("built sitemap.xml")


if __name__ == "__main__":
    build()

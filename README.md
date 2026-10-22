# Caffrey Recreation Area — Website

New site for [caffreyrecreation.com](https://caffreyrecreation.com/), built from Concept C ("Trip Planner").

## Pages
| URL | Source |
|---|---|
| `/` | `src/pages/home.html`, with the trip calculator and quick answers |
| `/camping/` | `src/pages/camping.html` |
| `/rates/` | `src/pages/rates.html` |
| `/boating/` | `src/pages/boating.html` |
| `/lake-wallenpaupack-guide/` | `src/pages/guide.html` |
| `/faq/` | `src/pages/faq.html` (questions come from `src/faq.json`) |
| `/contact/` | `src/pages/contact.html` |

## Editing
Edit files in `src/`, then rebuild:

```bash
python3 build.py
```

`build.py` wraps each page with the shared header and footer. It also adds the title, meta and Open Graph tags, the JSON-LD schema (Campground/LocalBusiness, FAQPage, BreadcrumbList), and regenerates `sitemap.xml`. Business details such as phone and address live in `BUSINESS` at the top of `build.py`. Styles are in `assets/css/site.css` and behavior (calculator, hours, menu) in `assets/js/site.js`.

## Preview
```bash
python3 -m http.server 4321
```

## Also here
- `concepts/`: the original three design directions (A, B, C), plus `concepts/capri-marine/`, the companion concept for Capri Marine next door
- `mockups/`: desktop and phone screenshots for the pitch deck
- `SEO-AEO-PLAN.md`: search and AI-answer strategy
- `robots.txt`, `llms.txt`
- `export_mockup.py`: writes a portable, clearly labelled mockup (both sites, relative links, noindex) to `dist/` and zips it for sharing

## Confirm with the client before launch
- Season open/close dates, and the full campground rules
- Lake facts on the guide page (acreage, shoreline, fish species, drive times)
- Capri Marine relationship and wording
- ZIP 18438 (some directories list 18348)

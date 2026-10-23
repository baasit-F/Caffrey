#!/usr/bin/env python3
"""Export a portable, clearly-labelled mockup of the Caffrey site.

The live build uses root-relative URLs (/camping/, /assets/...) meant for
hosting at caffreyrecreation.com. This flattens every page to a top-level
.html file with relative links, so the mockup opens straight from disk
(double-click index.html) or from any static host, and adds a
"design mockup" banner so it's never mistaken for the official site.
The mockup is Caffrey-only: every Capri Marine mention is stripped.
Run after build.py:  python3 export_mockup.py
"""
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "dist" / "caffrey-mockup"

PAGES = {  # built page -> flat file name
    "index.html": "index.html",
    "camping/index.html": "camping.html",
    "rates/index.html": "rates.html",
    "boating/index.html": "boating.html",
    "lake-wallenpaupack-guide/index.html": "lake-guide.html",
    "faq/index.html": "faq.html",
    "contact/index.html": "contact.html",
}
ROUTES = {"/": "index.html", "/camping/": "camping.html", "/rates/": "rates.html", "/boating/": "boating.html",
          "/lake-wallenpaupack-guide/": "lake-guide.html", "/faq/": "faq.html", "/contact/": "contact.html"}

BANNER = ('<div style="position:relative;z-index:50;background:#ffb454;color:#0d1b1e;font:600 13px/1.4 system-ui,sans-serif;'
          'text-align:center;padding:8px 16px">Design mockup prepared for Caffrey Recreation Area, not the official website.</div>')


def relink(html):
    # Internal page routes, with optional #fragment
    def route(m):
        path, frag = m.group(2), m.group(3) or ""
        return f'{m.group(1)}="{ROUTES[path]}{frag}"'
    pattern = "|".join(re.escape(r) for r in sorted(ROUTES, key=len, reverse=True))
    html = re.sub(rf'(href)="({pattern})(#[\w-]+)?"', route, html)
    html = html.replace('"/assets/', '"assets/').replace("url(/assets/", "url(assets/")
    return html


def strip_capri(html):
    html = re.sub(r'<li><a href="[^"]*#capri-marine">[^<]*</a></li>', "", html)
    html = re.sub(r'<section id="capri-marine">.*?</section>\s*', "", html, flags=re.S)
    html = re.sub(r'<details class="qa"><summary>[^<]*</summary><p>[^<]*Capri[^<]*</p></details>\s*', "", html)

    def faq_ld(m):
        data = json.loads(m.group(1))
        if data.get("@type") == "FAQPage":
            data["mainEntity"] = [q for q in data["mainEntity"] if "Capri" not in json.dumps(q)]
        return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'
    return re.sub(r'<script type="application/ld\+json">(.*?)</script>', faq_ld, html, flags=re.S)


def main():
    for old in (OUT, OUT.with_suffix(".zip")):
        if old.is_dir():
            shutil.rmtree(old)
        elif old.exists():
            old.unlink()
    shutil.copytree(ROOT / "assets", OUT / "assets")
    for src, dst in PAGES.items():
        html = strip_capri(relink((ROOT / src).read_text()))
        # Inside the header, so the fixed/sticky header carries it on every page
        html = html.replace('<header class="site-head">', '<header class="site-head">\n' + BANNER, 1)
        html = html.replace('<meta name="viewport"', '<meta name="robots" content="noindex">\n<meta name="viewport"', 1)
        (OUT / dst).write_text(html)

    for f in OUT.glob("*.html"):
        text = f.read_text()
        bad = re.findall(r'(?:href|src)="/(?!/)[^"]*"', text)
        if bad:
            raise SystemExit(f"{f.name}: unconverted links {bad[:3]}")
        if re.search("capri", text, re.I):
            raise SystemExit(f"{f.name}: still mentions Capri")
    archive = shutil.make_archive(str(OUT), "zip", OUT.parent, OUT.name)
    print("exported", OUT.relative_to(ROOT), "and", Path(archive).relative_to(ROOT))


if __name__ == "__main__":
    main()

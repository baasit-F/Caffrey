#!/usr/bin/env python3
"""Export a portable, clearly-labelled mockup of the Caffrey site + Capri concept.

The live build uses root-relative URLs (/camping/, /assets/...) meant for
hosting at caffreyrecreation.com. This flattens every page to a top-level
.html file with relative links, so the mockup opens straight from disk
(double-click index.html) or from any static host, and adds a
"design mockup" banner so it's never mistaken for the official site.
Run after build.py:  python3 export_mockup.py
"""
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "dist" / "caffrey-capri-mockup"

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
          'text-align:center;padding:8px 16px">Design mockup prepared for {who}, not the official website. '
          '<a href="{other}" style="color:inherit">{other_label} →</a></div>')


def relink(html):
    # Internal page routes, with optional #fragment
    def route(m):
        path, frag = m.group(2), m.group(3) or ""
        return f'{m.group(1)}="{ROUTES[path]}{frag}"'
    pattern = "|".join(re.escape(r) for r in sorted(ROUTES, key=len, reverse=True))
    html = re.sub(rf'(href)="({pattern})(#[\w-]+)?"', route, html)
    html = html.replace('"/assets/', '"assets/').replace("url(/assets/", "url(assets/")
    return html


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "assets", OUT / "assets")
    caffrey_banner = BANNER.format(who="Caffrey Recreation Area", other="capri-marine.html", other_label="See the Capri Marine concept")
    for src, dst in PAGES.items():
        html = relink((ROOT / src).read_text())
        html = html.replace('<a class="skip"', caffrey_banner + '\n<a class="skip"', 1)
        html = html.replace('<meta name="viewport"', '<meta name="robots" content="noindex">\n<meta name="viewport"', 1)
        (OUT / dst).write_text(html)

    capri = (ROOT / "concepts/capri-marine/index.html").read_text().replace("../../assets/", "assets/")
    capri = capri.replace("<body>", "<body>\n" + BANNER.format(who="Capri Marine", other="index.html", other_label="See the Caffrey Recreation site"), 1)
    capri = capri.replace('<meta name="viewport"', '<meta name="robots" content="noindex">\n<meta name="viewport"', 1)
    (OUT / "capri-marine.html").write_text(capri)

    # Leftover root-relative links would break from disk
    for f in OUT.glob("*.html"):
        bad = re.findall(r'(?:href|src)="/(?!/)[^"]*"', f.read_text())
        if bad:
            raise SystemExit(f"{f.name}: unconverted links {bad[:3]}")
    archive = shutil.make_archive(str(OUT), "zip", OUT.parent, OUT.name)
    print("exported", OUT.relative_to(ROOT), "and", Path(archive).relative_to(ROOT))


if __name__ == "__main__":
    main()

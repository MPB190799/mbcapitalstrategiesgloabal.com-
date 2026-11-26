#!/usr/bin/env python3
"""
Add branded site navigation header to EN glossary pages.
EN-AdSense Endspurt: glossary pages lack visible site nav — looks orphaned to Google reviewers.
"""
import os
import glob
import re

GLOSSARY_DIR = "/home/mbcap/websites/EN-Seite/glossary"

SITE_NAV_HTML = '''<!-- Site navigation header: trust signal for Google AdSense review -->
<header style="background:#050508;border-bottom:1px solid rgba(212,175,55,0.18);padding:12px 0;position:sticky;top:0;z-index:100;margin-bottom:0">
  <div style="max-width:1100px;margin:0 auto;padding:0 20px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px">
    <a href="/index.html" style="display:flex;align-items:center;gap:10px;text-decoration:none;color:inherit" aria-label="MB Capital Strategies home">
      <img src="/Logo.webp" onerror="this.src='/Logo.png'" alt="MB Capital Strategies Logo" style="height:32px;width:auto" fetchpriority="high">
      <span style="color:#d4af37;font-weight:700;font-size:0.95rem;white-space:nowrap">MB Capital Strategies <span style="font-weight:400;color:#9aa0b8">Global</span></span>
    </a>
    <nav aria-label="Site navigation" style="display:flex;gap:18px;flex-wrap:wrap;align-items:center">
      <a href="/pages/blog.html" style="color:#c8cfe0;text-decoration:none;font-size:0.88rem;transition:color .2s">Research</a>
      <a href="/pages/shipping.html" style="color:#c8cfe0;text-decoration:none;font-size:0.88rem">Shipping</a>
      <a href="/pages/mining.html" style="color:#c8cfe0;text-decoration:none;font-size:0.88rem">Mining</a>
      <a href="/pages/calculators.html" style="color:#c8cfe0;text-decoration:none;font-size:0.88rem">Calculators</a>
      <a href="/pages/glossary.html" style="color:#d4af37;text-decoration:none;font-size:0.88rem;font-weight:600">Glossary</a>
      <a href="/pages/about.html" style="color:#c8cfe0;text-decoration:none;font-size:0.88rem">About</a>
    </nav>
  </div>
</header>
'''

def needs_nav(html_content):
    """Check if the page already has the site navigation header."""
    return 'header style=' not in html_content and '<nav class="navbar"' not in html_content and '<nav class="nav"' not in html_content

def add_nav_after_body(html_content, filename):
    """Insert site nav immediately after <body> tag."""
    if '<body>' in html_content:
        return html_content.replace('<body>\n', '<body>\n' + SITE_NAV_HTML, 1)
    elif '<body>' in html_content:
        return html_content.replace('<body>', '<body>\n' + SITE_NAV_HTML, 1)
    return html_content

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if not needs_nav(content):
        print(f"  SKIP (already has nav): {os.path.basename(filepath)}")
        return False

    new_content = add_nav_after_body(content, filepath)
    if new_content == content:
        print(f"  SKIP (no <body> tag found): {os.path.basename(filepath)}")
        return False

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"  OK: {os.path.basename(filepath)}")
    return True

def main():
    files = glob.glob(os.path.join(GLOSSARY_DIR, "*.html"))
    files.sort()

    updated = 0
    skipped = 0

    print(f"Processing {len(files)} glossary pages...")
    for fp in files:
        result = process_file(fp)
        if result:
            updated += 1
        else:
            skipped += 1

    print(f"\nDone: {updated} updated, {skipped} skipped")

if __name__ == "__main__":
    main()

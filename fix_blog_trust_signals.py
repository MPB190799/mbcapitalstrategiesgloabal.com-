#!/usr/bin/env python3
"""
fix_blog_trust_signals.py
EN Blog Trust Signal Fix — web-design-agent 2026-06-07

Fixes two categories of issues in EN blog pages:
1. Thin site-footer (Privacy + Imprint only) → full footer with all trust links
2. Broken author-box-text structure → proper author-box with Marco's photo

Run from: /home/mbcap/websites/EN-Seite/
"""

import os
import re

BASE = '/home/mbcap/websites/EN-Seite/blog'

# ── 1. THIN FOOTER FIX ──────────────────────────────────────────────────────
# These 9 pages use <footer class="site-footer"> with only Privacy | Imprint

THIN_FOOTER_PAGES = [
    'dno-asa-analysis-2026.html',
    'bw-lpg-q1-2026-earnings-preview.html',
    'inplay-oil-analysis-2026.html',
    'cmb-tech-ex-dividend-june-2026.html',
    'opec-june-2026-tanker-stocks.html',
    'riley-exploration-analysis-2026.html',
    'shipping-dividend-double-payday-june-2026.html',
    'torm-dividend-analysis-2026.html',
    'weekly-recap-kw15-2026.html',
]

# The old thin footer pattern (regex)
THIN_FOOTER_PATTERN = re.compile(
    r'<footer class="site-footer">.*?</footer>',
    re.DOTALL
)

# Replacement: full footer using absolute paths (these pages use /pages/ prefix)
FULL_FOOTER_ABSOLUTE = '''<footer class="site-footer" style="background:#0a0a12;border-top:1px solid rgba(212,175,55,0.15);padding:28px 20px;text-align:center;margin-top:48px;">
  <div style="max-width:860px;margin:0 auto;">
    <div style="display:flex;justify-content:center;gap:16px;margin-bottom:14px;flex-wrap:wrap;">
      <a href="https://www.youtube.com/@mbcapitalstrategies" target="_blank" rel="noopener" aria-label="YouTube" style="color:#6b7a99;transition:color 0.2s;">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
      </a>
      <a href="https://www.linkedin.com/company/mb-capital-strategies/" target="_blank" rel="noopener" aria-label="LinkedIn" style="color:#6b7a99;transition:color 0.2s;">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
      </a>
    </div>
    <p style="color:#6b7a99;font-size:0.82rem;margin:0 0 12px;">&copy; 2026 MB Capital Strategies Global &middot; Marco Bozem</p>
    <nav aria-label="Footer links" style="display:flex;justify-content:center;gap:12px;flex-wrap:wrap;font-size:0.8rem;">
      <a href="/pages/contact.html" style="color:#6b7a99;text-decoration:none;">Contact</a>
      <a href="/pages/imprint.html" style="color:#6b7a99;text-decoration:none;">Imprint</a>
      <a href="/pages/privacy.html" style="color:#6b7a99;text-decoration:none;">Privacy Policy</a>
      <a href="/pages/disclaimer.html" style="color:#6b7a99;text-decoration:none;">Disclaimer</a>
      <a href="/pages/affiliate-disclosure.html" style="color:#6b7a99;text-decoration:none;">Affiliate Disclosure</a>
      <a href="https://mbcapitalstrategies.com" target="_blank" rel="noopener" style="color:#6b7a99;text-decoration:none;">Deutsche Version</a>
    </nav>
  </div>
</footer>'''


# ── 2. BROKEN AUTHOR BOX FIX ────────────────────────────────────────────────
# 4 pages use <div class="author-box"><div class="author-box-text">...
# They need the proper author-box with Marco's photo

BROKEN_AUTHOR_PAGES = [
    'cmb-tech-ex-dividend-june-2026.html',
    'opec-june-2026-tanker-stocks.html',
    'weekly-recap-kw15-2026.html',
    'weekly-recap-kw22-2026.html',
]

# Match the broken author-box-text pattern
BROKEN_AUTHOR_PATTERN = re.compile(
    r'<div class="author-box">\s*<div class="author-box-text">.*?</div>\s*</div>',
    re.DOTALL
)

# Replacement: proper author-box structure matching styles.css
PROPER_AUTHOR_BOX = '''<div class="author-box">
  <picture>
    <source srcset="/marco.webp" type="image/webp">
    <img src="/marco.jpg" alt="Marco Bozem — Independent Investor, MB Capital Strategies" class="author-img" width="76" height="76" loading="lazy">
  </picture>
  <div class="author-info">
    <span class="author-label">About the Author</span>
    <span class="author-name">Marco Bozem</span>
    <p class="author-bio">Independent investor focused on hard assets: shipping, mining, energy, pipelines. Long-term dividend-oriented strategy based on cashflow logic. All positions disclosed where relevant. Not a financial advisor.</p>
    <div class="author-links">
      <a href="/pages/about.html" rel="author">About Marco</a>
      <a href="https://www.linkedin.com/company/mb-capital-strategies/" rel="noopener" target="_blank">LinkedIn</a>
      <a href="https://www.youtube.com/@mbcapitalstrategies" rel="noopener" target="_blank">YouTube</a>
    </div>
  </div>
</div>'''


def fix_thin_footer(filepath):
    """Replace thin site-footer with full footer."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'class="site-footer"' not in content:
        return False, 'no site-footer found'

    new_content = THIN_FOOTER_PATTERN.sub(FULL_FOOTER_ABSOLUTE, content)

    if new_content == content:
        return False, 'no change (pattern did not match)'

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    return True, 'thin footer upgraded'


def fix_broken_author_box(filepath):
    """Replace broken author-box-text with proper author-box structure."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'author-box-text' not in content:
        return False, 'no broken author-box found'

    new_content = BROKEN_AUTHOR_PATTERN.sub(PROPER_AUTHOR_BOX, content)

    if new_content == content:
        return False, 'no change (pattern did not match)'

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    return True, 'author-box fixed'


def main():
    fixed_footer = []
    fixed_author = []
    errors = []

    print('=== EN Blog Trust Signal Fix — web-design-agent 2026-06-07 ===')
    print()

    # Fix thin footers
    print('--- Fixing thin footers (9 pages) ---')
    for page in THIN_FOOTER_PAGES:
        path = os.path.join(BASE, page)
        if not os.path.exists(path):
            errors.append(f'NOT FOUND: {page}')
            continue
        ok, msg = fix_thin_footer(path)
        if ok:
            fixed_footer.append(page)
            print(f'  [OK] {page}: {msg}')
        else:
            errors.append(f'{page}: {msg}')
            print(f'  [SKIP] {page}: {msg}')

    print()

    # Fix broken author boxes
    print('--- Fixing broken author boxes (4 pages) ---')
    for page in BROKEN_AUTHOR_PAGES:
        path = os.path.join(BASE, page)
        if not os.path.exists(path):
            errors.append(f'NOT FOUND: {page}')
            continue
        ok, msg = fix_broken_author_box(path)
        if ok:
            fixed_author.append(page)
            print(f'  [OK] {page}: {msg}')
        else:
            errors.append(f'{page}: {msg}')
            print(f'  [SKIP] {page}: {msg}')

    print()
    print('=== SUMMARY ===')
    print(f'Footers upgraded: {len(fixed_footer)}/{len(THIN_FOOTER_PAGES)}')
    print(f'Author boxes fixed: {len(fixed_author)}/{len(BROKEN_AUTHOR_PAGES)}')
    if errors:
        print(f'Errors/Skips ({len(errors)}):')
        for e in errors:
            print(f'  - {e}')
    print()
    print('Total pages modified:', len(fixed_footer) + len(fixed_author))


if __name__ == '__main__':
    main()

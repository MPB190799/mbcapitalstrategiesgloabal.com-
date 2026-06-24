#!/usr/bin/env python3
"""
Remove visible DE-companion markers from EN-Seite for AdSense eligibility.
CONSERVATIVE approach: only remove elements that are UNAMBIGUOUSLY companion markers.

Patterns targeted:
  A) <aside aria-label="Cross-language link"...>...</aside>
  B) Single-line div blocks: <div...>...<p...>Deutsche Version:...</p></div>  (all on one line)
  C) Multi-line compact div block containing ONLY companion text
  D) <p style="...font-size:0.85rem...">Deutsche Version: ... auf Deutsch lesen ...</p>  (inline p)
  E) Footer-nav: <a href="https://mbcapitalstrategies.com...">Deutsche Version</a>  (anchor only)
  F) Author-box trailing: middot + <a href="...">Deutsche Version</a>
  G) Copyright line: "© 2026 ... English companion to the original German site <a>...</a>"
  H) Footer companion paragraph: <p>English companion to the original German site ...</p>
  I) Nav lang-flag: <a ... class="lang-flag" title="Deutsche Version">...</a>
  J) Flag emoji lines: 🇩🇪 <strong>Deutsche Version:</strong> <a href="...">Diesen Artikel auf Deutsch lesen</a>

WHAT WE DO NOT TOUCH:
  - <div> blocks that only have gold border but contain real content (FCF links, tool links, etc.)
  - hreflang in <head>
  - Article text, headings, affiliate blocks, etc.
"""

import re
import sys
from pathlib import Path

EN_ROOT = Path("/home/mbcap/websites/EN-Seite")

# ================================================================
# PATTERN A: <aside aria-label="Cross-language link">...</aside>
# ================================================================
# These are entire aside elements dedicated to the language switch.
# They always start with aria-label="Cross-language link".
# Removal: remove the entire <aside>...</aside> block.

def remove_aside_cross_language(lines: list[str]) -> tuple[list[str], int]:
    """Remove <aside aria-label="Cross-language link"> blocks."""
    out = []
    count = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        # Detect opening
        if re.search(r'<aside[^>]+aria-label=["\']Cross-language link', line, re.IGNORECASE):
            # Check if self-closed on same line
            rest = line[line.find('<aside'):]
            if '</aside>' in rest:
                count += 1
                i += 1
                continue
            # Multi-line: scan for closing </aside>
            j = i + 1
            while j < len(lines) and '</aside>' not in lines[j]:
                j += 1
            # j points to </aside> line or end
            if j < len(lines):
                count += 1
                i = j + 1  # skip through closing tag
            else:
                # Not found: keep to be safe
                out.append(line)
                i += 1
        else:
            out.append(line)
            i += 1
    return out, count


# ================================================================
# PATTERN B/C: Companion div blocks
# ================================================================
# The companion div blocks have ONE of these exact signatures:
#
# Signature 1 (single line):
#   <div style="margin:2rem 0;padding:1.5rem;border:1px solid rgba(212,175,55,...">
#     <p ...>Deutsche Version: <a ...>Auf Deutsch lesen</a></p></div>
#
# Signature 2 (multi-line):
#   <div style="margin: 2rem 0; padding: 1.5rem; border: 1px solid rgba(212,175,55,0.3)...">
#       <p style="margin: 0; ...">
#           🇩🇪 <strong>Deutsche Version:</strong> <a href="...">Diesen Artikel auf Deutsch lesen</a>
#           ...
#       </p>
#   </div>
#
# Key distinguisher: "padding:1.5rem" OR "padding: 1.5rem" combined with "Deutsche Version" text
# This combo is UNIQUE to companion boxes (real link divs use padding:12px/16px/20px)

COMPANION_DIV_OPEN = re.compile(
    r'<div[^>]+(?:padding:\s*1\.5rem|padding:1\.5rem)[^>]*>',
    re.IGNORECASE
)

def remove_companion_div_blocks(lines: list[str]) -> tuple[list[str], int]:
    """Remove companion div blocks (identified by padding:1.5rem + Deutsche Version content)."""
    out = []
    count = 0
    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if this line has a companion-div opener (padding:1.5rem)
        if COMPANION_DIV_OPEN.search(line):
            # Collect this block to check content
            block = [line]

            # Single-line block? (everything on one line including </div>)
            if line.count('<div') <= line.count('</div>'):
                # Balanced on one line - check if it contains companion text
                if re.search(r'Deutsche Version|Diesen Artikel auf Deutsch|Auf Deutsch lesen|auf Deutsch lesen', line, re.IGNORECASE):
                    count += 1
                    i += 1
                    continue
                else:
                    out.append(line)
                    i += 1
                    continue

            # Multi-line: scan ahead for closing </div> (max 20 lines)
            div_depth = line.count('<div') - line.count('</div>')
            j = i + 1
            max_lookahead = min(i + 20, len(lines))
            while j < max_lookahead:
                block.append(lines[j])
                div_depth += lines[j].count('<div') - lines[j].count('</div>')
                if div_depth <= 0:
                    break
                j += 1

            # Check if block contains companion text
            block_text = '\n'.join(block)
            if re.search(r'Deutsche Version|Diesen Artikel auf Deutsch|Auf Deutsch lesen|auf Deutsch lesen', block_text, re.IGNORECASE):
                # ALSO verify this block does NOT contain actual content (headings, paragraphs with text)
                # Companion blocks only have a single <p> with the link - no <h1-6>, no article text
                has_actual_content = re.search(r'<h[1-6]|<article|<section|<img[^>]+src=', block_text, re.IGNORECASE)
                if not has_actual_content:
                    count += 1
                    i = j + 1
                    continue

            # Not a companion block or contains real content - keep as-is
            out.extend(block)
            i = j + 1 if div_depth <= 0 else i + 1
        else:
            out.append(line)
            i += 1
    return out, count


# ================================================================
# PATTERN D: Inline <p> companion markers
# ================================================================
# These <p> tags ARE the companion box (entire <p> content = marker).
# Distinguishing feature:
#   - font-size:0.85rem + color:#888aa0 + "Deutsche Version:" text
#   - OR starts with "Deutsche Version:" directly
# They may span 2 lines (opening + closing).

def remove_inline_p_companion(lines: list[str]) -> tuple[list[str], int]:
    """Remove <p> tags that contain ONLY companion marker text."""
    out = []
    count = 0
    i = 0
    while i < len(lines):
        line = lines[i]

        # Detect: <p ...>Deutsche Version: ... (with or without closing </p> on same line)
        # Must contain "Deutsche Version:" or "English companion to the original German site"
        # AND be a companion-styled p (font-size:0.85rem, color:#888aa0 OR background:rgba(212,175,55)

        if re.search(r'<p[^>]+>(?:\s*|&#127465;&#127466;|🇩🇪\s*)(?:Deutsche Version:|English companion to the original German site)', line, re.IGNORECASE):
            # Check if it closes on same line
            rest = line[line.find('<p'):]
            if '</p>' in rest:
                count += 1
                i += 1
                continue
            # Multi-line: find closing </p> within next 5 lines
            j = i + 1
            max_look = min(i + 6, len(lines))
            found_close = False
            while j < max_look:
                if '</p>' in lines[j] and '<p' not in lines[j]:
                    found_close = True
                    break
                j += 1
            if found_close:
                count += 1
                i = j + 1
                continue
            # No close found - remove just this line
            count += 1
            i += 1
            continue

        out.append(line)
        i += 1
    return out, count


# ================================================================
# PATTERN J: Flag emoji lines (standalone)
# ================================================================
# Lines containing: 🇩🇪 <strong>Deutsche Version:</strong> <a href="...">Diesen Artikel auf Deutsch lesen</a>
# These appear as standalone lines inside a div block (the div itself is separate).

def remove_flag_emoji_lines(lines: list[str]) -> tuple[list[str], int]:
    """Remove standalone flag emoji companion lines."""
    out = []
    count = 0
    for line in lines:
        # Flag emoji + Deutsche Version: + Deutsch lesen link
        if re.search(
            r'(?:&#127465;&#127466;|🇩🇪|\?\?)\s*<strong[^>]*>Deutsche Version[^<]*</strong>\s*<a[^>]+href=["\']https://mbcapitalstrategies\.com',
            line, re.IGNORECASE
        ):
            count += 1
            continue
        # Also catch line that's just the href of the flag block
        # (some are split over 2 lines: emoji on one, <a> on next)
        out.append(line)
    return out, count


def remove_flag_multiline_blocks(lines: list[str]) -> tuple[list[str], int]:
    """Remove multi-line flag blocks:
    Line N:   &#127465;&#127466; <strong style="...">Deutsche Version:</strong>
    Line N+1: <a href="https://mbcapitalstrategies.com/...">Diesen Artikel auf Deutsch lesen</a>
    Line N+2: (optional: &nbsp;|&nbsp; <a href="...">MB Capital Strategies (DE)</a>)
    Line N+3: (optional: &nbsp;|&nbsp; <a href="...">mbcapitalstrategies.com</a>)
    """
    out = []
    count = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        # Detect "Deutsche Version:" strong tag (flag emoji may be on same or prior context)
        if re.search(r'(?:&#127465;&#127466;|🇩🇪|\?\?)\s*<strong[^>]*>\s*Deutsche Version:', line, re.IGNORECASE):
            # Check if this is a self-contained line with <a> tag
            if re.search(r'<a[^>]+href=["\']https://mbcapitalstrategies\.com', line, re.IGNORECASE):
                # Check if it ends with </a> or has more continuations
                # Look ahead for closing of the block (usually a blank line or </div> or <!-- comment -->)
                j = i + 1
                continuation_count = 0
                while j < len(lines) and continuation_count < 4:
                    next_line = lines[j].strip()
                    # If next line contains a mbcapitalstrategies.com link or is empty/whitespace
                    if re.search(r'mbcapitalstrategies\.com', next_line, re.IGNORECASE) and '<a' in next_line:
                        j += 1
                        continuation_count += 1
                    elif not next_line:
                        j += 1
                        break
                    else:
                        break
                count += 1
                i = j
                continue
            else:
                # Flag on this line, link on next line
                if i + 1 < len(lines) and re.search(r'<a[^>]+href=["\']https://mbcapitalstrategies\.com', lines[i+1], re.IGNORECASE):
                    # Skip this and next 1-3 lines that are part of the block
                    j = i + 1
                    while j < len(lines) and j < i + 4:
                        next_line = lines[j].strip()
                        if re.search(r'mbcapitalstrategies\.com', next_line, re.IGNORECASE):
                            j += 1
                        elif not next_line:
                            break
                        else:
                            j += 1
                            break
                    count += 1
                    i = j
                    continue
        out.append(line)
        i += 1
    return out, count


# ================================================================
# PATTERN E: Footer anchor "Deutsche Version"
# ================================================================
# <a href="https://mbcapitalstrategies.com...">Deutsche Version</a>
# These appear ONLY in footer-links divs. We remove just the anchor.

def remove_footer_deutsche_version_anchor(lines: list[str]) -> tuple[list[str], int]:
    """Remove Deutsche Version footer anchor (just the <a> tag)."""
    out = []
    count = 0
    pattern = re.compile(
        r'[ \t]*<a[^>]+href=["\']https://mbcapitalstrategies\.com[^"\']{0,200}["\'][^>]{0,200}>\s*Deutsche Version\s*</a>[ \t]*\n?',
        re.IGNORECASE
    )
    for line in lines:
        new_line, c = pattern.subn('', line)
        count += c
        if new_line.strip():  # Keep line if it has remaining content
            out.append(new_line)
        elif c == 0:  # No change made - keep original
            out.append(line)
        # If change made AND line is now empty/whitespace - skip it
    return out, count


# ================================================================
# PATTERN F: Author-box trailing middot + Deutsche Version
# ================================================================
# &middot; <a href="...">Deutsche Version</a>  at end of author p tag

def remove_author_box_deutsche_version(lines: list[str]) -> tuple[list[str], int]:
    """Remove trailing Deutsche Version links in author boxes."""
    out = []
    count = 0
    pattern = re.compile(
        r'(?:&middot;|·|\s*&middot;\s*)\s*<a[^>]+href=["\']https://mbcapitalstrategies\.com[^"\']{0,200}["\'][^>]{0,200}>\s*Deutsche Version\s*</a>',
        re.IGNORECASE
    )
    for line in lines:
        new_line, c = pattern.subn('', line)
        count += c
        out.append(new_line)
    return out, count


# ================================================================
# PATTERN G/H: "English companion to the original German site"
# ================================================================

def remove_english_companion_phrases(lines: list[str]) -> tuple[list[str], int]:
    """Remove English companion phrases."""
    out = []
    count = 0

    # Pattern G: copyright line with embedded companion phrase
    # © 2026 MB Capital Strategies Global. English companion to the original German site <a>...</a>.
    copyright_pattern = re.compile(
        r'(?:©|&copy;)\s*\d{4}\s+MB Capital Strategies[^.]{0,150}\.\s*'
        r'English companion to the original German site\s*(?:<a[^>]{0,200}>[^<]{0,100}</a>\.?)?\s*',
        re.IGNORECASE
    )

    # Pattern H: standalone English companion p tags
    companion_p_pattern = re.compile(
        r'[ \t]*<p[^>]{0,300}>\s*English companion to the original German site[^<]{0,300}'
        r'(?:<[^>]{0,200}>[^<]{0,200}</[^>]{0,50}>)*[^<]{0,100}</p>[ \t]*',
        re.IGNORECASE
    )

    # Pattern I: within a <p> that has copyright + companion (footer-bottom style)
    companion_in_p_pattern = re.compile(
        r'\.\s*English companion to the original German site\s*(?:<a[^>]{0,200}>[^<]{0,200}</a>\.?)?\s*(?=</p>)',
        re.IGNORECASE
    )

    for line in lines:
        # Try copyright replacement first (keeps the © ... part)
        new_line = copyright_pattern.sub(
            lambda m: m.group(0)[:m.group(0).find('English')].rstrip('. ') + '.',
            line
        )
        if new_line != line:
            count += 1
            out.append(new_line)
            continue

        # Try standalone companion p
        new_line, c = companion_p_pattern.subn('', line)
        if c > 0:
            count += c
            if new_line.strip():
                out.append(new_line)
            continue

        # Try inline companion phrase
        new_line, c = companion_in_p_pattern.subn('.', line)
        if c > 0:
            count += c
            out.append(new_line)
            continue

        out.append(line)
    return out, count


# ================================================================
# PATTERN I: Nav lang-flag
# ================================================================

def remove_nav_lang_flag(lines: list[str]) -> tuple[list[str], int]:
    """Remove <a class="lang-flag" title="Deutsche Version">...</a>"""
    out = []
    count = 0
    pattern = re.compile(
        r'[ \t]*<a[^>]+(?:class=["\']lang-flag["\'][^>]+title=["\']Deutsche Version["\']|title=["\']Deutsche Version["\'][^>]+class=["\']lang-flag["\'])[^>]{0,100}>.*?</a>',
        re.IGNORECASE | re.DOTALL
    )
    for line in lines:
        new_line, c = pattern.subn('', line)
        count += c
        if new_line.strip() or c == 0:
            out.append(new_line)
    return out, count


# ================================================================
# hreflang helpers
# ================================================================

def has_hreflang_de(html: str) -> bool:
    head_m = re.search(r'<head[^>]*>(.*?)</head>', html, re.DOTALL | re.IGNORECASE)
    if not head_m:
        return False
    return bool(re.search(r'hreflang=["\']de["\']', head_m.group(1), re.IGNORECASE))


def extract_de_url(html: str) -> str | None:
    for m in re.finditer(
        r'href=["\']https://mbcapitalstrategies\.com/([^"\'?#\s]+)["\']',
        html, re.IGNORECASE
    ):
        path = m.group(1).strip('/')
        if path:
            return 'https://mbcapitalstrategies.com/' + path
    return None


# ================================================================
# Main file processor
# ================================================================

def process_file(filepath: Path, dry_run: bool = False) -> dict:
    try:
        html = filepath.read_text(encoding='utf-8', errors='replace')
    except Exception as e:
        return {'file': str(filepath.relative_to(EN_ROOT)), 'error': str(e), 'changed': False}

    # Quick pre-check
    MARKER_STRINGS = [
        'Deutsche Version', 'auf Deutsch lesen', 'Auf Deutsch lesen',
        'English companion to the original German site',
        'Diesen Artikel auf Deutsch', 'lang-flag',
    ]
    if not any(m in html for m in MARKER_STRINGS):
        return {'file': str(filepath.relative_to(EN_ROOT)), 'changed': False, 'removals': 0}

    original = html
    had_hreflang = has_hreflang_de(html)
    de_url = extract_de_url(html)
    total_removals = 0
    hreflang_injected = False

    lines = html.split('\n')

    # Apply patterns in order
    lines, c = remove_aside_cross_language(lines); total_removals += c
    lines, c = remove_companion_div_blocks(lines); total_removals += c
    lines, c = remove_inline_p_companion(lines); total_removals += c
    lines, c = remove_flag_multiline_blocks(lines); total_removals += c
    lines, c = remove_flag_emoji_lines(lines); total_removals += c
    lines, c = remove_footer_deutsche_version_anchor(lines); total_removals += c
    lines, c = remove_author_box_deutsche_version(lines); total_removals += c
    lines, c = remove_english_companion_phrases(lines); total_removals += c
    lines, c = remove_nav_lang_flag(lines); total_removals += c

    html = '\n'.join(lines)

    # Clean up multiple blank lines
    html = re.sub(r'\n{3,}', '\n\n', html)

    # hreflang injection if was missing
    if not had_hreflang:
        rel_path = str(filepath.relative_to(EN_ROOT)).replace('\\', '/')
        en_url = f'https://mbcapitalstrategiesgloabal.com/{rel_path}'
        de_href = de_url or 'https://mbcapitalstrategies.com/'
        inject = (
            f'    <link rel="alternate" hreflang="de" href="{de_href}">\n'
            f'    <link rel="alternate" hreflang="en" href="{en_url}">\n'
            f'    <link rel="alternate" hreflang="x-default" href="{en_url}">'
        )
        new_html = re.sub(r'(</head>)', inject + '\n' + r'\1', html, count=1, flags=re.IGNORECASE)
        if new_html != html:
            html = new_html
            hreflang_injected = True

    changed = html != original

    if changed and not dry_run:
        filepath.write_text(html, encoding='utf-8')

    return {
        'file': str(filepath.relative_to(EN_ROOT)),
        'changed': changed,
        'removals': total_removals,
        'hreflang_injected': hreflang_injected,
        'had_hreflang_before': had_hreflang,
    }


def main():
    dry_run = '--dry-run' in sys.argv

    if dry_run:
        print("DRY RUN MODE — no files will be modified\n")

    html_files = sorted(EN_ROOT.rglob('*.html'))
    print(f"Scanning {len(html_files)} HTML files in {EN_ROOT}\n", flush=True)

    results = []
    for i, f in enumerate(html_files):
        if any(part.startswith('.') for part in f.parts):
            continue
        result = process_file(f, dry_run=dry_run)
        results.append(result)
        if (i + 1) % 50 == 0:
            print(f"  ... processed {i+1} files", flush=True)

    changed = [r for r in results if r.get('changed')]
    errors = [r for r in results if r.get('error')]
    hreflang_injected_list = [r for r in changed if r.get('hreflang_injected')]

    print(f"\nFiles scanned:        {len(results)}")
    print(f"Files changed:        {len(changed)}")
    print(f"Errors:               {len(errors)}")
    print(f"hreflang injected:    {len(hreflang_injected_list)}")
    print()

    print("--- Changed files ---")
    for r in sorted(changed, key=lambda x: x['file']):
        hi = " [hreflang-injected]" if r.get('hreflang_injected') else ""
        print(f"  {r['file']} ({r['removals']} removals){hi}")

    if errors:
        print()
        print("--- Errors ---")
        for r in errors:
            print(f"  {r['file']}: {r['error']}")

    return len(changed), len(errors)


if __name__ == '__main__':
    changed, errors = main()
    sys.exit(0 if errors == 0 else 1)

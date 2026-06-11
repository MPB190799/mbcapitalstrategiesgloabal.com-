#!/usr/bin/env python3
"""
Fix: Revert incorrectly-converted videoseries/playlist yt-lite back to iframes.
Also fix the duplicate content issue created by the previous script.

web-design-agent 2026-06-11
"""
import os
import re
import glob

BLOG_DIR = "/home/mbcap/websites/EN-Seite/blog"

# Pattern for the broken videoseries yt-lite div (with deduplication issue)
# Matches the yt-lite block with data-id="videoseries" including any duplicate trailing content
BROKEN_PATTERN = re.compile(
    r'<div class="yt-lite" data-id="videoseries"[^>]*>.*?'
    r'(?:data-id="videoseries"[^>]*>.*?)?'  # possible duplicate
    r'</div>(?:\s*</div>)?'
    r'(?:ideoseries/hqdefault\.jpg[^>]*>.*?</div>\s*</div>)?',  # cleanup trailing dupe
    re.DOTALL
)

# What the original playlist iframe looked like (approximate - we need to restore it)
# Original: <iframe loading="lazy" width="100%" height="380"
#           src="https://www.youtube.com/embed/videoseries?list=PLb7T0VuyV9dei7BFRgzB7nRBy4ZYCAl6Q"
#           title="..." allowfullscreen></iframe>

PLAYLIST_IFRAME = '''<iframe loading="lazy" width="100%" height="380"
src="https://www.youtube.com/embed/videoseries?list=PLb7T0VuyV9dei7BFRgzB7nRBy4ZYCAl6Q"
title="MB Capital Strategies — komplette Playlist" allowfullscreen
style="border-radius:12px;border:1px solid #d4af37;"></iframe>'''


def fix_file(filepath):
    """Fix broken videoseries yt-lite conversions in a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'data-id="videoseries"' not in content:
        return False, "no videoseries issue"

    # More targeted approach: find and replace the broken videoseries yt-lite block
    # The pattern is complex due to duplicates, so let's use a string search approach

    original = content

    # Strategy: find all yt-lite blocks with data-id="videoseries" and replace with iframe
    # Use a simpler regex that matches from <div class="yt-lite" data-id="videoseries" to </div>

    # First, let's handle the complex duplicate case
    # The duplicate looks like:
    # <div class="yt-lite" data-id="videoseries" ...>
    #   <img ...>
    #   <div class="yt-play">...</div>
    #   <div class="yt-label">...</div>
    # </div>ideoseries/hqdefault.jpg..." ...>
    #   <div class="yt-play">...</div>
    #   <div class="yt-label">...</div>
    # </div>

    # Clean approach: remove any yt-lite div where data-id="videoseries"
    # and replace with the proper iframe

    # Step 1: Remove the malformed duplicate suffix first
    # Pattern: </div>ideoseries/... to the next </div>
    content = re.sub(
        r'</div>ideoseries/hqdefault\.jpg[^>]*>.*?</div>\s*</div>',
        '</div>',
        content,
        flags=re.DOTALL
    )

    # Step 2: Now replace clean yt-lite[data-id="videoseries"] with iframe
    # Extract title from the yt-lite label div
    def replace_videoseries_ytlite(m):
        block = m.group(0)
        # Extract title from data-title attribute
        title_match = re.search(r'data-title="([^"]*)"', block)
        title = title_match.group(1) if title_match else "MB Capital Strategies — Playlist"
        # Extract list ID from ... we don't have it anymore, use default
        list_id = "PLb7T0VuyV9dei7BFRgzB7nRBy4ZYCAl6Q"
        return (
            f'<iframe loading="lazy" width="100%" height="380" '
            f'src="https://www.youtube.com/embed/videoseries?list={list_id}" '
            f'title="{title}" allowfullscreen '
            f'style="border-radius:12px;border:1px solid #d4af37;"></iframe>'
        )

    content = re.sub(
        r'<div class="yt-lite" data-id="videoseries"[^>]*>.*?</div>',
        replace_videoseries_ytlite,
        content,
        flags=re.DOTALL
    )

    if content == original:
        return False, "no changes made"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return True, "fixed videoseries iframe"


def main():
    html_files = glob.glob(os.path.join(BLOG_DIR, "*.html"))
    fixed_count = 0
    errors = []

    for filepath in sorted(html_files):
        try:
            fixed, reason = fix_file(filepath)
            fname = os.path.basename(filepath)
            if fixed:
                fixed_count += 1
                print(f"  FIXED: {fname}")
        except Exception as e:
            errors.append((filepath, str(e)))
            print(f"  ERROR: {os.path.basename(filepath)} — {e}")

    print(f"\nFixed {fixed_count} files, {len(errors)} errors")
    if errors:
        for fp, err in errors:
            print(f"  {fp}: {err}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Batch YouTube lite facade conversion for DE-Site blog pages.
Converts YouTube iframes (except playlists/videoseries) to yt-lite click-to-load divs.
Also adds:
  - Inline critical CSS in <head> if missing
  - LCP image preload for the YT thumbnail
  - Font preload for Outfit woff2
  - yt-lite JS init in <body> if missing

web-design-agent 2026-06-11 — P0 LCP fix, batch 167
"""
import os
import re
import glob

BLOG_DIR = "/home/mbcap/websites/EN-Seite/blog"

CRITICAL_CSS = '''<!-- LCP-Critical-CSS: Inline Above-the-Fold styles (web-design-agent batch-167, LCP fix) -->
<style>
:root{--gold:#d4af37;--bg:#050508;--bg-soft:#0c0e16;--text:#f0f1f5;--text-muted:#9aa0b8;--radius:16px}
*,*::before,*::after{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--text);font-family:'Outfit',system-ui,sans-serif;line-height:1.7;overflow-x:hidden}
h1{font-size:clamp(1.8rem,4.5vw,2.8rem);font-weight:800;color:var(--gold);margin:0 0 18px;line-height:1.1;letter-spacing:-0.02em}
.nav,header.header{position:sticky;top:0;z-index:100;background:rgba(5,5,8,0.94);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border-bottom:1px solid rgba(212,175,55,0.1)}
.nav-inner{max-width:1200px;margin:0 auto;padding:0 20px;display:flex;align-items:center;justify-content:space-between;height:60px}
.nav-brand{display:flex;align-items:center;gap:10px;text-decoration:none}
.nav-brand span{color:var(--gold);font-weight:700;font-size:.9rem;letter-spacing:.02em;white-space:nowrap}
.nav-hamburger{display:none;flex-direction:column;gap:4px;background:none;border:none;cursor:pointer;padding:4px}
.nav-hamburger span{display:block;width:20px;height:2px;background:var(--gold);border-radius:2px}
.container,.page-wrapper{max-width:1000px;margin:0 auto;padding:0 24px 80px}
.breadcrumbs{max-width:940px;margin:16px auto 0;padding:0 20px;font-size:.82em;color:var(--text-muted)}
.breadcrumbs a{color:var(--text-muted);text-decoration:none}
@media(max-width:768px){.nav-links{display:none}.nav-hamburger{display:flex}h1{font-size:1.6rem}}
</style>'''

FONT_PRELOAD = '<link rel="preload" as="font" type="font/woff2" href="https://fonts.gstatic.com/s/outfit/v15/QGYvz_MVcBeNP4NJuktqQ4E.woff2" crossorigin="anonymous">'

YT_LITE_JS = '''<!-- YouTube Lite Facade Init (web-design-agent batch-167) -->
<script>
(function(){
  function initYtLite(el){
    el.addEventListener('click',function activate(){
      el.removeEventListener('click',activate);
      var id=el.dataset.id;
      if(!id)return;
      var iframe=document.createElement('iframe');
      iframe.src='https://www.youtube.com/embed/'+id+'?autoplay=1&rel=0';
      iframe.title=el.dataset.title||'YouTube Video';
      iframe.allow='autoplay;encrypted-media;picture-in-picture';
      iframe.allowFullscreen=true;
      el.innerHTML='';
      el.appendChild(iframe);
      el.style.cursor='default';
    });
    el.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){el.click();}});
  }
  document.querySelectorAll('.yt-lite[data-id]').forEach(initYtLite);
})();
</script>'''


def extract_yt_id(src):
    """Extract YouTube video ID from embed URL."""
    m = re.search(r'youtube\.com/embed/([A-Za-z0-9_\-]{11})', src)
    if m:
        return m.group(1)
    return None


def convert_iframe_to_ytlite(iframe_html, video_id, title):
    """Convert an iframe HTML block to yt-lite div."""
    safe_title = title.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
    return (
        f'<div class="yt-lite" data-id="{video_id}" '
        f'data-title="{safe_title}" role="button" tabindex="0" '
        f'aria-label="Video abspielen: {safe_title}">\n'
        f'    <img class="yt-thumb" src="https://img.youtube.com/vi/{video_id}/hqdefault.jpg" '
        f'alt="{safe_title} Thumbnail" width="480" height="360" loading="lazy" decoding="async">\n'
        f'    <div class="yt-play" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></div>\n'
        f'    <div class="yt-label">{safe_title}</div>\n'
        f'</div>'
    )


def process_file(filepath):
    """Process a single HTML file. Returns (modified, reason) tuple."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip if already fully optimized (has yt-lite AND critical CSS)
    has_ytlite = 'class="yt-lite"' in content
    has_critical_css = 'batch-16' in content or 'LCP-Critical-CSS' in content

    # Check if there are any YouTube embed iframes to convert
    # Exclude videoseries/playlist iframes - those stay as iframes
    iframe_matches = list(re.finditer(
        r'(?s)(<div[^>]*class="video-wrapper"[^>]*>)?\s*'
        r'<iframe[^>]*src="https://www\.youtube\.com/embed/([A-Za-z0-9_\-]{11})[^"]*"'
        r'[^>]*(?:title="([^"]*)")?[^>]*(?:loading="lazy")?[^>]*>\s*</iframe>\s*'
        r'(?:</div>)?',
        content
    ))

    # Also match simple iframes without video-wrapper
    direct_matches = list(re.finditer(
        r'(?s)<iframe[^>]*src="https://www\.youtube\.com/embed/([A-Za-z0-9_\-]{11})[^"]*"'
        r'[^>]*(?:title="([^"]*)")?[^>]*>\s*</iframe>',
        content
    ))

    all_matches = iframe_matches + direct_matches
    if not all_matches and has_ytlite and has_critical_css:
        return False, "already optimized"

    if not all_matches:
        return False, "no youtube iframes to convert"

    modified = content
    first_video_id = None
    conversions = 0

    # Process in reverse order to preserve positions
    all_matches_sorted = sorted(set([(m.start(), m.end(), m.group()) for m in all_matches]),
                                 key=lambda x: x[0], reverse=True)

    for start, end, match_text in all_matches_sorted:
        video_id = extract_yt_id(match_text)
        if not video_id:
            continue

        # Skip if already in yt-lite context
        context_before = modified[max(0, start-100):start]
        if 'yt-lite' in context_before:
            continue

        # Extract title from iframe
        title_match = re.search(r'title="([^"]*)"', match_text)
        title = title_match.group(1) if title_match else f'Video {video_id}'

        yt_lite_html = convert_iframe_to_ytlite(match_text, video_id, title)
        modified = modified[:start] + yt_lite_html + modified[end:]
        conversions += 1

        if first_video_id is None:
            first_video_id = video_id

    if conversions == 0:
        return False, "no conversions made"

    # Add critical CSS if missing
    if not has_critical_css and CRITICAL_CSS not in modified:
        # Insert before </head> or before first <link rel="preconnect">
        if '<link rel="preconnect"' in modified:
            modified = modified.replace(
                '<link rel="preconnect"',
                CRITICAL_CSS + '\n<link rel="preconnect"',
                1
            )
        elif '</head>' in modified:
            modified = modified.replace('</head>', CRITICAL_CSS + '\n</head>', 1)

    # Add font preload if missing
    if FONT_PRELOAD not in modified and 'fonts.gstatic.com/s/outfit' not in modified:
        if '</head>' in modified:
            modified = modified.replace('</head>', FONT_PRELOAD + '\n</head>', 1)

    # Add LCP image preload for first video thumbnail if missing
    if first_video_id and f'img.youtube.com/vi/{first_video_id}/hqdefault.jpg' not in modified:
        preload_img = f'<!-- Preload LCP image: YT thumbnail above-fold (web-design-agent batch-167) -->\n<link rel="preload" as="image" href="https://img.youtube.com/vi/{first_video_id}/hqdefault.jpg" fetchpriority="high">'
        if '</head>' in modified:
            modified = modified.replace('</head>', preload_img + '\n</head>', 1)

    # Add yt-lite JS init if missing
    if 'initYtLite' not in modified and YT_LITE_JS not in modified:
        if '</body>' in modified:
            modified = modified.replace('</body>', YT_LITE_JS + '\n</body>', 1)

    if modified == content:
        return False, "no changes"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(modified)

    return True, f"converted {conversions} iframes, first_id={first_video_id}"


def main():
    html_files = glob.glob(os.path.join(BLOG_DIR, "*.html"))
    total = len(html_files)
    modified_count = 0
    skipped_count = 0
    errors = []

    print(f"Processing {total} HTML files in {BLOG_DIR}...")

    for filepath in sorted(html_files):
        try:
            modified, reason = process_file(filepath)
            fname = os.path.basename(filepath)
            if modified:
                modified_count += 1
                print(f"  UPDATED: {fname} — {reason}")
            else:
                skipped_count += 1
                # Only print skips for non-trivial reasons
                if "no youtube" not in reason and "already opt" not in reason:
                    print(f"  skip: {fname} — {reason}")
        except Exception as e:
            errors.append((filepath, str(e)))
            print(f"  ERROR: {filepath} — {e}")

    print(f"\nDone: {modified_count} modified, {skipped_count} skipped, {len(errors)} errors")
    if errors:
        print("Errors:")
        for fp, err in errors:
            print(f"  {fp}: {err}")

    return modified_count


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Surgical, byte-preserving removal of all newsletter UI from the EN site.
Removes only the targeted spans; everything else stays byte-identical."""
import re, sys, os, glob

APPLY = "--apply" in sys.argv

# Container blocks: (inner tag for nesting, opener regex). Opener may be a well-formed
# <div...> OR a pre-existing broken orphan (`class="mb-newsletter-cta" ...>` without <div).
BALANCED = [
    ("div",     re.compile(r'(?:<div\b[^>]*\bclass="[^"]*mb-newsletter-cta[^"]*"[^>]*>|^[ \t]*class="mb-newsletter-cta"[^>]*>)', re.I | re.M)),
    ("div",     re.compile(r'(?:<div\b[^>]*\bclass="[^"]*mb-newsletter-wrap[^"]*"[^>]*>|^[ \t]*class="mb-newsletter-wrap"[^>]*>)', re.I | re.M)),
    ("section", re.compile(r'<section\b[^>]*\bid="newsletter"[^>]*>', re.I)),
    ("div",     re.compile(r'<div\b[^>]*\bid="hero-inline-cta-en"[^>]*>', re.I)),
    ("div",     re.compile(r'<div\b[^>]*\bid="mb-sticky-cta"[^>]*>', re.I)),
]

def remove_balanced(html, tag, opener):
    """Remove every element matched by `opener`, balancing nesting of <tag>.

    Two opener shapes:
      * well-formed `<div ...>`  -> consume through its matching </tag> (inclusive).
      * broken orphan `class="..."...>` (the literal `<div` is missing in the source)
        -> the trailing </tag> after the block is load-bearing (closes a real parent
        opened elsewhere), so remove only the orphan line + its self-balanced inner
        children and KEEP that trailing close, leaving div-balance unchanged.
    """
    n_removed = 0
    token = re.compile(r'<(/?)' + tag + r'\b[^>]*>', re.IGNORECASE)
    while True:
        m0 = opener.search(html)
        if m0 is None:
            break
        start = m0.start()
        real = html[start] == '<'        # real opening tag vs orphan
        end = None
        if real:
            depth = 1
            for m in token.finditer(html, m0.end()):
                depth += -1 if m.group(1) else 1
                if depth == 0:
                    end = m.end(); break
        else:
            depth = 0
            for m in token.finditer(html, m0.end()):
                if m.group(1):           # closing </tag>
                    if depth == 0:       # load-bearing parent close -> stop before it
                        end = m.start(); break
                    depth -= 1
                else:
                    depth += 1
        if end is None:
            raise RuntimeError(f"unbalanced for opener {opener.pattern[:40]!r}")
        html = html[:start] + html[end:]
        n_removed += 1
    return html, n_removed

# Inline anchors whose href contains "newsletter" (nav "Free PDF", inline "Subscribe Newsletter", footer)
ANCHOR = re.compile(r'<a\b[^>]*href="[^"]*newsletter[^"]*"[^>]*>.*?</a>', re.IGNORECASE | re.DOTALL)
# <script> blocks that define a subscribe handler or hit the subscribe worker
SCRIPT = re.compile(r'<script\b[^>]*>(?:(?!</script>).)*?'
                    r'(?:mbHeroSubscribe|mbMidSubscribe|mbContactSubscribe|mbStickySubscribe|'
                    r'\bmbSubscribe\w*|SUBSCRIBE_URL|mb-newsletter-subscribe\.mbcapitalstrategies|'
                    r'sibforms\.com/serve)'
                    r'(?:(?!</script>).)*?</script>\s*', re.IGNORECASE | re.DOTALL)
# Orphan newsletter delimiter/section comments
COMMENTS = [
    re.compile(r'<!--\s*=*\s*MB CAPITAL INSIDER NEWSLETTER\s*=*\s*-->\s*', re.IGNORECASE),
    re.compile(r'<!--\s*=*\s*END NEWSLETTER\s*=*\s*-->\s*', re.IGNORECASE),
    re.compile(r'<!--[^>]*?Newsletter CTA[^>]*?-->\s*', re.IGNORECASE),
    re.compile(r'<!--\s*MB Capital Insider\b[^>]*?-->\s*', re.IGNORECASE),
    re.compile(r'<!--\s*NEWSLETTER\s*-->\s*', re.IGNORECASE),
    re.compile(r'<!--\s*Sticky Newsletter Bar\s*-->\s*', re.IGNORECASE),
]
# Stray content <li> mentioning the newsletter (e.g. about page channel list)
LI_NEWSLETTER = re.compile(r'<li\b[^>]*>(?:(?!</li>).)*?MB Capital Insider(?:(?!</li>).)*?</li>\s*',
                           re.IGNORECASE | re.DOTALL)

def process(html):
    stats = {}
    for tag, opener in BALANCED:
        html, n = remove_balanced(html, tag, opener)
        if n: stats[opener.pattern[:22]] = n
    html, n = ANCHOR.subn('', html);  stats['anchor'] = n if n else stats.get('anchor',0)
    html, n = SCRIPT.subn('', html);  stats['script'] = n if n else stats.get('script',0)
    html, n = LI_NEWSLETTER.subn('', html); stats['li'] = n if n else 0
    c = 0
    for rx in COMMENTS:
        html, k = rx.subn('', html); c += k
    html = html.replace('<!-- AdSense: between newsletter and FAQ -->', '<!-- AdSense: before FAQ -->')
    stats['comment'] = c
    return html, {k:v for k,v in stats.items() if v}

files = []
for d in ("blog", "glossary", "pages", "tools"):
    files += sorted(glob.glob(os.path.join(d, "*.html")))
files += ["index.html"]

changed = 0
totals = {}
for fp in files:
    with open(fp, encoding="utf-8") as f:
        orig = f.read()
    new, stats = process(orig)
    if new != orig:
        changed += 1
        for k,v in stats.items():
            totals[k] = totals.get(k,0)+v
        if APPLY:
            with open(fp, "w", encoding="utf-8") as f:
                f.write(new)

print(f"{'APPLIED' if APPLY else 'DRY-RUN'}: {changed}/{len(files)} files changed")
print("removed element totals:", totals)

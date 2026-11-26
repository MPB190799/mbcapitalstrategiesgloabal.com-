"""
Fix EN site SEO issues:
1. Add hreflang tags to sitemap-blog.xml and sitemap-tools.xml
2. Fix x-default hreflang in all EN HTML files to point to EN site
"""

import os
import re
import glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EN_DOMAIN = "https://mbcapitalstrategiesglobal.com"
DE_DOMAIN = "https://mbcapitalstrategies.com"


def get_hreflang_de_from_html(html_path):
    """Extract the hreflang de URL from an HTML file."""
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r'<link\s+rel="alternate"\s+hreflang="de"\s+href="([^"]+)"', content)
    if match:
        return match.group(1)
    return None


def get_en_url_from_html(html_path):
    """Extract the hreflang en URL from an HTML file."""
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r'<link\s+rel="alternate"\s+hreflang="en"\s+href="([^"]+)"', content)
    if match:
        return match.group(1)
    return None


def build_hreflang_map(subdir):
    """Build a map of EN URL -> DE URL from HTML files in a subdirectory."""
    hreflang_map = {}
    html_dir = os.path.join(BASE_DIR, subdir)
    if not os.path.isdir(html_dir):
        print(f"  Warning: directory {html_dir} not found")
        return hreflang_map
    for html_file in glob.glob(os.path.join(html_dir, "*.html")):
        filename = os.path.basename(html_file)
        en_url = f"{EN_DOMAIN}/{subdir}/{filename}"
        de_url = get_hreflang_de_from_html(html_file)
        hreflang_map[en_url] = de_url
    return hreflang_map


def fix_sitemap_with_hreflang(sitemap_filename, subdir):
    """Add hreflang tags to a sitemap XML file."""
    sitemap_path = os.path.join(BASE_DIR, sitemap_filename)
    print(f"\n--- Fixing {sitemap_filename} ---")

    with open(sitemap_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Build hreflang map from HTML files
    hreflang_map = build_hreflang_map(subdir)
    print(f"  Found {len(hreflang_map)} HTML files with hreflang data in {subdir}/")

    # Add xmlns:xhtml namespace to urlset tag
    content = content.replace(
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n        xmlns:xhtml="http://www.w3.org/1999/xhtml">'
    )

    # For each <url> block, add hreflang links before </url>
    def add_hreflang(match):
        url_block = match.group(0)
        loc_match = re.search(r"<loc>([^<]+)</loc>", url_block)
        if not loc_match:
            return url_block
        loc_url = loc_match.group(1)

        # Build hreflang lines
        en_href = loc_url
        de_href = hreflang_map.get(loc_url)

        hreflang_lines = f'    <xhtml:link rel="alternate" hreflang="en" href="{en_href}"/>'
        if de_href:
            hreflang_lines += f'\n    <xhtml:link rel="alternate" hreflang="de" href="{de_href}"/>'

        # Insert before </url>
        url_block = url_block.replace("  </url>", f"{hreflang_lines}\n  </url>")
        return url_block

    content = re.sub(r"<url>.*?</url>", add_hreflang, content, flags=re.DOTALL)

    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  Done: {sitemap_filename} updated with hreflang tags")


def fix_xdefault_hreflang():
    """Fix x-default hreflang in all EN HTML files to point to EN site."""
    print("\n--- Fixing x-default hreflang in EN HTML files ---")
    count = 0
    # Find all HTML files recursively
    for html_file in glob.glob(os.path.join(BASE_DIR, "**", "*.html"), recursive=True):
        with open(html_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Check if file has x-default pointing to DE site
        pattern = r'(<link\s+rel="alternate"\s+hreflang="x-default"\s+href=")https://mbcapitalstrategies\.com/([^"]*")'
        if re.search(pattern, content):
            # Get the EN URL from the same file
            en_match = re.search(r'<link\s+rel="alternate"\s+hreflang="en"\s+href="([^"]+)"', content)
            if en_match:
                en_url = en_match.group(1)
                # Replace x-default href with the EN URL
                new_content = re.sub(
                    r'(<link\s+rel="alternate"\s+hreflang="x-default"\s+href=")[^"]+(")',
                    f'\\1{en_url}\\2',
                    content
                )
                if new_content != content:
                    with open(html_file, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    rel_path = os.path.relpath(html_file, BASE_DIR)
                    count += 1

    print(f"  Fixed x-default hreflang in {count} HTML files")


if __name__ == "__main__":
    # Task 1: Fix sitemaps
    fix_sitemap_with_hreflang("sitemap-blog.xml", "blog")
    fix_sitemap_with_hreflang("sitemap-tools.xml", "tools")

    # Task 2: Fix x-default hreflang
    fix_xdefault_hreflang()

    print("\nAll done!")

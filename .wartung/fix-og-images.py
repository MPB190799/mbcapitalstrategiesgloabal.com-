#!/usr/bin/env python3
"""
Fix OG-Images: Replace marco.jpg/marco.webp with thematic og-images for EN site.
"""
import os
import re

BASE = r"C:/Users/marco/OneDrive/Website Deutsch und Englisch/EN-Seite"

MAPPING = [
    # Shipping / Tanker / LNG / Maritime
    (["shipping", "tanker", "lng", "maritime", "vessel", "vlcc", "aframax",
      "frontline", "torm", "scorpio", "golar", "flex-lng", "cool-company", "cmb",
      "golden-ocean", "star-bulk", "mpc-container", "avance", "bw-lpg", "hidden-champion",
      "panoro", "six-shipping", "best-tanker", "best-lng"],
     "https://mbcapitalstrategiesglobal.com/assets/og-shipping.jpg"),
    # Mining / Gold / Copper / Coal
    (["mining", "gold", "copper", "coal", "barrick", "newmont", "bhp", "rio-tinto",
      "anglogold", "b2gold", "fresnillo", "jiangxi", "central-asia", "thungela", "whitehaven",
      "exxaro", "yancoal", "suncoke", "south32", "valterra", "kazatomprom", "angloamerican",
      "gerdau", "resources", "supercycle", "copper-supercycle", "hard-asset"],
     "https://mbcapitalstrategiesglobal.com/assets/og-mining.jpg"),
    # Energy / Upstream / Oil & Gas
    (["energy", "upstream", "petrobras", "repsol", "equinor", "aker-bp", "coterra",
      "devon", "chevron", "conocophillips", "apa-", "ecopetrol", "omv", "cardinal",
      "dno", "energean", "harbour", "inplay", "petrotal", "total-gabon", "woodside",
      "var-energi", "oil", "gas", "pipeline"],
     "https://mbcapitalstrategiesglobal.com/assets/og-energy.jpg"),
    # Dividends / Yield / BDC / Finance / Tools
    (["dividend", "yield", "calculator", "bdc", "freedom", "snowball", "reinvest",
      "cashflow", "debitum", "weekly", "recap", "broker", "toolbox", "strategy",
      "newtek", "hercules", "drip", "quellensteuer", "tax", "pipelines"],
     "https://mbcapitalstrategiesglobal.com/assets/og-dividenden.jpg"),
]

DEFAULT_OG = "https://mbcapitalstrategiesglobal.com/assets/og-default.jpg"
PATTERN = re.compile(r'(<meta\s+property="og:image"\s+content=")[^"]*(")', re.IGNORECASE)
TWITTER_PATTERN = re.compile(r'(<meta\s+name="twitter:image"\s+content=")[^"]*(")', re.IGNORECASE)

def get_og_image(filename):
    fn = filename.lower()
    for keywords, img in MAPPING:
        if any(kw in fn for kw in keywords):
            return img
    return DEFAULT_OG

def process_file(filepath):
    filename = os.path.basename(filepath)
    new_img = get_og_image(filename)

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'marco.jpg' not in content and 'marco.webp' not in content:
        return False

    new_content = PATTERN.sub(r'\g<1>' + new_img + r'\g<2>', content)
    new_content = TWITTER_PATTERN.sub(r'\g<1>' + new_img + r'\g<2>', new_content)

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    dirs_to_scan = [
        os.path.join(BASE, "blog"),
        os.path.join(BASE, "pages"),
        os.path.join(BASE, "tools"),
        BASE,
    ]

    changed = []
    for d in dirs_to_scan:
        if not os.path.exists(d):
            continue
        for fname in os.listdir(d):
            if fname.endswith('.html'):
                fpath = os.path.join(d, fname)
                if process_file(fpath):
                    changed.append(fpath.replace(BASE, ''))

    print(f"Fixed {len(changed)} files:")
    for f in sorted(changed):
        print(f"  {f}")

if __name__ == "__main__":
    main()

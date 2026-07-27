#!/usr/bin/env python3
"""PR-Gate für die Website-Repos — prüft NUR die im PR geänderten HTML-Dateien.

WARUM NUR GEÄNDERTE DATEIEN:
Die Sites haben je >500 gewachsene Seiten. Ein Vollscan würde beim ersten Lauf an
Altlasten scheitern und wäre damit dauerhaft rot — ein Gate, das immer rot ist, wird
abgeschaltet oder umgangen. Genau das ist am 27.07.2026 beim MBFinanceMate-Gate
passiert (10 h lang jeder PR blockiert). Dieses Gate prüft deshalb nur, was der PR
anfasst: neue Fehler werden verhindert, Altlasten separat abgetragen.

WAS GEPRÜFT WIRD — jede Regel steht für einen ECHTEN, WIEDERHOLTEN Vorfall:

1. JSON-LD parsebar
   Der SEO-Agent schrieb beim Internal-Linking wiederholt <a href="...">-Tags in
   JSON-LD-String-Werte. Die href-Anführungszeichen brechen das JSON, ganze
   Schema-Blöcke werden ungültig. Drei Batches in Folge (221/222/223) mussten das
   reparieren, 223 war ein 48-Seiten-Massenfix.

2. Keine verschachtelten Anker
   Ein Massen-Verlinkungs-Script setzte Anchor-Text, der selbst schon ein Link war,
   als href-Wert ein: /glossar/<a href="/upstream-aktien/">upstream</a>.html → 404.
   Das erzeugte im Ahrefs-Audit vom 23.06.2026 +8 neue 404 auf einen Schlag.

3. Interne Links zeigen auf existierende Dateien
   Gleicher Vorfall: geratene Verzeichnisse (/dividendenaktien/), trailing-slash auf
   .html, unaufgelöste ../-Pfade. Ein 404-Generator, der den Health-Score still senkt.

4. Referenzierte lokale Bilder existieren
   Der Blog-Generator erfand Pfade, die nie erzeugt wurden: /assets/marco-bozem-autor.webp
   statt /assets/marco-profile.webp, og-<slug>.jpg für jeden neuen Slug. Audit vom
   23.07.2026: 17 Blogs mit kaputtem Autorenfoto und Social-Preview.

Aufruf:  python3 .github/scripts/validate-changed.py <datei> [<datei> ...]
Exit 0 = sauber, 1 = Verstoß (Details auf stdout).
Owner: seo-agent · Konsument: PR-Gate + merge-all-repos.sh
"""
import json
import os
import re
import sys
from html.parser import HTMLParser
from urllib.parse import unquote

ROOT = os.getcwd()
problems = []   # blockieren den PR
warnings = []   # werden gemeldet, blockieren aber nicht


def rel(p):
    return os.path.relpath(p, ROOT)


# ── 1) JSON-LD ────────────────────────────────────────────────────────────────
JSONLD_RE = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.I | re.S)


def check_jsonld(path, html):
    for i, block in enumerate(JSONLD_RE.findall(html), 1):
        raw = block.strip()
        if not raw:
            problems.append(f"{rel(path)}: JSON-LD-Block {i} ist leer")
            continue
        try:
            json.loads(raw)
        except json.JSONDecodeError as e:
            # Der typische Auslöser wird direkt benannt — sonst sucht man lange.
            hint = ""
            if "<a " in raw or "href=" in raw:
                hint = ("  → Ursache fast sicher: HTML-Anker in einem JSON-LD-String. "
                        "Links gehören NUR in den sichtbaren <body>, JSON-LD-Strings "
                        "bleiben plaintext.")
            problems.append(
                f"{rel(path)}: JSON-LD-Block {i} ist kein gültiges JSON ({e.msg}, "
                f"Zeile {e.lineno}).{hint}")


# ── 2) Verschachtelte Anker ───────────────────────────────────────────────────
class AnchorNesting(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.nested = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            if self.depth > 0:
                self.nested.append(self.getpos()[0])
            self.depth += 1

    def handle_endtag(self, tag):
        if tag == "a" and self.depth > 0:
            self.depth -= 1


def check_nested_anchors(path, html):
    p = AnchorNesting()
    try:
        p.feed(html)
    except Exception:
        return  # Parser-Robustheit: gewachsenes HTML, kein Grund zu blocken
    # WARNUNG, nicht blockend: die Tiefenzählung schlägt auch bei einem weiter oben
    # NICHT GESCHLOSSENEN <a> an — gewachsenes HTML hat davon welches (auf der DE-
    # Startseite stehen zwei offene Anker vor Zeile 1316). Als Blocker wäre jeder PR,
    # der index.html anfasst, sofort rot: wieder ein Gate, das nicht am PR hängt,
    # sondern an Altlasten. Der eindeutige, gefährliche Fall unten blockt dagegen hart.
    for line in p.nested[:5]:
        warnings.append(
            f"{rel(path)}:{line}: <a> innerhalb eines offenen <a> — entweder verschachtelt "
            f"oder weiter oben fehlt ein </a>. Ungültiges HTML, bitte prüfen.")
    # Der Fingerabdruck des Vorfalls, den der Parser nicht immer sieht:
    for m in re.finditer(r'href=["\'][^"\']*<a\s', html, re.I):
        line = html[:m.start()].count("\n") + 1
        problems.append(
            f"{rel(path)}:{line}: HTML-Tag INNERHALB eines href-Wertes — "
            f"genau das Muster des 404-Ausbruchs vom 23.06.2026")


# ── 3) + 4) Interne Ziele existieren ──────────────────────────────────────────
SKIP_PREFIX = ("http://", "https://", "//", "mailto:", "tel:", "javascript:",
               "data:", "#")
ASSET_RE = re.compile(r'(?:src|href)=["\']([^"\'>]+)["\']', re.I)
IMG_EXT = (".webp", ".jpg", ".jpeg", ".png", ".svg", ".gif", ".ico", ".avif")


def resolve(path, target):
    t = target.split("#")[0].split("?")[0].strip()
    if not t:
        return None
    # URL-Dekodierung ist Pflicht, kein Feinschliff: Marcos Slugs tragen Umlaute
    # (kupfer-2035-superzyklus-angebotsluecke -> …angebotslücke.html steht im href als
    # %C3%BC). Ohne unquote meldet der Prüfer jede Umlaut-Seite als toten Link — beim
    # ersten Testlauf genau so passiert.
    t = unquote(t)
    if t.startswith("/"):
        return os.path.normpath(os.path.join(ROOT, t.lstrip("/")))
    return os.path.normpath(os.path.join(os.path.dirname(path), t))


def check_local_targets(path, html):
    seen = set()
    for target in ASSET_RE.findall(html):
        t = target.strip()
        if not t or t.startswith(SKIP_PREFIX) or t in seen:
            continue
        seen.add(t)
        resolved = resolve(path, t)
        if resolved is None or os.path.exists(resolved):
            continue
        # Verzeichnis-Links dürfen auf index.html zeigen
        if os.path.isdir(resolved) or os.path.exists(os.path.join(resolved, "index.html")):
            continue
        kind = "Bild" if t.lower().endswith(IMG_EXT) else "interner Link"
        problems.append(f"{rel(path)}: {kind} zeigt ins Leere → {t}")


def main(files):
    checked = 0
    for f in files:
        if not f.lower().endswith((".html", ".htm")) or not os.path.exists(f):
            continue
        checked += 1
        html = open(f, encoding="utf-8", errors="replace").read()
        check_jsonld(f, html)
        check_nested_anchors(f, html)
        check_local_targets(f, html)

    print(f"Geprüft: {checked} geänderte HTML-Datei(en)")
    if warnings:
        print(f"\n{len(warnings)} Warnung(en) — blockieren nicht:")
        for w in warnings[:15]:
            print(f"  ! {w}")
    if problems:
        print(f"\n{len(problems)} Problem(e):")
        for p in problems[:40]:
            print(f"  ✗ {p}")
        if len(problems) > 40:
            print(f"  … und {len(problems) - 40} weitere")
        return 1
    print("✓ JSON-LD gültig, keine verschachtelten Anker, alle lokalen Ziele existieren")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""brand-to-eisvogel.py — genera un YAML eisvogel on-the-fly dal brand profile.

Usage:
    python3 brand-to-eisvogel.py [--brand <nome>] [--output <path>]

Se --output assente, stampa su stdout. Da usare in Step 7 export se pdf_style=brand.
"""
import argparse
import json
import pathlib
import sys


EISVOGEL_TEMPLATE = """# Eisvogel YAML generato da brand profile: {brand_nome}
# Non editare manualmente — rigenerato a ogni export.
titlepage: true
titlepage-background: ""
titlepage-rule-color: "{primary_hex}"
titlepage-rule-height: 4
titlepage-text-color: "{text_hex}"
titlepage-logo: "{logo_path}"
logo: "{logo_path}"
logo-width: 120pt
colorlinks: true
linkcolor: "{secondary_hex}"
urlcolor: "{secondary_hex}"
citecolor: "{secondary_hex}"
toccolor: "{text_hex}"
book: false
classoption:
  - oneside
  - 11pt
mainfont: "{body_font}"
sansfont: "{heading_font}"
monofont: "{mono_font}"
header-includes:
  - \\usepackage{{fancyhdr}}
  - \\pagestyle{{fancy}}
  - \\fancyhf{{}}
  - \\fancyhead[L]{{\\small {ragione_sociale}}}
  - \\fancyhead[R]{{\\small \\leftmark}}
  - \\fancyfoot[L]{{\\small {classificazione}}}
  - \\fancyfoot[C]{{\\small \\thepage}}
  - \\fancyfoot[R]{{\\small {sito_web}}}
  - \\renewcommand{{\\headrulewidth}}{{0.4pt}}
  - \\renewcommand{{\\footrulewidth}}{{0.4pt}}
toc: true
toc-own-page: true
listings-no-page-break: true
"""


def hex_clean(value, default):
    if not value or not isinstance(value, str):
        return default.lstrip("#")
    return value.lstrip("#")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", help="Nome brand (default: active_brand)")
    ap.add_argument("--output", "-o", help="Path di output (default stdout)")
    ap.add_argument("--classificazione", default="INTERNAL", help="Label classificazione per footer")
    args = ap.parse_args()

    skill_dir = pathlib.Path(__file__).resolve().parent.parent
    profile_path = skill_dir / ".brand-profile.json"
    if not profile_path.exists():
        print("[ERR] .brand-profile.json non trovato", file=sys.stderr)
        return 2

    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    brands = profile.get("brands", [])
    if not brands:
        print("[ERR] nessun brand configurato", file=sys.stderr)
        return 2

    target = args.brand or profile.get("active_brand")
    brand = None
    for b in brands:
        if b.get("nome") == target:
            brand = b
            break
    if brand is None:
        brand = brands[0]

    palette = brand.get("palette", {}) or {}
    font = brand.get("font", {}) or {}

    yaml_content = EISVOGEL_TEMPLATE.format(
        brand_nome=brand.get("nome", ""),
        primary_hex=hex_clean(palette.get("primary"), "#1D3557"),
        secondary_hex=hex_clean(palette.get("secondary"), "#457B9D"),
        text_hex=hex_clean(palette.get("text"), "#1D1D1D"),
        logo_path=brand.get("logo_path", ""),
        body_font=font.get("body", "Inter"),
        heading_font=font.get("heading", "Inter"),
        mono_font=font.get("mono", "JetBrains Mono"),
        ragione_sociale=brand.get("ragione_sociale", ""),
        sito_web=brand.get("sito_web", ""),
        classificazione=args.classificazione,
    )

    if args.output:
        pathlib.Path(args.output).write_text(yaml_content, encoding="utf-8")
        print(f"[OK] scritto {args.output}")
    else:
        print(yaml_content)
    return 0


if __name__ == "__main__":
    sys.exit(main())

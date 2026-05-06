#!/usr/bin/env python3
"""brand-loader.py — carica brand profile e applica preferred_terms al draft.

Modalità:
    --info [--brand <nome>]                  # stampa info brand attivo (json)
    --list                                   # lista brand disponibili
    --apply-preferred-terms <file> [--brand] # sostituisce termini generici -> aziendali
    --banned-words [--brand]                 # stampa banned_words (una per riga)
    --glossario [--brand]                    # stampa glossario k=v
"""
import argparse
import json
import pathlib
import re
import sys


def load_profile():
    skill_dir = pathlib.Path(__file__).resolve().parent.parent
    p = skill_dir / ".brand-profile.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def get_brand(profile, name=None):
    brands = profile.get("brands", []) if profile else []
    if not brands:
        return None
    if name:
        for b in brands:
            if b.get("nome") == name:
                return b
        return None
    default_name = profile.get("active_brand")
    if default_name:
        for b in brands:
            if b.get("nome") == default_name:
                return b
    return brands[0]


def apply_preferred(text, preferred):
    """Sostituisce termini generici con aziendali, case-preserving su prima lettera."""
    for generic, aziendale in preferred.items():
        if not generic or not aziendale:
            continue
        pattern = re.compile(r"\b" + re.escape(generic) + r"\b", flags=re.IGNORECASE)

        def replace(match):
            matched = match.group(0)
            if matched[0].isupper():
                return aziendale[0].upper() + aziendale[1:]
            return aziendale

        text = pattern.sub(replace, text)
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", help="Nome brand (default active_brand)")
    ap.add_argument("--info", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--banned-words", action="store_true")
    ap.add_argument("--glossario", action="store_true")
    ap.add_argument("--apply-preferred-terms", metavar="FILE")
    ap.add_argument("--in-place", action="store_true")
    args = ap.parse_args()

    profile = load_profile()
    if profile is None:
        print("[WARN] Nessun brand profile configurato (.brand-profile.json)", file=sys.stderr)
        return 2

    if args.list:
        for b in profile.get("brands", []):
            active = " (active)" if b.get("nome") == profile.get("active_brand") else ""
            print(f"  {b.get('nome')}{active} — {b.get('ragione_sociale', '')}")
        return 0

    brand = get_brand(profile, args.brand)
    if brand is None:
        print(f"[ERR] Brand non trovato: {args.brand}", file=sys.stderr)
        return 1

    if args.info:
        print(json.dumps(brand, indent=2, ensure_ascii=False))
        return 0

    if args.banned_words:
        for w in brand.get("banned_words", []):
            print(w)
        return 0

    if args.glossario:
        for k, v in (brand.get("glossario") or {}).items():
            print(f"{k}={v}")
        return 0

    if args.apply_preferred_terms:
        path = pathlib.Path(args.apply_preferred_terms)
        if not path.exists():
            print(f"[ERR] file non trovato: {path}", file=sys.stderr)
            return 2
        text = path.read_text(encoding="utf-8")
        preferred = brand.get("preferred_terms") or {}
        if not preferred:
            print("[INFO] Nessun preferred_term configurato per questo brand")
            return 0
        new_text = apply_preferred(text, preferred)
        changes = sum(1 for a, b in zip(text.split(), new_text.split()) if a != b)
        if args.in_place:
            path.write_text(new_text, encoding="utf-8")
            print(f"[OK] {changes} sostituzioni applicate in {path}")
        else:
            print(new_text)
        return 0

    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())

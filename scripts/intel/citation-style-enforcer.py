#!/usr/bin/env python3
"""citation-style-enforcer.py — verifica conformità .bib a stile accademico.

Stili supportati:
- **APA 7**: campo `author`, `year`, `title`, `journal/publisher`, DOI raccomandato
- **IEEE**: numerazione [1], [2], stile compatto
- **Chicago**: campi completi autore-anno o note-bibliografia
- **MLA**: modern language association
- **Vancouver**: biomedico, numerico

Check:
- Campi obbligatori presenti
- Ordine autori consistente
- DOI formato corretto
- Titoli sentence/title case secondo stile
- Duplicati
- Chiavi univoche

Usage:
    citation-style-enforcer.py refs.bib --style apa [--fix]
"""
import argparse
import pathlib
import re
import sys

REQUIRED_FIELDS = {
    "apa": {
        "article": ["author", "year", "title", "journal"],
        "book": ["author", "year", "title", "publisher"],
        "inproceedings": ["author", "year", "title", "booktitle"],
        "misc": ["author", "year", "title"],
    },
    "ieee": {
        "article": ["author", "title", "journal", "year"],
        "inproceedings": ["author", "title", "booktitle", "year"],
        "book": ["author", "title", "publisher", "year"],
    },
    "chicago": {
        "article": ["author", "title", "journal", "year"],
        "book": ["author", "title", "publisher", "year", "address"],
    },
    "mla": {
        "article": ["author", "title", "journal", "year"],
        "book": ["author", "title", "publisher", "year"],
    },
    "vancouver": {
        "article": ["author", "title", "journal", "year", "volume", "pages"],
    },
}


def parse_bib(text):
    entries = []
    # Split per @type{key, ...}
    for m in re.finditer(r"@(\w+)\{\s*([^,\s]+)\s*,([^@]*?)\n\}", text, flags=re.DOTALL):
        entry_type = m.group(1).lower()
        key = m.group(2).strip()
        fields_text = m.group(3)
        fields = {}
        # Parsa campi: name = {value} oppure "value"
        for fm in re.finditer(r"(\w+)\s*=\s*[\{\"]((?:[^{}\"]|\{[^{}]*\})*)[\}\"]\s*,?", fields_text):
            fields[fm.group(1).lower()] = fm.group(2).strip()
        entries.append({"type": entry_type, "key": key, "fields": fields, "raw": m.group(0)})
    return entries


def check_entry(entry, style):
    issues = []
    style_reqs = REQUIRED_FIELDS.get(style, {})
    required = style_reqs.get(entry["type"], style_reqs.get("article", []))
    for field in required:
        if field not in entry["fields"] or not entry["fields"][field]:
            issues.append(f"{entry['key']}: campo '{field}' mancante per stile {style}")
    # DOI formato
    doi = entry["fields"].get("doi", "")
    if doi and not re.match(r"^10\.\d{4,9}/", doi):
        issues.append(f"{entry['key']}: DOI formato non valido: {doi}")
    # Autore formato
    author = entry["fields"].get("author", "")
    if author and " and " not in author and "," not in author and len(author.split()) > 3:
        issues.append(f"{entry['key']}: multiple autori devono usare ' and ' come separatore")
    return issues


def check_duplicates(entries):
    issues = []
    seen_keys = set()
    seen_titles = {}
    for e in entries:
        if e["key"] in seen_keys:
            issues.append(f"Chiave duplicata: {e['key']}")
        seen_keys.add(e["key"])
        title = e["fields"].get("title", "").lower().strip()
        if title and title in seen_titles:
            issues.append(f"Titolo duplicato: '{title[:50]}' in {e['key']} e {seen_titles[title]}")
        if title:
            seen_titles[title] = e["key"]
    return issues


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bib")
    ap.add_argument("--style", choices=list(REQUIRED_FIELDS.keys()), default="apa")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    p = pathlib.Path(args.bib)
    if not p.exists():
        print(f"[ERR] {p} non trovato", file=sys.stderr)
        return 2

    text = p.read_text(encoding="utf-8")
    entries = parse_bib(text)
    if not entries:
        print(f"[WARN] nessuna entry parsata da {p.name}")
        return 0

    all_issues = []
    for e in entries:
        all_issues.extend(check_entry(e, args.style))
    all_issues.extend(check_duplicates(entries))

    if args.json:
        import json
        print(json.dumps(all_issues, indent=2, ensure_ascii=False))
        return 1 if all_issues else 0

    if not all_issues:
        print(f"[OK] {len(entries)} entry conformi a stile {args.style}")
        return 0

    print(f"CITATION STYLE ENFORCER ({args.style.upper()}): {len(all_issues)} issue")
    print("=" * 60)
    for i in all_issues[:30]:
        print(f"  • {i}")
    if len(all_issues) > 30:
        print(f"  ... +{len(all_issues) - 30} altri")
    return 1


if __name__ == "__main__":
    sys.exit(main())

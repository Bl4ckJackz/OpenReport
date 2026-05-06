#!/usr/bin/env python3
"""fact-check.py — verifica URL/DOI/citazioni del draft contro research-notes.md.

Flag ogni claim non supportato:
- URL nel draft non presenti in research-notes
- DOI nel draft non presenti in research-notes
- Nomi autori in citazioni che non compaiono in research-notes
- Anni in citazioni senza corrispondenza

Usage:
    python3 fact-check.py <draft_file> --research <research-notes.md> [--state <state.json>]

Exit: 0 = clean (o solo warning), 1 = issue trovati. Stampa report strutturato.
"""
import argparse
import json
import pathlib
import re
import sys

URL_RE = re.compile(r"https?://[^\s)\]}\"'>]+", re.IGNORECASE)
DOI_RE = re.compile(r"10\.\d{4,9}/[-._;()/:a-z0-9A-Z]+", re.IGNORECASE)
CITE_RE = re.compile(r"\\cite\{([^}]+)\}|\\citep\{([^}]+)\}|\\citet\{([^}]+)\}")
AUTHOR_YEAR_RE = re.compile(r"\(([A-Z][a-zà-ú\-']+(?:\s+(?:&|et\s+al\.|and)\s+[A-Z][a-zà-ú\-']+)?)[,;]\s*(\d{4})\)")


def extract(text, pattern, group=0):
    if isinstance(group, int):
        return set(m.group(group) for m in pattern.finditer(text))
    else:
        out = set()
        for m in pattern.finditer(text):
            for g in m.groups():
                if g:
                    for k in g.split(","):
                        out.add(k.strip())
        return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("draft")
    ap.add_argument("--research", required=True)
    ap.add_argument("--state", default=None)
    ap.add_argument("--json", action="store_true", help="Output JSON machine-readable")
    args = ap.parse_args()

    draft_path = pathlib.Path(args.draft)
    research_path = pathlib.Path(args.research)
    if not draft_path.exists():
        print(f"[ERR] draft non trovato: {draft_path}", file=sys.stderr)
        return 2
    if not research_path.exists():
        print(f"[WARN] research-notes non trovato: {research_path}. Salto fact-check.", file=sys.stderr)
        return 0

    draft = draft_path.read_text(encoding="utf-8")
    research = research_path.read_text(encoding="utf-8")

    draft_urls = {u.rstrip(".,;:)]}") for u in extract(draft, URL_RE)}
    draft_dois = {d.rstrip(".,;:)]}") for d in extract(draft, DOI_RE)}
    draft_cite_keys = set()
    for m in CITE_RE.finditer(draft):
        for g in m.groups():
            if g:
                for key in g.split(","):
                    draft_cite_keys.add(key.strip())
    draft_author_years = {(a, y) for a, y in AUTHOR_YEAR_RE.findall(draft)}

    research_text_lower = research.lower()
    research_urls = {u.rstrip(".,;:)]}") for u in extract(research, URL_RE)}
    research_dois = {d.rstrip(".,;:)]}") for d in extract(research, DOI_RE)}

    issues = {
        "urls_unsupported": sorted(u for u in draft_urls if u not in research_urls),
        "dois_unsupported": sorted(d for d in draft_dois if d not in research_dois),
        "cite_keys_unverified": sorted(draft_cite_keys),
        "author_year_unsupported": sorted(
            f"({a}, {y})" for a, y in draft_author_years
            if a.split()[0].lower() not in research_text_lower
        ),
    }

    has_issues = any(v for v in issues.values())

    if args.json:
        print(json.dumps(issues, indent=2, ensure_ascii=False))
    else:
        if not has_issues:
            print("[OK] Fact-check superato: tutte le citazioni/URL/DOI del draft risultano in research-notes")
        else:
            print("FACT-CHECK REPORT")
            print("=" * 60)
            if issues["urls_unsupported"]:
                print(f"\n[FAIL] {len(issues['urls_unsupported'])} URL nel draft non trovati in research-notes:")
                for u in issues["urls_unsupported"][:15]:
                    print(f"  • {u}")
            if issues["dois_unsupported"]:
                print(f"\n[FAIL] {len(issues['dois_unsupported'])} DOI non verificati:")
                for d in issues["dois_unsupported"][:15]:
                    print(f"  • {d}")
            if issues["author_year_unsupported"]:
                print(f"\n[WARN] {len(issues['author_year_unsupported'])} citazioni (Autore, anno) senza corrispondenza in research-notes:")
                for c in issues["author_year_unsupported"][:15]:
                    print(f"  • {c}")
            if issues["cite_keys_unverified"]:
                print(f"\n[INFO] {len(issues['cite_keys_unverified'])} chiavi \\cite{{}} — verifica presenza in .bib separatamente")

    if args.state:
        state_path = pathlib.Path(args.state)
        if state_path.exists():
            try:
                state = json.loads(state_path.read_text(encoding="utf-8"))
                state.setdefault("self_check_results", {})["fact_check_issues"] = (
                    issues["urls_unsupported"] + issues["dois_unsupported"] + issues["author_year_unsupported"]
                )
                state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
            except Exception as e:
                print(f"[WARN] impossibile aggiornare state: {e}", file=sys.stderr)

    return 1 if has_issues else 0


if __name__ == "__main__":
    sys.exit(main())

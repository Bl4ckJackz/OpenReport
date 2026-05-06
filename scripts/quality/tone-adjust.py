#!/usr/bin/env python3
"""tone-adjust.py — identifica frasi con tono non allineato e propone riformulazioni.

Rileva:
- Formale → informale (se target è formale): colloquialismi, contrazioni
- Informale → formale (se target è semi-formale): eccesso di gergo accademico
- Certezza eccessiva ("ovviamente", "chiaramente", "è evidente")
- Debole ("probabilmente", "forse", "potrebbe essere", "tendenzialmente")
- Hype marketing ("rivoluzionario", "straordinario", "unico nel suo genere")

Output: lista di frasi con categoria + suggerimenti (non applica in auto).

Usage:
    tone-adjust.py <file> --target formale|semi-formale|tecnico|narrativo
"""
import argparse
import pathlib
import re
import sys


PATTERNS = {
    "colloquiale": {
        "pattern": r"\b(tipo\s+che|insomma|boh|roba|fregare|sta|stanno\s+a)\b",
        "msg": "Espressione colloquiale — rimuovi o riformula in registro formale",
    },
    "contrazioni": {
        "pattern": r"\b(po'|l'|ce\s+l'ho|c'è\s+che)\b",
        "msg": "Contrazione informale — estendi",
    },
    "certezza-eccessiva": {
        "pattern": r"\b(ovviamente|chiaramente|è evidente|è scontato|è chiaro che|naturalmente)\b",
        "msg": "Tono eccessivamente assertivo — se l'affermazione è ovvia è inutile, se non lo è è presuntuoso",
    },
    "debolezza": {
        "pattern": r"\b(forse|probabilmente|potrebbe\s+essere|tendenzialmente|diciamo|in\s+qualche\s+modo)\b",
        "msg": "Tono incerto — o rafforza con dati o ammetti limitazione esplicitamente",
    },
    "hype-marketing": {
        "pattern": r"\b(rivoluzionario|straordinario|unico\s+nel\s+suo\s+genere|best-in-class|state-of-the-art|game-changer|disruptive)\b",
        "msg": "Iperbole marketing — sostituisci con descrizione oggettiva delle caratteristiche",
    },
    "filler": {
        "pattern": r"\b(basically|in pratica|sostanzialmente|di\s+fatto|nella\s+fattispecie)\b",
        "msg": "Filler word — di solito eliminabile",
    },
    "prima-persona-in-formale": {
        "pattern": r"\b(io\s+penso|secondo\s+me|a\s+parer\s+mio|personalmente\s+credo)\b",
        "msg": "Soggettività — in testo formale riformula in impersonale o con riferimento a fonte",
    },
    "jargon-non-definito": {
        "pattern": r"\b(leverage|drill-down|actionable|deliverable|onboarding|touchpoint)\b",
        "msg": "Anglicismo/gergo — se il pubblico non è bilingue, definisci al primo uso o traduci",
    },
}


TARGET_INTENSITIES = {
    "formale": {"colloquiale": 3, "contrazioni": 3, "certezza-eccessiva": 2, "debolezza": 2,
                "hype-marketing": 3, "prima-persona-in-formale": 3, "jargon-non-definito": 2},
    "semi-formale": {"colloquiale": 2, "hype-marketing": 2, "filler": 2},
    "tecnico": {"hype-marketing": 3, "prima-persona-in-formale": 2, "filler": 2},
    "narrativo": {"jargon-non-definito": 2},
}


def scan(text, target):
    intensities = TARGET_INTENSITIES.get(target, {})
    findings = []
    for category, spec in PATTERNS.items():
        if intensities.get(category, 1) == 0:
            continue
        for m in re.finditer(spec["pattern"], text, flags=re.IGNORECASE):
            start = m.start()
            # Extract sentence around match
            sentence_start = max(0, text.rfind(".", 0, start))
            sentence_end = text.find(".", start)
            if sentence_end == -1:
                sentence_end = min(len(text), start + 200)
            sentence = text[sentence_start:sentence_end].strip().lstrip(".").strip()
            findings.append({
                "category": category,
                "severity": intensities.get(category, 1),
                "msg": spec["msg"],
                "match": m.group(0),
                "sentence": sentence[:250],
                "offset": start,
            })
    return findings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--target", choices=list(TARGET_INTENSITIES.keys()), default="formale")
    ap.add_argument("--min-severity", type=int, default=1)
    args = ap.parse_args()

    p = pathlib.Path(args.file)
    if not p.exists():
        print(f"[ERR] {p} non trovato", file=sys.stderr)
        return 2

    text = p.read_text(encoding="utf-8")
    findings = [f for f in scan(text, args.target) if f["severity"] >= args.min_severity]

    if not findings:
        print(f"[OK] Tone allineato al target '{args.target}' in {p.name}")
        return 0

    print(f"TONE ADJUSTMENT — target '{args.target}' — {len(findings)} issue")
    print("=" * 70)
    by_cat = {}
    for f in findings:
        by_cat.setdefault(f["category"], []).append(f)

    for cat, items in sorted(by_cat.items(), key=lambda x: -max(i["severity"] for i in x[1])):
        print(f"\n[{cat}] ({len(items)} occorrenze)")
        print(f"  Suggerimento: {items[0]['msg']}")
        for i in items[:5]:
            highlighted = i["sentence"].replace(i["match"], f"«{i['match']}»")
            print(f"  • {highlighted}")

    return 1


if __name__ == "__main__":
    sys.exit(main())

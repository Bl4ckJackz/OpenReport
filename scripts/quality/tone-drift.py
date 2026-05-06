#!/usr/bin/env python3
"""tone-drift.py — rileva drift di tono tra sezioni di un documento.

Confronta ogni sezione vs sezione baseline (la prima, o quella indicata).
Marker analizzati:
  - lunghezza media frase (avg sentence length)
  - persona dominante (1ps / 1pp / impersonale / 3ps)
  - tempo verbale dominante (presente / passato prossimo / passato remoto / futuro)
  - densità subordinate (proxy: virgole + congiunzioni subordinanti per frase)

Usage:
  tone-drift.py <file> [--baseline=<n>] [--threshold=0.30]

Exit: 0 se nessun WARN, 1 se rilevati drift > soglia.
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path
from collections import Counter


SUBORDINATING_IT = {
    "che", "cui", "perché", "poiché", "siccome", "quando", "mentre",
    "se", "qualora", "affinché", "benché", "sebbene", "nonostante",
    "purché", "sennonché", "appena", "finché", "dopo che", "prima che",
}
SUBORDINATING_EN = {
    "that", "which", "because", "since", "when", "while", "if",
    "although", "though", "unless", "after", "before", "until",
    "whereas", "whenever", "as soon as",
}

PERSON_IT = {
    "prima-singolare": [r"\bho\b", r"\bsono\b", r"\bmio\b", r"\bmia\b", r"\bmi\b"],
    "prima-plurale":  [r"\babbiamo\b", r"\bsiamo\b", r"\bnostro\b", r"\bnostra\b", r"\bci\b"],
    "impersonale":    [r"\bsi è\b", r"\bsi sono\b", r"\bè stato\b", r"\bsono stati\b"],
    "terza":          [r"\bè\b", r"\bha\b", r"\bsuo\b", r"\bsua\b"],
}

TENSE_IT = {
    "presente":         [r"\bè\b", r"\bha\b", r"\bsono\b", r"\bvanno\b"],
    "passato-prossimo": [r"\bha\s+\w+to\b", r"\bha\s+\w+ato\b", r"\bha\s+\w+uto\b"],
    "passato-remoto":   [r"\b\w+ò\b", r"\b\w+ettero\b", r"\bfu\b", r"\bfurono\b"],
    "futuro":           [r"\b\w+rà\b", r"\b\w+ranno\b", r"\b\w+rò\b"],
}


def split_sections(text: str) -> list[tuple[str, str]]:
    sections, title, buf = [], "PROEMIO", []
    for line in text.splitlines():
        m = re.match(r"^(#{1,3})\s+(.+)$", line) or re.match(
            r"^\\(section|subsection|chapter)\*?\{(.+?)\}", line)
        if m:
            sections.append((title, "\n".join(buf)))
            title, buf = (m.group(2)[:60]), []
        else:
            buf.append(line)
    sections.append((title, "\n".join(buf)))
    return [(t, b) for t, b in sections if b.strip() and len(re.findall(r"\b\w+\b", b)) > 50]


def avg_sentence_len(text: str) -> float:
    sents = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    if not sents: return 0
    words = sum(len(re.findall(r"\b\w+\b", s)) for s in sents)
    return words / len(sents)


def dominant(patterns: dict[str, list[str]], text: str) -> str:
    counts = {k: sum(len(re.findall(p, text, re.IGNORECASE)) for p in v) for k, v in patterns.items()}
    return max(counts, key=counts.get) if counts else "N/A"


def subordinate_density(text: str, lang: str) -> float:
    sents = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    if not sents: return 0
    sub = SUBORDINATING_IT if lang == "it" else SUBORDINATING_EN
    pattern = r"\b(" + "|".join(re.escape(w) for w in sub) + r")\b"
    matches = len(re.findall(pattern, text, re.IGNORECASE))
    commas = text.count(",")
    return (matches + commas * 0.3) / len(sents)


def analyze(text: str, lang: str) -> dict:
    return {
        "avg_sentence_len": avg_sentence_len(text),
        "person": dominant(PERSON_IT, text) if lang == "it" else "N/A",
        "tense": dominant(TENSE_IT, text) if lang == "it" else "N/A",
        "subordinate_density": subordinate_density(text, lang),
    }


def delta_pct(a: float, b: float) -> float:
    if a == 0: return 0
    return abs(b - a) / a


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("file")
    p.add_argument("--baseline", type=int, default=0, help="Section index for baseline (default 0)")
    p.add_argument("--threshold", type=float, default=0.30)
    p.add_argument("--lang", default="it")
    args = p.parse_args()

    text = Path(args.file).read_text(encoding="utf-8")
    sections = split_sections(text)
    if len(sections) < 2:
        print("Solo una sezione: niente da confrontare.")
        return 0

    base_title, base_body = sections[args.baseline]
    base = analyze(base_body, args.lang)
    print(f"=== TONE DRIFT vs baseline: '{base_title}' ===")
    print(f"Baseline: avg-sent={base['avg_sentence_len']:.1f}, persona={base['person']}, tempo={base['tense']}, sub-density={base['subordinate_density']:.2f}\n")

    warns = 0
    for i, (title, body) in enumerate(sections):
        if i == args.baseline: continue
        m = analyze(body, args.lang)
        d_sent = delta_pct(base["avg_sentence_len"], m["avg_sentence_len"])
        d_sub = delta_pct(base["subordinate_density"], m["subordinate_density"])
        flags = []
        if d_sent > args.threshold:
            flags.append(f"avg-sent {m['avg_sentence_len']:.1f} (Δ{d_sent*100:.0f}%)")
        if m["person"] != base["person"] and base["person"] != "N/A":
            flags.append(f"persona {m['person']} (era {base['person']})")
        if m["tense"] != base["tense"] and base["tense"] != "N/A":
            flags.append(f"tempo {m['tense']} (era {base['tense']})")
        if d_sub > args.threshold + 0.1:
            flags.append(f"sub-density Δ{d_sub*100:.0f}%")
        if flags:
            warns += 1
            print(f"[WARN] '{title}': " + "; ".join(flags))
        else:
            print(f"[OK]   '{title}'")

    print(f"\nTotale WARN: {warns}/{len(sections)-1}")
    return 1 if warns > 0 else 0


if __name__ == "__main__":
    sys.exit(main())

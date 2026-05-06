#!/usr/bin/env python3
"""bilingual-generator.py — affianca due versioni linguistiche del doc.

Modalità:
1. Split-page: genera .tex con minipage IT | EN affiancate per sezione
2. Sequential: genera .md con sezione italiana poi sezione inglese
3. Glossary sync: estrae termini chiave e mantiene consistenza tra i due

Usage:
    bilingual-generator.py --primary RELAZIONE-it.md --secondary RELAZIONE-en.md \\
                           --mode split-page --output bilingual.tex
    bilingual-generator.py --primary it.md --secondary en.md --mode sequential --output out.md
    bilingual-generator.py --glossary --primary it.md --secondary en.md --output glossary.json
"""
import argparse
import json
import pathlib
import re
import sys


MD_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", flags=re.MULTILINE)


def split_by_headings(text):
    sections = []
    matches = list(MD_HEADING_RE.finditer(text))
    if not matches:
        return [("", text)]
    for i, m in enumerate(matches):
        title = m.group(2).strip()
        start = m.start()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        sections.append((title, text[start:end]))
    return sections


def mode_split_page(primary_sections, secondary_sections):
    out = [r"\documentclass[a4paper,11pt]{article}",
           r"\usepackage{polyglossia}",
           r"\setdefaultlanguage{italian}",
           r"\setotherlanguage{english}",
           r"\usepackage{fontspec}",
           r"\usepackage{geometry}",
           r"\geometry{margin=2cm,landscape}",
           r"\begin{document}"]
    n = max(len(primary_sections), len(secondary_sections))
    for i in range(n):
        _, it_text = primary_sections[i] if i < len(primary_sections) else ("", "")
        _, en_text = secondary_sections[i] if i < len(secondary_sections) else ("", "")
        out.append(r"\noindent\begin{minipage}[t]{0.48\textwidth}")
        out.append(it_text)
        out.append(r"\end{minipage}\hfill\begin{minipage}[t]{0.48\textwidth}")
        out.append(r"\begin{english}")
        out.append(en_text)
        out.append(r"\end{english}")
        out.append(r"\end{minipage}\vspace{1em}")
    out.append(r"\end{document}")
    return "\n".join(out)


def mode_sequential(primary_sections, secondary_sections):
    out = []
    n = max(len(primary_sections), len(secondary_sections))
    for i in range(n):
        it_title, it_text = primary_sections[i] if i < len(primary_sections) else ("", "")
        en_title, en_text = secondary_sections[i] if i < len(secondary_sections) else ("", "")
        out.append("---\n\n" + it_text.rstrip() + "\n\n_English version below_\n\n" + en_text.rstrip() + "\n")
    return "\n".join(out)


def extract_glossary(primary, secondary):
    """Estrae termini chiave (parole frequenti) con proposta di traduzione basata su posizione."""
    p_words = re.findall(r"\b[A-Z][a-zà-ú]{4,}\b", primary)
    s_words = re.findall(r"\b[A-Z][a-z]{4,}\b", secondary)
    from collections import Counter
    p_freq = Counter(p_words).most_common(30)
    s_freq = Counter(s_words).most_common(30)
    return {"italiano": p_freq, "inglese": s_freq}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--primary", required=True)
    ap.add_argument("--secondary", required=True)
    ap.add_argument("--mode", choices=["split-page", "sequential"], default="sequential")
    ap.add_argument("--glossary", action="store_true")
    ap.add_argument("--output", "-o", required=True)
    args = ap.parse_args()

    primary = pathlib.Path(args.primary).read_text(encoding="utf-8")
    secondary = pathlib.Path(args.secondary).read_text(encoding="utf-8")

    if args.glossary:
        gloss = extract_glossary(primary, secondary)
        pathlib.Path(args.output).write_text(json.dumps(gloss, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[OK] glossario candidato -> {args.output}")
        return 0

    primary_sections = split_by_headings(primary)
    secondary_sections = split_by_headings(secondary)

    if args.mode == "split-page":
        out_text = mode_split_page(primary_sections, secondary_sections)
    else:
        out_text = mode_sequential(primary_sections, secondary_sections)

    pathlib.Path(args.output).write_text(out_text, encoding="utf-8")
    print(f"[OK] bilingual {args.mode} -> {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

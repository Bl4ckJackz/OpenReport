#!/usr/bin/env python3
"""diff-summary.py — diff markdown human-readable tra due versioni di una relazione.

Output: sezione "Variazioni rispetto al periodo precedente" con sezioni aggiunte, rimosse, modificate (con stima % cambiamento).

Usage:
    diff-summary.py <old.md> <new.md> [--output diff.md]
"""
import argparse
import difflib
import pathlib
import re
import sys


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", flags=re.MULTILINE)


def split_by_sections(text):
    sections = {}
    matches = list(HEADING_RE.finditer(text))
    for i, m in enumerate(matches):
        title = m.group(2).strip()
        start = m.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        sections[title] = text[start:end].strip()
    return sections


def similarity(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("old")
    ap.add_argument("new")
    ap.add_argument("--output", "-o")
    args = ap.parse_args()

    old = pathlib.Path(args.old).read_text(encoding="utf-8")
    new = pathlib.Path(args.new).read_text(encoding="utf-8")

    s_old = split_by_sections(old)
    s_new = split_by_sections(new)

    added = sorted(set(s_new) - set(s_old))
    removed = sorted(set(s_old) - set(s_new))
    common = set(s_old) & set(s_new)

    modified = []
    for title in common:
        sim = similarity(s_old[title], s_new[title])
        if sim < 0.95:
            modified.append((title, 1.0 - sim))
    modified.sort(key=lambda x: -x[1])

    out = ["## Variazioni rispetto al periodo precedente\n"]
    if added:
        out.append(f"### Sezioni nuove ({len(added)})")
        for t in added:
            out.append(f"- {t}")
        out.append("")
    if removed:
        out.append(f"### Sezioni rimosse ({len(removed)})")
        for t in removed:
            out.append(f"- {t}")
        out.append("")
    if modified:
        out.append(f"### Sezioni modificate ({len(modified)})")
        for t, change in modified[:15]:
            out.append(f"- {t} ({change*100:.0f}% cambiato)")
        out.append("")
    if not (added or removed or modified):
        out.append("_Nessuna variazione significativa rispetto al periodo precedente._")

    # Word delta
    old_words = len(re.findall(r"\S+", old))
    new_words = len(re.findall(r"\S+", new))
    delta = new_words - old_words
    out.append(f"\n**Word count**: {old_words} → {new_words} ({'+' if delta >= 0 else ''}{delta})")

    text = "\n".join(out)
    if args.output:
        pathlib.Path(args.output).write_text(text, encoding="utf-8")
        print(f"[OK] {args.output}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())

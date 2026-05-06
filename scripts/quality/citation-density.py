#!/usr/bin/env python3
"""citation-density.py — verifica densità citazioni per sezione.

Per ogni sezione > soglia parole, conta `\\cite{}` (LaTeX) o `[^N]` (markdown).
WARN se densità sotto minimo.

Usage:
  citation-density.py <file> [--min-words=800] [--min-cites-per-section=2]
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path


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
    return [(t, b) for t, b in sections if b.strip()]


def count_citations(body: str) -> int:
    latex_cites = len(re.findall(r"\\cite[a-z]*\{[^}]+\}", body))
    md_footnotes = len(set(re.findall(r"\[\^[a-zA-Z0-9_-]+\]", body)))
    md_links = len(re.findall(r"\[[^\]]+\]\(https?://", body))
    return latex_cites + md_footnotes + md_links


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("file")
    p.add_argument("--min-words", type=int, default=800)
    p.add_argument("--min-cites", type=int, default=2)
    args = p.parse_args()

    text = Path(args.file).read_text(encoding="utf-8")
    sections = split_sections(text)

    print(f"=== CITATION DENSITY: {args.file} ===\n")
    warns = 0
    for title, body in sections:
        words = len(re.findall(r"\b\w+\b", body))
        if words < args.min_words:
            continue
        cites = count_citations(body)
        if cites < args.min_cites:
            warns += 1
            print(f"[WARN] '{title}': {words} parole, {cites} citazioni (minimo {args.min_cites})")
        else:
            print(f"[OK]   '{title}': {words} parole, {cites} citazioni")
    print(f"\nTotale WARN: {warns}")
    return 1 if warns > 0 else 0


if __name__ == "__main__":
    sys.exit(main())

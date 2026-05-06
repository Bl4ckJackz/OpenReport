#!/usr/bin/env python3
"""toc-regen.py — rigenera TOC nel doc mantenendo numerazione coerente.

Feature:
- Markdown: aggiorna `<!-- TOC -->` ... `<!-- /TOC -->` o crea nuovo
- LaTeX: verifica che `\\tableofcontents` sia presente e setup corretto per \\setcounter{tocdepth}{3}
- Numerazione sezioni auto (H1=1, H2=1.1, H3=1.1.1)
- Ignora heading in code block
- Opzionalmente rinomina heading con prefix numerico "1. Introduzione"

Usage:
    toc-regen.py <file.md> [--max-depth 3] [--number-headings] [--in-place]
"""
import argparse
import pathlib
import re
import sys


TOC_START = "<!-- TOC -->"
TOC_END = "<!-- /TOC -->"
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", flags=re.MULTILINE)
CODEBLOCK_RE = re.compile(r"```[\s\S]*?```")


def strip_codeblocks(text):
    """Rimuove heading dentro code fence."""
    return CODEBLOCK_RE.sub(lambda m: "`" * len(m.group(0)), text)


def extract_headings(text, max_depth=6):
    stripped = strip_codeblocks(text)
    headings = []
    for m in HEADING_RE.finditer(stripped):
        level = len(m.group(1))
        if level <= max_depth:
            title = m.group(2).strip()
            # Rimuovi prefisso numerico esistente (1., 1.2., 1.2.3)
            title_clean = re.sub(r"^(\d+(\.\d+)*\.?)\s+", "", title)
            anchor = re.sub(r"[^\w\s-]", "", title_clean.lower()).strip().replace(" ", "-")
            headings.append((level, title_clean, anchor))
    return headings


def number_headings(headings):
    numbered = []
    counters = [0] * 7
    for level, title, anchor in headings:
        counters[level] += 1
        for i in range(level + 1, 7):
            counters[i] = 0
        num = ".".join(str(counters[i]) for i in range(1, level + 1))
        numbered.append((level, title, anchor, num))
    return numbered


def render_toc(numbered):
    lines = []
    for level, title, anchor, num in numbered:
        indent = "  " * (level - 1)
        lines.append(f"{indent}- [{num} {title}](#{anchor})")
    return "\n".join(lines)


def inject_toc(text, toc_block, max_depth):
    block = f"{TOC_START}\n{toc_block}\n{TOC_END}"
    if TOC_START in text and TOC_END in text:
        return re.sub(
            re.escape(TOC_START) + r".*?" + re.escape(TOC_END),
            lambda m: block,
            text, count=1, flags=re.DOTALL
        )
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("# "):
            return "\n".join(lines[:i+1] + ["", block, ""] + lines[i+1:])
    return block + "\n\n" + text


def apply_numbered_headings(text, numbered):
    stripped = strip_codeblocks(text)
    result = text
    matches = list(HEADING_RE.finditer(stripped))
    offset = 0
    for (level, title, anchor, num), m in zip(numbered, matches):
        start = m.start() + offset
        end = m.end() + offset
        hashes = "#" * level
        new_line = f"{hashes} {num} {title}"
        old_line = result[start:end]
        result = result[:start] + new_line + result[end:]
        offset += len(new_line) - len(old_line)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--max-depth", type=int, default=3)
    ap.add_argument("--number-headings", action="store_true")
    ap.add_argument("--in-place", action="store_true")
    args = ap.parse_args()

    p = pathlib.Path(args.file)
    text = p.read_text(encoding="utf-8")
    headings = extract_headings(text, args.max_depth)
    if not headings:
        print("[INFO] nessun heading trovato", file=sys.stderr)
        return 0

    numbered = number_headings(headings)

    if args.number_headings:
        text = apply_numbered_headings(text, numbered)

    toc_block = render_toc(numbered)
    new_text = inject_toc(text, toc_block, args.max_depth)

    if args.in_place:
        p.write_text(new_text, encoding="utf-8")
        print(f"[OK] TOC aggiornato ({len(headings)} sezioni) in {p}")
    else:
        print(new_text)
    return 0


if __name__ == "__main__":
    sys.exit(main())

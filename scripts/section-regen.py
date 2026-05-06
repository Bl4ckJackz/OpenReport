#!/usr/bin/env python3
"""section-regen.py — sostituisce una singola sezione in un draft md/tex.

In modalità 'modifica sezione' durante refinement, evita di riscrivere l'intero documento:
estrae la sezione target, la sostituisce con nuovo contenuto (letto da file o stdin), aggiorna
il draft in-place mantenendo il resto.

Usage:
    section-regen.py <draft> --title "Introduzione" --new-content <file>
    section-regen.py <draft> --title "Risultati" --stdin < new.md
    section-regen.py <draft> --list-sections

Supporta markdown (# heading) e LaTeX (\\section{}, \\subsection{}, \\subsubsection{}).
"""
import argparse
import pathlib
import re
import sys

MD_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", flags=re.MULTILINE)
TEX_HEADING_RE = re.compile(r"^\\(section|subsection|subsubsection|chapter|paragraph)\*?\{([^}]+)\}", flags=re.MULTILINE)


def detect_format(text):
    if TEX_HEADING_RE.search(text) and not MD_HEADING_RE.search(text):
        return "tex"
    if TEX_HEADING_RE.search(text) and "\\documentclass" in text:
        return "tex"
    return "md"


def list_sections(text, fmt):
    out = []
    if fmt == "md":
        for m in MD_HEADING_RE.finditer(text):
            level = len(m.group(1))
            out.append((level, m.group(2).strip(), m.start()))
    else:
        levels = {"chapter": 1, "section": 2, "subsection": 3, "subsubsection": 4, "paragraph": 5}
        for m in TEX_HEADING_RE.finditer(text):
            out.append((levels.get(m.group(1), 3), m.group(2).strip(), m.start()))
    return out


def find_section(sections, title):
    needle = title.strip().lower()
    for idx, (lvl, name, pos) in enumerate(sections):
        if name.lower() == needle:
            return idx
    for idx, (lvl, name, pos) in enumerate(sections):
        if needle in name.lower():
            return idx
    return -1


def extract_replace(text, sections, idx, new_content):
    lvl, name, start = sections[idx]
    end = len(text)
    for next_idx in range(idx + 1, len(sections)):
        next_lvl, _, next_start = sections[next_idx]
        if next_lvl <= lvl:
            end = next_start
            break
    old = text[start:end]
    new = new_content
    if not new.endswith("\n"):
        new += "\n"
    if not old.endswith("\n") and end < len(text):
        new += "\n"
    return text[:start] + new + text[end:], old


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("draft")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--title")
    g.add_argument("--list-sections", action="store_true")
    ap.add_argument("--new-content", help="Path file contenente nuovo testo sezione")
    ap.add_argument("--stdin", action="store_true", help="Leggi nuovo contenuto da stdin")
    ap.add_argument("--backup", action="store_true", help="Salva .bak prima di sovrascrivere")
    ap.add_argument("--dry-run", action="store_true", help="Stampa diff senza scrivere")
    args = ap.parse_args()

    path = pathlib.Path(args.draft)
    if not path.exists():
        print(f"[ERR] draft non trovato: {path}", file=sys.stderr)
        return 2

    text = path.read_text(encoding="utf-8")
    fmt = detect_format(text)
    sections = list_sections(text, fmt)

    if args.list_sections:
        print(f"Formato rilevato: {fmt}")
        print(f"{len(sections)} sezioni:")
        for lvl, name, _ in sections:
            print(f"  {'  ' * (lvl - 1)}[{lvl}] {name}")
        return 0

    if not args.title:
        ap.print_help()
        return 2

    idx = find_section(sections, args.title)
    if idx < 0:
        print(f"[ERR] sezione non trovata: '{args.title}'", file=sys.stderr)
        print("Sezioni disponibili:", file=sys.stderr)
        for lvl, name, _ in sections:
            print(f"  [{lvl}] {name}", file=sys.stderr)
        return 1

    if args.stdin:
        new_content = sys.stdin.read()
    elif args.new_content:
        new_content = pathlib.Path(args.new_content).read_text(encoding="utf-8")
    else:
        print("[ERR] fornire --new-content <file> oppure --stdin", file=sys.stderr)
        return 2

    new_text, old = extract_replace(text, sections, idx, new_content)

    if args.dry_run:
        print(f"--- Old section: {args.title} ---")
        print(old)
        print(f"--- New section ---")
        print(new_content)
        return 0

    if args.backup:
        bak = path.with_suffix(path.suffix + ".bak")
        bak.write_text(text, encoding="utf-8")
        print(f"[OK] backup: {bak}")

    path.write_text(new_text, encoding="utf-8")
    print(f"[OK] sezione '{args.title}' sostituita ({len(old)} -> {len(new_content)} char)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

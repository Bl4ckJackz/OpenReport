#!/usr/bin/env python3
"""slide-deck.py — genera slide deck (Marp o Beamer) dalla relazione completa.

Strategia:
  - 1 slide titolo (estratta da frontmatter / H1)
  - 1 slide TOC
  - 1-2 slide per ogni sezione H1/H2 (titolo + 3-5 bullet estratti)
  - 1 slide per ogni figura referenziata
  - 1 slide conclusioni
  - 1 slide Q&A finale

Usage:
  slide-deck.py <relazione.md> --engine={marp|beamer} -o SLIDES.md
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path


def extract_frontmatter(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m: return {}, text
    fm = {}
    for line in m.group(1).splitlines():
        m2 = re.match(r"^(\w+):\s*(.+)$", line)
        if m2:
            fm[m2.group(1)] = m2.group(2).strip().strip('"\'').strip("[]")
    return fm, text[m.end():]


def split_sections(text: str) -> list[tuple[int, str, str]]:
    """Returns (level, title, body)."""
    sections = []
    title, body, level = "", [], 1
    for line in text.splitlines():
        m = re.match(r"^(#{1,3})\s+(.+)$", line)
        if m:
            if title:
                sections.append((level, title, "\n".join(body).strip()))
            level = len(m.group(1))
            title = m.group(2).strip()
            body = []
        else:
            body.append(line)
    if title:
        sections.append((level, title, "\n".join(body).strip()))
    return sections


def extract_bullets(body: str, max_n: int = 5) -> list[str]:
    """Estrae bullet espliciti, o sentenze chiave se non ci sono bullet."""
    bullets = re.findall(r"^[\-\*]\s+(.+)$", body, re.MULTILINE)
    if bullets:
        return [b.strip()[:120] for b in bullets[:max_n]]
    sents = re.split(r"(?<=[.!?])\s+", body)
    sents = [s.strip() for s in sents if 30 < len(s) < 200]
    return sents[:max_n]


def find_images(body: str) -> list[tuple[str, str]]:
    """Returns (alt, path) for markdown images and LaTeX includegraphics."""
    out = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", body)
    out += [(m.group(2) if m.group(2) else "", m.group(1))
            for m in re.finditer(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}(?:\s*\\caption\{([^}]+)\})?", body)]
    return out


def render_marp(fm: dict, sections: list[tuple[int, str, str]], theme: str = "default") -> str:
    title = fm.get("title", sections[0][1] if sections else "Presentazione")
    author = fm.get("author", "")
    date = fm.get("date", "")

    out = ["---", f"marp: true", f"theme: {theme}", "paginate: true",
           f"title: \"{title}\"", "---", ""]
    out += [f"# {title}", ""]
    if author: out.append(f"**{author}**")
    if date: out.append(f"\n*{date}*")
    out.append("\n---\n")

    out += ["## Indice", ""]
    for lvl, t, _ in sections:
        if lvl <= 2:
            out.append(f"- {t}")
    out.append("\n---\n")

    for lvl, t, body in sections:
        if lvl > 2: continue
        bullets = extract_bullets(body)
        if not bullets: continue
        out += [f"## {t}", ""]
        for b in bullets:
            out.append(f"- {b}")

        for alt, path in find_images(body)[:1]:
            out.append("")
            out.append(f"![{alt}]({path})")
            if alt: out.append(f"\n*{alt}*")
        out.append("\n---\n")

    out += ["## Domande?", "", "Grazie per l'attenzione."]
    return "\n".join(out)


def render_beamer(fm: dict, sections: list[tuple[int, str, str]], theme: str = "Madrid") -> str:
    title = fm.get("title", sections[0][1] if sections else "Presentazione")
    author = fm.get("author", "")
    date = fm.get("date", "\\today")

    out = [
        r"\documentclass{beamer}",
        f"\\usetheme{{{theme}}}",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage[italian]{babel}",
        r"\usepackage{graphicx}",
        f"\\title{{{title}}}",
        f"\\author{{{author}}}",
        f"\\date{{{date}}}",
        r"\begin{document}",
        r"\frame{\titlepage}",
        r"\begin{frame}{Indice}\tableofcontents\end{frame}",
    ]

    for lvl, t, body in sections:
        if lvl > 2: continue
        bullets = extract_bullets(body)
        if not bullets: continue
        if lvl == 1:
            out.append(f"\\section{{{t}}}")
        out.append(f"\\begin{{frame}}{{{t}}}")
        out.append(r"\begin{itemize}")
        for b in bullets:
            out.append(f"  \\item {b}")
        out.append(r"\end{itemize}")
        out.append(r"\end{frame}")

    out.append(r"\begin{frame}{Domande?}\centering\Huge Grazie\end{frame}")
    out.append(r"\end{document}")
    return "\n".join(out)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("relazione")
    p.add_argument("--engine", choices=["marp", "beamer"], default="marp")
    p.add_argument("--theme", default="")
    p.add_argument("-o", "--out", default="SLIDES.md")
    args = p.parse_args()

    text = Path(args.relazione).read_text(encoding="utf-8")
    fm, body = extract_frontmatter(text)
    sections = split_sections(body)

    if args.engine == "marp":
        out = render_marp(fm, sections, args.theme or "default")
        ext = ".md"
    else:
        out = render_beamer(fm, sections, args.theme or "Madrid")
        ext = ".tex"

    out_path = Path(args.out)
    if out_path.suffix != ext and "." not in out_path.name[-5:]:
        out_path = out_path.with_suffix(ext)

    out_path.write_text(out, encoding="utf-8")
    n_slides = out.count("\n---\n") if args.engine == "marp" else out.count("\\begin{frame}")
    print(f"Slide deck: {out_path} ({n_slides} slide, engine={args.engine})")
    if args.engine == "marp":
        print(f"Compila con: marp {out_path} -o SLIDES.pdf  (oppure --pptx)")
    else:
        print(f"Compila con: pdflatex {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""executive-summary.py — estrae 1-pagina riassuntiva da una relazione completa.

Cerca:
  - Frontmatter YAML (title, author, date) o H1 + autore + data
  - Sezione "Abstract" / "Sommario esecutivo" / "Sommario"
  - Sezione "Risultati" / "Conclusioni" / "Outcomes"
  - Sezione "Sviluppi futuri" / "Future work" / "Next steps"

Compila SUMMARY.md max 1 pagina (~400 parole).

Usage:
  executive-summary.py <relazione.md> -o SUMMARY.md
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path


SECTION_NAMES_ABSTRACT = ["abstract", "sommario esecutivo", "sommario", "executive summary", "riepilogo"]
SECTION_NAMES_RESULTS = ["risultati", "conclusioni", "results", "conclusions", "outcomes", "discussion"]
SECTION_NAMES_FUTURE  = ["sviluppi futuri", "future work", "lavori futuri", "next steps", "prossimi passi", "roadmap"]


def extract_frontmatter(text: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m: return {}
    fm = {}
    for line in m.group(1).splitlines():
        m2 = re.match(r"^(\w+):\s*(.+)$", line)
        if m2:
            k, v = m2.group(1), m2.group(2).strip().strip('"\'')
            fm[k] = v
    return fm


def extract_h1(text: str) -> str:
    m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else "Titolo"


def find_section(text: str, names: list[str], max_words: int = 200) -> str:
    """Trova la prima sezione il cui titolo matcha uno dei nomi."""
    pattern = r"^#{1,3}\s+(?:\d+\.?\s+)?(" + "|".join(names) + r")\b.*$"
    m = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
    if not m: return ""
    start = m.end()
    next_h = re.search(r"^#{1,3}\s+", text[start:], re.MULTILINE)
    body = text[start:start + next_h.start()] if next_h else text[start:]
    body = body.strip()
    words = body.split()
    if len(words) > max_words:
        body = " ".join(words[:max_words]) + "..."
    return body


def first_paragraph_after(text: str, marker: str = "Introduzione") -> str:
    m = re.search(rf"^#{{1,3}}\s+(?:\d+\.?\s+)?{marker}", text, re.MULTILINE | re.IGNORECASE)
    if not m: return ""
    start = m.end()
    paragraphs = re.split(r"\n\s*\n", text[start:].strip())
    for p in paragraphs:
        cleaned = re.sub(r"^#{1,3}\s+.*", "", p).strip()
        if len(cleaned.split()) > 30:
            return " ".join(cleaned.split()[:150])
    return ""


def extract_results_bullets(text: str, n: int = 5) -> list[str]:
    section = find_section(text, SECTION_NAMES_RESULTS, max_words=500)
    if not section: return []
    bullets = re.findall(r"^[\-\*]\s+(.+)$", section, re.MULTILINE)
    if bullets:
        return [b.strip()[:150] for b in bullets[:n]]
    sents = re.split(r"(?<=[.!?])\s+", section)
    return [s.strip()[:150] for s in sents if len(s) > 30][:n]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("relazione")
    p.add_argument("-o", "--out", default="SUMMARY.md")
    args = p.parse_args()

    text = Path(args.relazione).read_text(encoding="utf-8")
    fm = extract_frontmatter(text)
    title = fm.get("title", extract_h1(text))
    author = fm.get("author", "[autore]")
    date = fm.get("date", "")

    abstract = find_section(text, SECTION_NAMES_ABSTRACT, max_words=120) or first_paragraph_after(text)
    results = extract_results_bullets(text, n=5)
    future = find_section(text, SECTION_NAMES_FUTURE, max_words=80)

    out = []
    out.append(f"# {title}")
    out.append(f"**{author}** — {date}")
    out.append("")
    out.append("## In sintesi")
    out.append(abstract or "_Sezione abstract non trovata nel sorgente._")
    out.append("")
    out.append("## Risultati chiave")
    if results:
        for r in results: out.append(f"- {r}")
    else:
        out.append("_Sezione risultati non trovata._")
    out.append("")
    if future:
        out.append("## Prossimi passi")
        out.append(future)
        out.append("")
    out.append("---")
    out.append(f"*Riferimento completo: `{Path(args.relazione).name}`*")

    Path(args.out).write_text("\n".join(out), encoding="utf-8")
    n_words = sum(len(line.split()) for line in out)
    print(f"Executive summary scritto in {args.out} ({n_words} parole, ~{n_words//400 + 1} pagina)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

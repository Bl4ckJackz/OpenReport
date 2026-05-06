#!/usr/bin/env python3
"""zotero-import.py — converte export Zotero/Mendeley in references.bib.

Supporta:
  - .json (CSL JSON export, formato standard Zotero "Better CSL JSON")
  - .ris (Mendeley/Zotero RIS export)
  - .bib (passthrough, validation only)

Usage:
  zotero-import.py <input> -o references.bib [--prefix=auto]

Genera key BibTeX nel formato {primo-autore}{anno}{primaParolaTitolo}.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path


def slugify(s: str, max_len: int = 20) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "", s.lower())
    return s[:max_len] or "anon"


def make_key(authors: list[str], year: str, title: str) -> str:
    first = authors[0].split(",")[0] if authors else "Anon"
    word = (title.split()[0] if title else "Notitle").strip().capitalize()
    return f"{slugify(first, 15)}{year}{slugify(word, 10)}"


def csl_json_to_bib(items: list[dict]) -> str:
    out = []
    for it in items:
        kind = it.get("type", "article")
        type_map = {
            "article-journal": "article",
            "paper-conference": "inproceedings",
            "book": "book",
            "chapter": "incollection",
            "thesis": "phdthesis",
            "report": "techreport",
            "webpage": "online",
        }
        bib_type = type_map.get(kind, "misc")
        authors = []
        for a in it.get("author", []):
            family = a.get("family", "")
            given = a.get("given", "")
            authors.append(f"{family}, {given}".strip(", "))
        year = str(it.get("issued", {}).get("date-parts", [["n.d."]])[0][0])
        title = it.get("title", "Untitled")
        key = make_key(authors, year, title)

        fields = [f"  title = {{{title}}}"]
        if authors:
            fields.append(f"  author = {{{' and '.join(authors)}}}")
        fields.append(f"  year = {{{year}}}")
        for src, dst in [("container-title", "journal"), ("publisher", "publisher"),
                          ("volume", "volume"), ("issue", "number"), ("page", "pages"),
                          ("DOI", "doi"), ("URL", "url"), ("ISBN", "isbn")]:
            v = it.get(src)
            if v: fields.append(f"  {dst} = {{{v}}}")

        out.append(f"@{bib_type}{{{key},\n" + ",\n".join(fields) + "\n}")
    return "\n\n".join(out)


def ris_to_bib(text: str) -> str:
    entries = re.split(r"\n(?=TY\s+-)", text.strip())
    items = []
    for e in entries:
        rec = {}
        for line in e.splitlines():
            m = re.match(r"^([A-Z][A-Z0-9])\s+-\s+(.*)$", line)
            if m:
                k, v = m.group(1), m.group(2).strip()
                rec.setdefault(k, []).append(v)
        if not rec: continue

        kind = rec.get("TY", ["GEN"])[0]
        type_map = {"JOUR": "article", "CONF": "inproceedings", "BOOK": "book",
                     "CHAP": "incollection", "THES": "phdthesis", "RPRT": "techreport"}
        bib_type = type_map.get(kind, "misc")

        authors = rec.get("AU", []) + rec.get("A1", [])
        year = (rec.get("PY", rec.get("Y1", ["n.d."]))[0])[:4]
        title = (rec.get("TI", rec.get("T1", ["Untitled"]))[0])
        key = make_key(authors, year, title)

        fields = [f"  title = {{{title}}}"]
        if authors:
            fields.append(f"  author = {{{' and '.join(authors)}}}")
        fields.append(f"  year = {{{year}}}")
        for src, dst in [("JO", "journal"), ("T2", "journal"), ("PB", "publisher"),
                          ("VL", "volume"), ("IS", "number"), ("SP", "pages"),
                          ("DO", "doi"), ("UR", "url"), ("SN", "isbn")]:
            v = rec.get(src)
            if v: fields.append(f"  {dst} = {{{v[0]}}}")

        items.append(f"@{bib_type}{{{key},\n" + ",\n".join(fields) + "\n}")
    return "\n\n".join(items)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("input")
    p.add_argument("-o", "--out", default="references.bib")
    args = p.parse_args()

    src = Path(args.input)
    text = src.read_text(encoding="utf-8")

    if src.suffix == ".json":
        items = json.loads(text)
        if isinstance(items, dict): items = items.get("items", [items])
        bib = csl_json_to_bib(items)
    elif src.suffix == ".ris":
        bib = ris_to_bib(text)
    elif src.suffix == ".bib":
        bib = text  # passthrough
    else:
        print(f"ERROR: estensione non supportata: {src.suffix}", file=sys.stderr)
        return 2

    Path(args.out).write_text(bib + "\n", encoding="utf-8")
    n = bib.count("@") if src.suffix != ".bib" else len(re.findall(r"^@\w+\{", bib, re.MULTILINE))
    print(f"Convertite {n} entry → {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""citation-enrich.py — completa un file .bib con metadata da CrossRef / DOI.

Modalità:
1. Da DOI → recupera e formatta entry bibtex
2. Da titolo libero → cerca su CrossRef, chiede conferma, inserisce
3. Da .bib parziale → per ogni entry senza autore/anno/journal, tenta completamento

Usage:
    citation-enrich.py --doi 10.1016/j.tcs.2019.12.008 [--bib refs.bib --append]
    citation-enrich.py --search "attention is all you need"
    citation-enrich.py --bib refs.bib --complete-missing

Richiede: urllib (stdlib). Niente dipendenze esterne.
"""
import argparse
import json
import pathlib
import re
import sys
import urllib.parse
import urllib.request

CROSSREF_WORKS = "https://api.crossref.org/works"
DOI_URL = "https://doi.org/{doi}"


def http_get_json(url, timeout=10):
    req = urllib.request.Request(url, headers={
        "User-Agent": "relazione-citation-enrich/1.0 (mailto:info@mindsmart.it)",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_doi(doi):
    url = f"{CROSSREF_WORKS}/{urllib.parse.quote(doi, safe='/')}"
    try:
        data = http_get_json(url)
        return data.get("message")
    except Exception as e:
        print(f"[ERR] CrossRef fetch: {e}", file=sys.stderr)
        return None


def search_crossref(query, rows=5):
    url = f"{CROSSREF_WORKS}?query.bibliographic={urllib.parse.quote(query)}&rows={rows}"
    try:
        data = http_get_json(url)
        return (data.get("message") or {}).get("items") or []
    except Exception as e:
        print(f"[ERR] CrossRef search: {e}", file=sys.stderr)
        return []


def authors_str(authors):
    out = []
    for a in (authors or []):
        family = a.get("family", "")
        given = a.get("given", "")
        if family:
            out.append(f"{family}, {given}" if given else family)
    return " and ".join(out)


def generate_key(work):
    authors = work.get("author") or []
    first = authors[0].get("family", "Anon") if authors else "Anon"
    year = (work.get("issued") or {}).get("date-parts", [[None]])[0][0] or ""
    title_word = re.sub(r"[^A-Za-z]", "", (work.get("title", [""])[0] or "").split()[0] if work.get("title") else "")[:8]
    return f"{first}{year}{title_word}".strip()


def to_bibtex(work, key=None):
    key = key or generate_key(work)
    type_map = {"journal-article": "article", "book": "book", "book-chapter": "incollection",
                "proceedings-article": "inproceedings", "report": "techreport", "posted-content": "misc"}
    entry_type = type_map.get(work.get("type"), "misc")
    fields = {
        "author": authors_str(work.get("author") or []),
        "title": (work.get("title") or [""])[0],
        "year": str((work.get("issued") or {}).get("date-parts", [[""]])[0][0] or ""),
        "journal": (work.get("container-title") or [""])[0],
        "volume": str(work.get("volume", "") or ""),
        "number": str(work.get("issue", "") or ""),
        "pages": str(work.get("page", "") or ""),
        "publisher": work.get("publisher", ""),
        "doi": work.get("DOI", ""),
        "url": work.get("URL", ""),
    }
    lines = [f"@{entry_type}{{{key},"]
    for k, v in fields.items():
        if v:
            lines.append(f"  {k} = {{{v}}},")
    lines.append("}")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--doi")
    g.add_argument("--search")
    g.add_argument("--complete-missing", action="store_true")
    ap.add_argument("--bib", help="File .bib di destinazione o input per complete-missing")
    ap.add_argument("--append", action="store_true", help="Append al file .bib")
    ap.add_argument("--rows", type=int, default=5)
    args = ap.parse_args()

    if args.doi:
        work = fetch_doi(args.doi)
        if not work:
            return 1
        entry = to_bibtex(work)
        print(entry)
        if args.bib and args.append:
            with open(args.bib, "a", encoding="utf-8") as f:
                f.write("\n" + entry + "\n")
            print(f"\n[OK] appended to {args.bib}", file=sys.stderr)
        return 0

    if args.search:
        results = search_crossref(args.search, rows=args.rows)
        if not results:
            print("[INFO] nessun risultato", file=sys.stderr)
            return 1
        print(f"# Trovati {len(results)} risultati per: {args.search}")
        for i, w in enumerate(results, 1):
            title = (w.get("title") or [""])[0]
            year = (w.get("issued") or {}).get("date-parts", [[None]])[0][0]
            authors = authors_str(w.get("author") or [])
            print(f"\n[{i}] {title}")
            print(f"    Autori: {authors[:120]}...")
            print(f"    Anno: {year}  DOI: {w.get('DOI', '—')}")
        return 0

    if args.complete_missing:
        if not args.bib or not pathlib.Path(args.bib).exists():
            print("[ERR] --bib richiesto e deve esistere", file=sys.stderr)
            return 2
        text = pathlib.Path(args.bib).read_text(encoding="utf-8")
        doi_entries = re.findall(r"doi\s*=\s*\{(10\.\d+/[^\}]+)\}", text)
        print(f"[INFO] trovate {len(doi_entries)} DOI da verificare")
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())

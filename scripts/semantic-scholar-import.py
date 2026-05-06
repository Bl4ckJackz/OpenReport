#!/usr/bin/env python3
"""semantic-scholar-import.py — import paper da Semantic Scholar API.

Feature superiori a CrossRef:
- TL;DR autogenerato
- Citation count / influential citations
- Open access PDF URL quando disponibile
- Related papers

Usage:
    semantic-scholar-import.py --doi 10.1016/xxx
    semantic-scholar-import.py --paper-id S2CORPUS:12345
    semantic-scholar-import.py --search "graph neural networks" --limit 10
    semantic-scholar-import.py --doi 10.x --bibtex --append refs.bib
"""
import argparse
import json
import os
import pathlib
import re
import sys
import urllib.parse
import urllib.request

API_BASE = "https://api.semanticscholar.org/graph/v1"
FIELDS = "title,authors,year,venue,externalIds,abstract,tldr,citationCount,influentialCitationCount,openAccessPdf"


def api_get(path):
    url = f"{API_BASE}{path}"
    headers = {"User-Agent": "relazione-s2/1.0"}
    key = os.environ.get("S2_API_KEY")
    if key:
        headers["x-api-key"] = key
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        print(f"[ERR] API: {e}", file=sys.stderr)
        return None


def get_paper(paper_id):
    return api_get(f"/paper/{urllib.parse.quote(paper_id, safe=':')}?fields={FIELDS}")


def get_paper_by_doi(doi):
    return get_paper(f"DOI:{doi}")


def search(query, limit=10):
    path = f"/paper/search?query={urllib.parse.quote(query)}&limit={limit}&fields={FIELDS}"
    data = api_get(path)
    return data.get("data", []) if data else []


def to_bibtex(paper):
    authors = paper.get("authors") or []
    author_str = " and ".join(a.get("name", "") for a in authors)
    first_family = (authors[0].get("name", "").split()[-1] if authors else "Anon")
    year = str(paper.get("year", ""))
    title = paper.get("title", "")
    title_word = re.sub(r"[^A-Za-z]", "", title.split()[0])[:8] if title else ""
    key = f"{first_family}{year}{title_word}"
    ext = paper.get("externalIds") or {}
    lines = [f"@article{{{key},"]
    lines.append(f"  author = {{{author_str}}},")
    lines.append(f"  title = {{{title}}},")
    if paper.get("venue"):
        lines.append(f"  journal = {{{paper['venue']}}},")
    if year:
        lines.append(f"  year = {{{year}}},")
    if ext.get("DOI"):
        lines.append(f"  doi = {{{ext['DOI']}}},")
    if ext.get("ArXiv"):
        lines.append(f"  note = {{arXiv:{ext['ArXiv']}}},")
    lines.append("}")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--doi")
    g.add_argument("--paper-id")
    g.add_argument("--search")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--bibtex", action="store_true")
    ap.add_argument("--append")
    args = ap.parse_args()

    if args.search:
        papers = search(args.search, args.limit)
    else:
        single = get_paper_by_doi(args.doi) if args.doi else get_paper(args.paper_id)
        papers = [single] if single else []

    if not papers:
        print("[INFO] nessun risultato", file=sys.stderr)
        return 1

    for p in papers:
        if args.bibtex or args.append:
            bib = to_bibtex(p)
            if args.append:
                with open(args.append, "a", encoding="utf-8") as f:
                    f.write("\n" + bib + "\n")
                print(f"[OK] appended -> {args.append}", file=sys.stderr)
            else:
                print(bib + "\n")
        else:
            print(f"\n### {p.get('title', '')}")
            authors = p.get("authors") or []
            print(f"  Autori: {', '.join(a.get('name', '') for a in authors[:4])}")
            print(f"  Anno: {p.get('year', '')}  Venue: {p.get('venue', '')}")
            print(f"  Citazioni: {p.get('citationCount', 0)} (influential: {p.get('influentialCitationCount', 0)})")
            if p.get("tldr"):
                print(f"  TL;DR: {p['tldr'].get('text', '')}")
            oa = p.get("openAccessPdf")
            if oa:
                print(f"  PDF open: {oa.get('url', '')}")
            ext = p.get("externalIds") or {}
            if ext.get("DOI"):
                print(f"  DOI: {ext['DOI']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

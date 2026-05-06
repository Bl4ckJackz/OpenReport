#!/usr/bin/env python3
"""arxiv-import.py — import paper da arXiv via API.

Usage:
    arxiv-import.py --id 2301.12345                    # fetch per ID
    arxiv-import.py --search "attention transformer" --max 10
    arxiv-import.py --id 2301.12345 --bibtex           # emit bibtex entry
    arxiv-import.py --id 2301.12345 --append refs.bib  # append a .bib

Nessuna dipendenza esterna (stdlib only).
"""
import argparse
import pathlib
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ARXIV_API = "http://export.arxiv.org/api/query"
ATOM_NS = "{http://www.w3.org/2005/Atom}"


def http_get(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "relazione-arxiv/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8")


def parse_entry(entry):
    arxiv_id = entry.find(f"{ATOM_NS}id").text.split("/abs/")[-1]
    title = entry.find(f"{ATOM_NS}title").text.strip().replace("\n", " ")
    summary = entry.find(f"{ATOM_NS}summary").text.strip().replace("\n", " ")
    authors = [a.find(f"{ATOM_NS}name").text for a in entry.findall(f"{ATOM_NS}author")]
    published = entry.find(f"{ATOM_NS}published").text
    year = published[:4] if published else ""
    categories = [c.attrib.get("term") for c in entry.findall(f"{ATOM_NS}category")]
    doi_elem = entry.find("{http://arxiv.org/schemas/atom}doi")
    doi = doi_elem.text if doi_elem is not None else ""
    return {
        "arxiv_id": arxiv_id, "title": title, "summary": summary,
        "authors": authors, "year": year, "published": published,
        "categories": categories, "doi": doi,
        "url": f"https://arxiv.org/abs/{arxiv_id}",
    }


def fetch_by_id(arxiv_id):
    url = f"{ARXIV_API}?id_list={urllib.parse.quote(arxiv_id)}"
    xml = http_get(url)
    root = ET.fromstring(xml)
    entries = root.findall(f"{ATOM_NS}entry")
    return [parse_entry(e) for e in entries]


def search(query, max_results=10):
    url = f"{ARXIV_API}?search_query=all:{urllib.parse.quote(query)}&max_results={max_results}"
    xml = http_get(url)
    root = ET.fromstring(xml)
    return [parse_entry(e) for e in root.findall(f"{ATOM_NS}entry")]


def to_bibtex(entry):
    authors_family = [a.split()[-1] for a in entry["authors"]]
    key = f"{authors_family[0] if authors_family else 'Anon'}{entry['year']}{re.sub(r'[^A-Za-z]', '', entry['title'].split()[0])[:8]}"
    lines = [f"@article{{{key},"]
    lines.append(f"  author = {{{' and '.join(entry['authors'])}}},")
    lines.append(f"  title = {{{entry['title']}}},")
    lines.append(f"  journal = {{arXiv preprint arXiv:{entry['arxiv_id']}}},")
    lines.append(f"  year = {{{entry['year']}}},")
    if entry.get("doi"):
        lines.append(f"  doi = {{{entry['doi']}}},")
    lines.append(f"  url = {{{entry['url']}}},")
    lines.append("}")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--id")
    g.add_argument("--search")
    ap.add_argument("--max", type=int, default=10)
    ap.add_argument("--bibtex", action="store_true")
    ap.add_argument("--append", help="Append bibtex a file")
    args = ap.parse_args()

    entries = fetch_by_id(args.id) if args.id else search(args.search, args.max)
    if not entries:
        print("[INFO] nessun risultato", file=sys.stderr)
        return 1

    for e in entries:
        if args.bibtex or args.append:
            bib = to_bibtex(e)
            if args.append:
                with open(args.append, "a", encoding="utf-8") as f:
                    f.write("\n" + bib + "\n")
                print(f"[OK] appended {e['arxiv_id']} -> {args.append}", file=sys.stderr)
            else:
                print(bib + "\n")
        else:
            print(f"[{e['arxiv_id']}] {e['title']}")
            print(f"  Autori: {', '.join(e['authors'][:4])}{'...' if len(e['authors'])>4 else ''}")
            print(f"  Anno: {e['year']}  Categorie: {', '.join(e['categories'][:3])}")
            print(f"  URL: {e['url']}")
            print(f"  Abstract: {e['summary'][:300]}...\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

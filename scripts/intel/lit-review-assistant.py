#!/usr/bin/env python3
"""lit-review-assistant.py — clusterizzazione tematica paper per literature review.

Legge research-notes.md (con entry formattate), estrae:
- Temi ricorrenti (keyword frequency)
- Cluster paper per tema (TF-IDF simplified)
- Tabella comparativa autori × temi
- Propone struttura capitolo "Stato dell'arte"

Input atteso — research-notes.md formato:
    ## Paper 1
    Titolo: ...
    Autori: ...
    Anno: ...
    Abstract: ...
    Keywords: ...

Output: lit-review-map.md con clusterizzazione e proposta capitoli.

Usage:
    lit-review-assistant.py research-notes.md [-o lit-review.md]
"""
import argparse
import pathlib
import re
import sys
from collections import Counter, defaultdict

PAPER_BLOCK_RE = re.compile(r"^##\s+.+?$((?:(?!^##\s).)*)", flags=re.MULTILINE | re.DOTALL)
FIELD_RE = re.compile(r"^(Titolo|Autori|Anno|Abstract|Keywords|URL|DOI):\s*(.+?)$", flags=re.MULTILINE | re.IGNORECASE)

STOPWORDS = {
    "the", "and", "for", "are", "with", "this", "that", "from", "have", "was",
    "della", "dello", "delle", "degli", "sono", "essere", "hanno", "questa", "questo",
    "paper", "study", "work", "result", "analysis", "method", "approach", "using", "use",
}


def extract_papers(text):
    papers = []
    for m in re.finditer(r"^##\s+(.+?)\s*$", text, flags=re.MULTILINE):
        title_line = m.group(1)
        start = m.end()
        next_match = re.search(r"^##\s", text[start:], flags=re.MULTILINE)
        end = start + next_match.start() if next_match else len(text)
        block = text[start:end]
        fields = {"section": title_line}
        for fm in FIELD_RE.finditer(block):
            key = fm.group(1).lower()
            value = fm.group(2).strip()
            fields[key] = value
        # Abstract se multilinea
        abstract_match = re.search(r"^Abstract:\s*(.+?)(?=\n(?:[A-Z]\w+:|$))", block, flags=re.MULTILINE | re.DOTALL | re.IGNORECASE)
        if abstract_match:
            fields["abstract"] = abstract_match.group(1).strip().replace("\n", " ")
        papers.append(fields)
    return papers


def extract_keywords(paper, n=5):
    text = " ".join(paper.get(k, "") for k in ("titolo", "abstract", "keywords"))
    words = re.findall(r"\b[a-zà-ú]{4,}\b", text.lower())
    filtered = [w for w in words if w not in STOPWORDS]
    return [k for k, _ in Counter(filtered).most_common(n)]


def cluster_papers(papers, num_clusters=5):
    all_keywords = Counter()
    paper_keywords = {}
    for i, p in enumerate(papers):
        kws = extract_keywords(p, n=10)
        paper_keywords[i] = set(kws)
        all_keywords.update(kws)

    top_themes = [k for k, _ in all_keywords.most_common(num_clusters)]
    clusters = defaultdict(list)
    unassigned = []
    for i, p in enumerate(papers):
        assigned = False
        for theme in top_themes:
            if theme in paper_keywords[i]:
                clusters[theme].append(p)
                assigned = True
                break
        if not assigned:
            unassigned.append(p)
    return top_themes, clusters, unassigned


def render_report(papers, themes, clusters, unassigned):
    out = ["# Literature Review Map\n"]
    out.append(f"Paper analizzati: **{len(papers)}**  ")
    out.append(f"Temi principali identificati: **{len(themes)}**\n")

    out.append("## Cluster tematici\n")
    for theme in themes:
        bucket = clusters.get(theme, [])
        out.append(f"\n### Tema: {theme} ({len(bucket)} paper)\n")
        for p in bucket:
            title = p.get("titolo", p.get("section", ""))
            authors = p.get("autori", "?")
            year = p.get("anno", "?")
            out.append(f"- **{title[:100]}** — {authors[:60]} ({year})")

    if unassigned:
        out.append(f"\n### Altri paper ({len(unassigned)})\n")
        for p in unassigned:
            out.append(f"- {p.get('titolo', p.get('section', ''))[:100]}")

    out.append("\n## Proposta struttura capitolo \"Stato dell'arte\"\n")
    out.append("```")
    out.append("2. Stato dell'arte")
    for i, theme in enumerate(themes, 1):
        out.append(f"    2.{i} {theme.capitalize()}")
    out.append(f"    2.{len(themes)+1} Sintesi e posizionamento della tesi")
    out.append("```\n")

    out.append("## Tabella comparativa\n")
    out.append("| Paper | " + " | ".join(themes) + " |")
    out.append("|---|" + "|".join("---" for _ in themes) + "|")
    for p in papers[:20]:
        title = p.get("titolo", p.get("section", ""))[:40]
        row = [title]
        kws = set(extract_keywords(p, n=10))
        for theme in themes:
            row.append("✓" if theme in kws else "")
        out.append("| " + " | ".join(row) + " |")

    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("research_notes")
    ap.add_argument("--clusters", type=int, default=5)
    ap.add_argument("-o", "--output")
    args = ap.parse_args()

    p = pathlib.Path(args.research_notes)
    if not p.exists():
        print(f"[ERR] {p} non trovato", file=sys.stderr)
        return 2

    text = p.read_text(encoding="utf-8")
    papers = extract_papers(text)
    if len(papers) < 2:
        print(f"[WARN] solo {len(papers)} paper trovati, lit-review minimo 5", file=sys.stderr)

    themes, clusters, unassigned = cluster_papers(papers, args.clusters)
    report = render_report(papers, themes, clusters, unassigned)

    if args.output:
        pathlib.Path(args.output).write_text(report, encoding="utf-8")
        print(f"[OK] {args.output}")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""import-feedback.py — estrae commenti e track-changes da docx di revisione.

Output: JSON machine-readable con tutti i commenti + track-changes, per applicazione
interattiva nel refinement loop.

Strategia:
1. docx è uno zip con word/comments.xml e word/document.xml
2. Parsa comments.xml per estrarre (author, data, testo, range_id)
3. Parsa document.xml per estrarre w:ins / w:del (track-changes)

Usage:
    import-feedback.py <feedback.docx> [--output feedback.json] [--markdown]
"""
import argparse
import json
import pathlib
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def extract_comments(docx_path):
    comments = []
    try:
        with zipfile.ZipFile(docx_path) as z:
            if "word/comments.xml" in z.namelist():
                tree = ET.fromstring(z.read("word/comments.xml"))
                for c in tree.findall(f"{W_NS}comment"):
                    text = "".join(t.text or "" for t in c.iter(f"{W_NS}t"))
                    comments.append({
                        "id": c.attrib.get(f"{W_NS}id"),
                        "author": c.attrib.get(f"{W_NS}author", ""),
                        "date": c.attrib.get(f"{W_NS}date", ""),
                        "text": text.strip(),
                    })
    except Exception as e:
        print(f"[ERR] lettura comments: {e}", file=sys.stderr)
    return comments


def extract_track_changes(docx_path):
    insertions = []
    deletions = []
    try:
        with zipfile.ZipFile(docx_path) as z:
            if "word/document.xml" in z.namelist():
                tree = ET.fromstring(z.read("word/document.xml"))
                for ins in tree.iter(f"{W_NS}ins"):
                    text = "".join(t.text or "" for t in ins.iter(f"{W_NS}t"))
                    insertions.append({
                        "author": ins.attrib.get(f"{W_NS}author", ""),
                        "date": ins.attrib.get(f"{W_NS}date", ""),
                        "text": text.strip(),
                    })
                for delete in tree.iter(f"{W_NS}del"):
                    text = "".join(t.text or "" for t in delete.iter(f"{W_NS}delText"))
                    deletions.append({
                        "author": delete.attrib.get(f"{W_NS}author", ""),
                        "date": delete.attrib.get(f"{W_NS}date", ""),
                        "text": text.strip(),
                    })
    except Exception as e:
        print(f"[ERR] lettura track-changes: {e}", file=sys.stderr)
    return insertions, deletions


def format_markdown(comments, insertions, deletions):
    lines = ["# Feedback ricevuto\n"]
    if comments:
        lines.append(f"## Commenti ({len(comments)})\n")
        for c in comments:
            lines.append(f"- **{c.get('author', '?')}** ({c.get('date', '')[:10]}): {c.get('text')}")
    if insertions:
        lines.append(f"\n## Inserimenti proposti ({len(insertions)})\n")
        for i in insertions:
            lines.append(f"- _{i.get('author', '?')}_ aggiunge: \"{i.get('text')}\"")
    if deletions:
        lines.append(f"\n## Cancellazioni proposte ({len(deletions)})\n")
        for d in deletions:
            lines.append(f"- _{d.get('author', '?')}_ rimuove: \"{d.get('text')}\"")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--output", "-o", default=None)
    ap.add_argument("--markdown", action="store_true")
    args = ap.parse_args()

    p = pathlib.Path(args.file)
    if not p.exists() or p.suffix.lower() != ".docx":
        print(f"[ERR] file docx non valido: {p}", file=sys.stderr)
        return 2

    comments = extract_comments(str(p))
    insertions, deletions = extract_track_changes(str(p))

    data = {
        "source": str(p.name),
        "comments": comments,
        "insertions": insertions,
        "deletions": deletions,
    }

    if args.markdown:
        out_text = format_markdown(comments, insertions, deletions)
    else:
        out_text = json.dumps(data, indent=2, ensure_ascii=False)

    if args.output:
        pathlib.Path(args.output).write_text(out_text, encoding="utf-8")
        print(f"[OK] {len(comments)} commenti + {len(insertions)} ins + {len(deletions)} del -> {args.output}")
    else:
        print(out_text)

    return 0


if __name__ == "__main__":
    sys.exit(main())

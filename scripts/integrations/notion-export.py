#!/usr/bin/env python3
"""notion-export.py — crea pagina Notion con contenuto della relazione.

Notion API richiede block structure limitata; convertiamo markdown in un subset (h1-h3, paragrafi, list, code).

Usage:
    export NOTION_API_KEY=secret_xxx
    export NOTION_PARENT_DB=database_id_or_page_id
    notion-export.py <file.md> --title "Titolo"
"""
import argparse
import json
import os
import pathlib
import re
import sys
import urllib.request

NOTION_API = "https://api.notion.com/v1"


def api(method, path, body=None):
    key = os.environ.get("NOTION_API_KEY")
    parent = os.environ.get("NOTION_PARENT_DB")
    if not (key and parent):
        print("[ERR] set NOTION_API_KEY, NOTION_PARENT_DB", file=sys.stderr)
        sys.exit(2)
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(f"{NOTION_API}{path}", data=data, method=method, headers={
        "Authorization": f"Bearer {key}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def md_to_blocks(md):
    blocks = []
    for line in md.split("\n"):
        if line.startswith("# "):
            blocks.append({"type": "heading_1", "heading_1": {"rich_text": [{"type": "text", "text": {"content": line[2:].strip()}}]}})
        elif line.startswith("## "):
            blocks.append({"type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": line[3:].strip()}}]}})
        elif line.startswith("### "):
            blocks.append({"type": "heading_3", "heading_3": {"rich_text": [{"type": "text", "text": {"content": line[4:].strip()}}]}})
        elif re.match(r"^[-*]\s+", line):
            blocks.append({"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": re.sub(r'^[-*]\s+', '', line)}}]}})
        elif line.strip():
            blocks.append({"type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": line}}]}})
    return blocks[:100]  # Notion limit


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--title", required=True)
    args = ap.parse_args()

    md = pathlib.Path(args.file).read_text(encoding="utf-8")
    blocks = md_to_blocks(md)
    parent = os.environ.get("NOTION_PARENT_DB")
    body = {
        "parent": {"database_id": parent} if len(parent) == 32 else {"page_id": parent},
        "properties": {"title": {"title": [{"text": {"content": args.title}}]}} if len(parent) == 32 else {"title": [{"text": {"content": args.title}}]},
        "children": blocks,
    }
    result = api("POST", "/pages", body)
    print(f"[OK] pagina Notion creata: {result.get('url', '')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

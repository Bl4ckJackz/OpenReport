#!/usr/bin/env python3
"""confluence-export.py — pubblica markdown/HTML su Confluence Cloud.

Usage:
    export CONFLUENCE_BASE_URL=https://your.atlassian.net/wiki
    export CONFLUENCE_EMAIL=user@example.com
    export CONFLUENCE_API_TOKEN=xxx
    confluence-export.py <file.md> --space KEY --title "Titolo" [--parent PAGE_ID]
"""
import argparse
import base64
import json
import os
import pathlib
import subprocess
import sys
import urllib.request


def api(method, path, body=None):
    base = os.environ.get("CONFLUENCE_BASE_URL")
    email = os.environ.get("CONFLUENCE_EMAIL")
    token = os.environ.get("CONFLUENCE_API_TOKEN")
    if not (base and email and token):
        print("[ERR] set CONFLUENCE_BASE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN", file=sys.stderr)
        sys.exit(2)
    auth = base64.b64encode(f"{email}:{token}".encode()).decode()
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(f"{base}{path}", data=data, method=method, headers={
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def md_to_html(md_path):
    try:
        return subprocess.check_output(["pandoc", md_path, "-t", "html", "--wrap=none"]).decode()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return pathlib.Path(md_path).read_text(encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--space", required=True, help="Confluence space key")
    ap.add_argument("--title", required=True)
    ap.add_argument("--parent", help="Parent page ID")
    args = ap.parse_args()

    html = md_to_html(args.file)
    body = {
        "type": "page",
        "title": args.title,
        "space": {"key": args.space},
        "body": {"storage": {"value": html, "representation": "storage"}},
    }
    if args.parent:
        body["ancestors"] = [{"id": args.parent}]
    result = api("POST", "/rest/api/content", body)
    print(f"[OK] pubblicata: {result.get('_links', {}).get('webui', '')}")
    print(f"    ID: {result.get('id')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

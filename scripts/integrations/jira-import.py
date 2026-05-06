#!/usr/bin/env python3
"""jira-import.py — importa issue e sprint da Jira per status-report.

Usage:
    export JIRA_BASE_URL=https://your.atlassian.net
    export JIRA_EMAIL=user@example.com
    export JIRA_API_TOKEN=...
    jira-import.py --project PRJ --jql "sprint in openSprints()" --output issues.json
    jira-import.py --project PRJ --since 2026-04-01 --md > section.md
"""
import argparse
import base64
import json
import os
import pathlib
import sys
import urllib.parse
import urllib.request


def api_get(path, params=None):
    base = os.environ.get("JIRA_BASE_URL")
    email = os.environ.get("JIRA_EMAIL")
    token = os.environ.get("JIRA_API_TOKEN")
    if not (base and email and token):
        print("[ERR] set JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN", file=sys.stderr)
        sys.exit(2)
    url = f"{base}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    auth = base64.b64encode(f"{email}:{token}".encode()).decode()
    req = urllib.request.Request(url, headers={
        "Authorization": f"Basic {auth}",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def search(jql, fields="summary,status,assignee,priority,issuetype,resolutiondate"):
    params = {"jql": jql, "maxResults": 100, "fields": fields}
    return api_get("/rest/api/3/search", params)


def format_md(issues):
    out = [f"## Issue Jira ({len(issues)})\n",
           "| Key | Titolo | Tipo | Status | Assegnatario |",
           "|---|---|---|---|---|"]
    for i in issues:
        f = i.get("fields", {})
        assignee = (f.get("assignee") or {}).get("displayName", "—")
        out.append(f"| {i['key']} | {f.get('summary', '')} | {f.get('issuetype', {}).get('name', '')} | {f.get('status', {}).get('name', '')} | {assignee} |")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project")
    ap.add_argument("--jql")
    ap.add_argument("--since", help="Issue risolti dopo YYYY-MM-DD")
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--output", default=None)
    args = ap.parse_args()

    jql = args.jql or ""
    if args.project and not jql:
        jql = f"project = {args.project}"
    if args.since:
        jql = (jql + " AND " if jql else "") + f"resolved >= '{args.since}'"

    data = search(jql)
    issues = data.get("issues", [])
    if args.md:
        out = format_md(issues)
    else:
        out = json.dumps(issues, indent=2, ensure_ascii=False)

    if args.output:
        pathlib.Path(args.output).write_text(out, encoding="utf-8")
        print(f"[OK] {len(issues)} issues -> {args.output}", file=sys.stderr)
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())

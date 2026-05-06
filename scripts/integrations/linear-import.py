#!/usr/bin/env python3
"""linear-import.py — importa issues e cycles da Linear via GraphQL.

Usage:
    export LINEAR_API_KEY=lin_api_xxx
    linear-import.py --team ENG --cycle current --md
    linear-import.py --team ENG --since 2026-04-01 --output issues.json
"""
import argparse
import json
import os
import pathlib
import sys
import urllib.request

LINEAR_API = "https://api.linear.app/graphql"


def gql(query, variables=None):
    key = os.environ.get("LINEAR_API_KEY")
    if not key:
        print("[ERR] set LINEAR_API_KEY", file=sys.stderr)
        sys.exit(2)
    payload = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(LINEAR_API, data=payload, headers={
        "Authorization": key,
        "Content-Type": "application/json",
    }, method="POST")
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.loads(r.read().decode("utf-8"))
    if "errors" in data:
        print(f"[ERR] {data['errors']}", file=sys.stderr)
        sys.exit(1)
    return data["data"]


def fetch_issues(team_key, since=None):
    filter_clause = f'team: {{ key: {{ eq: "{team_key}" }} }}'
    if since:
        filter_clause += f', completedAt: {{ gte: "{since}T00:00:00Z" }}'
    q = f"""
    query {{
      issues(filter: {{ {filter_clause} }}, first: 100) {{
        nodes {{ identifier title state {{ name }} assignee {{ name }} priority }}
      }}
    }}
    """
    return gql(q)["issues"]["nodes"]


def format_md(issues):
    out = [f"## Issue Linear ({len(issues)})\n",
           "| ID | Titolo | Status | Assegnatario | Priorità |",
           "|---|---|---|---|---|"]
    prio_map = {0: "No", 1: "Urgente", 2: "Alta", 3: "Media", 4: "Bassa"}
    for i in issues:
        state = (i.get("state") or {}).get("name", "")
        assignee = (i.get("assignee") or {}).get("name", "—")
        out.append(f"| {i['identifier']} | {i['title']} | {state} | {assignee} | {prio_map.get(i.get('priority', 0), '')} |")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--team", required=True)
    ap.add_argument("--since")
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--output")
    args = ap.parse_args()

    issues = fetch_issues(args.team, args.since)
    out = format_md(issues) if args.md else json.dumps(issues, indent=2, ensure_ascii=False)
    if args.output:
        pathlib.Path(args.output).write_text(out, encoding="utf-8")
        print(f"[OK] {len(issues)} -> {args.output}", file=sys.stderr)
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())

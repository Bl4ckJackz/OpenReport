#!/usr/bin/env python3
"""tag-manager.py — tag system per session-state.

Aggiunge/rimuove/cerca tag su sessioni /relazione per organizzazione e search.

Storage: `state.tags[]` come array di stringhe lower-case.

Usage:
    tag-manager.py add <state.json> <tag1> <tag2>...
    tag-manager.py remove <state.json> <tag>
    tag-manager.py list <state.json>
    tag-manager.py search --root relazioni/ --any cliente,acme
    tag-manager.py search --root relazioni/ --all urgent,2026
    tag-manager.py tags --root relazioni/     # conta tag totali
"""
import argparse
import json
import pathlib
import sys
from collections import Counter


def load_state(path):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


def save_state(path, state):
    pathlib.Path(path).write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def cmd_add(args):
    state = load_state(args.state)
    existing = set(state.get("tags", []))
    new_tags = {t.lower().strip() for t in args.tags if t.strip()}
    state["tags"] = sorted(existing | new_tags)
    save_state(args.state, state)
    print(f"[OK] tags: {', '.join(state['tags'])}")
    return 0


def cmd_remove(args):
    state = load_state(args.state)
    existing = set(state.get("tags", []))
    to_remove = {args.tag.lower().strip()}
    state["tags"] = sorted(existing - to_remove)
    save_state(args.state, state)
    print(f"[OK] rimosso '{args.tag}'; tags rimanenti: {', '.join(state['tags']) or '(nessuno)'}")
    return 0


def cmd_list(args):
    state = load_state(args.state)
    tags = state.get("tags", [])
    if not tags:
        print("(nessun tag)")
    else:
        for t in tags:
            print(f"  {t}")
    return 0


def scan_sessions(root):
    root = pathlib.Path(root)
    results = []
    for state_path in root.rglob(".session/session-state.json"):
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
            results.append((state_path.parent.parent, state))
        except Exception:
            continue
    return results


def cmd_search(args):
    root = pathlib.Path(args.root)
    sessions = scan_sessions(root)

    any_tags = {t.lower().strip() for t in args.any.split(",") if t.strip()} if args.any else set()
    all_tags = {t.lower().strip() for t in args.all.split(",") if t.strip()} if args.all else set()

    matches = []
    for folder, state in sessions:
        tags = set(state.get("tags", []))
        if any_tags and not (any_tags & tags):
            continue
        if all_tags and not all_tags.issubset(tags):
            continue
        matches.append((folder, state))

    if not matches:
        print("[INFO] nessun match")
        return 1

    for folder, state in matches:
        title = (state.get("cover") or {}).get("titolo", folder.name)
        tipo = (state.get("answers") or {}).get("tipologia", "?")
        status = state.get("status", "?")
        tags = ", ".join(state.get("tags", []))
        print(f"  [{status}] {folder.name:30} — {tipo:20} — \"{title[:40]}\"")
        print(f"      tags: {tags}")
    print(f"\n{len(matches)} match su {len(sessions)} sessioni totali")
    return 0


def cmd_tags(args):
    sessions = scan_sessions(args.root)
    counter = Counter()
    for _, state in sessions:
        for t in state.get("tags", []):
            counter[t] += 1
    if not counter:
        print("(nessun tag in alcuna sessione)")
        return 0
    print(f"Tag frequenti ({sum(counter.values())} tag totali su {len(sessions)} sessioni):")
    for tag, count in counter.most_common():
        print(f"  {count:4d}  {tag}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add")
    a.add_argument("state")
    a.add_argument("tags", nargs="+")

    r = sub.add_parser("remove")
    r.add_argument("state")
    r.add_argument("tag")

    l = sub.add_parser("list")
    l.add_argument("state")

    s = sub.add_parser("search")
    s.add_argument("--root", default=".")
    s.add_argument("--any", help="match se almeno uno tra questi tag (csv)")
    s.add_argument("--all", help="match se tutti questi tag (csv)")

    t = sub.add_parser("tags")
    t.add_argument("--root", default=".")

    args = ap.parse_args()
    handlers = {"add": cmd_add, "remove": cmd_remove, "list": cmd_list,
                "search": cmd_search, "tags": cmd_tags}
    return handlers[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""audit-trail.py — logger append-only per approval workflow.

Append riga JSONL a .session/audit-trail.jsonl per ogni evento rilevante:
- status_change (draft → in-review → approved → archived)
- review_requested (mittente, destinatari, data)
- approval_granted (approver, data)
- feedback_imported (source file, num commenti)
- document_signed (approver, signature ref)

Usage:
    audit-trail.py log --state <state.json> --action <action> [--by <name>] [--note "..."]
    audit-trail.py show --state <state.json>
    audit-trail.py verify --state <state.json>       # verifica hash chain (se --hashed)
"""
import argparse
import hashlib
import json
import pathlib
import sys
from datetime import datetime


def trail_path(state_path):
    state = json.loads(pathlib.Path(state_path).read_text(encoding="utf-8"))
    out_folder = state.get("output_folder", pathlib.Path(state_path).parent.parent)
    return pathlib.Path(out_folder) / ".session" / "audit-trail.jsonl"


def append(trail_p, entry, prev_hash=""):
    trail_p.parent.mkdir(parents=True, exist_ok=True)
    entry["ts"] = datetime.now().isoformat()
    if prev_hash:
        entry["prev_hash"] = prev_hash
    canonical = json.dumps(entry, sort_keys=True, ensure_ascii=False).encode("utf-8")
    entry["hash"] = hashlib.sha256(canonical).hexdigest()[:16]
    with open(trail_p, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def get_last_hash(trail_p):
    if not trail_p.exists():
        return ""
    lines = trail_p.read_text(encoding="utf-8").strip().split("\n")
    if not lines:
        return ""
    try:
        return json.loads(lines[-1]).get("hash", "")
    except Exception:
        return ""


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("log")
    l.add_argument("--state", required=True)
    l.add_argument("--action", required=True)
    l.add_argument("--by", default="")
    l.add_argument("--note", default="")
    l.add_argument("--from-status", default="")
    l.add_argument("--to-status", default="")
    s = sub.add_parser("show")
    s.add_argument("--state", required=True)
    v = sub.add_parser("verify")
    v.add_argument("--state", required=True)
    args = ap.parse_args()

    trail_p = trail_path(args.state)

    if args.cmd == "log":
        prev = get_last_hash(trail_p)
        entry = {"action": args.action, "by": args.by, "note": args.note}
        if args.from_status:
            entry["from_status"] = args.from_status
        if args.to_status:
            entry["to_status"] = args.to_status
        append(trail_p, entry, prev_hash=prev)
        print(f"[OK] audit entry logged in {trail_p}")
        return 0

    if args.cmd == "show":
        if not trail_p.exists():
            print(f"[INFO] nessun audit trail: {trail_p}")
            return 0
        for line in trail_p.read_text(encoding="utf-8").strip().split("\n"):
            try:
                e = json.loads(line)
                print(f"  [{e.get('ts', '?')[:19]}] {e.get('action')} by {e.get('by', '-')} — {e.get('note', '')}")
            except Exception:
                pass
        return 0

    if args.cmd == "verify":
        if not trail_p.exists():
            print(f"[INFO] nessun audit trail: {trail_p}")
            return 0
        lines = trail_p.read_text(encoding="utf-8").strip().split("\n")
        prev = ""
        broken = 0
        for i, line in enumerate(lines):
            try:
                e = json.loads(line)
                declared_prev = e.get("prev_hash", "")
                if i > 0 and declared_prev != prev:
                    print(f"[FAIL] riga {i+1}: prev_hash mismatch (atteso {prev}, trovato {declared_prev})")
                    broken += 1
                prev = e.get("hash", "")
            except Exception:
                print(f"[FAIL] riga {i+1}: JSON invalido")
                broken += 1
        if broken == 0:
            print(f"[OK] audit trail integro: {len(lines)} entry verificate")
        return 0 if broken == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

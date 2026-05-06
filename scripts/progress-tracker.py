#!/usr/bin/env python3
"""progress-tracker.py — calcola e aggiorna progresso relazione in session-state.

Analizza draft corrente e popola `state.progress`:
- pages_estimated (da word count / 400)
- pages_target (da answers)
- placeholders_remaining ([DA COMPLETARE: ...])
- mock_remaining ([MOCK])
- riferimenti_da_verificare ([RIFERIMENTO DA VERIFICARE])

Usage:
    progress-tracker.py <draft> --state <state.json> [--print-bar]
"""
import argparse
import json
import pathlib
import re
import sys
from datetime import datetime


def count(text, pattern):
    return len(re.findall(pattern, text))


def render_bar(current, target, width=40):
    if target <= 0:
        return f"[{'?' * width}]"
    pct = min(1.0, current / target)
    filled = int(pct * width)
    return f"[{'█' * filled}{'░' * (width - filled)}] {current}/{target} ({pct*100:.0f}%)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("draft")
    ap.add_argument("--state", required=True)
    ap.add_argument("--print-bar", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    draft_path = pathlib.Path(args.draft)
    state_path = pathlib.Path(args.state)
    if not draft_path.exists():
        print(f"[ERR] draft non trovato: {draft_path}", file=sys.stderr)
        return 2
    if not state_path.exists():
        print(f"[ERR] state non trovato: {state_path}", file=sys.stderr)
        return 2

    text = draft_path.read_text(encoding="utf-8")
    words = len(re.findall(r"\S+", text))
    pages = round(words / 400, 1)

    placeholders = count(text, r"\[DA COMPLETARE[^\]]*\]")
    mocks = count(text, r"\[MOCK\]")
    ref_to_verify = count(text, r"\[RIFERIMENTO DA VERIFICARE\]")

    state = json.loads(state_path.read_text(encoding="utf-8"))
    target = (state.get("answers") or {}).get("lunghezza_target_pagine", 0)

    progress = {
        "pages_estimated": pages,
        "pages_target": target,
        "placeholders_remaining": placeholders,
        "mock_remaining": mocks,
        "ref_to_verify": ref_to_verify,
        "words": words,
        "last_checked_at": datetime.now().isoformat(),
    }

    state["progress"] = {**state.get("progress", {}), **progress}
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")

    if args.json:
        print(json.dumps(progress, indent=2, ensure_ascii=False))
        return 0

    print(f"Draft: {draft_path.name}")
    print(f"  Parole: {words}    Pagine stimate: {pages}")
    if target > 0:
        print(f"  Target: {target} pp     {render_bar(pages, target)}")
    if placeholders:
        print(f"  [DA COMPLETARE]: {placeholders}")
    if mocks:
        print(f"  [MOCK]: {mocks}")
    if ref_to_verify:
        print(f"  [RIFERIMENTO DA VERIFICARE]: {ref_to_verify}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""redline-generator.py — word-level diff of two markdown files → CriticMarkup."""
from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

TOKEN_RE = re.compile(r"(\s+|[^\s\w]|\w+)")

SUBSTITUTION_MAX_TOKENS = 8


def tokenize(text: str) -> list[str]:
    return [t for t in TOKEN_RE.findall(text) if t]


def diff_to_critic(baseline_tokens: list[str], current_tokens: list[str]) -> str:
    sm = difflib.SequenceMatcher(a=baseline_tokens, b=current_tokens, autojunk=False)
    out: list[str] = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        old = "".join(baseline_tokens[i1:i2])
        new = "".join(current_tokens[j1:j2])
        if tag == "equal":
            out.append(new)
        elif tag == "insert":
            out.append(f"{{++{new}++}}")
        elif tag == "delete":
            out.append(f"{{--{old}--}}")
        elif tag == "replace":
            old_token_count = i2 - i1
            new_token_count = j2 - j1
            if old_token_count <= SUBSTITUTION_MAX_TOKENS and new_token_count <= SUBSTITUTION_MAX_TOKENS:
                out.append(f"{{~~{old.strip()}~>{new.strip()}~~}}")
            else:
                out.append(f"{{--{old}--}}{{++{new}++}}")
    return "".join(out)


def generate(baseline_path: str, current_path: str, out_path: str, mode: str = "word") -> dict:
    baseline = Path(baseline_path).read_text(encoding="utf-8")
    current = Path(current_path).read_text(encoding="utf-8")
    b_tokens = tokenize(baseline)
    c_tokens = tokenize(current)
    redlined = diff_to_critic(b_tokens, c_tokens)
    Path(out_path).write_text(redlined, encoding="utf-8")
    return {
        "baseline_tokens": len(b_tokens),
        "current_tokens": len(c_tokens),
        "mode": mode,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("baseline")
    ap.add_argument("current")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--mode", choices=["word", "sentence"], default="word")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args(argv)
    stats = generate(args.baseline, args.current, args.output, mode=args.mode)
    if args.verbose:
        print(f"[redline] mode={stats['mode']} baseline={stats['baseline_tokens']} current={stats['current_tokens']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

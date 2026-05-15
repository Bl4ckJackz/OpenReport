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
BLOCK_REWRITE_THRESHOLD = 0.7
PARAGRAPH_SPLIT_RE = re.compile(r"(\n\s*\n)")


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


def _diff_paragraph(b_text: str, c_text: str) -> str:
    b_tokens = tokenize(b_text)
    c_tokens = tokenize(c_text)
    # Compute change ratio over non-whitespace tokens only, so that shared
    # inter-word spaces don't artificially lower the changed fraction.
    b_content = [t for t in b_tokens if t.strip()]
    c_content = [t for t in c_tokens if t.strip()]
    sm_content = difflib.SequenceMatcher(a=b_content, b=c_content, autojunk=False)
    matching = sum(size for _, _, size in sm_content.get_matching_blocks())
    total = max(len(b_content), len(c_content))
    if total > 0 and (1.0 - matching / total) >= BLOCK_REWRITE_THRESHOLD:
        return f"{{--{b_text}--}}{{++{c_text}++}}"
    return diff_to_critic(b_tokens, c_tokens)


def generate(baseline_path: str, current_path: str, out_path: str, mode: str = "word") -> dict:
    baseline = Path(baseline_path).read_text(encoding="utf-8")
    current = Path(current_path).read_text(encoding="utf-8")
    b_parts = PARAGRAPH_SPLIT_RE.split(baseline)
    c_parts = PARAGRAPH_SPLIT_RE.split(current)
    b_paras = [p for p in b_parts if p and not PARAGRAPH_SPLIT_RE.fullmatch(p)]
    c_paras = [p for p in c_parts if p and not PARAGRAPH_SPLIT_RE.fullmatch(p)]
    b_seps = [p for p in b_parts if PARAGRAPH_SPLIT_RE.fullmatch(p)]
    sm = difflib.SequenceMatcher(a=b_paras, b=c_paras, autojunk=False)
    out_parts: list[str] = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for p in c_paras[j1:j2]:
                out_parts.append(p)
        elif tag == "insert":
            for p in c_paras[j1:j2]:
                out_parts.append(f"{{++{p}++}}")
        elif tag == "delete":
            for p in b_paras[i1:i2]:
                out_parts.append(f"{{--{p}--}}")
        elif tag == "replace":
            for b_para, c_para in zip(b_paras[i1:i2], c_paras[j1:j2]):
                out_parts.append(_diff_paragraph(b_para, c_para))
            extra_b = b_paras[i1 + (j2 - j1) : i2]
            extra_c = c_paras[j1 + (i2 - i1) : j2]
            for p in extra_b:
                out_parts.append(f"{{--{p}--}}")
            for p in extra_c:
                out_parts.append(f"{{++{p}++}}")
    sep = b_seps[0] if b_seps else "\n\n"
    redlined = sep.join(out_parts)
    Path(out_path).write_text(redlined, encoding="utf-8")
    n_ins = redlined.count("{++")
    n_del = redlined.count("{--")
    n_sub = redlined.count("{~~")
    return {
        "baseline_tokens": sum(len(tokenize(p)) for p in b_paras),
        "current_tokens": sum(len(tokenize(p)) for p in c_paras),
        "mode": mode,
        "ins_count": n_ins,
        "del_count": n_del,
        "sub_count": n_sub,
        "total_spans": n_ins + n_del + n_sub,
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

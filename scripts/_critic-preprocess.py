#!/usr/bin/env python3
"""_critic-preprocess.py — convert CriticMarkup syntax to pandoc bracketed-span markdown.

Why: pandoc 3.x removed the `critic_markup` extension. Bracketed-span syntax
`[text]{.critic-add}` produces the same AST Span node with the same class
that our critic-to-latex.py / critic-to-typst.py filters detect.

Usage:
    _critic-preprocess.py <input.md> -o <output.md>
    cat input.md | _critic-preprocess.py -

Output: a `.md` where:
    {++inserito++}    →  [inserito]{.critic-add}
    {--cancellato--}  →  [cancellato]{.critic-del}
    {~~vecchio~>nuovo~~} → [vecchio]{.critic-del}[nuovo]{.critic-add}

Escaped markers (`\\{++`, etc.) are restored to literal form: `\\{++` → `{++`.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Order matters: substitution BEFORE single insert/delete (it contains ~~ which would conflict).
SUB_RE = re.compile(r"(?<!\\)\{~~(.+?)~>(.+?)~~\}", flags=re.DOTALL)
INS_RE = re.compile(r"(?<!\\)\{\+\+(.+?)\+\+\}", flags=re.DOTALL)
DEL_RE = re.compile(r"(?<!\\)\{--(.+?)--\}", flags=re.DOTALL)

# After transform, restore backslash-escapes inserted by redline-generator
ESCAPED_OPENERS_RE = re.compile(r"\\(\{\+\+|\{--|\{~~|\+\+\}|--\}|~~\}|~>)")


def transform(text: str) -> str:
    text = SUB_RE.sub(lambda m: f"[{m.group(1)}]{{.critic-del}}[{m.group(2)}]{{.critic-add}}", text)
    text = INS_RE.sub(lambda m: f"[{m.group(1)}]{{.critic-add}}", text)
    text = DEL_RE.sub(lambda m: f"[{m.group(1)}]{{.critic-del}}", text)
    text = ESCAPED_OPENERS_RE.sub(r"\1", text)
    return text


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="input .md file, or '-' for stdin")
    ap.add_argument("-o", "--output", help="output path; default: stdout")
    args = ap.parse_args(argv)

    if args.input == "-":
        text = sys.stdin.read()
    else:
        text = Path(args.input).read_text(encoding="utf-8")

    out = transform(text)
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())

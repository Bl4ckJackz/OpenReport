#!/usr/bin/env python3
"""critic-to-latex.py — pandoc JSON-AST filter: CriticMarkup → LaTeX `changes` package."""
from __future__ import annotations

import json
import os
import sys

_FALLBACK = os.environ.get("REDLINE_LATEX_FALLBACK") == "soul"


def _ins_macro(text: str) -> str:
    if _FALLBACK:
        return f"\\uline{{{text}}}"
    return f"\\added{{{text}}}"


def _del_macro(text: str) -> str:
    if _FALLBACK:
        return f"\\sout{{{text}}}"
    return f"\\deleted{{{text}}}"


def _repl_macro(new: str, old: str) -> str:
    if _FALLBACK:
        return f"\\sout{{{old}}}\\uline{{{new}}}"
    return f"\\replaced{{{new}}}{{{old}}}"


def raw_latex(s: str) -> dict:
    return {"t": "RawInline", "c": ["latex", s]}


def _span_has_class(span: dict, classes_to_check: tuple) -> bool:
    attrs = span["c"][0]
    classes = attrs[1] if len(attrs) >= 2 else []
    return any(c in classes for c in classes_to_check)


def _inline_to_text(inlines: list) -> str:
    parts: list[str] = []
    for n in inlines:
        t = n.get("t")
        c = n.get("c")
        if t == "Str":
            parts.append(c)
        elif t == "Space":
            parts.append(" ")
        elif t == "SoftBreak" or t == "LineBreak":
            parts.append(" ")
        elif isinstance(c, list):
            parts.append(_inline_to_text(c))
    return "".join(parts)


def transform_inlines(inlines: list) -> list:
    out: list = []
    i = 0
    while i < len(inlines):
        node = inlines[i]
        # Pandoc emits {~~old~>new~~} as adjacent del+ins; collapse here.
        if (
            node.get("t") == "Span"
            and _span_has_class(node, ("critic-del", "del"))
            and i + 1 < len(inlines)
            and inlines[i + 1].get("t") == "Span"
            and _span_has_class(inlines[i + 1], ("critic-add", "ins"))
        ):
            old = _inline_to_text(node["c"][1])
            new = _inline_to_text(inlines[i + 1]["c"][1])
            out.append(raw_latex(_repl_macro(new, old)))
            i += 2
            continue
        if node.get("t") == "Span":
            attrs, children = node["c"]
            classes = attrs[1] if len(attrs) >= 2 else []
            text = _inline_to_text(children)
            if "critic-add" in classes or "ins" in classes:
                out.append(raw_latex(_ins_macro(text)))
                i += 1
                continue
            if "critic-del" in classes or "del" in classes:
                out.append(raw_latex(_del_macro(text)))
                i += 1
                continue
        if isinstance(node.get("c"), list):
            node = {**node, "c": _recurse(node["c"])}
        out.append(node)
        i += 1
    return out


def _recurse(c):
    if isinstance(c, list):
        if c and isinstance(c[0], dict) and "t" in c[0]:
            return transform_inlines(c)
        return [_recurse(x) for x in c]
    if isinstance(c, dict):
        return {k: _recurse(v) for k, v in c.items()}
    return c


def main() -> int:
    doc = json.load(sys.stdin)
    doc["blocks"] = _recurse(doc.get("blocks", []))
    json.dump(doc, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())

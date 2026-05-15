#!/usr/bin/env python3
"""critic-to-docx.py — pandoc JSON-AST filter: critic-add/critic-del spans → Underline/Strikeout.

Converts [text]{.critic-add} → Underline (w:u in DOCX)
         [text]{.critic-del} → Strikeout (w:strike in DOCX)
         Adjacent del+add → Strikeout(old) + Underline(new)

This produces visually distinct track-changes-style markup in Word-compatible DOCX output.
"""
from __future__ import annotations

import json
import sys


def _span_has_class(span: dict, classes_to_check: tuple) -> bool:
    attrs = span["c"][0]
    classes = attrs[1] if len(attrs) >= 2 else []
    return any(c in classes for c in classes_to_check)


def transform_inlines(inlines: list) -> list:
    out: list = []
    i = 0
    while i < len(inlines):
        node = inlines[i]
        # Collapse adjacent del+ins into strikeout(old)+underline(new)
        if (
            node.get("t") == "Span"
            and _span_has_class(node, ("critic-del", "del"))
            and i + 1 < len(inlines)
            and inlines[i + 1].get("t") == "Span"
            and _span_has_class(inlines[i + 1], ("critic-add", "ins"))
        ):
            old_children = node["c"][1]
            new_children = inlines[i + 1]["c"][1]
            out.append({"t": "Strikeout", "c": old_children})
            out.append({"t": "Underline", "c": new_children})
            i += 2
            continue
        if node.get("t") == "Span":
            attrs, children = node["c"]
            classes = attrs[1] if len(attrs) >= 2 else []
            if "critic-add" in classes or "ins" in classes:
                out.append({"t": "Underline", "c": children})
                i += 1
                continue
            if "critic-del" in classes or "del" in classes:
                out.append({"t": "Strikeout", "c": children})
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

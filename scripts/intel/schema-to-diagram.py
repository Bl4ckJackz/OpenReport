#!/usr/bin/env python3
"""schema-to-diagram.py — converte schema DB in diagramma ER (Mermaid o TikZ).

Supporta:
  - Prisma schema (schema.prisma)
  - SQL DDL (CREATE TABLE statements)

Usage:
  schema-to-diagram.py <input> -o output.md [--format=mermaid|tikz]
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class Field:
    name: str
    type: str
    nullable: bool = False
    is_pk: bool = False
    is_fk: bool = False
    fk_target: str = ""

@dataclass
class Table:
    name: str
    fields: list[Field] = field(default_factory=list)
    relations: list[tuple[str, str]] = field(default_factory=list)


def parse_prisma(text: str) -> list[Table]:
    tables = []
    blocks = re.findall(r"model\s+(\w+)\s*\{([^}]+)\}", text, re.DOTALL)
    for name, body in blocks:
        t = Table(name)
        for line in body.strip().splitlines():
            line = line.strip()
            if not line or line.startswith("//") or line.startswith("@@"):
                continue
            m = re.match(r"(\w+)\s+(\w+)(\?)?\s*(.*)", line)
            if not m: continue
            fname, ftype, opt, attrs = m.groups()
            f = Field(fname, ftype, nullable=bool(opt))
            if "@id" in attrs: f.is_pk = True
            rel = re.search(r"@relation\(\"?(\w+)?\"?(?:.*?fields:\s*\[(\w+)\])?(?:.*?references:\s*\[(\w+)\])?\)", attrs)
            if rel:
                f.is_fk = True
                f.fk_target = ftype
                t.relations.append((ftype, rel.group(1) or fname))
            t.fields.append(f)
        tables.append(t)
    return tables


def parse_sql(text: str) -> list[Table]:
    tables = []
    blocks = re.findall(r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[\"`]?(\w+)[\"`]?\s*\((.*?)\)\s*;", text, re.IGNORECASE | re.DOTALL)
    for name, body in blocks:
        t = Table(name)
        for raw_line in body.split(","):
            line = raw_line.strip()
            if not line or line.upper().startswith(("PRIMARY", "FOREIGN", "UNIQUE", "INDEX", "CONSTRAINT", "CHECK")):
                fk_m = re.search(r"FOREIGN\s+KEY\s*\(\s*[\"`]?(\w+)[\"`]?\s*\)\s+REFERENCES\s+[\"`]?(\w+)[\"`]?", line, re.IGNORECASE)
                if fk_m:
                    fname, ftarget = fk_m.groups()
                    for f in t.fields:
                        if f.name == fname:
                            f.is_fk = True
                            f.fk_target = ftarget
                    t.relations.append((ftarget, fname))
                continue
            m = re.match(r"[\"`]?(\w+)[\"`]?\s+(\w+)(?:\([^)]+\))?\s*(.*)", line, re.IGNORECASE)
            if not m: continue
            fname, ftype, attrs = m.groups()
            f = Field(fname, ftype.lower(), nullable="NOT NULL" not in attrs.upper())
            if "PRIMARY KEY" in attrs.upper(): f.is_pk = True
            t.fields.append(f)
        tables.append(t)
    return tables


def to_mermaid(tables: list[Table]) -> str:
    out = ["```mermaid", "erDiagram"]
    for t in tables:
        out.append(f"  {t.name} {{")
        for f in t.fields:
            tag = "PK" if f.is_pk else ("FK" if f.is_fk else "")
            out.append(f"    {f.type} {f.name} {tag}".rstrip())
        out.append("  }")
    for t in tables:
        for target, fname in t.relations:
            out.append(f"  {t.name} ||--o{{ {target} : \"{fname}\"")
    out.append("```")
    return "\n".join(out)


def to_tikz(tables: list[Table]) -> str:
    out = [
        "\\begin{figure}[H]\\centering",
        "\\begin{tikzpicture}[node distance=3cm, every node/.style={draw, rectangle, rounded corners, align=left}]",
    ]
    for i, t in enumerate(tables):
        fields_str = "\\\\".join([f"\\textbf{{{f.name}}} : {f.type}" for f in t.fields[:6]])
        if len(t.fields) > 6:
            fields_str += f"\\\\... (+{len(t.fields) - 6} altri)"
        pos = f"right=of {tables[i-1].name}" if i > 0 else ""
        out.append(f"\\node ({t.name}) [{pos}] {{\\textbf{{{t.name}}}\\\\{fields_str}}};")
    for t in tables:
        for target, fname in t.relations:
            out.append(f"\\draw[->] ({t.name}) -- ({target}) node[midway, above] {{{fname}}};")
    out.append("\\end{tikzpicture}")
    out.append("\\caption{Schema entità-relazione}")
    out.append("\\label{fig:er-diagram}")
    out.append("\\end{figure}")
    return "\n".join(out)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("input")
    p.add_argument("-o", "--out", default="-")
    p.add_argument("--format", choices=["mermaid", "tikz"], default="mermaid")
    args = p.parse_args()

    src = Path(args.input)
    text = src.read_text(encoding="utf-8")

    if "model " in text and "{" in text:
        tables = parse_prisma(text)
    elif re.search(r"CREATE\s+TABLE", text, re.IGNORECASE):
        tables = parse_sql(text)
    else:
        print("ERROR: input non riconosciuto (atteso Prisma o SQL DDL)", file=sys.stderr)
        return 2

    out = to_mermaid(tables) if args.format == "mermaid" else to_tikz(tables)

    if args.out == "-":
        print(out)
    else:
        Path(args.out).write_text(out + "\n", encoding="utf-8")
        print(f"Diagramma scritto in {args.out} ({len(tables)} tabelle)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

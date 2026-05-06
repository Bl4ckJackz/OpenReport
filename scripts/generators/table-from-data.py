#!/usr/bin/env python3
"""table-from-data.py — converte CSV/Excel/JSON in tabelle md/tex formattate.

Feature:
- Auto-detect separatore CSV (,/;/\\t)
- Auto-detect tipo colonna (numero/stringa/data)
- Allineamento smart (numeri a destra, testo a sinistra)
- Formattazione numeri locale (IT: 1.234,56)
- Troncamento celle lunghe
- Limit righe (head N)

Usage:
    table-from-data.py data.csv [--format md|tex] [--locale it|en] [--head 20]
                        [--caption "Titolo"] [--label tab:dati]
    table-from-data.py data.xlsx --sheet "Sheet1"
    table-from-data.py data.json --path "records"
"""
import argparse
import csv
import json
import pathlib
import re
import sys


def detect_separator(path):
    text = pathlib.Path(path).read_text(encoding="utf-8", errors="ignore")
    first = text.split("\n")[0]
    counts = {sep: first.count(sep) for sep in (",", ";", "\t", "|")}
    return max(counts, key=counts.get) if max(counts.values()) > 0 else ","


def load_csv(path):
    sep = detect_separator(path)
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=sep)
        rows = list(reader)
    return rows[0], rows[1:]


def load_xlsx(path, sheet=None):
    try:
        from openpyxl import load_workbook
    except ImportError:
        print("[ERR] openpyxl non installato: pip install openpyxl", file=sys.stderr)
        sys.exit(2)
    wb = load_workbook(path, data_only=True)
    ws = wb[sheet] if sheet else wb.active
    rows = list(ws.values)
    return list(rows[0]), [list(r) for r in rows[1:] if any(c is not None for c in r)]


def load_json(path, json_path=None):
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    if json_path:
        for key in json_path.split("."):
            data = data[key]
    if not isinstance(data, list) or not data:
        return [], []
    headers = list(data[0].keys())
    rows = [[item.get(h, "") for h in headers] for item in data]
    return headers, rows


def is_numeric(cell):
    if cell is None or cell == "":
        return False
    s = str(cell).replace(",", ".").replace(" ", "")
    try:
        float(s)
        return True
    except ValueError:
        return False


def format_number(value, locale="it"):
    try:
        n = float(str(value).replace(",", ".").replace(" ", ""))
    except (ValueError, TypeError):
        return str(value) if value is not None else ""
    if n.is_integer():
        s = f"{int(n):,}"
    else:
        s = f"{n:,.2f}"
    if locale == "it":
        s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return s


def format_cell(value, is_num, locale, max_width=40):
    if value is None:
        return ""
    if is_num:
        s = format_number(value, locale)
    else:
        s = str(value)
    if len(s) > max_width:
        s = s[:max_width - 1] + "…"
    return s.replace("\n", " ").replace("|", "\\|")


def emit_md(headers, rows, locale, numeric_cols):
    out = ["| " + " | ".join(headers) + " |"]
    align = [":---:" if i in numeric_cols else ":---" for i in range(len(headers))]
    out.append("|" + "|".join(f" {a} " for a in align) + "|")
    for row in rows:
        cells = [format_cell(c, i in numeric_cols, locale) for i, c in enumerate(row)]
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def emit_tex(headers, rows, locale, numeric_cols, caption=None, label=None):
    col_spec = "".join("r" if i in numeric_cols else "l" for i in range(len(headers)))
    out = [f"\\begin{{table}}[htbp]", "\\centering"]
    if caption:
        out.append(f"\\caption{{{caption}}}")
    if label:
        out.append(f"\\label{{{label}}}")
    out.append(f"\\begin{{tabular}}{{{col_spec}}}")
    out.append("\\toprule")
    out.append(" & ".join(headers) + " \\\\")
    out.append("\\midrule")
    for row in rows:
        cells = [format_cell(c, i in numeric_cols, locale) for i, c in enumerate(row)]
        cells = [c.replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#") for c in cells]
        out.append(" & ".join(cells) + " \\\\")
    out.append("\\bottomrule")
    out.append("\\end{tabular}")
    out.append("\\end{table}")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--format", choices=["md", "tex"], default="md")
    ap.add_argument("--locale", choices=["it", "en"], default="it")
    ap.add_argument("--head", type=int, default=0, help="Limita a N righe")
    ap.add_argument("--caption")
    ap.add_argument("--label")
    ap.add_argument("--sheet", help="Nome sheet (xlsx)")
    ap.add_argument("--path", help="JSON path (es. 'records.items')")
    ap.add_argument("-o", "--output")
    args = ap.parse_args()

    p = pathlib.Path(args.file)
    if not p.exists():
        print(f"[ERR] file non trovato: {p}", file=sys.stderr)
        return 2

    ext = p.suffix.lower()
    if ext in (".csv", ".tsv"):
        headers, rows = load_csv(p)
    elif ext == ".xlsx":
        headers, rows = load_xlsx(p, args.sheet)
    elif ext == ".json":
        headers, rows = load_json(p, args.path)
    else:
        print(f"[ERR] estensione non supportata: {ext}", file=sys.stderr)
        return 2

    if args.head:
        rows = rows[:args.head]

    # Numeric col detection: >80% delle celle non-empty sono numeriche
    numeric_cols = set()
    for i, h in enumerate(headers):
        non_empty = [r[i] for r in rows if i < len(r) and r[i] not in (None, "")]
        if non_empty and sum(1 for c in non_empty if is_numeric(c)) / len(non_empty) > 0.8:
            numeric_cols.add(i)

    if args.format == "md":
        out = emit_md(headers, rows, args.locale, numeric_cols)
    else:
        out = emit_tex(headers, rows, args.locale, numeric_cols, args.caption, args.label)

    if args.output:
        pathlib.Path(args.output).write_text(out + "\n", encoding="utf-8")
        print(f"[OK] {args.output}")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())

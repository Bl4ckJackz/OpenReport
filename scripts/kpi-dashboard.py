#!/usr/bin/env python3
"""kpi-dashboard.py — tabella KPI con trend vs target.

Input YAML:
    kpis:
      - nome: "NPS"
        valore_attuale: 42
        target: 50
        unita: ""
        periodo: "2026-Q1"
        trend: "up"          # up/down/stable
        comment: "Miglioramento Q1 vs Q4 2025"
      - nome: "MRR"
        valore_attuale: 48500
        target: 60000
        unita: "€"

Output: tabella md/tex con colonne valore/target/%/trend.

Usage:
    kpi-dashboard.py config.yaml [--format md|tex]
"""
import argparse
import json
import pathlib
import sys

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

TREND_ICON = {"up": "↑", "down": "↓", "stable": "→"}


def load_config(path):
    p = pathlib.Path(path)
    text = p.read_text(encoding="utf-8")
    if p.suffix in (".yaml", ".yml") and HAS_YAML:
        return yaml.safe_load(text)
    return json.loads(text)


def pct(actual, target):
    try:
        return f"{actual / target * 100:.0f}%"
    except (ZeroDivisionError, TypeError):
        return "—"


def fmt_value(v, u):
    if isinstance(v, (int, float)):
        if u == "€" or u == "$":
            return f"{u} {v:,.0f}".replace(",", ".")
        if u == "%":
            return f"{v:.1f}%"
        return f"{v:,}".replace(",", ".") + (f" {u}" if u else "")
    return str(v)


def format_md(kpis):
    header = ["KPI", "Valore", "Target", "% target", "Trend", "Periodo", "Note"]
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    for k in kpis:
        u = k.get("unita", "")
        row = [
            k.get("nome", ""),
            fmt_value(k.get("valore_attuale"), u),
            fmt_value(k.get("target"), u),
            pct(k.get("valore_attuale", 0), k.get("target", 1)),
            TREND_ICON.get(k.get("trend", "stable"), "→"),
            k.get("periodo", ""),
            k.get("comment", ""),
        ]
        out.append("| " + " | ".join(str(x) for x in row) + " |")
    return "\n".join(out)


def format_tex(kpis):
    cols = "l" * 7
    out = [f"\\begin{{tabular}}{{{cols}}}", "\\toprule"]
    out.append("KPI & Valore & Target & \\% & Trend & Periodo & Note \\\\")
    out.append("\\midrule")
    for k in kpis:
        u = k.get("unita", "")
        row = [
            k.get("nome", ""),
            fmt_value(k.get("valore_attuale"), u),
            fmt_value(k.get("target"), u),
            pct(k.get("valore_attuale", 0), k.get("target", 1)),
            TREND_ICON.get(k.get("trend", "stable"), "→"),
            k.get("periodo", ""),
            k.get("comment", ""),
        ]
        out.append(" & ".join(str(x) for x in row) + " \\\\")
    out.append("\\bottomrule")
    out.append("\\end{tabular}")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--format", choices=["md", "tex"], default="md")
    ap.add_argument("-o", "--output", default=None)
    args = ap.parse_args()
    cfg = load_config(args.config)
    kpis = cfg.get("kpis", [])
    out = format_md(kpis) if args.format == "md" else format_tex(kpis)
    if args.output:
        pathlib.Path(args.output).write_text(out + "\n", encoding="utf-8")
        print(f"[OK] {args.output}")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())

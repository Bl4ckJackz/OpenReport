#!/usr/bin/env python3
"""risk-register.py — produce risk register con scoring e trend.

Input YAML/JSON:
    risks:
      - id: R-01
        titolo: "Ritardo consegna vendor X"
        categoria: "fornitore"
        probabilita: 3         # 1-5
        impatto: 4             # 1-5
        owner: "M. Rossi"
        mitigation: "Second source vendor Y qualificato"
        trend: "up"            # up/down/stable
        status: "active"

Output: tabella md/tex con score=P*I, top-risk sorting.

Usage:
    risk-register.py config.yaml [--format md|tex] [--top N]
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


def severity_label(score):
    if score >= 16:
        return "critico"
    if score >= 10:
        return "alto"
    if score >= 5:
        return "medio"
    return "basso"


def format_md(risks):
    header = ["ID", "Titolo", "Cat.", "P", "I", "Score", "Sev", "Trend", "Owner", "Mitigazione"]
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    for r in risks:
        p = r.get("probabilita", 0)
        i = r.get("impatto", 0)
        score = p * i
        row = [
            r.get("id", ""),
            r.get("titolo", ""),
            r.get("categoria", ""),
            str(p), str(i), str(score),
            severity_label(score),
            TREND_ICON.get(r.get("trend", "stable"), "→"),
            r.get("owner", ""),
            r.get("mitigation", ""),
        ]
        out.append("| " + " | ".join(row) + " |")
    return "\n".join(out)


def format_tex(risks):
    header = ["ID", "Titolo", "P", "I", "Score", "Sev", "Trend", "Owner", "Mitigazione"]
    cols = "l" * len(header)
    out = [f"\\begin{{tabular}}{{{cols}}}", "\\toprule", " & ".join(header) + " \\\\", "\\midrule"]
    for r in risks:
        p = r.get("probabilita", 0)
        i = r.get("impatto", 0)
        score = p * i
        row = [
            r.get("id", ""), r.get("titolo", ""), str(p), str(i), str(score),
            severity_label(score),
            TREND_ICON.get(r.get("trend", "stable"), "→"),
            r.get("owner", ""), r.get("mitigation", ""),
        ]
        out.append(" & ".join(row) + " \\\\")
    out.append("\\bottomrule")
    out.append("\\end{tabular}")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--format", choices=["md", "tex"], default="md")
    ap.add_argument("--top", type=int, default=0, help="Mostra solo top N per score")
    ap.add_argument("-o", "--output", default=None)
    args = ap.parse_args()
    cfg = load_config(args.config)
    risks = cfg.get("risks", [])
    risks.sort(key=lambda r: r.get("probabilita", 0) * r.get("impatto", 0), reverse=True)
    if args.top:
        risks = risks[:args.top]
    out = format_md(risks) if args.format == "md" else format_tex(risks)
    if args.output:
        pathlib.Path(args.output).write_text(out + "\n", encoding="utf-8")
        print(f"[OK] {args.output}")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())

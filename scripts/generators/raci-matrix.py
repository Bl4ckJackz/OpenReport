#!/usr/bin/env python3
"""raci-matrix.py — genera tabella RACI da YAML/JSON config.

Input YAML:
    activities:
      - name: "Kick-off meeting"
        R: "Project Manager"
        A: "Sponsor"
        C: ["Product Owner", "Tech Lead"]
        I: ["Team"]

Output: tabella markdown o LaTeX.

Usage:
    raci-matrix.py config.yaml [--format md|tex] [-o out.md]
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


def load_config(path):
    p = pathlib.Path(path)
    content = p.read_text(encoding="utf-8")
    if p.suffix in (".yaml", ".yml") and HAS_YAML:
        return yaml.safe_load(content)
    return json.loads(content)


def collect_actors(activities):
    actors = set()
    for a in activities:
        for role in ("R", "A", "C", "I"):
            v = a.get(role)
            if v is None:
                continue
            if isinstance(v, list):
                actors.update(v)
            else:
                actors.add(v)
    return sorted(actors)


def format_md(activities, actors):
    lines = []
    header = ["Attività"] + actors
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "|".join("---" for _ in header) + "|")
    for a in activities:
        row = [a.get("name", "")]
        for actor in actors:
            tokens = []
            for role in ("R", "A", "C", "I"):
                v = a.get(role)
                if v is None:
                    continue
                if isinstance(v, list):
                    if actor in v:
                        tokens.append(role)
                elif v == actor:
                    tokens.append(role)
            row.append("/".join(tokens) if tokens else "")
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def format_tex(activities, actors):
    cols = "l" + "c" * len(actors)
    lines = [f"\\begin{{tabular}}{{{cols}}}"]
    lines.append("\\toprule")
    lines.append(" & ".join(["Attività"] + actors) + " \\\\")
    lines.append("\\midrule")
    for a in activities:
        row = [a.get("name", "")]
        for actor in actors:
            tokens = []
            for role in ("R", "A", "C", "I"):
                v = a.get(role)
                if v is None:
                    continue
                if isinstance(v, list):
                    if actor in v:
                        tokens.append(role)
                elif v == actor:
                    tokens.append(role)
            row.append("/".join(tokens) if tokens else "")
        lines.append(" & ".join(row) + " \\\\")
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--format", choices=["md", "tex"], default="md")
    ap.add_argument("-o", "--output", default=None)
    args = ap.parse_args()
    if not HAS_YAML and pathlib.Path(args.config).suffix in (".yaml", ".yml"):
        print("[ERR] PyYAML non installato; fornisci JSON o installa pyyaml", file=sys.stderr)
        return 2
    cfg = load_config(args.config)
    activities = cfg.get("activities", [])
    if not activities:
        print("[ERR] 'activities' vuoto", file=sys.stderr)
        return 2
    actors = collect_actors(activities)
    out = format_md(activities, actors) if args.format == "md" else format_tex(activities, actors)
    if args.output:
        pathlib.Path(args.output).write_text(out + "\n", encoding="utf-8")
        print(f"[OK] scritto {args.output}")
    else:
        print(out)
    print("\n# Legenda: R=Responsible, A=Accountable, C=Consulted, I=Informed", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

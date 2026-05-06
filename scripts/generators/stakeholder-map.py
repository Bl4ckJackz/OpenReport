#!/usr/bin/env python3
"""stakeholder-map.py — Mermaid quadrant power/interest.

Input YAML:
    stakeholders:
      - nome: "CTO cliente"
        influence: 5     # 1-5
        interest: 5      # 1-5
        note: "Decisore"
      - nome: "Team dev cliente"
        influence: 2
        interest: 4

Output: quadrant Mermaid.

Usage:
    stakeholder-map.py config.yaml
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
    text = p.read_text(encoding="utf-8")
    if p.suffix in (".yaml", ".yml") and HAS_YAML:
        return yaml.safe_load(text)
    return json.loads(text)


def render_mermaid(cfg):
    out = ["```mermaid", "quadrantChart"]
    out.append('    title Mappa stakeholder — Influenza vs Interesse')
    out.append('    x-axis Basso interesse --> Alto interesse')
    out.append('    y-axis Bassa influenza --> Alta influenza')
    out.append('    quadrant-1 "Key players (gestire attentamente)"')
    out.append('    quadrant-2 "Tenere soddisfatti"')
    out.append('    quadrant-3 "Monitorare (min effort)"')
    out.append('    quadrant-4 "Tenere informati"')
    for s in cfg.get("stakeholders", []):
        name = s.get("nome", "")
        influence = max(1, min(5, int(s.get("influence", 3)))) / 5.0
        interest = max(1, min(5, int(s.get("interest", 3)))) / 5.0
        out.append(f'    "{name}": [{interest:.2f}, {influence:.2f}]')
    out.append("```")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("-o", "--output", default=None)
    args = ap.parse_args()
    cfg = load_config(args.config)
    out = render_mermaid(cfg)
    if args.output:
        pathlib.Path(args.output).write_text(out + "\n", encoding="utf-8")
        print(f"[OK] {args.output}")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())

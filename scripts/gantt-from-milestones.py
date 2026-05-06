#!/usr/bin/env python3
"""gantt-from-milestones.py — genera Mermaid Gantt da lista milestone.

Input YAML/JSON:
    project_name: "Progetto ACME"
    milestones:
      - name: "Kick-off"
        start: 2026-04-20
        duration: 3       # giorni
        section: "Fase 1"
        deps: []
      - name: "Analisi"
        after: "Kick-off"
        duration: 10
        section: "Fase 1"

Output: blocco ```mermaid ... ``` da includere nel doc.

Usage:
    gantt-from-milestones.py config.yaml [--output out.md]
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
    out = ["```mermaid", "gantt"]
    out.append(f"    title {cfg.get('project_name', 'Progetto')}")
    out.append("    dateFormat  YYYY-MM-DD")
    out.append("    axisFormat  %d %b")
    sections = {}
    for m in cfg.get("milestones", []):
        sections.setdefault(m.get("section", "Default"), []).append(m)
    for section, milestones in sections.items():
        out.append(f"\n    section {section}")
        for m in milestones:
            name = m.get("name", "")
            m_id = name.lower().replace(" ", "_").replace(":", "")
            duration = m.get("duration", 1)
            if m.get("start"):
                out.append(f"    {name:<30} :{m_id}, {m['start']}, {duration}d")
            elif m.get("after"):
                after_id = m["after"].lower().replace(" ", "_").replace(":", "")
                out.append(f"    {name:<30} :{m_id}, after {after_id}, {duration}d")
            else:
                out.append(f"    {name:<30} :{m_id}, {duration}d")
            if m.get("milestone"):
                out.append(f"    {name} deliverable :milestone, after {m_id}, 0d")
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

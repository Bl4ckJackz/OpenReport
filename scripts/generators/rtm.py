#!/usr/bin/env python3
"""rtm.py — Requirements Traceability Matrix generator.

Input YAML/JSON:
    requirements:
      - id: RF-01
        descrizione: "Login utente con email/password"
        priorita: "MUST"
        tipo: "funzionale"
        implementazione: ["src/auth/login.ts", "src/auth/password.ts"]
        user_stories: ["US-042"]
        test_cases: ["TC-001", "TC-002"]
        status: "verified"

Output: tabella md/tex con gap (req senza test, test senza req, ecc.).

Usage:
    rtm.py config.yaml [--format md|tex] [--gap-only]
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


def list_field(v):
    if v is None:
        return ""
    if isinstance(v, list):
        return ", ".join(str(x) for x in v)
    return str(v)


def find_gaps(reqs):
    gaps = []
    for r in reqs:
        if not r.get("test_cases"):
            gaps.append((r.get("id"), "nessun test case"))
        if not r.get("implementazione"):
            gaps.append((r.get("id"), "nessuna implementazione tracciata"))
        if r.get("status") not in ("verified", "implemented"):
            gaps.append((r.get("id"), f"status={r.get('status', 'unknown')}"))
    return gaps


def format_md(reqs):
    header = ["ID", "Priorità", "Tipo", "Descrizione", "User Stories", "Implementazione", "Test", "Status"]
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    for r in reqs:
        row = [
            r.get("id", ""),
            r.get("priorita", ""),
            r.get("tipo", ""),
            r.get("descrizione", ""),
            list_field(r.get("user_stories")),
            list_field(r.get("implementazione")),
            list_field(r.get("test_cases")),
            r.get("status", ""),
        ]
        out.append("| " + " | ".join(row) + " |")
    return "\n".join(out)


def format_tex(reqs):
    cols = "l" * 8
    out = [f"\\begin{{longtable}}{{{cols}}}", "\\toprule"]
    header = ["ID", "Priorità", "Tipo", "Descrizione", "US", "Impl", "Test", "Status"]
    out.append(" & ".join(header) + " \\\\")
    out.append("\\midrule")
    for r in reqs:
        row = [r.get("id", ""), r.get("priorita", ""), r.get("tipo", ""),
               r.get("descrizione", ""), list_field(r.get("user_stories")),
               list_field(r.get("implementazione")), list_field(r.get("test_cases")),
               r.get("status", "")]
        out.append(" & ".join(str(x) for x in row) + " \\\\")
    out.append("\\bottomrule")
    out.append("\\end{longtable}")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--format", choices=["md", "tex"], default="md")
    ap.add_argument("--gap-only", action="store_true")
    ap.add_argument("-o", "--output", default=None)
    args = ap.parse_args()
    cfg = load_config(args.config)
    reqs = cfg.get("requirements", [])
    if args.gap_only:
        gaps = find_gaps(reqs)
        for rid, msg in gaps:
            print(f"  [GAP] {rid}: {msg}")
        return 0 if not gaps else 1
    out = format_md(reqs) if args.format == "md" else format_tex(reqs)
    if args.output:
        pathlib.Path(args.output).write_text(out + "\n", encoding="utf-8")
        print(f"[OK] {args.output}")
    else:
        print(out)
    gaps = find_gaps(reqs)
    if gaps:
        print(f"\n# [WARN] {len(gaps)} gap individuati (usa --gap-only per dettaglio)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

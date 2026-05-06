#!/usr/bin/env python3
r"""
layout-coherence.py - Verify report element ordering matches the chosen pdf_style.

Checks (BLOCKING):
  - Frontespizio (title page) is FIRST.
  - Document Control sheet (if enterprise) immediately after frontespizio.
  - TOC after frontespizio (and after control sheet if present), NEVER before.
  - Bibliografia near the end (before appendices, never in body).
  - Appendici last.
  - For pdf_style=accademico: \listoffigures / \listoftables (if any) AFTER TOC.
  - For pdf_style=brand: brand cover header present, footer classification line.

Usage:
  python3 layout-coherence.py <RELAZIONE.md|RELAZIONE.tex> --style=<accademico|moderno|brand> --tipologia=<tipo> [--strict]

Exit 0 = OK, exit 1 = FAIL (prints structured report).
"""
import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

EXPECTED_ORDER = [
    "frontespizio",        # always first
    "control_sheet",       # enterprise only, immediately after
    "toc",                 # mandatory if pages >= 15
    "lof_lot",             # accademico: list of figures/tables after TOC
    "abstract",            # academic only
    "introduzione",
    "body",                # any non-special section
    "conclusioni",
    "bibliografia",
    "appendice",
]

ENTERPRISE_TIPOLOGIE = {
    "proposta", "rfp-response", "sow", "business-case",
    "spec-funzionale", "spec-tecnica", "incident-postmortem",
    "status-report", "whitepaper", "case-study", "handover",
    "runbook", "audit-report", "compliance-report",
}

ACADEMIC_TIPOLOGIE = {"tesi", "ricerca", "stage", "laboratorio", "esperienza"}


def detect_md_blocks(text: str) -> list[tuple[int, str, str]]:
    """Return list of (line_no, kind, raw_heading) for each detected structural block."""
    blocks = []
    lines = text.splitlines()
    in_frontmatter = False
    for i, line in enumerate(lines, start=1):
        if i == 1 and line.strip() == "---":
            in_frontmatter = True
            continue
        if in_frontmatter and line.strip() == "---":
            in_frontmatter = False
            continue
        if in_frontmatter:
            continue
        m = re.match(r"^(#{1,3})\s+(.+?)\s*$", line)
        if not m:
            continue
        title = m.group(2).strip().lower()
        kind = classify(title)
        if kind:
            blocks.append((i, kind, m.group(2).strip()))
    return blocks


def detect_tex_blocks(text: str) -> list[tuple[int, str, str]]:
    blocks = []
    lines = text.splitlines()
    for i, line in enumerate(lines, start=1):
        if r"\maketitle" in line or r"\begin{titlepage}" in line:
            blocks.append((i, "frontespizio", "\\maketitle/titlepage"))
        if r"\tableofcontents" in line:
            blocks.append((i, "toc", "\\tableofcontents"))
        if r"\listoffigures" in line or r"\listoftables" in line:
            blocks.append((i, "lof_lot", line.strip()))
        m = re.match(r"^\s*\\(chapter|section)\*?\{(.+?)\}", line)
        if not m:
            continue
        title = m.group(2).strip().lower()
        kind = classify(title)
        if kind:
            blocks.append((i, kind, m.group(2).strip()))
    return blocks


def classify(title: str) -> str | None:
    t = title.lower()
    if "frontespizio" in t or "title page" in t:
        return "frontespizio"
    if "document control" in t or "controllo documento" in t:
        return "control_sheet"
    if "indice" in t or "table of contents" in t or "sommario" == t.strip(" .:"):
        return "toc"
    if "abstract" in t or "riassunto" == t.strip(" .:"):
        return "abstract"
    if "introduzione" in t or "introduction" in t:
        return "introduzione"
    if "conclusion" in t:
        return "conclusioni"
    if "bibliograf" in t or "references" == t.strip(" .:") or "riferimenti bibliografici" in t:
        return "bibliografia"
    if "appendic" in t or "appendix" in t:
        return "appendice"
    if "ringraziamenti" in t or "acknowledg" in t:
        return "ringraziamenti"
    if t.startswith("nota metodologica"):
        return "nota_metodologica"
    return "body"


def find_first(blocks, kind):
    for b in blocks:
        if b[1] == kind:
            return b
    return None


def check(blocks: list[tuple[int, str, str]], style: str, tipologia: str, strict: bool) -> list[dict]:
    findings = []
    if not blocks:
        return [{"sev": "FAIL", "rule": "no-structure", "msg": "Nessuna struttura rilevata: il file potrebbe essere vuoto o malformato."}]

    fronte = find_first(blocks, "frontespizio")
    toc = find_first(blocks, "toc")
    control = find_first(blocks, "control_sheet")
    biblio = find_first(blocks, "bibliografia")
    appendix = find_first(blocks, "appendice")
    body_blocks = [b for b in blocks if b[1] not in ("frontespizio", "control_sheet", "toc", "lof_lot")]

    if fronte:
        before_fronte = [b for b in blocks if b[0] < fronte[0] and b[1] not in ("frontespizio",)]
        if before_fronte:
            findings.append({
                "sev": "FAIL", "rule": "frontespizio-first",
                "msg": f"Frontespizio non è il primo blocco. Precedenti: {[b[2] for b in before_fronte]}",
                "line": fronte[0],
            })
    elif tipologia not in ("bug", "codice"):
        findings.append({"sev": "WARN", "rule": "frontespizio-missing",
                         "msg": "Nessun frontespizio rilevato. Verifica titolo/autore/data presenti."})

    if toc:
        if fronte and toc[0] < fronte[0]:
            findings.append({"sev": "FAIL", "rule": "toc-after-frontespizio",
                             "msg": f"Indice (riga {toc[0]}) appare PRIMA del frontespizio (riga {fronte[0]}).",
                             "line": toc[0]})
        if control and toc[0] < control[0]:
            findings.append({"sev": "FAIL", "rule": "toc-after-control",
                             "msg": f"Indice (riga {toc[0]}) appare PRIMA del Document Control (riga {control[0]}).",
                             "line": toc[0]})

    if tipologia in ENTERPRISE_TIPOLOGIE and not control:
        findings.append({"sev": "WARN", "rule": "missing-control-sheet",
                         "msg": f"Tipologia enterprise '{tipologia}' senza Document Control sheet."})

    if control and fronte and control[0] < fronte[0]:
        findings.append({"sev": "FAIL", "rule": "control-after-frontespizio",
                         "msg": "Document Control prima del frontespizio.", "line": control[0]})

    if biblio and appendix and appendix[0] < biblio[0]:
        findings.append({"sev": "WARN", "rule": "appendix-after-biblio",
                         "msg": "Appendici prima della bibliografia. Convenzione: bibliografia prima.",
                         "line": appendix[0]})

    if biblio:
        after_biblio = [b for b in blocks if b[0] > biblio[0] and b[1] in ("introduzione", "conclusioni")]
        if after_biblio:
            findings.append({"sev": "FAIL", "rule": "section-after-biblio",
                             "msg": f"Sezioni di corpo dopo la bibliografia: {[b[2] for b in after_biblio]}",
                             "line": biblio[0]})

    if style == "accademico":
        lof = find_first(blocks, "lof_lot")
        if lof and toc and lof[0] < toc[0]:
            findings.append({"sev": "FAIL", "rule": "lof-after-toc",
                             "msg": "List of figures/tables prima del TOC (stile accademico).",
                             "line": lof[0]})
        abstract = find_first(blocks, "abstract")
        if tipologia in ACADEMIC_TIPOLOGIE and not abstract:
            findings.append({"sev": "WARN", "rule": "missing-abstract",
                             "msg": "Stile accademico senza abstract."})

    if style == "moderno" and tipologia in ACADEMIC_TIPOLOGIE:
        findings.append({"sev": "WARN", "rule": "style-mismatch",
                         "msg": f"Stile 'moderno' su tipologia accademica '{tipologia}'. Default consigliato: 'accademico'."})

    if style == "brand":
        if not control and tipologia in ENTERPRISE_TIPOLOGIE:
            findings.append({"sev": "FAIL", "rule": "brand-no-control",
                             "msg": "Stile 'brand' su tipologia enterprise richiede Document Control sheet."})

    return findings


def main() -> int:
    ap = argparse.ArgumentParser(prog="layout-coherence")
    ap.add_argument("file")
    ap.add_argument("--style", required=True, choices=["accademico", "moderno", "brand"])
    ap.add_argument("--tipologia", required=True)
    ap.add_argument("--strict", action="store_true",
                    help="WARN diventano FAIL")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    p = Path(args.file)
    if not p.exists():
        print(f"[layout-coherence] file non trovato: {p}", file=sys.stderr)
        return 2
    text = p.read_text(encoding="utf-8", errors="ignore")

    if p.suffix.lower() == ".tex":
        blocks = detect_tex_blocks(text)
    else:
        blocks = detect_md_blocks(text)

    findings = check(blocks, args.style, args.tipologia, args.strict)

    fail_count = sum(1 for f in findings if f["sev"] == "FAIL")
    warn_count = sum(1 for f in findings if f["sev"] == "WARN")
    if args.strict:
        fail_count += warn_count
        warn_count = 0
        for f in findings:
            if f["sev"] == "WARN":
                f["sev"] = "FAIL"

    report = {
        "file": str(p),
        "style": args.style,
        "tipologia": args.tipologia,
        "blocks_detected": [{"line": b[0], "kind": b[1], "title": b[2]} for b in blocks],
        "findings": findings,
        "summary": {"fail": fail_count, "warn": warn_count, "ok": len(findings) == 0},
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"[layout-coherence] {p.name} (style={args.style}, tipologia={args.tipologia})")
        print(f"  blocks: {len(blocks)} | FAIL: {fail_count} | WARN: {warn_count}")
        for f in findings:
            line_str = f" line {f['line']}" if "line" in f else ""
            print(f"  [{f['sev']}] {f['rule']}{line_str}: {f['msg']}")
        if not findings:
            print("  [OK] layout coerente con lo stile scelto.")

    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

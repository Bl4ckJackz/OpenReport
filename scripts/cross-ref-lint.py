#!/usr/bin/env python3
"""cross-ref-lint.py — verifica integrita riferimenti interni.

Verifica:
- \\ref{label} e \\eqref{label} → \\label{label} esiste
- \\cite{key} → key presente nel .bib (se fornito)
- Markdown link [text](#anchor) → anchor esiste come heading
- "Figura N"/"Fig. N"/"Tabella N"/"Tab. N" → numero coerente con figure/tabelle presenti
- Immagini citate come ![](path) → file esiste

Usage:
    python3 cross-ref-lint.py <file> [--bib <refs.bib>] [--base-dir <dir>]
"""
import argparse
import json
import pathlib
import re
import sys


def check_latex(text):
    issues = []
    labels = set(re.findall(r"\\label\{([^}]+)\}", text))
    refs = set(re.findall(r"\\(?:e?ref|autoref|cref|pageref)\{([^}]+)\}", text))
    missing_refs = sorted(refs - labels)
    unused_labels = sorted(labels - refs)
    if missing_refs:
        issues.append(("LATEX-REF-BROKEN", f"{len(missing_refs)} ref senza label corrispondente", missing_refs))
    if unused_labels:
        issues.append(("LATEX-LABEL-UNUSED", f"{len(unused_labels)} label mai referenziate (info)", unused_labels[:20]))
    return issues


def check_bib(text, bib_path):
    if not bib_path or not pathlib.Path(bib_path).exists():
        return []
    bib_keys = set(re.findall(r"@\w+\{\s*([^,\s]+)\s*,", pathlib.Path(bib_path).read_text(encoding="utf-8", errors="ignore")))
    cited_keys = set()
    for m in re.finditer(r"\\cite[a-z]*\{([^}]+)\}", text):
        for k in m.group(1).split(","):
            cited_keys.add(k.strip())
    missing = sorted(cited_keys - bib_keys)
    if missing:
        return [("BIB-KEY-MISSING", f"{len(missing)} \\cite chiavi non in {pathlib.Path(bib_path).name}", missing)]
    return []


def check_md_anchors(text):
    issues = []
    headings = set()
    for m in re.finditer(r"^(#{1,6})\s+(.+?)\s*$", text, flags=re.MULTILINE):
        h = m.group(2).strip().lower()
        anchor = re.sub(r"[^\w\s-]", "", h).strip().replace(" ", "-")
        headings.add(anchor)
    anchors_used = set(re.findall(r"\]\(#([^)]+)\)", text))
    missing = sorted(anchors_used - headings)
    if missing:
        issues.append(("MD-ANCHOR-BROKEN", f"{len(missing)} link markdown a heading inesistente", missing))
    return issues


def check_figure_table_refs(text):
    issues = []
    fig_nums_cited = set(m.group(1) for m in re.finditer(r"(?:Figur[ea]|Fig\.)\s+(\d+)", text))
    tab_nums_cited = set(m.group(1) for m in re.finditer(r"(?:Tabell[ae]|Tab\.)\s+(\d+)", text))

    fig_captions = re.findall(r"(?:Figur[ea]|Fig\.)\s+(\d+)[\s:.]", text)
    tab_captions = re.findall(r"(?:Tabell[ae]|Tab\.)\s+(\d+)[\s:.]", text)

    all_fig = set(fig_nums_cited) | set(fig_captions)
    all_tab = set(tab_nums_cited) | set(tab_captions)

    if all_fig:
        fig_int = sorted(int(n) for n in all_fig)
        gaps = [n for n in range(1, max(fig_int) + 1) if n not in fig_int]
        if gaps:
            issues.append(("FIG-NUMBERING-GAP", f"numerazione figure non sequenziale, mancano: {gaps}", gaps))
    if all_tab:
        tab_int = sorted(int(n) for n in all_tab)
        gaps = [n for n in range(1, max(tab_int) + 1) if n not in tab_int]
        if gaps:
            issues.append(("TAB-NUMBERING-GAP", f"numerazione tabelle non sequenziale, mancano: {gaps}", gaps))
    return issues


def check_images(text, base_dir):
    base = pathlib.Path(base_dir)
    issues = []
    missing = []
    for m in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", text):
        p = m.group(1).split()[0]
        if p.startswith(("http://", "https://")):
            continue
        img_path = (base / p).resolve() if not pathlib.Path(p).is_absolute() else pathlib.Path(p)
        if not img_path.exists():
            missing.append(p)
    if missing:
        issues.append(("IMG-PATH-BROKEN", f"{len(missing)} immagini referenziate non esistono", missing))

    for m in re.finditer(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", text):
        p = m.group(1)
        candidates = [p, p + ".png", p + ".jpg", p + ".jpeg", p + ".pdf", p + ".svg"]
        found = any((base / c).exists() for c in candidates)
        if not found:
            missing.append(p)
    if missing:
        issues.append(("TEX-IMG-BROKEN", f"{len(missing)} \\includegraphics non risolve", missing))
    return issues


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--bib", default=None)
    ap.add_argument("--base-dir", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    path = pathlib.Path(args.file)
    if not path.exists():
        print(f"[ERR] file non trovato: {path}", file=sys.stderr)
        return 2

    text = path.read_text(encoding="utf-8")
    base_dir = args.base_dir or str(path.parent)

    all_issues = []
    all_issues.extend(check_latex(text))
    all_issues.extend(check_bib(text, args.bib))
    all_issues.extend(check_md_anchors(text))
    all_issues.extend(check_figure_table_refs(text))
    all_issues.extend(check_images(text, base_dir))

    has_fail = any(label.endswith(("-BROKEN", "-MISSING")) for label, *_ in all_issues)

    if args.json:
        print(json.dumps([{"code": c, "msg": m, "items": it} for c, m, it in all_issues], indent=2, ensure_ascii=False))
    else:
        if not all_issues:
            print(f"[OK] Cross-ref lint passato: {path.name}")
        else:
            for code, msg, items in all_issues:
                tag = "[FAIL]" if code.endswith(("-BROKEN", "-MISSING")) else "[WARN]"
                print(f"\n{tag} [{code}] {msg}")
                for it in items[:15]:
                    print(f"  • {it}")

    return 1 if has_fail else 0


if __name__ == "__main__":
    sys.exit(main())

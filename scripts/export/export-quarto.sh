#!/usr/bin/env bash
# export-quarto.sh — export via Quarto per report data-science / accademici moderni.
#
# Quarto supporta Python/R embedded, LaTeX, HTML, ePub, Word, Revealjs slides.
# Install: https://quarto.org/docs/get-started/
#
# Usage:
#   export-quarto.sh <file.md> --format pdf|html|docx|epub|revealjs [--theme cosmo]
set -uo pipefail

FILE=""
FORMAT="pdf"
THEME=""

while [ $# -gt 0 ]; do
  case "$1" in
    --format) FORMAT="$2"; shift 2 ;;
    --theme) THEME="$2"; shift 2 ;;
    *) FILE="$1"; shift ;;
  esac
done

if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
  echo "Usage: $0 <file.md> --format pdf|html|docx|epub|revealjs [--theme NAME]" >&2
  exit 2
fi

if ! command -v quarto >/dev/null 2>&1; then
  echo "[ERR] quarto non installato" >&2
  echo "  Install: https://quarto.org/docs/get-started/" >&2
  exit 3
fi

BASE="${FILE%.md}"
QMD="${BASE}.qmd"

# Converti .md in .qmd aggiungendo front-matter Quarto
if [ ! -f "$QMD" ]; then
  python3 << EOF > "$QMD"
import pathlib, re
md = pathlib.Path("$FILE").read_text(encoding="utf-8")
theme = "$THEME"
format_val = "$FORMAT"

# Se già frontmatter, parse e arricchisci
if md.startswith("---"):
    end = md.find("---", 3)
    front = md[3:end]
    body = md[end+3:]
else:
    front = ""
    body = md

title_match = re.search(r'^title:\s*(.+)$', front, flags=re.MULTILINE)
title = title_match.group(1).strip() if title_match else pathlib.Path("$FILE").stem

print("---")
print(f"title: \"{title}\"")
print(f"lang: it")

if format_val == "pdf":
    print("format:")
    print("  pdf:")
    print("    documentclass: report")
    print("    papersize: a4")
    print("    fontsize: 11pt")
    print("    toc: true")
    print("    toc-depth: 3")
elif format_val == "html":
    print("format:")
    print(f"  html:")
    print(f"    theme: {theme or 'cosmo'}")
    print("    toc: true")
    print("    code-fold: true")
elif format_val == "docx":
    print("format: docx")
elif format_val == "epub":
    print("format:")
    print("  epub:")
    print("    toc: true")
elif format_val == "revealjs":
    print("format:")
    print("  revealjs:")
    print(f"    theme: {theme or 'simple'}")
    print("    slide-level: 2")
print("---")
print()
print(body)
EOF
fi

OUTPUT="${BASE}.$(case $FORMAT in html) echo html;; pdf) echo pdf;; docx) echo docx;; epub) echo epub;; revealjs) echo html;; *) echo $FORMAT;; esac)"

echo "[INFO] quarto render $QMD --to $FORMAT"
quarto render "$QMD" --to "$FORMAT"

if [ -f "$OUTPUT" ]; then
  echo "[OK] $OUTPUT"
  exit 0
else
  echo "[FAIL] output non generato" >&2
  exit 1
fi

#!/usr/bin/env bash
# latex-sandbox-test.sh — compila LaTeX in sandbox prima della consegna finale.
#
# Feature:
# - Tenta compile con xelatex (o lualatex, pdflatex fallback)
# - Cattura tutti gli errori (non solo exit code)
# - Verifica biber/bibtex se bibliografia presente
# - Test compilazione 2 volte (per TOC/cross-ref)
# - Output report con errori classificati
#
# Usage:
#   latex-sandbox-test.sh <RELAZIONE.tex> [--engine xelatex|lualatex|pdflatex]
set -uo pipefail

FILE=""
ENGINE="xelatex"
KEEP_ARTIFACTS=0

while [ $# -gt 0 ]; do
  case "$1" in
    --engine) ENGINE="$2"; shift 2 ;;
    --keep) KEEP_ARTIFACTS=1; shift ;;
    *) FILE="$1"; shift ;;
  esac
done

if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
  echo "Usage: $0 <file.tex> [--engine xelatex|lualatex|pdflatex] [--keep]" >&2
  exit 2
fi

if ! command -v "$ENGINE" >/dev/null 2>&1; then
  echo "[ERR] $ENGINE non installato" >&2
  for alt in xelatex lualatex pdflatex; do
    if command -v "$alt" >/dev/null 2>&1; then
      echo "  Alternative disponibile: $alt" >&2
    fi
  done
  exit 3
fi

SANDBOX=$(mktemp -d)
trap "[ $KEEP_ARTIFACTS -eq 0 ] && rm -rf $SANDBOX" EXIT

DIR=$(dirname "$FILE")
BASE=$(basename "$FILE" .tex)

# Copia tutto (file, bib, immagini, template)
cp -r "$DIR"/* "$SANDBOX"/ 2>/dev/null || true

echo "[INFO] sandbox: $SANDBOX"
echo "[INFO] engine: $ENGINE"
echo ""

cd "$SANDBOX" || exit 2

# Pass 1
echo "=== Pass 1 ==="
"$ENGINE" -interaction=nonstopmode -halt-on-error "$BASE.tex" > pass1.log 2>&1
PASS1_CODE=$?

if [ $PASS1_CODE -ne 0 ]; then
  echo "[FAIL] compilazione fallita (exit $PASS1_CODE)"
  echo ""
  echo "Errori principali:"
  grep -E '^!' pass1.log | head -10 | sed 's/^/  /'
  echo ""
  echo "Prime 20 righe di log:"
  head -40 pass1.log | sed 's/^/  /'
  exit 1
fi

# Biber se presente references.bib
if [ -f "references.bib" ] || [ -f "refs.bib" ]; then
  if command -v biber >/dev/null 2>&1; then
    echo ""
    echo "=== Biber ==="
    biber "$BASE" > biber.log 2>&1 || {
      echo "[WARN] biber errori, vedi biber.log"
      tail -10 biber.log | sed 's/^/  /'
    }
  elif command -v bibtex >/dev/null 2>&1; then
    echo ""
    echo "=== BibTeX ==="
    bibtex "$BASE" > bibtex.log 2>&1 || true
  fi
fi

# Pass 2 (risolve reference forward)
echo ""
echo "=== Pass 2 ==="
"$ENGINE" -interaction=nonstopmode "$BASE.tex" > pass2.log 2>&1 || true

# Pass 3 (risolve bibliografia)
echo "=== Pass 3 ==="
"$ENGINE" -interaction=nonstopmode "$BASE.tex" > pass3.log 2>&1
PASS3_CODE=$?

if [ $PASS3_CODE -ne 0 ]; then
  echo "[FAIL] pass 3 fallito"
  grep -E '^!' pass3.log | head -10 | sed 's/^/  /'
  exit 1
fi

# Analisi warning
echo ""
echo "=== Warning analysis ==="
UNDEF_REFS=$(grep -c "LaTeX Warning: Reference.*undefined" pass3.log || true)
UNDEF_CITES=$(grep -c "LaTeX Warning: Citation.*undefined" pass3.log || true)
OVERFULL=$(grep -c "Overfull" pass3.log || true)
UNDERFULL=$(grep -c "Underfull" pass3.log || true)

echo "  Riferimenti non definiti: $UNDEF_REFS"
echo "  Citazioni non risolte: $UNDEF_CITES"
echo "  Overfull hbox/vbox: $OVERFULL"
echo "  Underfull: $UNDERFULL"

if [ ! -f "$BASE.pdf" ]; then
  echo ""
  echo "[FAIL] PDF non generato"
  exit 1
fi

SIZE=$(stat -c %s "$BASE.pdf" 2>/dev/null || stat -f %z "$BASE.pdf" 2>/dev/null)
PAGES=$(pdfinfo "$BASE.pdf" 2>/dev/null | awk '/^Pages:/ {print $2}')

echo ""
echo "[OK] PDF compilato: $(du -h "$BASE.pdf" | cut -f1), ${PAGES:-?} pagine"

if [ "$UNDEF_REFS" -gt 0 ] || [ "$UNDEF_CITES" -gt 0 ]; then
  echo "[WARN] riferimenti/citazioni non risolte — rivedi prima di consegnare"
  exit 1
fi

exit 0

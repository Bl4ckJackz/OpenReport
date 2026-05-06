#!/usr/bin/env bash
# parallel-export.sh — esegue export pdf/docx/epub in parallelo per accelerare Step 7.
#
# Usage:
#   parallel-export.sh <input.md> [--pdf] [--docx] [--epub] [--tex-too]
#                        [--template <yaml>] [--bib <file>] [--toc]
#
# Se tutti i flag format sono assenti, assume --pdf --docx.
# Ritorna 0 se tutti successo, 1 se almeno uno fallisce (riporta quali).
set -uo pipefail

INPUT=""
DO_PDF=0
DO_DOCX=0
DO_EPUB=0
DO_TEX=0
TEMPLATE=""
BIB=""
EXTRA_ARGS=()

while [ $# -gt 0 ]; do
  case "$1" in
    --pdf) DO_PDF=1; shift ;;
    --docx) DO_DOCX=1; shift ;;
    --epub) DO_EPUB=1; shift ;;
    --tex-too) DO_TEX=1; shift ;;
    --template) TEMPLATE="$2"; shift 2 ;;
    --bib) BIB="$2"; shift 2 ;;
    --toc) EXTRA_ARGS+=(--toc); shift ;;
    -h|--help) echo "Usage: $0 <input.md> [--pdf] [--docx] [--epub] [--tex-too] [--template yaml] [--bib file]"; exit 0 ;;
    *) if [ -z "$INPUT" ]; then INPUT="$1"; else EXTRA_ARGS+=("$1"); fi; shift ;;
  esac
done

if [ -z "$INPUT" ] || [ ! -f "$INPUT" ]; then
  echo "Usage: $0 <input.md> [--pdf] [--docx] [--epub] [--tex-too]" >&2
  exit 2
fi

if [ $DO_PDF -eq 0 ] && [ $DO_DOCX -eq 0 ] && [ $DO_EPUB -eq 0 ] && [ $DO_TEX -eq 0 ]; then
  DO_PDF=1
  DO_DOCX=1
fi

if ! command -v pandoc >/dev/null 2>&1; then
  echo "[ERR] pandoc non installato" >&2
  exit 3
fi

BASE="${INPUT%.md}"
TMPDIR=$(mktemp -d)
trap "rm -rf '$TMPDIR'" EXIT

PIDS=()
declare -A JOBS
declare -A LOGS

run_job() {
  local name="$1"; shift
  local logfile="$TMPDIR/$name.log"
  LOGS[$name]="$logfile"
  ("$@" >"$logfile" 2>&1) &
  local pid=$!
  PIDS+=($pid)
  JOBS[$pid]="$name"
  echo "[START] $name (pid $pid)"
}

PANDOC_COMMON=(--standalone "${EXTRA_ARGS[@]}")
[ -n "$BIB" ] && [ -f "$BIB" ] && PANDOC_COMMON+=(--bibliography="$BIB" --citeproc)

if [ $DO_PDF -eq 1 ]; then
  PDF_ARGS=(pandoc "$INPUT" -o "${BASE}.pdf" "${PANDOC_COMMON[@]}" --pdf-engine=xelatex)
  [ -n "$TEMPLATE" ] && [ -f "$TEMPLATE" ] && PDF_ARGS+=(--template="$TEMPLATE")
  run_job "pdf" "${PDF_ARGS[@]}"
fi

if [ $DO_DOCX -eq 1 ]; then
  run_job "docx" pandoc "$INPUT" -o "${BASE}.docx" "${PANDOC_COMMON[@]}"
fi

if [ $DO_EPUB -eq 1 ]; then
  run_job "epub" pandoc "$INPUT" -o "${BASE}.epub" "${PANDOC_COMMON[@]}"
fi

if [ $DO_TEX -eq 1 ]; then
  run_job "tex" pandoc "$INPUT" -o "${BASE}.tex" "${PANDOC_COMMON[@]}"
fi

FAIL=0
FAILED_LIST=()
for pid in "${PIDS[@]}"; do
  name="${JOBS[$pid]}"
  if wait "$pid"; then
    echo "[OK] $name completato"
  else
    echo "[FAIL] $name — log:"
    cat "${LOGS[$name]}" | tail -20 | sed 's/^/    /'
    FAILED_LIST+=("$name")
    FAIL=1
  fi
done

if [ $FAIL -eq 0 ]; then
  echo ""
  echo "[OK] tutti i formati esportati in parallelo"
  exit 0
else
  echo ""
  echo "[FAIL] export falliti: ${FAILED_LIST[*]}"
  exit 1
fi

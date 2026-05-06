#!/usr/bin/env bash
# full-text-search.sh — full-text search su tutte le relazioni passate.
#
# Cerca in: RELAZIONE.md/.tex, .session/scan-summary.md, research-notes.md, state cover.
#
# Usage:
#   full-text-search.sh "query testuale" [--root relazioni/] [--type md|tex|all]
#                          [--context 3] [--limit 50]
set -uo pipefail

QUERY=""
ROOT=""
TYPE="all"
CONTEXT=2
LIMIT=50
CASE_INSENSITIVE=1

while [ $# -gt 0 ]; do
  case "$1" in
    --root) ROOT="$2"; shift 2 ;;
    --type) TYPE="$2"; shift 2 ;;
    --context) CONTEXT="$2"; shift 2 ;;
    --limit) LIMIT="$2"; shift 2 ;;
    --case) CASE_INSENSITIVE=0; shift ;;
    *) QUERY="$1"; shift ;;
  esac
done

if [ -z "$QUERY" ]; then
  echo "Usage: $0 \"query\" [--root relazioni/] [--type md|tex|all] [--context 3]" >&2
  exit 2
fi

ROOT="${ROOT:-.}"

GREP_TOOL=""
if command -v rg >/dev/null 2>&1; then
  GREP_TOOL="rg"
else
  GREP_TOOL="grep"
fi

FILE_PATTERN=""
case "$TYPE" in
  md) FILE_PATTERN='*.md' ;;
  tex) FILE_PATTERN='*.tex' ;;
  all) FILE_PATTERN='*' ;;
esac

echo "[INFO] search '$QUERY' in $ROOT/ (type: $TYPE)"
echo ""

if [ "$GREP_TOOL" = "rg" ]; then
  RG_ARGS=(--context "$CONTEXT" --color=always -m "$LIMIT")
  [ $CASE_INSENSITIVE -eq 1 ] && RG_ARGS+=(-i)
  [ "$TYPE" != "all" ] && RG_ARGS+=(--type "$TYPE")
  rg "${RG_ARGS[@]}" "$QUERY" "$ROOT" \
    --glob '!**/__pycache__/**' \
    --glob '!**/.session/backups/**' \
    --glob '!**/node_modules/**' 2>/dev/null | head -200
else
  GREP_ARGS=(-rn --color=always -C "$CONTEXT")
  [ $CASE_INSENSITIVE -eq 1 ] && GREP_ARGS+=(-i)
  if [ "$TYPE" != "all" ]; then
    find "$ROOT" -type f -name "$FILE_PATTERN" \
      ! -path '*/__pycache__/*' ! -path '*/.session/backups/*' \
      -print0 2>/dev/null | xargs -0 grep "${GREP_ARGS[@]}" "$QUERY" 2>/dev/null | head -200
  else
    grep "${GREP_ARGS[@]}" --exclude-dir=__pycache__ --exclude-dir=backups "$QUERY" -r "$ROOT" 2>/dev/null | head -200
  fi
fi

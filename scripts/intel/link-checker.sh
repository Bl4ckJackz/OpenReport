#!/usr/bin/env bash
# link-checker.sh — verifica che URL nel doc siano ancora raggiungibili.
#
# Feature:
# - Scan tutti http(s) URL del file
# - HEAD request con timeout
# - Fallback GET se HEAD non supportato
# - Output report md con status per ogni URL
# - Rate-limit configurabile (--sleep)
# - Wayback fallback (suggerisce archive.org snapshot per 404)
#
# Usage:
#   link-checker.sh <file.md> [--sleep 0.5] [--output broken-links.md]
set -uo pipefail

FILE=""
SLEEP=0.3
OUTPUT=""
TIMEOUT=10

while [ $# -gt 0 ]; do
  case "$1" in
    --sleep) SLEEP="$2"; shift 2 ;;
    --output) OUTPUT="$2"; shift 2 ;;
    --timeout) TIMEOUT="$2"; shift 2 ;;
    *) FILE="$1"; shift ;;
  esac
done

if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
  echo "Usage: $0 <file> [--sleep 0.5] [--output out.md]" >&2
  exit 2
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "[ERR] curl richiesto" >&2
  exit 3
fi

URLS=$(grep -oE 'https?://[^[:space:])\]"'"'"'>]+' "$FILE" | sort -u)
TOTAL=$(echo "$URLS" | wc -l)
[ -z "$URLS" ] && { echo "[OK] Nessun URL trovato in $FILE"; exit 0; }

REPORT=""
append() { REPORT="$REPORT$1"$'\n'; }

append "# Link-check report"
append ""
append "File: \`$FILE\`  "
append "URL trovati: $TOTAL  "
append "Data: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
append ""

OK_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

while IFS= read -r url; do
  url=${url%[.,;:]}  # strip trailing punct
  code=$(curl -sL -o /dev/null -w '%{http_code}' --max-time "$TIMEOUT" -I "$url" 2>/dev/null || echo "000")
  if [ "$code" = "000" ] || [ "$code" = "405" ] || [ "$code" = "403" ]; then
    # Fallback GET
    code=$(curl -sL -o /dev/null -w '%{http_code}' --max-time "$TIMEOUT" "$url" 2>/dev/null || echo "000")
  fi

  case "$code" in
    2*)
      append "- [OK $code] $url"
      OK_COUNT=$((OK_COUNT + 1))
      ;;
    3*)
      final=$(curl -sL -o /dev/null -w '%{url_effective}' --max-time "$TIMEOUT" "$url" 2>/dev/null || echo "")
      append "- [WARN $code] $url → $final"
      WARN_COUNT=$((WARN_COUNT + 1))
      ;;
    *)
      append "- [FAIL $code] $url"
      append "    suggerimento Wayback: https://web.archive.org/web/*/$url"
      FAIL_COUNT=$((FAIL_COUNT + 1))
      ;;
  esac
  sleep "$SLEEP"
done <<< "$URLS"

append ""
append "## Summary"
append ""
append "- OK: $OK_COUNT"
append "- WARN (redirect): $WARN_COUNT"
append "- FAIL: $FAIL_COUNT"

if [ -n "$OUTPUT" ]; then
  printf '%s' "$REPORT" > "$OUTPUT"
  echo "[OK] report -> $OUTPUT" >&2
else
  printf '%s' "$REPORT"
fi

[ $FAIL_COUNT -eq 0 ]

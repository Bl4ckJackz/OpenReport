#!/usr/bin/env bash
# auto-save.sh — crea snapshot del draft ogni N modifiche significative durante refinement.
#
# Usage:
#   auto-save.sh <draft> --output-dir .session/backups [--threshold-chars 500]
#
# Confronta md5 del draft con ultimo snapshot; se diff > threshold, salva nuovo backup.
set -uo pipefail

FILE=""
OUTDIR=""
THRESHOLD=500

while [ $# -gt 0 ]; do
  case "$1" in
    --output-dir) OUTDIR="$2"; shift 2 ;;
    --threshold-chars) THRESHOLD="$2"; shift 2 ;;
    *) FILE="$1"; shift ;;
  esac
done

if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
  echo "Usage: $0 <draft> --output-dir <dir> [--threshold-chars N]" >&2
  exit 2
fi
if [ -z "$OUTDIR" ]; then
  OUTDIR="$(dirname "$FILE")/.session/backups"
fi

mkdir -p "$OUTDIR"
CURRENT_SIZE=$(wc -c < "$FILE")
TS=$(date -u +"%Y%m%dT%H%M%SZ")
NAME=$(basename "$FILE")
SNAPSHOT="$OUTDIR/autosave-$TS-$NAME"

# trova ultimo autosave
LAST_AUTOSAVE=$(ls -1t "$OUTDIR"/autosave-*"$NAME" 2>/dev/null | head -1 || true)
if [ -n "$LAST_AUTOSAVE" ] && [ -f "$LAST_AUTOSAVE" ]; then
  LAST_SIZE=$(wc -c < "$LAST_AUTOSAVE")
  DIFF=$((CURRENT_SIZE - LAST_SIZE))
  [ $DIFF -lt 0 ] && DIFF=$((-DIFF))
  if [ "$DIFF" -lt "$THRESHOLD" ]; then
    echo "[SKIP] diff ($DIFF bytes) < threshold ($THRESHOLD)"
    exit 0
  fi
fi

cp "$FILE" "$SNAPSHOT"
echo "[OK] autosave: $SNAPSHOT"

# Prune oltre 10 autosave più recenti
ls -1t "$OUTDIR"/autosave-*"$NAME" 2>/dev/null | tail -n +11 | xargs -r rm -f
echo "[INFO] mantenuti ultimi 10 autosave"

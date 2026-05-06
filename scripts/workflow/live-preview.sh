#!/usr/bin/env bash
# live-preview.sh — server HTML locale con auto-reload del draft.
#
# Usage:
#   live-preview.sh <file.md> [--port 8765]
#
# Avvia Python http.server, rigenera HTML a ogni modifica del file md.
# Richiede pandoc (opzionale: entr per file-watch, altrimenti polling).
set -uo pipefail

FILE=""
PORT=8765
while [ $# -gt 0 ]; do
  case "$1" in
    --port) PORT="$2"; shift 2 ;;
    -h|--help) echo "Usage: $0 <file.md> [--port 8765]"; exit 0 ;;
    *) FILE="$1"; shift ;;
  esac
done

if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
  echo "Usage: $0 <file.md> [--port N]" >&2
  exit 2
fi

if ! command -v pandoc >/dev/null 2>&1; then
  echo "[ERR] pandoc mancante" >&2
  exit 3
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "[ERR] python3 mancante" >&2
  exit 3
fi

DIR=$(dirname "$FILE")
NAME=$(basename "$FILE" .md)
HTML="$DIR/.preview-$NAME.html"

render() {
  pandoc "$FILE" -o "$HTML" --standalone --toc --metadata title="Preview: $NAME" \
    --css="data:text/css,body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;max-width:780px;margin:2em auto;padding:0 1em;line-height:1.6;color:#222}h1,h2,h3{line-height:1.25}code{background:#f4f4f4;padding:.2em .4em;border-radius:3px}pre{background:#2d2d2d;color:#eee;padding:1em;border-radius:6px;overflow-x:auto}table{border-collapse:collapse;margin:1em 0}td,th{border:1px solid #ddd;padding:.5em 1em}" \
    2>&1 | head -5
  # Inject auto-reload
  printf '<meta http-equiv="refresh" content="3">\n' >> "$HTML"
}

render
echo "[OK] Preview disponibile: http://localhost:$PORT/.preview-$NAME.html"
echo "    Ctrl-C per fermare"

(
  cd "$DIR" || exit
  python3 -m http.server "$PORT" --bind 127.0.0.1 >/dev/null 2>&1 &
  SERVER_PID=$!
  trap "kill $SERVER_PID 2>/dev/null; rm -f '$HTML'" EXIT

  LAST_MTIME=0
  while true; do
    if [ -f "$FILE" ]; then
      MTIME=$(stat -c %Y "$FILE" 2>/dev/null || stat -f %m "$FILE" 2>/dev/null)
      if [ "$MTIME" != "$LAST_MTIME" ]; then
        render >/dev/null 2>&1
        LAST_MTIME="$MTIME"
        echo "[reload] $(date +%H:%M:%S)"
      fi
    fi
    sleep 2
  done
)

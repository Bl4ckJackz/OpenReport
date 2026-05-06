#!/usr/bin/env bash
# gpg-sign.sh — firma GPG del PDF/documento per authenticity proof.
#
# Produce:
# - FILE.sig (detached signature, binary)
# - FILE.asc (detached signature, ASCII armored)
#
# Verify con: gpg --verify FILE.sig FILE
#
# Usage:
#   gpg-sign.sh <file> [--key KEY_ID] [--ascii]
set -uo pipefail

FILE=""
KEY=""
ASCII=0

while [ $# -gt 0 ]; do
  case "$1" in
    --key) KEY="$2"; shift 2 ;;
    --ascii) ASCII=1; shift ;;
    *) FILE="$1"; shift ;;
  esac
done

if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
  echo "Usage: $0 <file> [--key KEY_ID] [--ascii]" >&2
  exit 2
fi

if ! command -v gpg >/dev/null 2>&1; then
  echo "[ERR] gpg non installato" >&2
  echo "  Install: apt install gnupg | brew install gnupg | winget install GnuPG.GnuPG" >&2
  exit 3
fi

# Verifica chiave privata
if [ -z "$KEY" ]; then
  KEYS=$(gpg --list-secret-keys --keyid-format LONG 2>/dev/null | grep '^sec' | wc -l)
  if [ "$KEYS" -eq 0 ]; then
    echo "[ERR] nessuna chiave GPG privata disponibile" >&2
    echo "  Generala con: gpg --full-generate-key" >&2
    exit 2
  fi
fi

GPG_ARGS=(--detach-sign)
[ $ASCII -eq 1 ] && GPG_ARGS+=(--armor)
[ -n "$KEY" ] && GPG_ARGS+=(--local-user "$KEY")

SIG_EXT=$([ $ASCII -eq 1 ] && echo "asc" || echo "sig")
SIG_FILE="${FILE}.${SIG_EXT}"

if gpg "${GPG_ARGS[@]}" --output "$SIG_FILE" "$FILE"; then
  echo "[OK] firmato: $SIG_FILE"
  echo ""
  echo "Verifica con:"
  echo "  gpg --verify \"$SIG_FILE\" \"$FILE\""
else
  echo "[FAIL] firma GPG fallita" >&2
  exit 1
fi

#!/usr/bin/env bash
# integrity-hash.sh — calcola SHA256 dei file della relazione per integrity check.
#
# Genera file HASHES.txt con SHA256 di ogni deliverable.
# Permette a destinatari di verificare che non siano stati alterati.
#
# Usage:
#   integrity-hash.sh <relazioni-dir>                    # calcola e crea HASHES.txt
#   integrity-hash.sh <relazioni-dir> --verify           # verifica hashes esistenti
set -uo pipefail

DIR=""
MODE="create"

while [ $# -gt 0 ]; do
  case "$1" in
    --verify) MODE="verify"; shift ;;
    *) DIR="$1"; shift ;;
  esac
done

if [ -z "$DIR" ] || [ ! -d "$DIR" ]; then
  echo "Usage: $0 <relazioni-dir> [--verify]" >&2
  exit 2
fi

HASH_TOOL=""
for tool in sha256sum shasum; do
  if command -v "$tool" >/dev/null 2>&1; then
    HASH_TOOL="$tool"
    break
  fi
done

if [ -z "$HASH_TOOL" ]; then
  echo "[ERR] sha256sum/shasum non disponibili" >&2
  exit 3
fi

cd "$DIR" || exit 2

if [ "$MODE" = "verify" ]; then
  if [ ! -f "HASHES.txt" ]; then
    echo "[ERR] HASHES.txt non trovato in $DIR" >&2
    exit 2
  fi
  echo "[INFO] verifica integrità $DIR..."
  if [ "$HASH_TOOL" = "sha256sum" ]; then
    sha256sum -c HASHES.txt
  else
    shasum -a 256 -c HASHES.txt
  fi
  exit $?
fi

# Create mode
echo "[INFO] calcolo SHA256 di tutti i file in $DIR..."
{
  echo "# Integrity hashes (SHA256)"
  echo "# Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "# Directory: $(basename "$DIR")"
  echo "# Verify con: bash integrity-hash.sh $(basename "$DIR") --verify"
  echo ""
  if [ "$HASH_TOOL" = "sha256sum" ]; then
    find . -type f ! -path "./.session/*" ! -name "HASHES.txt" | sort | xargs sha256sum 2>/dev/null
  else
    find . -type f ! -path "./.session/*" ! -name "HASHES.txt" | sort | xargs shasum -a 256 2>/dev/null
  fi
} > HASHES.txt

COUNT=$(grep -c '^[a-f0-9]' HASHES.txt || echo 0)
echo "[OK] HASHES.txt generato ($COUNT file)"

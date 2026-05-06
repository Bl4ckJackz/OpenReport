#!/usr/bin/env bash
# self-check.sh — orchestratore di tutti i check pre-output per /relazione.
# Usage: self-check.sh <file> [--lang=it|en] [--state=path/session-state.json]
# Exit: 0 clean, 1 WARN, 2 FAIL (blocking)

set -uo pipefail

FILE=""
LANG="it"
STATE=""
TARGET_PAGES=0
RESEARCH=""
BIB=""
BRAND=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --lang=*) LANG="${1#*=}"; shift ;;
    --state=*) STATE="${1#*=}"; shift ;;
    --target-pages=*) TARGET_PAGES="${1#*=}"; shift ;;
    --research=*) RESEARCH="${1#*=}"; shift ;;
    --bib=*) BIB="${1#*=}"; shift ;;
    --brand=*) BRAND="${1#*=}"; shift ;;
    *) FILE="$1"; shift ;;
  esac
done

if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
  echo "Usage: $0 <file> [--lang=it|en] [--state=path] [--target-pages=N]" >&2
  exit 3
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXIT=0

echo "=========================================="
echo "  SELF-CHECK: $FILE"
echo "=========================================="

# 1. Word count vs target
WORDS=$(wc -w < "$FILE")
echo ""
echo "--- Word count ---"
echo "Parole: $WORDS"
if [ "$TARGET_PAGES" -gt 0 ]; then
  TARGET_WORDS=$((TARGET_PAGES * 400))
  DEV=$(awk -v w="$WORDS" -v t="$TARGET_WORDS" 'BEGIN { printf "%.2f", (w - t) / t }')
  ABS_DEV=$(awk -v d="$DEV" 'BEGIN { print (d < 0) ? -1 * d : d }')
  echo "Target: ~$TARGET_WORDS ($TARGET_PAGES pagine), deviazione: $(awk -v d="$DEV" 'BEGIN { printf "%.0f", d*100 }')%"
  if awk -v a="$ABS_DEV" 'BEGIN { exit !(a > 0.40) }'; then
    echo "[FAIL] Lunghezza fuori range (>40% deviazione)"
    EXIT=2
  elif awk -v a="$ABS_DEV" 'BEGIN { exit !(a > 0.20) }'; then
    echo "[WARN] Lunghezza fuori target (>20%)"
    [ $EXIT -lt 1 ] && EXIT=1
  fi
fi

# 2. Forbidden terms (+brand/user extensions)
echo ""
echo "--- Forbidden terms / AI tells ---"
FORBIDDEN_ARGS=("$FILE")
[ -n "$BRAND" ] && FORBIDDEN_ARGS+=(--brand "$BRAND")
[ -f "$SCRIPT_DIR/../.user-profile.json" ] && FORBIDDEN_ARGS+=(--user-profile)
if bash "$SCRIPT_DIR/forbidden-check.sh" "${FORBIDDEN_ARGS[@]}"; then
  :
else
  echo "[FAIL] Forbidden terms presenti — vedi sopra"
  EXIT=2
fi

# 3. Citation density
echo ""
echo "--- Citation density ---"
if command -v python3 >/dev/null 2>&1; then
  if python3 "$SCRIPT_DIR/citation-density.py" "$FILE"; then
    :
  else
    [ $EXIT -lt 1 ] && EXIT=1
  fi
fi

# 4. Image references
echo ""
echo "--- Image references ---"
DIR=$(dirname "$FILE")
MISSING=0
# Markdown images
while IFS= read -r line; do
  IMG_PATH=$(echo "$line" | grep -oE '!\[[^]]*\]\([^)]+\)' | sed -E 's/.*\(([^)]+)\).*/\1/' | head -1)
  if [ -n "$IMG_PATH" ] && [[ ! "$IMG_PATH" =~ ^https?:// ]]; then
    if [ ! -f "$DIR/$IMG_PATH" ] && [ ! -f "$IMG_PATH" ]; then
      echo "[FAIL] missing: $IMG_PATH"
      MISSING=$((MISSING + 1))
    fi
  fi
done < <(grep -nE '!\[[^]]*\]\([^)]+\)' "$FILE" 2>/dev/null || true)
# LaTeX images
while IFS= read -r line; do
  IMG_PATH=$(echo "$line" | grep -oE '\\includegraphics(\[[^]]*\])?\{[^}]+\}' | sed -E 's/.*\{([^}]+)\}.*/\1/' | head -1)
  if [ -n "$IMG_PATH" ]; then
    FOUND=0
    for ext in "" .png .jpg .jpeg .pdf .svg; do
      if [ -f "$DIR/${IMG_PATH}${ext}" ] || [ -f "${IMG_PATH}${ext}" ]; then
        FOUND=1; break
      fi
    done
    if [ $FOUND -eq 0 ]; then
      echo "[FAIL] missing: $IMG_PATH"
      MISSING=$((MISSING + 1))
    fi
  fi
done < <(grep -nE '\\includegraphics' "$FILE" 2>/dev/null || true)
if [ $MISSING -eq 0 ]; then
  echo "[OK] Tutte le immagini referenziate esistono"
else
  echo "[FAIL] $MISSING immagini mancanti"
  EXIT=2
fi

# 5. Citation keys (LaTeX)
if [[ "$FILE" == *.tex ]] && [ -f "$DIR/references.bib" ]; then
  echo ""
  echo "--- Citation keys consistency (BibTeX) ---"
  ORPHAN=0
  while IFS= read -r key; do
    if ! grep -q "@\w*{[[:space:]]*$key[[:space:]]*," "$DIR/references.bib"; then
      echo "[FAIL] \\cite{$key} non trovata in references.bib"
      ORPHAN=$((ORPHAN + 1))
    fi
  done < <(grep -oE '\\cite[a-z]*\{[^}]+\}' "$FILE" | sed -E 's/\\cite[a-z]*\{([^}]+)\}/\1/' | tr ',' '\n' | sort -u)
  if [ $ORPHAN -eq 0 ]; then
    echo "[OK] Tutte le \\cite{} hanno chiave in references.bib"
  else
    EXIT=2
  fi
fi

# 6. Mock inventory consistency
echo ""
echo "--- Mock inventory ---"
MOCK_COUNT=$(grep -c '\[MOCK\]' "$FILE" 2>/dev/null || echo 0)
if [ "$MOCK_COUNT" -gt 0 ]; then
  if grep -qiE "(Nota metodologica|Methodology note)" "$FILE"; then
    echo "[OK] $MOCK_COUNT marker [MOCK] presenti, sezione 'Nota metodologica' trovata"
  else
    echo "[FAIL] $MOCK_COUNT [MOCK] usati ma manca sezione 'Nota metodologica'"
    EXIT=2
  fi
else
  echo "[OK] Nessun [MOCK] nel documento"
fi

# 7. Readability
if command -v python3 >/dev/null 2>&1; then
  echo ""
  python3 "$SCRIPT_DIR/readability.py" "$FILE" --lang="$LANG" || true
fi

# 8. Tone drift
if command -v python3 >/dev/null 2>&1; then
  echo ""
  if python3 "$SCRIPT_DIR/tone-drift.py" "$FILE" --lang="$LANG"; then
    :
  else
    [ $EXIT -lt 1 ] && EXIT=1
  fi
fi

# 9. Voice lock verify (se state ha voice_profile)
if [ -n "$STATE" ] && [ -f "$STATE" ] && command -v python3 >/dev/null 2>&1; then
  if grep -q '"voice_profile"' "$STATE"; then
    echo ""
    if python3 "$SCRIPT_DIR/voice-lock.py" verify "$FILE" --state "$STATE"; then
      :
    else
      [ $EXIT -lt 1 ] && EXIT=1
    fi
  fi
fi

# 10. Fact-check (solo se --research fornito o esiste .session/research-notes.md)
if command -v python3 >/dev/null 2>&1; then
  AUTO_RESEARCH="$DIR/.session/research-notes.md"
  RES_FILE=""
  if [ -n "$RESEARCH" ] && [ -f "$RESEARCH" ]; then
    RES_FILE="$RESEARCH"
  elif [ -f "$AUTO_RESEARCH" ]; then
    RES_FILE="$AUTO_RESEARCH"
  fi
  if [ -n "$RES_FILE" ]; then
    echo ""
    echo "--- Fact-check (URL/DOI/citazioni vs research-notes) ---"
    FC_ARGS=("$FILE" --research "$RES_FILE")
    [ -n "$STATE" ] && FC_ARGS+=(--state "$STATE")
    if python3 "$SCRIPT_DIR/fact-check.py" "${FC_ARGS[@]}"; then
      :
    else
      [ $EXIT -lt 1 ] && EXIT=1
    fi
  fi
fi

# 11. Cross-ref lint (label/ref, \cite, anchor md, figure/tabelle, immagini)
if command -v python3 >/dev/null 2>&1; then
  echo ""
  echo "--- Cross-ref lint ---"
  CR_ARGS=("$FILE" --base-dir "$DIR")
  AUTO_BIB="$DIR/references.bib"
  if [ -n "$BIB" ] && [ -f "$BIB" ]; then
    CR_ARGS+=(--bib "$BIB")
  elif [ -f "$AUTO_BIB" ]; then
    CR_ARGS+=(--bib "$AUTO_BIB")
  fi
  if python3 "$SCRIPT_DIR/cross-ref-lint.py" "${CR_ARGS[@]}"; then
    :
  else
    EXIT=2
  fi
fi

# 12. Temporal check (date coerenti, range, mismatch cover)
if command -v python3 >/dev/null 2>&1; then
  echo ""
  echo "--- Temporal check ---"
  TC_ARGS=("$FILE")
  [ -n "$STATE" ] && TC_ARGS+=(--state "$STATE")
  if python3 "$SCRIPT_DIR/temporal-check.py" "${TC_ARGS[@]}"; then
    :
  else
    [ $EXIT -lt 1 ] && EXIT=1
  fi
fi

echo ""
echo "=========================================="
case $EXIT in
  0) echo "  RISULTATO: ✓ CLEAN — pronto per output finale" ;;
  1) echo "  RISULTATO: ⚠ WARN — rivedere prima di consegnare" ;;
  2) echo "  RISULTATO: ✗ FAIL — BLOCCA output, fix obbligatorio" ;;
esac
echo "=========================================="
exit $EXIT

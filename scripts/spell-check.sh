#!/usr/bin/env bash
# spell-check.sh — spell-check del draft via hunspell.
#
# Supporta dizionari custom (glossari brand, termini tecnici).
# Skip code block markdown e LaTeX math.
#
# Requisiti: hunspell (apt install hunspell hunspell-it; brew install hunspell)
#            dizionari: /usr/share/hunspell/it_IT.dic (o en_US.dic)
#
# Usage:
#   spell-check.sh <file> [--lang it_IT|en_US] [--dict custom-words.txt]
set -uo pipefail

FILE=""
LANG="it_IT"
CUSTOM_DICT=""

while [ $# -gt 0 ]; do
  case "$1" in
    --lang) LANG="$2"; shift 2 ;;
    --dict) CUSTOM_DICT="$2"; shift 2 ;;
    *) FILE="$1"; shift ;;
  esac
done

if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
  echo "Usage: $0 <file> [--lang it_IT|en_US] [--dict words.txt]" >&2
  exit 2
fi

if ! command -v hunspell >/dev/null 2>&1; then
  echo "[WARN] hunspell non installato; skip spell-check" >&2
  echo "  Install: apt install hunspell hunspell-it  (Linux)" >&2
  echo "           brew install hunspell && brew install hunspell-it  (macOS)" >&2
  echo "           Windows: installa da https://hunspell.github.io/" >&2
  exit 0
fi

# Costruisce dict aggiuntivo con glossario brand + termini tecnici
TMP_DICT=$(mktemp)
trap "rm -f $TMP_DICT ${TMP_DICT}.pre" EXIT

{
  # Glossario brand
  SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  if [ -f "$SKILL_DIR/.brand-profile.json" ] && command -v python3 >/dev/null 2>&1; then
    python3 -c "
import json
try:
    bp = json.load(open(r'$SKILL_DIR/.brand-profile.json'))
    for b in bp.get('brands', []):
        for g in (b.get('glossario') or {}).values():
            print(g)
        print(b.get('ragione_sociale', ''))
        print(b.get('nome', ''))
except Exception:
    pass
" 2>/dev/null
  fi
  [ -n "$CUSTOM_DICT" ] && [ -f "$CUSTOM_DICT" ] && cat "$CUSTOM_DICT"
} | grep -v '^$' | sort -u > "$TMP_DICT"

# Prepara doc pulito: rimuove code blocks, latex math, link URL
python3 << EOF > "${TMP_DICT}.pre"
import re
text = open(r"$FILE", encoding="utf-8").read()
text = re.sub(r'\`\`\`[\s\S]*?\`\`\`', ' ', text)
text = re.sub(r'\`[^\`]+\`', ' ', text)
text = re.sub(r'\$\$[\s\S]*?\$\$', ' ', text)
text = re.sub(r'\$[^\$]+\$', ' ', text)
text = re.sub(r'https?://\S+', ' ', text)
text = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', ' ', text)  # LaTeX commands
print(text)
EOF

# Esegui hunspell con dictionary personale
HUNSPELL_ARGS=(-d "$LANG" -l)
[ -s "$TMP_DICT" ] && HUNSPELL_ARGS+=(-p "$TMP_DICT")

MISSPELLED=$(hunspell "${HUNSPELL_ARGS[@]}" < "${TMP_DICT}.pre" | sort -u | head -80)

if [ -z "$MISSPELLED" ]; then
  echo "[OK] Nessun errore ortografico rilevato"
  exit 0
fi

COUNT=$(echo "$MISSPELLED" | wc -l)
echo "[WARN] $COUNT parole sconosciute al dizionario:"
echo "$MISSPELLED" | sed 's/^/  • /'
echo ""
echo "Suggerimento: se sono termini tecnici/propri corretti, aggiungili a:"
echo "  $SKILL_DIR/.brand-profile.json (glossario)"
echo "  oppure --dict <custom-words.txt>"
exit 1

#!/usr/bin/env bash
# export-typst.sh — converte markdown a Typst e compila.
#
# Typst = alternativa moderna a LaTeX, compile 10x più veloce.
#
# Flow:
# 1. pandoc md → typst (se pandoc supporta)
# 2. typst compile foo.typ → foo-typst.pdf
#
# Installa Typst: https://github.com/typst/typst (cargo install typst-cli)
#
# Usage:
#   export-typst.sh <file.md> [--template template.typ] [-o out.pdf] [--redline [backup|approved|imported|auto]]
set -uo pipefail

FILE=""
TEMPLATE=""
OUTPUT=""
REDLINE_MODE="off"
REDLINE_BASELINE="auto"

while [ $# -gt 0 ]; do
  case "$1" in
    --template) TEMPLATE="$2"; shift 2 ;;
    -o|--output) OUTPUT="$2"; shift 2 ;;
    --redline)
      REDLINE_MODE="on"
      if [[ "${2:-}" =~ ^(backup|approved|imported|auto)$ ]]; then
        REDLINE_BASELINE="$2"; shift 2
      else
        shift
      fi
      ;;
    --redline=*)
      REDLINE_MODE="on"
      REDLINE_BASELINE="${1#--redline=}"
      shift
      ;;
    *) FILE="$1"; shift ;;
  esac
done

if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
  echo "Usage: $0 <file.md> [--template t.typ] [-o out.pdf] [--redline [backup|approved|imported|auto]]" >&2
  exit 2
fi

if ! command -v pandoc >/dev/null 2>&1; then
  echo "[ERR] pandoc richiesto per conversione" >&2
  exit 3
fi

BASE="${FILE%.md}"
OUT_SUFFIX=""
TYPST_PREAMBLE=""

# --- Redline prep ---
PANDOC_INPUT="$FILE"

if [ "$REDLINE_MODE" = "on" ]; then
  source "$(dirname "${BASH_SOURCE[0]}")/../_check-pandoc-critic.sh"
  check_pandoc_critic || exit $?
  SESSION_DIR=$(dirname "$FILE")
  source "$(dirname "${BASH_SOURCE[0]}")/../_resolve-baseline.sh"
  BASELINE=$(resolve_baseline_path "$SESSION_DIR" "$REDLINE_BASELINE")
  if [ -n "$BASELINE" ] && [ -f "$BASELINE" ]; then
    REDLINED="$SESSION_DIR/.session/redline/.redlined-$(basename "$FILE")"
    REDLINED_BRACKETED="$SESSION_DIR/.session/redline/.redlined-bracketed-$(basename "$FILE")"
    mkdir -p "$(dirname "$REDLINED")"
    python3 "$(dirname "${BASH_SOURCE[0]}")/../workflow/redline-generator.py" "$BASELINE" "$FILE" -o "$REDLINED" --mode word
    python3 "$(dirname "${BASH_SOURCE[0]}")/../_critic-preprocess.py" "$REDLINED" -o "$REDLINED_BRACKETED"
    PANDOC_INPUT="$REDLINED_BRACKETED"
    OUT_SUFFIX="-redline"
    TYPST_PREAMBLE='#let ins(body) = text(fill: rgb("#2A9D8F"))[#underline(body)]
#let del(body) = text(fill: rgb("#E63946"))[#strike(body)]
#let repl(new, old) = [#del(old)#ins(new)]
'
  else
    echo "[redline] WARN: baseline non trovata, export pulito" >&2
  fi
fi

TYP_FILE="${BASE}${OUT_SUFFIX}-typst.typ"
if [ -n "$OUT_SUFFIX" ]; then
  OUTPUT="${OUTPUT:-${BASE}${OUT_SUFFIX}.pdf}"
else
  OUTPUT="${OUTPUT:-${BASE}-typst.pdf}"
fi

# Build pandoc filter args
PANDOC_FILTERS=()
if [ "$REDLINE_MODE" = "on" ] && [ -n "$OUT_SUFFIX" ]; then
  PANDOC_FILTERS=(--filter "$(dirname "${BASH_SOURCE[0]}")/critic-to-typst.py")
fi

# pandoc output in typst
echo "[1/2] pandoc: md → typst"
pandoc "$PANDOC_INPUT" -o "$TYP_FILE" "${PANDOC_FILTERS[@]}" 2>/dev/null || {
  # Fallback: pandoc vecchio non supporta typst, genera template base
  echo "[INFO] pandoc non supporta typst direttamente, genero wrapper minimale..."
  python3 - "$PANDOC_INPUT" "$TYP_FILE" << 'PYEOF'
import re, pathlib, sys
md = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
out = pathlib.Path(sys.argv[2])
lines = []
lines.append('#set document(title: "Relazione")')
lines.append('#set page(paper: "a4", margin: 2.5cm)')
lines.append('#set text(font: "New Computer Modern", size: 11pt, lang: "it")')
lines.append('#set heading(numbering: "1.1")')
lines.append('#show heading.where(level: 1): it => [#pagebreak(weak: true) #it]')
lines.append('')
# Convert heading
md = re.sub(r'^(#+)\s+(.+)$', lambda m: '=' * len(m.group(1)) + ' ' + m.group(2), md, flags=re.MULTILINE)
# Convert bold/italic
md = re.sub(r'\*\*(.+?)\*\*', r'*\1*', md)
md = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'_\1_', md)
# Code blocks
md = re.sub(r'\`\`\`(\w*)\n([\s\S]*?)\n\`\`\`', lambda m: f'```{m.group(1)}\n{m.group(2)}\n```', md)
lines.append(md)
out.write_text('\n'.join(lines), encoding="utf-8")
PYEOF
}

# Inject preamble at top of .typ file if redline active
if [ -n "$TYPST_PREAMBLE" ]; then
  TMPF=$(mktemp --suffix=.typ 2>/dev/null || mktemp -t relazione-typ.XXXXXX)
  printf '%s\n' "$TYPST_PREAMBLE" > "$TMPF"
  cat "$TYP_FILE" >> "$TMPF"
  mv "$TMPF" "$TYP_FILE"
fi

# Check typst available before compile
if ! command -v typst >/dev/null 2>&1; then
  echo "[WARN] typst non installato — .typ generato ma non compilato" >&2
  echo "  Install: cargo install typst-cli" >&2
  echo "  oppure: brew install typst / scoop install typst" >&2
  echo "[OK] $TYP_FILE generato (typst assente, PDF non prodotto)"
  exit 0
fi

# Compila
echo "[2/2] typst compile"
if [ -n "$TEMPLATE" ] && [ -f "$TEMPLATE" ]; then
  typst compile --font-path "$(dirname "$TEMPLATE")" "$TYP_FILE" "$OUTPUT"
else
  typst compile "$TYP_FILE" "$OUTPUT"
fi

if [ $? -eq 0 ] && [ -f "$OUTPUT" ]; then
  SIZE=$(du -h "$OUTPUT" | cut -f1)
  echo "[OK] $OUTPUT ($SIZE)"
  exit 0
else
  echo "[FAIL] compilazione typst fallita" >&2
  exit 1
fi

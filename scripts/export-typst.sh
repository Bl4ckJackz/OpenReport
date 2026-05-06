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
#   export-typst.sh <file.md> [--template template.typ] [-o out.pdf]
set -uo pipefail

FILE=""
TEMPLATE=""
OUTPUT=""

while [ $# -gt 0 ]; do
  case "$1" in
    --template) TEMPLATE="$2"; shift 2 ;;
    -o|--output) OUTPUT="$2"; shift 2 ;;
    *) FILE="$1"; shift ;;
  esac
done

if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
  echo "Usage: $0 <file.md> [--template t.typ] [-o out.pdf]" >&2
  exit 2
fi

if ! command -v typst >/dev/null 2>&1; then
  echo "[ERR] typst non installato" >&2
  echo "  Install: cargo install typst-cli" >&2
  echo "  oppure: brew install typst / scoop install typst" >&2
  exit 3
fi

if ! command -v pandoc >/dev/null 2>&1; then
  echo "[ERR] pandoc richiesto per conversione" >&2
  exit 3
fi

BASE="${FILE%.md}"
TYP_FILE="${BASE}-typst.typ"
OUTPUT="${OUTPUT:-${BASE}-typst.pdf}"

# pandoc output in typst
echo "[1/2] pandoc: md → typst"
pandoc "$FILE" -o "$TYP_FILE" 2>/dev/null || {
  # Fallback: pandoc vecchio non supporta typst, genera template base
  echo "[INFO] pandoc non supporta typst direttamente, genero wrapper minimale..."
  python3 << EOF > "$TYP_FILE"
import re, pathlib
md = pathlib.Path("$FILE").read_text(encoding="utf-8")
print('#set document(title: "Relazione")')
print('#set page(paper: "a4", margin: 2.5cm)')
print('#set text(font: "New Computer Modern", size: 11pt, lang: "it")')
print('#set heading(numbering: "1.1")')
print('#show heading.where(level: 1): it => [#pagebreak(weak: true) #it]')
print()
# Convert heading
md = re.sub(r'^(#+)\s+(.+)$', lambda m: '=' * len(m.group(1)) + ' ' + m.group(2), md, flags=re.MULTILINE)
# Convert bold/italic
md = re.sub(r'\*\*(.+?)\*\*', r'*\1*', md)
md = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'_\1_', md)
# Code blocks
md = re.sub(r'\`\`\`(\w*)\n([\s\S]*?)\n\`\`\`', lambda m: f'```{m.group(1)}\n{m.group(2)}\n```', md)
print(md)
EOF
}

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

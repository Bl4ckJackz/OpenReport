#!/usr/bin/env bash
# bundle.sh — impacchetta tutti gli output finali in un .zip pronto da consegnare.
#
# Include: .md, .tex, .pdf, .docx, .epub, .bib, img/, SUMMARY.md, SLIDES.*
# Esclude: .session/, *.log, *.aux, *.toc, *.bbl, *.out, *.fls, *.fdb_latexmk
#
# Genera anche README-deliverable.md con: cosa contiene, ordine di lettura.
#
# Usage:
#   bundle.sh <output_folder> [--name=<slug>] [--no-pdf]

set -euo pipefail

DIR=""
NAME=""
NO_PDF=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --name=*) NAME="${1#*=}"; shift ;;
    --no-pdf) NO_PDF=1; shift ;;
    *) DIR="$1"; shift ;;
  esac
done

if [ -z "$DIR" ] || [ ! -d "$DIR" ]; then
  echo "Usage: $0 <output_folder> [--name=<slug>] [--no-pdf]" >&2
  exit 2
fi

cd "$DIR"

# Naming
DATE=$(date +%Y-%m-%d)
if [ -z "$NAME" ]; then
  # Try to extract title from session-state
  if [ -f .session/session-state.json ] && command -v python3 >/dev/null; then
    NAME=$(python3 -c "import json; print(json.load(open('.session/session-state.json')).get('cover',{}).get('titolo','relazione'))" 2>/dev/null | tr ' ' '-' | tr -cd '[:alnum:]-' | tr '[:upper:]' '[:lower:]')
  fi
  [ -z "$NAME" ] && NAME="relazione"
fi

ZIP_NAME="${NAME}-${DATE}.zip"
STAGING=".bundle-staging"

rm -rf "$STAGING"
mkdir -p "$STAGING"

# Files to include
INCLUDE_PATTERNS=(
  "*.md" "*.tex" "*.bib" "*.docx" "*.epub" "*.pptx"
  "img/*" "images/*" "assets/*" "figures/*"
  "SUMMARY.md" "SLIDES.md" "SLIDES.pdf" "SLIDES.pptx"
  "GLOSSARIO.md"
)

if [ $NO_PDF -eq 0 ]; then
  INCLUDE_PATTERNS+=("*.pdf")
fi

EXCLUDE_PATTERNS=(
  ".session/*" ".bundle-staging/*"
  "*.log" "*.aux" "*.toc" "*.lof" "*.lot" "*.bbl" "*.blg"
  "*.out" "*.fls" "*.fdb_latexmk" "*.synctex.gz"
)

# Copy matching files
for pat in "${INCLUDE_PATTERNS[@]}"; do
  for f in $pat; do
    [ -e "$f" ] || continue
    # check exclusions
    skip=0
    for ex in "${EXCLUDE_PATTERNS[@]}"; do
      [[ "$f" == $ex ]] && skip=1 && break
    done
    [ $skip -eq 1 ] && continue
    target="$STAGING/$f"
    mkdir -p "$(dirname "$target")"
    cp "$f" "$target" 2>/dev/null || true
  done
done

# Generate README-deliverable.md
cat > "$STAGING/README-deliverable.md" <<EOF
# Contenuto del bundle

**Generato:** $(date '+%Y-%m-%d %H:%M')
**Cartella sorgente:** \`$DIR\`

## File principali (ordine di lettura consigliato)

EOF

# Lista file finali in ordine logico
for f in SUMMARY.md *.pdf *.docx *.epub *.md *.tex *.bib; do
  if [ -e "$STAGING/$f" ]; then
    SIZE=$(du -h "$STAGING/$f" 2>/dev/null | cut -f1)
    echo "- \`$f\` ($SIZE)" >> "$STAGING/README-deliverable.md"
  fi
done

cat >> "$STAGING/README-deliverable.md" <<'EOF'

## Convenzioni

- `SUMMARY.md` — sintesi 1-pagina (leggi questo per primo)
- `RELAZIONE.pdf` — versione moderna (stile business, template Eisvogel)
- `RELAZIONE-tex.pdf` — versione accademica classica (compilata da LaTeX)
- `RELAZIONE.docx` — formato Word per editing/commenti
- `*.md` / `*.tex` — sorgenti modificabili
- `references.bib` — bibliografia (se presente)
- `img/` — figure incluse nel documento

## Note

I file sorgente (`.md`/`.tex`) sono editabili. PDF/DOCX sono derivati e vanno rigenerati se il sorgente cambia.
EOF

# Crea zip
ZIP_PATH="$DIR/$ZIP_NAME"
[ -f "$ZIP_PATH" ] && rm "$ZIP_PATH"

if command -v zip >/dev/null 2>&1; then
  (cd "$STAGING" && zip -rq "../$ZIP_NAME" .)
elif command -v 7z >/dev/null 2>&1; then
  (cd "$STAGING" && 7z a -tzip "../$ZIP_NAME" . > /dev/null)
elif command -v powershell >/dev/null 2>&1; then
  powershell -NoProfile -Command "Compress-Archive -Path '$STAGING/*' -DestinationPath '$ZIP_NAME' -Force"
else
  echo "ERROR: nessun tool zip disponibile (zip / 7z / powershell)" >&2
  rm -rf "$STAGING"
  exit 3
fi

rm -rf "$STAGING"

if [ -f "$ZIP_NAME" ]; then
  SIZE=$(du -h "$ZIP_NAME" | cut -f1)
  echo "✓ Bundle creato: $ZIP_NAME ($SIZE)"
  echo "  $(pwd)/$ZIP_NAME"
else
  echo "ERROR: bundle non creato" >&2
  exit 4
fi

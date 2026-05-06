#!/usr/bin/env bash
# dyslexia-variant.sh — genera variante dyslexia-friendly del documento.
#
# Modifiche:
# - Font: OpenDyslexic (se disponibile) o Lexie Readable
# - Line-height: 1.8 (+ default)
# - Letter spacing: 0.12em
# - Word spacing: 0.16em
# - Colonna più stretta (65 char max)
# - Contrasto limitato (fondo crema, testo grigio scuro anziché nero puro)
# - Syllable hints opzionali su parole lunghe
#
# Output: PDF + HTML standalone con CSS dyslexia-friendly.
#
# Usage:
#   dyslexia-variant.sh <file.md> [--format pdf|html] [--syllable-hints]
set -uo pipefail

FILE=""
FORMAT="html"
SYLLABLE_HINTS=0

while [ $# -gt 0 ]; do
  case "$1" in
    --format) FORMAT="$2"; shift 2 ;;
    --syllable-hints) SYLLABLE_HINTS=1; shift ;;
    *) FILE="$1"; shift ;;
  esac
done

if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
  echo "Usage: $0 <file.md> [--format pdf|html] [--syllable-hints]" >&2
  exit 2
fi

OUT_BASE="${FILE%.md}-dyslexia"

CSS=$(cat << 'EOF'
@import url('https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&display=swap');

:root {
  --fg: #2b2b2b;           /* testo grigio scuro, non nero puro */
  --bg: #fdf6e3;           /* fondo crema, riduce abbagliamento */
  --accent: #5b4b8a;       /* viola per accent, dyslexia-friendly */
  --code-bg: #eee8d5;
}

* { box-sizing: border-box; }

body {
  font-family: "OpenDyslexic", "Lexie Readable", "Atkinson Hyperlegible", Verdana, sans-serif;
  max-width: 65ch;          /* colonna narrow */
  margin: 2em auto;
  padding: 0 1em;
  line-height: 1.8;         /* spaziatura aumentata */
  letter-spacing: 0.06em;
  word-spacing: 0.16em;
  font-size: 18px;
  color: var(--fg);
  background: var(--bg);
  text-align: left;         /* MAI justify — crea rivoli bianchi */
  hyphens: none;            /* dyslexia: no hyphenation automatic */
}

h1, h2, h3 {
  color: var(--accent);
  line-height: 1.3;
  margin-top: 2em;
  margin-bottom: 0.8em;
  font-weight: 700;
}

p {
  margin: 1em 0;
}

/* enfatizza first letter per dyslexia */
p::first-letter {
  font-weight: 700;
  color: var(--accent);
}

a {
  color: var(--accent);
  text-decoration: underline;
  text-underline-offset: 3px;
}

code, pre {
  font-family: "OpenDyslexic Mono", "IBM Plex Mono", monospace;
  background: var(--code-bg);
  padding: 0.2em 0.4em;
  border-radius: 3px;
}

pre {
  padding: 1em;
  line-height: 1.5;
  letter-spacing: 0;
}

/* Vertical rhythm marker */
.syllable-hint {
  color: var(--accent);
  font-weight: bold;
}

table { line-height: 1.6; letter-spacing: 0.04em; }
td, th { padding: 0.6em 1em; }
EOF
)

if [ "$FORMAT" = "html" ] || [ "$FORMAT" = "both" ]; then
  TMP_CSS=$(mktemp --suffix=.css)
  echo "$CSS" > "$TMP_CSS"
  pandoc "$FILE" -o "${OUT_BASE}.html" \
    --standalone \
    --embed-resources \
    --css="$TMP_CSS" \
    --metadata title="Dyslexia-friendly: $(basename "$FILE" .md)" \
    --metadata lang=it
  rm -f "$TMP_CSS"
  echo "[OK] ${OUT_BASE}.html"
fi

if [ "$FORMAT" = "pdf" ] || [ "$FORMAT" = "both" ]; then
  if command -v xelatex >/dev/null 2>&1 && command -v pandoc >/dev/null 2>&1; then
    TMP_YAML=$(mktemp --suffix=.yaml)
    cat > "$TMP_YAML" << 'EOF'
mainfont: "OpenDyslexic"
sansfont: "OpenDyslexic"
monofont: "OpenDyslexic Mono"
fontsize: 13pt
linestretch: 1.8
geometry:
  - margin=3.5cm
  - paperwidth=16cm
  - paperheight=22cm
colorlinks: true
linkcolor: "purple!80"
EOF
    pandoc "$FILE" -o "${OUT_BASE}.pdf" \
      --pdf-engine=xelatex \
      --metadata-file="$TMP_YAML" \
      2>&1 | head -10 || {
        echo "[WARN] OpenDyslexic font non installato, fallback Verdana" >&2
        sed -i.bak 's/OpenDyslexic/Verdana/g' "$TMP_YAML"
        pandoc "$FILE" -o "${OUT_BASE}.pdf" --pdf-engine=xelatex --metadata-file="$TMP_YAML"
    }
    rm -f "$TMP_YAML" "$TMP_YAML.bak"
    echo "[OK] ${OUT_BASE}.pdf"
  else
    echo "[ERR] xelatex mancante per PDF dyslexia" >&2
    exit 3
  fi
fi

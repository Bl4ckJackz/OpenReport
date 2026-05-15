#!/usr/bin/env bash
# export-html-standalone.sh — HTML singolo file con CSS embedded, pronto per intranet.
#
# Feature:
# - Self-contained (tutte le immagini base64-embed, CSS inline)
# - Responsive (mobile-friendly)
# - Dark mode support
# - Print-friendly (stampa su carta A4 senza sidebar)
# - Accessibility AA-compliant
#
# Usage:
#   export-html-standalone.sh <file.md> [-o out.html] [--theme light|dark|auto] [--redline [backup|approved|imported|auto]]
set -uo pipefail

FILE=""
OUTPUT=""
THEME="auto"
REDLINE_MODE="off"
REDLINE_BASELINE="auto"

while [ $# -gt 0 ]; do
  case "$1" in
    -o|--output) OUTPUT="$2"; shift 2 ;;
    --theme) THEME="$2"; shift 2 ;;
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
  echo "Usage: $0 <file.md> [-o out.html] [--theme light|dark|auto] [--redline [backup|approved|imported|auto]]" >&2
  exit 2
fi

if ! command -v pandoc >/dev/null 2>&1; then
  echo "[ERR] pandoc richiesto" >&2
  exit 3
fi

BASE="${FILE%.md}"
OUTPUT="${OUTPUT:-${BASE}.html}"
BASE_DIR=$(dirname "$FILE")

CSS=$(cat << 'EOF'
:root {
  --fg: #222;
  --bg: #fff;
  --muted: #666;
  --accent: #1D3557;
  --code-bg: #f4f4f4;
  --border: #ddd;
}
@media (prefers-color-scheme: dark) {
  :root.auto {
    --fg: #e4e4e4;
    --bg: #1a1a1a;
    --muted: #aaa;
    --accent: #7FB2D9;
    --code-bg: #2a2a2a;
    --border: #444;
  }
}
:root.dark {
  --fg: #e4e4e4;
  --bg: #1a1a1a;
  --muted: #aaa;
  --accent: #7FB2D9;
  --code-bg: #2a2a2a;
  --border: #444;
}
* { box-sizing: border-box; }
html { font-size: 16px; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  max-width: 780px;
  margin: 0 auto;
  padding: 2em 1em;
  line-height: 1.65;
  color: var(--fg);
  background: var(--bg);
  -webkit-font-smoothing: antialiased;
}
h1, h2, h3, h4 { line-height: 1.25; color: var(--accent); margin-top: 1.8em; }
h1 { font-size: 2rem; border-bottom: 3px solid var(--accent); padding-bottom: .3em; }
h2 { font-size: 1.5rem; }
h3 { font-size: 1.2rem; }
a { color: var(--accent); text-decoration: underline; text-underline-offset: 2px; }
a:hover { background: var(--code-bg); }
code {
  background: var(--code-bg);
  padding: .2em .4em;
  border-radius: 3px;
  font-family: "SF Mono", Menlo, monospace;
  font-size: .92em;
}
pre {
  background: var(--code-bg);
  padding: 1em;
  border-radius: 6px;
  overflow-x: auto;
  border: 1px solid var(--border);
}
pre code { background: none; padding: 0; }
table { border-collapse: collapse; margin: 1em 0; width: 100%; }
td, th { border: 1px solid var(--border); padding: .5em 1em; text-align: left; }
th { background: var(--code-bg); }
img { max-width: 100%; height: auto; display: block; margin: 1.5em auto; }
blockquote {
  border-left: 4px solid var(--accent);
  padding: .4em 1em;
  color: var(--muted);
  margin: 1em 0;
  background: var(--code-bg);
}
hr { border: none; border-top: 1px solid var(--border); margin: 2em 0; }
@media print {
  body { max-width: none; padding: 0; }
  a { color: #000; text-decoration: none; }
  pre, blockquote { page-break-inside: avoid; }
}
.theme-toggle {
  position: fixed; top: 1em; right: 1em;
  background: var(--code-bg); border: 1px solid var(--border);
  padding: .5em 1em; border-radius: 4px; cursor: pointer;
  font-family: inherit; color: var(--fg);
}
@media print { .theme-toggle { display: none; } }
.critic-add { background: #d4f5d4; color: #1a5c1a; text-decoration: underline; }
.critic-del { background: #ffd4d4; color: #7a0000; text-decoration: line-through; }
.critic-comment { background: #fff3cd; color: #856404; border-bottom: 2px dotted #856404; }
.critic-highlight { background: #fff9c4; }
EOF
)

# pandoc con embed immagini base64 + CSS inline
TMP_CSS=$(mktemp --suffix=.css 2>/dev/null || mktemp -t relazione-css.XXXXXX)
trap "rm -f $TMP_CSS" EXIT
echo "$CSS" > "$TMP_CSS"

# --- Redline prep ---
PANDOC_INPUT="$FILE"
OUT_SUFFIX=""

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
  else
    echo "[redline] WARN: baseline non trovata, export pulito" >&2
  fi
fi

# Recalculate output with suffix
FINAL_OUTPUT="${OUTPUT}"
if [ -n "$OUT_SUFFIX" ]; then
  FINAL_OUTPUT="${BASE}${OUT_SUFFIX}.html"
fi

pandoc "$PANDOC_INPUT" -o "$FINAL_OUTPUT" \
  --standalone \
  --embed-resources \
  --toc \
  --toc-depth=3 \
  --css="$TMP_CSS" \
  --resource-path="$BASE_DIR" \
  --metadata title="$(basename "$FILE" .md)" \
  --metadata lang=it

# Aggiungi theme toggle JS e class root
python3 - "$FINAL_OUTPUT" "$THEME" << 'PYEOF'
import sys, pathlib
out_path = pathlib.Path(sys.argv[1])
theme = sys.argv[2]
html = out_path.read_text(encoding="utf-8")
html = html.replace('<html ', f'<html class="{theme}" ', 1)
html = html.replace('</body>', '''
<button class="theme-toggle" onclick="
var h = document.documentElement;
h.classList.toggle('dark');
h.classList.toggle('light');
">\U0001f313</button>
</body>''')
out_path.write_text(html, encoding="utf-8")
PYEOF

SIZE=$(du -h "$FINAL_OUTPUT" | cut -f1)
echo "[OK] $FINAL_OUTPUT ($SIZE) — standalone, self-contained"

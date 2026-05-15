#!/usr/bin/env bash
# live-preview-draft.sh — live preview con badge per sezione + auto-open browser
#
# Variante "skeleton-aware" di live-preview.sh: pre-elabora il draft per
# evidenziare lo stato di ogni SECTION (done/writing/pending) e i placeholder
# [DA RIEMPIRE] / [MOCK] mentre Step 4 li riempie.
#
# Usage:
#   live-preview-draft.sh <session-folder> [--port 8766] [--no-open]
#
# Esempio:
#   bash scripts/live-preview-draft.sh ./relazioni/
#
# Richiede: pandoc, python3.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./_browser-open.sh
source "$SCRIPT_DIR/_browser-open.sh"

SESSION=""
PORT=8766
DO_OPEN=1
while [ $# -gt 0 ]; do
  case "$1" in
    --port) PORT="$2"; shift 2 ;;
    --no-open) DO_OPEN=0; shift ;;
    -h|--help)
      echo "Usage: $0 <session-folder> [--port N] [--no-open]"
      exit 0 ;;
    *) SESSION="$1"; shift ;;
  esac
done

if [ -z "$SESSION" ] || [ ! -d "$SESSION" ]; then
  echo "Usage: $0 <session-folder>  (cartella tipo 'relazioni/' o 'relazioni-2026-...')" >&2
  exit 2
fi

for cmd in pandoc python3; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "[ERR] $cmd mancante" >&2
    exit 3
  fi
done

# Trova il file draft principale (primo che esiste)
DRAFT=""
for name in RELAZIONE.md TESI.md PAPER.md ANALISI.md DOC.md POSTMORTEM.md \
            RELAZIONE-FINALE.md ESPERIENZA.md; do
  if [ -f "$SESSION/$name" ]; then
    DRAFT="$SESSION/$name"
    break
  fi
done
# Fallback: primo .md nella root della sessione
if [ -z "$DRAFT" ]; then
  for f in "$SESSION"/*.md; do
    [ -f "$f" ] && DRAFT="$f" && break
  done
fi

if [ -z "$DRAFT" ]; then
  echo "[ERR] Nessun draft .md trovato in $SESSION" >&2
  echo "      Avvia /relazione prima per generare il draft." >&2
  exit 2
fi

NAME=$(basename "$DRAFT" .md)
WORK_DIR="$SESSION/.session/preview"
mkdir -p "$WORK_DIR"
PROCESSED="$WORK_DIR/_processed-$NAME.md"
HTML="$WORK_DIR/.preview-$NAME.html"

PREPROCESS_PY="$WORK_DIR/_preprocess.py"

# Scrivi lo script di pre-processing una volta sola (idempotente)
cat > "$PREPROCESS_PY" <<'PYEOF'
"""Pre-processing del draft: inserisce stato sezione + header sticky con conteggi."""
import re
import sys
from pathlib import Path

draft = Path(sys.argv[1])
out = Path(sys.argv[2])

text = draft.read_text(encoding="utf-8", errors="replace")

SECTION_RE = re.compile(
    r"<!--\s*SECTION:\s*(\S+)\s*\|\s*ORDER:\s*(\d+)\s*\|\s*(.*?)\s*-->"
)
PLACEHOLDER_RE = re.compile(r"\[DA RIEMPIRE[^\]]*\]")
MOCK_RE = re.compile(r"\[MOCK\]")

# Trova tutte le SECTION e i loro range
matches = list(SECTION_RE.finditer(text))
sections = []
for i, m in enumerate(matches):
    start = m.end()
    end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
    content = text[start:end]
    placeholders = len(PLACEHOLDER_RE.findall(content))
    real_content = PLACEHOLDER_RE.sub("", content)
    has_real = bool(re.search(r"\w", real_content))
    if placeholders == 0 and has_real:
        status = "done"
    elif has_real and placeholders > 0:
        status = "writing"
    else:
        status = "pending"
    sections.append({
        "slug": m.group(1),
        "order": int(m.group(2)),
        "status": status,
        "match_start": m.start(),
        "match_end": m.end(),
        "placeholders": placeholders,
    })

# Conteggi globali
total = len(sections) or 1
done = sum(1 for s in sections if s["status"] == "done")
writing = sum(1 for s in sections if s["status"] == "writing")
pending = sum(1 for s in sections if s["status"] == "pending")
words = len(re.findall(r"\b\w+\b", text))
mocks = len(MOCK_RE.findall(text))
pages_est = max(1, words // 400)

# Header sticky (HTML pre-pandoc)
header = (
    f'<div class="draft-status-header">'
    f'<div class="dsh-progress"><strong>{done}</strong>/{total} sezioni done · '
    f'<span class="badge writing">{writing}</span> writing · '
    f'<span class="badge pending">{pending}</span> pending</div>'
    f'<div class="dsh-stats">{words:,} parole · ~{pages_est} pp · '
    f'<span class="badge warn">{mocks} mock</span></div>'
    f'</div>\n\n'
)

# Inietta badge dopo ogni SECTION marker
def inject(m):
    slug = m.group(1)
    order = m.group(2)
    # cerca lo status nella lista sopra
    s = next((x for x in sections if x["slug"] == slug and str(x["order"]) == order), None)
    status = s["status"] if s else "pending"
    badge = (
        f'\n\n<div class="section-status" data-status="{status}">'
        f'<span class="ss-num">§{order}</span> '
        f'<span class="ss-slug">{slug}</span> '
        f'<span class="badge {status}">{status}</span>'
        f'</div>\n'
    )
    return m.group(0) + badge

# Costruisci output: header + draft con badge iniettati
processed = header + SECTION_RE.sub(inject, text)

out.write_text(processed, encoding="utf-8")
PYEOF

# CSS aggiuntivo per evidenziare placeholder e badge
EXTRA_CSS='body{font-family:-apple-system,BlinkMacSystemFont,"Inter",sans-serif;max-width:880px;margin:0 auto;padding:0 1em 4em;line-height:1.6;color:#222}
.draft-status-header{position:sticky;top:0;background:#fff;border-bottom:2px solid #1D3557;padding:12px 16px;margin:0 -1em 24px;display:flex;justify-content:space-between;align-items:center;font-size:.9em;z-index:100;box-shadow:0 2px 8px rgba(0,0,0,.06)}
.dsh-progress{font-weight:500}
.badge{display:inline-block;padding:1px 8px;border-radius:999px;font-size:.78em;font-weight:500;border:1px solid #ccc;background:#f4f4f4}
.badge.done{background:rgba(42,157,143,.12);color:#2A9D8F;border-color:#2A9D8F}
.badge.writing{background:rgba(244,162,97,.15);color:#c2691a;border-color:#F4A261}
.badge.pending{background:rgba(173,181,189,.15);color:#666;border-color:#ADB5BD}
.badge.warn{background:rgba(233,196,106,.15);color:#b8860b;border-color:#E9C46A}
.section-status{margin:8px 0 12px;padding:6px 10px;border-radius:6px;font-size:.85em;display:flex;gap:8px;align-items:center;background:#f8f9fa;border-left:4px solid #ADB5BD}
.section-status[data-status="done"]{border-left-color:#2A9D8F;background:rgba(42,157,143,.04)}
.section-status[data-status="writing"]{border-left-color:#F4A261;background:rgba(244,162,97,.06)}
.section-status[data-status="pending"]{border-left-color:#ADB5BD}
.ss-num{font-family:"JetBrains Mono",monospace;font-weight:600;color:#1D3557}
.ss-slug{font-family:"JetBrains Mono",monospace;font-size:.9em;color:#666}
h1,h2,h3{line-height:1.25}
code{background:#f4f4f4;padding:.2em .4em;border-radius:3px}
pre{background:#2d2d2d;color:#eee;padding:1em;border-radius:6px;overflow-x:auto}
table{border-collapse:collapse;margin:1em 0}
td,th{border:1px solid #ddd;padding:.5em 1em}
/* Highlight placeholders */
p:has-text("[DA RIEMPIRE"){background:rgba(230,57,70,.08);padding:8px;border-left:3px solid #E63946}
.preview-placeholder{background:rgba(230,57,70,.15);color:#E63946;padding:2px 6px;border-radius:3px;font-family:"JetBrains Mono",monospace;font-size:.85em;font-weight:600}
.preview-mock{background:rgba(244,162,97,.18);color:#c2691a;padding:2px 6px;border-radius:3px;font-family:"JetBrains Mono",monospace;font-size:.85em;font-weight:600}'

render() {
  python3 "$PREPROCESS_PY" "$DRAFT" "$PROCESSED"
  pandoc "$PROCESSED" -o "$HTML" --standalone --toc --metadata title="Live: $NAME" \
    --css="data:text/css,$(echo "$EXTRA_CSS" | tr '\n' ' ')" 2>&1 | head -3
  # Post-process HTML: wrappa [DA RIEMPIRE:...] e [MOCK] in span colorati
  python3 - <<'POSTPY' "$HTML"
import re, sys
p = sys.argv[1]
with open(p, 'r', encoding='utf-8') as f:
    h = f.read()
h = re.sub(r"\[DA RIEMPIRE[^\]]*\]", lambda m: f'<span class="preview-placeholder">{m.group(0)}</span>', h)
h = re.sub(r"\[MOCK\]", '<span class="preview-mock">[MOCK]</span>', h)
with open(p, 'w', encoding='utf-8') as f:
    f.write(h)
POSTPY
  # Inject auto-reload meta
  printf '<meta http-equiv="refresh" content="3">\n' >> "$HTML"
}

render
URL="http://localhost:$PORT/.preview-$NAME.html"
echo "[OK] Live preview: $URL"
echo "    Sessione: $SESSION"
echo "    Draft: $DRAFT"
echo "    Ctrl-C per fermare"

(
  cd "$WORK_DIR" || exit
  python3 -m http.server "$PORT" --bind 127.0.0.1 >/dev/null 2>&1 &
  SERVER_PID=$!
  trap "kill $SERVER_PID 2>/dev/null; rm -f '$HTML' '$PROCESSED'" EXIT

  # Auto-open browser dopo 1 secondo
  if [ "$DO_OPEN" = "1" ]; then
    (sleep 1 && open_in_browser "$HTML" >/dev/null 2>&1) &
  fi

  LAST_MTIME=0
  while true; do
    if [ -f "$DRAFT" ]; then
      MTIME=$(stat -c %Y "$DRAFT" 2>/dev/null || stat -f %m "$DRAFT" 2>/dev/null)
      if [ "$MTIME" != "$LAST_MTIME" ]; then
        render >/dev/null 2>&1
        LAST_MTIME="$MTIME"
        echo "[reload] $(date +%H:%M:%S)"
      fi
    fi
    sleep 2
  done
)

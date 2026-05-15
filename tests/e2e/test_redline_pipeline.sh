#!/usr/bin/env bash
# End-to-end test of redline pipeline: baseline + draft → 4 formats with track-changes.
set -euo pipefail

SKILL_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
WORK=$(mktemp -d)
trap "rm -rf '$WORK'" EXIT

mkdir -p "$WORK/.session/backups"
cat > "$WORK/.session/backups/2026-05-14-RELAZIONE.md" <<'EOF'
# Test E2E

Versione originale del documento.
EOF
cat > "$WORK/RELAZIONE.md" <<'EOF'
# Test E2E

Versione modificata e ampliata del documento.
EOF

# HTML
bash "$SKILL_DIR/scripts/export/export-html-standalone.sh" "$WORK/RELAZIONE.md" --redline backup
[ -f "$WORK/RELAZIONE-redline.html" ] || { echo "FAIL: html missing"; exit 1; }
grep -qE "critic-add|critic-del" "$WORK/RELAZIONE-redline.html" || { echo "FAIL: html no critic spans"; exit 1; }
echo "[OK] HTML"

# DOCX via parallel-export
bash "$SKILL_DIR/scripts/export/parallel-export.sh" "$WORK/RELAZIONE.md" --docx --redline backup
[ -f "$WORK/RELAZIONE-redline.docx" ] || { echo "FAIL: docx missing"; exit 1; }
# DOCX markers: pandoc-via-our-filter emits w:strike / w:u for visual track-changes.
if unzip -p "$WORK/RELAZIONE-redline.docx" word/document.xml 2>/dev/null | grep -qE "w:strike|w:u w:val"; then
  echo "[OK] DOCX (w:strike/w:u visual track-changes)"
else
  echo "FAIL: docx no track-changes markers"; exit 1
fi

# PDF Typst (skip if typst absent)
if command -v typst >/dev/null 2>&1; then
  bash "$SKILL_DIR/scripts/export/export-typst.sh" "$WORK/RELAZIONE.md" --redline backup
  [ -f "$WORK"/RELAZIONE-redline*.pdf ] || { echo "FAIL: typst pdf missing"; exit 1; }
  echo "[OK] Typst PDF"
else
  echo "[SKIP] typst not installed"
fi

# PDF LaTeX via parallel-export (skip if xelatex absent)
if command -v xelatex >/dev/null 2>&1; then
  bash "$SKILL_DIR/scripts/export/parallel-export.sh" "$WORK/RELAZIONE.md" --pdf --redline backup
  [ -f "$WORK/RELAZIONE-redline.pdf" ] || { echo "FAIL: latex pdf missing"; exit 1; }
  echo "[OK] LaTeX PDF"
else
  echo "[SKIP] xelatex not installed"
fi

echo ""
echo "OK: e2e redline pipeline"

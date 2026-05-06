#!/usr/bin/env bash
# git-activity-extended.sh — estrae attivita git + PR/issue via gh CLI per status-report.
#
# Output md con: commit per autore, PR merged, issue chiusi, contributor top.
#
# Usage:
#   git-activity-extended.sh --since "2 weeks ago" [--repo owner/repo] [--output report.md]
set -uo pipefail

SINCE="2 weeks ago"
REPO=""
OUTPUT=""

while [ $# -gt 0 ]; do
  case "$1" in
    --since) SINCE="$2"; shift 2 ;;
    --repo) REPO="$2"; shift 2 ;;
    --output) OUTPUT="$2"; shift 2 ;;
    *) shift ;;
  esac
done

OUT=""
append() { OUT="$OUT$1"$'\n'; }

append "## Git Activity ($SINCE)"
append ""

# Commits per autore
append "### Commit per autore"
append '```'
git log --since="$SINCE" --pretty=format:'%an' 2>/dev/null | sort | uniq -c | sort -rn | head -20 | while read -r count author; do
  printf '%5d  %s\n' "$count" "$author"
done
append '```'
append ""

# Top file modificati
append "### Top file modificati"
append '```'
git log --since="$SINCE" --name-only --pretty=format: 2>/dev/null | sort | uniq -c | sort -rn | head -15
append '```'
append ""

# PR e issue via gh se disponibile
if command -v gh >/dev/null 2>&1; then
  GH_REPO_ARGS=()
  [ -n "$REPO" ] && GH_REPO_ARGS+=(--repo "$REPO")

  append "### Pull Request chiuse"
  gh pr list --state merged --limit 20 --search "merged:>$(date -d "$SINCE" +%Y-%m-%d 2>/dev/null || date -v-14d +%Y-%m-%d)" "${GH_REPO_ARGS[@]}" --json number,title,author 2>/dev/null \
    | python3 -c "import json,sys; [print(f\"- #{p['number']} {p['title']} — @{p['author']['login']}\") for p in json.load(sys.stdin)]" 2>/dev/null || append "(gh list fallito)"
  append ""

  append "### Issue chiusi"
  gh issue list --state closed --limit 20 --search "closed:>$(date -d "$SINCE" +%Y-%m-%d 2>/dev/null || date -v-14d +%Y-%m-%d)" "${GH_REPO_ARGS[@]}" --json number,title 2>/dev/null \
    | python3 -c "import json,sys; [print(f\"- #{i['number']} {i['title']}\") for i in json.load(sys.stdin)]" 2>/dev/null || append "(gh list fallito)"
fi

if [ -n "$OUTPUT" ]; then
  printf '%s' "$OUT" > "$OUTPUT"
  echo "[OK] -> $OUTPUT" >&2
else
  printf '%s' "$OUT"
fi

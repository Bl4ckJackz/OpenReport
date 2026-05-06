#!/usr/bin/env bash
# git-history-miner.sh — estrae cronologia attività da repo git per /relazione
#
# Per tipologie stage/finale/progetto/tesi: genera tabella settimanale di commit
# da inserire nelle sezioni "Cronologia attività" o "Attività svolte".
#
# Usage:
#   git-history-miner.sh [--repo=<path>] [--since=YYYY-MM-DD] [--until=YYYY-MM-DD]
#                        [--author=<email>] [--out=<file>] [--format=md|tex|json]

set -euo pipefail

REPO="."
SINCE=""
UNTIL=""
AUTHOR=""
OUT="-"
FORMAT="md"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo=*)   REPO="${1#*=}"; shift ;;
    --since=*)  SINCE="${1#*=}"; shift ;;
    --until=*)  UNTIL="${1#*=}"; shift ;;
    --author=*) AUTHOR="${1#*=}"; shift ;;
    --out=*)    OUT="${1#*=}"; shift ;;
    --format=*) FORMAT="${1#*=}"; shift ;;
    *) echo "Unknown: $1" >&2; exit 2 ;;
  esac
done

cd "$REPO"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "ERROR: $REPO non è un repo git" >&2
  exit 2
fi

GIT_OPTS=""
[ -n "$SINCE" ]  && GIT_OPTS="$GIT_OPTS --since=$SINCE"
[ -n "$UNTIL" ]  && GIT_OPTS="$GIT_OPTS --until=$UNTIL"
[ -n "$AUTHOR" ] && GIT_OPTS="$GIT_OPTS --author=$AUTHOR"

# Periodo coperto
FIRST=$(git log $GIT_OPTS --reverse --format=%aI | head -1)
LAST=$(git log $GIT_OPTS --format=%aI | head -1)
TOTAL=$(git log $GIT_OPTS --oneline | wc -l)
AUTHORS=$(git log $GIT_OPTS --format='%aN <%aE>' | sort -u)

emit() { if [ "$OUT" = "-" ]; then echo "$1"; else echo "$1" >> "$OUT"; fi; }

[ "$OUT" != "-" ] && > "$OUT"

case "$FORMAT" in
  md)
    emit "## Cronologia attività (estratto automatico da git history)"
    emit ""
    emit "**Periodo:** $FIRST → $LAST  "
    emit "**Commit totali:** $TOTAL  "
    emit "**Autori:**"
    while IFS= read -r a; do emit "- $a"; done <<< "$AUTHORS"
    emit ""
    emit "### Attività per settimana"
    emit ""
    emit "| Settimana | Commit | Sintesi |"
    emit "|---|---|---|"

    # Group commits per settimana ISO
    git log $GIT_OPTS --format='%aI%x09%s' | while IFS=$'\t' read -r DATE MSG; do
      WEEK=$(date -d "$DATE" +"%Y-W%V" 2>/dev/null || echo "$DATE" | cut -c1-10)
      echo "$WEEK"
    done | sort | uniq -c | sort | while read -r COUNT WEEK; do
      SAMPLE=$(git log $GIT_OPTS --format=%s --since="$WEEK-1" --until="$WEEK-7" 2>/dev/null | head -3 | tr '\n' '; ' || echo "")
      emit "| $WEEK | $COUNT | ${SAMPLE:0:120} |"
    done

    emit ""
    emit "### Highlights (commit più rilevanti)"
    emit ""
    git log $GIT_OPTS --format='- **%ad** — %s' --date=short | head -30 | while IFS= read -r line; do
      emit "$line"
    done

    emit ""
    emit "### Distribuzione modifiche (file toccati)"
    emit ""
    emit "\`\`\`"
    git log $GIT_OPTS --name-only --format='' | sort | uniq -c | sort -rn | head -20
    emit "\`\`\`"
    ;;

  tex)
    emit "\\section{Cronologia attività (estratto automatico da git history)}"
    emit "\\textbf{Periodo:} $FIRST $\\to$ $LAST \\\\"
    emit "\\textbf{Commit totali:} $TOTAL \\\\"
    emit ""
    emit "\\begin{longtable}{|l|r|p{8cm}|}"
    emit "\\hline"
    emit "\\textbf{Settimana} & \\textbf{Commit} & \\textbf{Sintesi} \\\\"
    emit "\\hline"
    git log $GIT_OPTS --format='%aI%x09%s' | while IFS=$'\t' read -r DATE MSG; do
      WEEK=$(date -d "$DATE" +"%Y-W%V" 2>/dev/null || echo "$DATE" | cut -c1-10)
      echo "$WEEK"
    done | sort | uniq -c | while read -r COUNT WEEK; do
      emit "$WEEK & $COUNT & \\\\"
    done
    emit "\\hline"
    emit "\\end{longtable}"
    ;;

  json)
    emit "{"
    emit "  \"period\": {\"first\": \"$FIRST\", \"last\": \"$LAST\"},"
    emit "  \"total_commits\": $TOTAL,"
    emit "  \"commits\": ["
    git log $GIT_OPTS --format='    {"date":"%aI","author":"%aN","subject":%s}' | head -100 | sed 's/$/,/' | sed '$ s/,$//'
    emit "  ]"
    emit "}"
    ;;
esac

echo "Done. Output: $OUT" >&2

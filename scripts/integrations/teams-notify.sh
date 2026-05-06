#!/usr/bin/env bash
# teams-notify.sh — notifica Microsoft Teams via webhook.
#
# Usage:
#   export TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/...
#   teams-notify.sh --title "Relazione pronta" --text "ACME proposta v1.0 approvata"
set -uo pipefail

TITLE=""
TEXT=""
while [ $# -gt 0 ]; do
  case "$1" in
    --title) TITLE="$2"; shift 2 ;;
    --text) TEXT="$2"; shift 2 ;;
    *) shift ;;
  esac
done

if [ -z "$TITLE" ] || [ -z "$TEXT" ]; then
  echo "Usage: $0 --title TITLE --text TEXT" >&2
  exit 2
fi

if [ -z "${TEAMS_WEBHOOK_URL:-}" ]; then
  echo "[ERR] set TEAMS_WEBHOOK_URL" >&2
  exit 2
fi

PAYLOAD=$(python3 -c "
import json, sys
print(json.dumps({
    '@type': 'MessageCard',
    '@context': 'https://schema.org/extensions',
    'summary': '$TITLE',
    'title': '$TITLE',
    'text': '''$TEXT''',
}))
")

curl -s -X POST -H "Content-Type: application/json" --data "$PAYLOAD" "$TEAMS_WEBHOOK_URL"
echo ""

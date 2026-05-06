#!/usr/bin/env bash
# slack-notify.sh — invia notifica Slack via webhook incoming.
#
# Usage:
#   export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
#   slack-notify.sh "Relazione ACME approvata" [--channel "#general"] [--color good]
set -uo pipefail

MSG=""
CHANNEL=""
COLOR="good"
while [ $# -gt 0 ]; do
  case "$1" in
    --channel) CHANNEL="$2"; shift 2 ;;
    --color) COLOR="$2"; shift 2 ;;
    *) MSG="$1"; shift ;;
  esac
done

if [ -z "$MSG" ]; then
  echo "Usage: $0 <message> [--channel X] [--color good|warning|danger]" >&2
  exit 2
fi

if [ -z "${SLACK_WEBHOOK_URL:-}" ]; then
  echo "[ERR] set SLACK_WEBHOOK_URL" >&2
  exit 2
fi

PAYLOAD=$(cat <<EOF
{
  "attachments": [{
    "color": "$COLOR",
    "text": $(printf '%s' "$MSG" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')
    $([ -n "$CHANNEL" ] && echo ', "channel": "'"$CHANNEL"'"' || echo '')
  }]
}
EOF
)

if command -v curl >/dev/null 2>&1; then
  curl -s -X POST -H "Content-Type: application/json" --data "$PAYLOAD" "$SLACK_WEBHOOK_URL" | tee /dev/stderr
  echo ""
else
  echo "[ERR] curl mancante" >&2
  exit 3
fi

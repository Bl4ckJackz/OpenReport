#!/usr/bin/env bash
# secret-scan.sh — scansiona file relazione per secret/token noti
# Usage: secret-scan.sh <file>
# Exit: 0 clean, 1 secret found (BLOCCANTE per export)

set -uo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <file>" >&2
  exit 2
fi

FILE="$1"
[ -f "$FILE" ] || { echo "ERROR: $FILE non trovato" >&2; exit 2; }

FOUND=0

check() {
  local label="$1" pattern="$2"
  local matches
  matches=$(grep -nE "$pattern" "$FILE" 2>/dev/null || true)
  if [ -n "$matches" ]; then
    echo ""
    echo "[$label]"
    echo "$matches" | head -10
    FOUND=1
  fi
}

check "AWS_ACCESS_KEY"   "AKIA[0-9A-Z]{16}"
check "GITHUB_TOKEN"     "gh[pousr]_[A-Za-z0-9]{36,}"
check "GITLAB_TOKEN"     "glpat-[A-Za-z0-9_-]{20,}"
check "ANTHROPIC_KEY"    "sk-ant-(api|sid)[a-zA-Z0-9_-]{20,}"
check "OPENAI_KEY"       "sk-[A-Za-z0-9]{40,}"
check "GOOGLE_API_KEY"   "AIza[0-9A-Za-z_-]{35}"
check "SLACK_TOKEN"      "xox[baprs]-[A-Za-z0-9-]{10,}"
check "STRIPE_LIVE"      "sk_live_[0-9a-zA-Z]{24,}"
check "STRIPE_PUB_LIVE"  "pk_live_[0-9a-zA-Z]{24,}"
check "DISCORD_TOKEN"    "[MN][A-Za-z\\d]{23}\\.[\\w-]{6}\\.[\\w-]{27,}"
check "GENERIC_PASSWORD" "(password|passwd|pwd)[\"' :=]+[\"' ]?[A-Za-z0-9!@#\$%^&*()_+-]{6,}[\"' ]?"
check "API_KEY_GENERIC"  "(api[_-]?key|apikey|api_secret)[\"' :=]+[\"' ]?[A-Za-z0-9_-]{16,}[\"' ]?"
check "PRIVATE_KEY"      "-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"
check "JWT_TOKEN"        "eyJ[A-Za-z0-9_-]+\\.eyJ[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+"
check "DB_URL_CREDS"     "(postgres|mysql|mongodb|redis)://[^:]+:[^@]+@"
check "ENV_FILE_PATTERN" "^[A-Z_]+=[\"']?[A-Za-z0-9_-]{8,}"
check "BEARER_TOKEN"     "Bearer\\s+[A-Za-z0-9_.-]{20,}"

echo ""
if [ $FOUND -eq 0 ]; then
  echo "[OK] Nessun secret rilevato in $FILE"
  exit 0
else
  echo ""
  echo "✗ BLOCCANTE — secret nel documento. RIMUOVI prima di consegnare."
  echo "  Sostituisci con placeholder: [API_KEY_REDACTED] / [TOKEN_REDACTED] / etc."
  exit 1
fi

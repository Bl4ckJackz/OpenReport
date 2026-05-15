#!/usr/bin/env bash
# _check-pandoc-critic.sh — sourced helper. Defines check_pandoc_critic().
# Verifies pandoc is installed (we use a preprocessor for CriticMarkup, no extension needed).
# Returns 0 on success, 3 on failure with a clear error.

check_pandoc_critic() {
  if ! command -v pandoc >/dev/null 2>&1; then
    echo "[redline] ERR: pandoc non installato. Installa pandoc e riprova." >&2
    return 3
  fi
  return 0
}

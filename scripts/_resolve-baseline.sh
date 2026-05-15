#!/usr/bin/env bash
# _resolve-baseline.sh — shared baseline path resolver for redline-aware exports.
# Sourced, not executed. Defines resolve_baseline_path().

resolve_baseline_path() {
  local session="$1"
  local kind="$2"
  case "$kind" in
    auto)
      if [ -f "$session/.session/redline/baseline.md" ]; then
        echo "$session/.session/redline/baseline.md"; return
      fi
      ls -d "$session"/archive/*/ 2>/dev/null | sort | tail -n1 | while read -r d; do
        [ -f "${d}RELAZIONE.md" ] && echo "${d}RELAZIONE.md"
      done
      ;;
    approved)
      local latest
      latest=$(ls -d "$session"/archive/*/ 2>/dev/null | sort | tail -n1)
      [ -n "$latest" ] && [ -f "${latest}RELAZIONE.md" ] && echo "${latest}RELAZIONE.md"
      ;;
    backup)
      ls -t "$session"/.session/backups/*.md 2>/dev/null | head -n1
      ;;
    imported)
      ls -t "$session"/.session/feedback/applied-*.md 2>/dev/null | head -n1
      ;;
  esac
}

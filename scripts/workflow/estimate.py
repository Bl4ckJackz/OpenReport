#!/usr/bin/env python3
"""
relazione-estimate — predict token usage, context-window pressure, and time
for a relazione before starting.

The skill runs inside Claude Code and is free at the point of use; this tool
helps you decide:

  - Whether to enable outline-first (Step 3.6) for long docs
  - Whether to split the work in two sessions (Pausa + /clear)
  - Whether --draft-only mode is more appropriate
  - How long to expect the interactive session to take

Usage:
    python scripts/workflow/estimate.py --tipologia tesi --pages 80 --online
    python scripts/workflow/estimate.py --tipologia tecnica --pages 30 --outline-first
    python scripts/workflow/estimate.py --pages 50 --json
"""
from __future__ import annotations

import argparse
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Heuristics derived from steps/token-budget-guard.md and observed sessions.
# All numbers are token counts.

OUTPUT_TOKENS_PER_PAGE = 530          # ~400 words/page * 1.33 tokens/word
REFINEMENT_TOKENS_PER_PAGE = 250      # Step 5 iterations
COMPANION_TOKENS = 1500               # exec summary, slide deck, etc.

BASE_INPUT_TOKENS = 8000              # SKILL.md base + scan + state churn
ONLINE_INPUT_PER_PAGE = 150
ONLINE_INPUT_CAP = 8000
MOCK_INPUT_PER_PAGE = 80
STATE_CHURN_PER_PAGE = 100

# Claude Code context window assumed (Sonnet 4.6 1M-context GA at time of writing).
# The skill aims to stay well under this; pressure thresholds below.
CONTEXT_WINDOW = 200_000              # conservative — most workflows behave like 200k


def estimate_tokens(pages: int, online: bool, mock: bool, outline_first: bool) -> dict:
    output = (
        pages * OUTPUT_TOKENS_PER_PAGE
        + pages * REFINEMENT_TOKENS_PER_PAGE
        + COMPANION_TOKENS
    )
    if outline_first and pages >= 30:
        output = int(output * 0.7) + 2500  # +2500 for the outline pass itself

    research = min(pages * ONLINE_INPUT_PER_PAGE, ONLINE_INPUT_CAP) if online else 0
    mock_overhead = pages * MOCK_INPUT_PER_PAGE if mock else 0
    input_total = (
        BASE_INPUT_TOKENS + research + mock_overhead + pages * STATE_CHURN_PER_PAGE
    )

    return {
        "input_tokens": input_total,
        "output_tokens": output,
        "total_tokens": input_total + output,
    }


def context_pressure(total_tokens: int) -> dict:
    """Peak fraction of the context window expected during the session."""
    pct = round(100 * total_tokens / CONTEXT_WINDOW)
    if pct < 30:
        verdict = "comfortable"
    elif pct < 60:
        verdict = "moderate"
    elif pct < 90:
        verdict = "tight — consider Pausa + /clear at checkpoints"
    else:
        verdict = "over budget — split in 2 sessions or use --draft-only"
    return {"peak_percent": pct, "verdict": verdict}


def estimate_minutes(pages: int) -> tuple[int, int]:
    """Interactive session duration, min and max minutes."""
    return (max(5, int(pages * 1.5)), max(10, int(pages * 3)))


def recommendations(args, tokens: dict, pressure: dict) -> list[str]:
    out: list[str] = []
    if not args.outline_first and args.pages >= 60:
        out.append("Attiva --outline-first: per pages >= 60 risparmia ~30% output e cattura problemi di scope subito.")
    elif not args.outline_first and args.pages >= 30:
        out.append("Considera --outline-first: per pages >= 30 spesso vale il round-trip dell'outline.")
    if pressure["peak_percent"] >= 60:
        out.append("Context tight: pianifica una Pausa + /clear a Step 5 (refinement) per liberare context.")
    if pressure["peak_percent"] >= 90:
        out.append("Modalità --draft-only: genera scheletro + 1 paragrafo per sezione, espandi tu manualmente.")
    if args.pages >= 40 and not args.online:
        out.append("Per pages >= 40 senza ricerca online il rischio di citazioni mancanti aumenta. Valuta se attivare --online.")
    return out


def render_human(args, tokens: dict, pressure: dict, recs: list[str]) -> None:
    print(f"\nrelazione-estimate — {args.tipologia} · {args.pages} pp · {args.lingua}\n")
    print("Token usage (heuristic, ±30%):")
    print(f"  Input:  {tokens['input_tokens']:>8,} tokens")
    print(f"  Output: {tokens['output_tokens']:>8,} tokens")
    print(f"  Total:  {tokens['total_tokens']:>8,} tokens\n")

    print(f"Context-window pressure: {pressure['peak_percent']}% di {CONTEXT_WINDOW:,}")
    print(f"  -> {pressure['verdict']}\n")

    mn, mx = estimate_minutes(args.pages)
    print(f"Tempo sessione interattiva (Step 1 -> Step 9): {mn}-{mx} minuti")
    print("  (1.5-3 min/pagina; setup veloce o codebase piccolo accorcia)\n")

    if args.outline_first and args.pages >= 30:
        print("Modificatori applicati: outline-first attivo (-30% output, +2.5k outline pass).")
    if args.online:
        print(f"Modificatori applicati: ricerca online (+input fino a {ONLINE_INPUT_CAP:,}).")
    if args.mock:
        print("Modificatori applicati: mock data tracking.")
    if args.outline_first or args.online or args.mock:
        print()

    if recs:
        print("Raccomandazioni:")
        for r in recs:
            print(f"  - {r}")
        print()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tipologia", default="generica",
                    help="tesi, tecnica, status-report, etc. (cosmetico nell'header)")
    ap.add_argument("--pages", type=int, required=True, help="numero di pagine A4 attese")
    ap.add_argument("--lingua", default="italiano", help="cosmetico nell'header")
    ap.add_argument("--online", action="store_true", help="conta ricerca online")
    ap.add_argument("--mock", action="store_true", help="conta tracking mock data")
    ap.add_argument("--outline-first", action="store_true",
                    help="conta sconto da Step 3.6 outline approval")
    ap.add_argument("--json", action="store_true", help="output JSON invece che human")
    args = ap.parse_args()

    if args.pages < 1:
        print("Pages must be >= 1", file=sys.stderr)
        return 2

    tokens = estimate_tokens(args.pages, args.online, args.mock, args.outline_first)
    pressure = context_pressure(tokens["total_tokens"])
    recs = recommendations(args, tokens, pressure)

    if args.json:
        json.dump(
            {
                "input": vars(args),
                "tokens": tokens,
                "context_pressure": pressure,
                "minutes": estimate_minutes(args.pages),
                "recommendations": recs,
            },
            sys.stdout,
            indent=2,
        )
        sys.stdout.write("\n")
    else:
        render_human(args, tokens, pressure, recs)

    return 0


if __name__ == "__main__":
    sys.exit(main())

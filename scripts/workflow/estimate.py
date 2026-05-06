#!/usr/bin/env python3
"""
relazione-estimate — predict token usage, cost, and time for a relazione before starting.

Usage:
    python scripts/workflow/estimate.py --tipologia tesi --pages 80 --lingua italiano
    python scripts/workflow/estimate.py --tipologia status-report --pages 3 --model haiku
    python scripts/workflow/estimate.py --json --tipologia tecnica --pages 30

The estimate is heuristic — actual usage varies by ±30%. Use it to decide:
  - Sync vs batch (batch = -50% if not interactive)
  - Sonnet vs Haiku (Haiku = ~3-4x cheaper, OK for short factual reports)
  - Whether to enable outline-first (Step 3.6) for long docs
"""
from __future__ import annotations

import argparse
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Pricing per million tokens, USD list price (late 2025 / early 2026)
# Source: https://www.anthropic.com/pricing#anthropic-api
PRICING_USD = {
    "haiku-4.5":  {"input": 1.00,  "output": 5.00},
    "sonnet-4.6": {"input": 3.00,  "output": 15.00},
    "opus-4.7":   {"input": 15.00, "output": 75.00},
}

# Approx EUR/USD rate (refresh periodically)
USD_TO_EUR = 0.92

# Output token cost per page of markdown report (~400 words/page * 1.33 tok/word)
OUTPUT_TOKENS_PER_PAGE = 530

# Refinement overhead per page (Step 5 iterations)
REFINEMENT_TOKENS_PER_PAGE = 250

# Companion artifacts (executive summary, slide deck, etc.) — flat
COMPANION_TOKENS = 1500

# Base input per session: SKILL.md + state + scan + tool registry roundtrips
BASE_INPUT_TOKENS = 8000

# Online research adds context per page, capped
ONLINE_INPUT_PER_PAGE = 150
ONLINE_INPUT_CAP = 8000

# Mock data inventory adds tracking overhead per page
MOCK_INPUT_PER_PAGE = 80


def estimate_tokens(pages: int, online: bool, mock: bool, outline_first: bool) -> dict:
    """Return a breakdown of expected token usage."""
    output = pages * OUTPUT_TOKENS_PER_PAGE + pages * REFINEMENT_TOKENS_PER_PAGE + COMPANION_TOKENS

    # Outline-first reduces output by ~30% on long docs (catches structural issues
    # before generating the full draft)
    if outline_first and pages >= 30:
        output = int(output * 0.7) + 2500  # +2500 for outline pass itself

    research = min(pages * ONLINE_INPUT_PER_PAGE, ONLINE_INPUT_CAP) if online else 0
    mock_overhead = pages * MOCK_INPUT_PER_PAGE if mock else 0
    input_total = BASE_INPUT_TOKENS + research + mock_overhead + pages * 100  # state churn

    return {
        "input_tokens": input_total,
        "output_tokens": output,
        "total_tokens": input_total + output,
    }


def cost(tokens: dict, model: str, batch: bool = False) -> dict:
    if model not in PRICING_USD:
        raise ValueError(f"Unknown model: {model}. Choices: {list(PRICING_USD)}")
    price = PRICING_USD[model]
    multiplier = 0.5 if batch else 1.0
    in_usd = (tokens["input_tokens"] / 1_000_000) * price["input"] * multiplier
    out_usd = (tokens["output_tokens"] / 1_000_000) * price["output"] * multiplier
    total_usd = in_usd + out_usd
    return {
        "input_usd": round(in_usd, 4),
        "output_usd": round(out_usd, 4),
        "total_usd": round(total_usd, 4),
        "total_eur": round(total_usd * USD_TO_EUR, 4),
    }


def estimate_minutes(pages: int, batch: bool) -> tuple[int, int]:
    """Return (min, max) minutes."""
    if batch:
        return (10, 60 * 24)  # batch SLA: typically <1h, max 24h
    # sync interactive: 1.5–3 min/page
    return (max(5, int(pages * 1.5)), max(10, int(pages * 3)))


def render_human(args, tokens: dict, results: list[tuple[str, bool, dict]]) -> None:
    print(f"\nrelazione-estimate — {args.tipologia} · {args.pages} pp · {args.lingua}\n")
    print("Token usage (heuristic, ±30%):")
    print(f"  Input:  {tokens['input_tokens']:>8,} tokens")
    print(f"  Output: {tokens['output_tokens']:>8,} tokens")
    print(f"  Total:  {tokens['total_tokens']:>8,} tokens\n")

    print(f"{'Model':<14} {'Mode':<7} {'EUR':>8} {'USD':>8}  {'Time':<14}")
    print("-" * 60)
    for model, batch, c in results:
        mode = "batch" if batch else "sync"
        mn, mx = estimate_minutes(args.pages, batch)
        time_str = f"{mn}–{mx}m" if not batch else f"{mn}m–{mx//60}h"
        print(f"{model:<14} {mode:<7} {c['total_eur']:>8.3f} {c['total_usd']:>8.3f}  {time_str:<14}")

    print()
    cheapest = min(results, key=lambda r: r[2]["total_eur"])
    most_exp = max(results, key=lambda r: r[2]["total_eur"])
    delta_eur = most_exp[2]["total_eur"] - cheapest[2]["total_eur"]
    if delta_eur > 0.05:
        print(f"Risparmio max scegliendo {cheapest[0]} {('batch' if cheapest[1] else 'sync')}: "
              f"€{delta_eur:.3f}")

    if args.outline_first and args.pages >= 30:
        print("\nNota: outline-first attivo -> -30% output, ~+2.5k token outline.")
    if args.online:
        print("Nota: ricerca online attiva -> +input proporzionale alle pagine (max +8k).")
    if args.mock:
        print("Nota: mock data attivo -> +tracking overhead.\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tipologia", default="generica",
                    help="tesi, tecnica, status-report, etc. (cosmetico)")
    ap.add_argument("--pages", type=int, required=True, help="numero di pagine A4 attese")
    ap.add_argument("--lingua", default="italiano", help="italiano, inglese, etc. (cosmetico)")
    ap.add_argument("--model", default="all", choices=["haiku-4.5", "sonnet-4.6", "opus-4.7", "all"],
                    help="default 'all' mostra tutti i modelli")
    ap.add_argument("--mode", default="all", choices=["sync", "batch", "all"])
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

    models = list(PRICING_USD.keys()) if args.model == "all" else [args.model]
    modes = [False, True] if args.mode == "all" else [args.mode == "batch"]

    results = [(m, b, cost(tokens, m, b)) for m in models for b in modes]

    if args.json:
        out = {
            "input": vars(args),
            "tokens": tokens,
            "estimates": [
                {"model": m, "batch": b, **c, "minutes": estimate_minutes(args.pages, b)}
                for m, b, c in results
            ],
        }
        json.dump(out, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        render_human(args, tokens, results)

    return 0


if __name__ == "__main__":
    sys.exit(main())

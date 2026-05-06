#!/usr/bin/env python3
"""grammar-check.py — grammar check via LanguageTool (public API o self-hosted).

Public API: https://api.languagetool.org (rate limit 20 req/min, 20k char/req)
Self-hosted: http://localhost:8010/v2/check (scarica LanguageTool jar)

Categorie errori rilevate:
- Grammar (accordo, tempo verbale)
- Style (ripetizioni, frasi troppo lunghe)
- Punctuation
- Typography (virgolette, apostrofi, trattini)

Usage:
    grammar-check.py <file> [--lang it|en|es|fr|de|pt]
                     [--api-url http://localhost:8010]
                     [--disable-rules STYLE,TYPOGRAPHY]
                     [--max-issues 50]
"""
import argparse
import json
import pathlib
import re
import sys
import urllib.parse
import urllib.request


def clean_text(text):
    """Rimuove elementi non da controllare."""
    text = re.sub(r"```[\s\S]*?```", " ", text)
    text = re.sub(r"`[^`]+`", " ", text)
    text = re.sub(r"\$\$[\s\S]*?\$\$", " ", text)
    text = re.sub(r"\$[^$]+\$", " ", text)
    text = re.sub(r"\\[a-zA-Z]+\{[^}]*\}", " ", text)
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", text)
    return text


def call_api(api_url, text, lang, disabled_categories):
    url = f"{api_url.rstrip('/')}/v2/check"
    data = urllib.parse.urlencode({
        "text": text[:20000],
        "language": lang,
        "disabledCategories": ",".join(disabled_categories) if disabled_categories else "",
    }).encode()
    req = urllib.request.Request(url, data=data, method="POST", headers={
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def format_issue(issue, text):
    offset = issue.get("offset", 0)
    length = issue.get("length", 0)
    context_start = max(0, offset - 30)
    context_end = min(len(text), offset + length + 30)
    context = text[context_start:context_end].replace("\n", " ")
    snippet = text[offset:offset+length]
    replacements = issue.get("replacements", [])
    suggestions = [r.get("value", "") for r in replacements[:3]]
    return {
        "message": issue.get("message", ""),
        "rule": issue.get("rule", {}).get("id", ""),
        "category": issue.get("rule", {}).get("category", {}).get("id", ""),
        "snippet": snippet,
        "context": context,
        "suggestions": suggestions,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--lang", default="it")
    ap.add_argument("--api-url", default="https://api.languagetool.org")
    ap.add_argument("--disable-rules", default="")
    ap.add_argument("--max-issues", type=int, default=50)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    p = pathlib.Path(args.file)
    if not p.exists():
        print(f"[ERR] {p} non trovato", file=sys.stderr)
        return 2

    lang_map = {"it": "it", "en": "en-US", "es": "es", "fr": "fr", "de": "de-DE", "pt": "pt-PT"}
    lang = lang_map.get(args.lang, args.lang)

    raw = p.read_text(encoding="utf-8")
    cleaned = clean_text(raw)
    disabled = [d.strip() for d in args.disable_rules.split(",") if d.strip()]

    try:
        result = call_api(args.api_url, cleaned, lang, disabled)
    except Exception as e:
        print(f"[ERR] LanguageTool API: {e}", file=sys.stderr)
        print("  Usa --api-url http://localhost:8010 se hai LanguageTool in locale", file=sys.stderr)
        return 2

    matches = result.get("matches", [])[:args.max_issues]
    issues = [format_issue(m, cleaned) for m in matches]

    if args.json:
        print(json.dumps(issues, indent=2, ensure_ascii=False))
        return 1 if issues else 0

    if not issues:
        print(f"[OK] Grammar check superato: nessun issue in {p.name}")
        return 0

    categories = {}
    for i in issues:
        categories.setdefault(i["category"], []).append(i)

    print(f"GRAMMAR CHECK: {len(issues)} issue in {p.name}")
    print("=" * 60)
    for cat, items in categories.items():
        print(f"\n[{cat}] ({len(items)})")
        for i in items[:10]:
            print(f"  • {i['message']}")
            print(f"    Contesto: ...{i['context']}...")
            if i['suggestions']:
                print(f"    Suggerimenti: {', '.join(i['suggestions'])}")

    return 1


if __name__ == "__main__":
    sys.exit(main())

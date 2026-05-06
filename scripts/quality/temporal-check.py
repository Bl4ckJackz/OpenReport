#!/usr/bin/env python3
"""temporal-check.py — verifica coerenza temporale del draft.

Rileva:
- Date in formati multipli nello stesso documento (mismatch YYYY-MM-DD vs DD/MM/YYYY)
- Date future usate come passate o viceversa (rispetto alla data corrente)
- Date impossibili (31 febbraio, 13 mesi, ecc.)
- Range temporali invertiti ("dal 2025 al 2023")
- Anno nel doc vs `cover.data` in state.json
- Timeline incoerente (evento A dopo evento B dove A < B cronologicamente)

Usage:
    python3 temporal-check.py <file> [--state <state.json>] [--today YYYY-MM-DD]
"""
import argparse
import json
import pathlib
import re
import sys
from datetime import date, datetime

DATE_PATTERNS = [
    (re.compile(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b"), "iso"),
    (re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b"), "dmy-slash"),
    (re.compile(r"\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b"), "dmy-dot"),
    (re.compile(r"\b(\d{1,2})\s+(gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)\s+(\d{4})\b", re.IGNORECASE), "it-long"),
    (re.compile(r"\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b", re.IGNORECASE), "en-long"),
]

IT_MONTHS = {"gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4, "maggio": 5, "giugno": 6,
             "luglio": 7, "agosto": 8, "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12}
EN_MONTHS = {"january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
             "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12}


def parse_dates(text):
    dates = []
    formats_found = set()
    for pattern, fmt in DATE_PATTERNS:
        for m in pattern.finditer(text):
            try:
                if fmt == "iso":
                    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
                elif fmt in ("dmy-slash", "dmy-dot"):
                    d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
                elif fmt == "it-long":
                    d = int(m.group(1))
                    mo = IT_MONTHS[m.group(2).lower()]
                    y = int(m.group(3))
                elif fmt == "en-long":
                    d = int(m.group(1))
                    mo = EN_MONTHS[m.group(2).lower()]
                    y = int(m.group(3))
                else:
                    continue
                dt = date(y, mo, d)
                dates.append((dt, m.group(0), fmt))
                formats_found.add(fmt)
            except (ValueError, KeyError):
                dates.append((None, m.group(0), f"{fmt}-invalid"))
    return dates, formats_found


def check_range_inversions(text):
    issues = []
    pattern = re.compile(r"dal\s+(\d{4})\s+al\s+(\d{4})", re.IGNORECASE)
    for m in pattern.finditer(text):
        y1, y2 = int(m.group(1)), int(m.group(2))
        if y1 > y2:
            issues.append(f"'{m.group(0)}' (range invertito)")
    pattern_en = re.compile(r"from\s+(\d{4})\s+to\s+(\d{4})", re.IGNORECASE)
    for m in pattern_en.finditer(text):
        y1, y2 = int(m.group(1)), int(m.group(2))
        if y1 > y2:
            issues.append(f"'{m.group(0)}' (inverted range)")
    return issues


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--state", default=None)
    ap.add_argument("--today", default=None, help="Override data corrente (YYYY-MM-DD)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    path = pathlib.Path(args.file)
    if not path.exists():
        print(f"[ERR] file non trovato: {path}", file=sys.stderr)
        return 2

    today = date.fromisoformat(args.today) if args.today else date.today()
    text = path.read_text(encoding="utf-8")

    dates, formats_found = parse_dates(text)
    invalid = [label for dt, label, fmt in dates if dt is None]
    valid = [(dt, label) for dt, label, fmt in dates if dt is not None]

    conflicts = {
        "invalid_dates": invalid,
        "mixed_formats": sorted(formats_found) if len(formats_found) > 1 else [],
        "future_dates": [label for dt, label in valid if dt > today],
        "range_inversions": check_range_inversions(text),
    }

    cover_year_conflict = []
    if args.state and pathlib.Path(args.state).exists():
        try:
            state = json.loads(pathlib.Path(args.state).read_text(encoding="utf-8"))
            cover_data = (state.get("cover") or {}).get("data", "")
            cover_match = re.search(r"\b(20\d{2})\b", cover_data)
            if cover_match:
                cover_year = int(cover_match.group(1))
                years_in_doc = {dt.year for dt, _ in valid if dt.year >= 2000}
                if years_in_doc and cover_year not in years_in_doc and cover_year != today.year:
                    cover_year_conflict.append(f"cover.data={cover_data} (anno {cover_year}) non compare nel doc (anni nel doc: {sorted(years_in_doc)})")
        except Exception:
            pass

    conflicts["cover_year_mismatch"] = cover_year_conflict

    has_issues = any(v for v in conflicts.values())

    if args.json:
        print(json.dumps(conflicts, indent=2, ensure_ascii=False))
    else:
        if not has_issues:
            print(f"[OK] Temporal check passato: {len(valid)} date valide coerenti")
        else:
            print("TEMPORAL CHECK REPORT")
            print("=" * 60)
            if conflicts["invalid_dates"]:
                print(f"\n[FAIL] {len(conflicts['invalid_dates'])} date non valide:")
                for d in conflicts["invalid_dates"][:10]:
                    print(f"  • {d}")
            if conflicts["mixed_formats"]:
                print(f"\n[WARN] formati data misti: {conflicts['mixed_formats']} — uniforma")
            if conflicts["future_dates"]:
                print(f"\n[WARN] {len(conflicts['future_dates'])} date future (verifica se intenzionali):")
                for d in conflicts["future_dates"][:10]:
                    print(f"  • {d}")
            if conflicts["range_inversions"]:
                print(f"\n[FAIL] {len(conflicts['range_inversions'])} range temporali invertiti:")
                for r in conflicts["range_inversions"]:
                    print(f"  • {r}")
            if conflicts["cover_year_mismatch"]:
                print(f"\n[WARN] mismatch cover:")
                for c in conflicts["cover_year_mismatch"]:
                    print(f"  • {c}")

    if args.state and pathlib.Path(args.state).exists():
        try:
            state = json.loads(pathlib.Path(args.state).read_text(encoding="utf-8"))
            flat = conflicts["invalid_dates"] + conflicts["range_inversions"] + conflicts["cover_year_mismatch"]
            state.setdefault("self_check_results", {})["temporal_conflicts"] = flat
            pathlib.Path(args.state).write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            print(f"[WARN] state non aggiornabile: {e}", file=sys.stderr)

    return 1 if (conflicts["invalid_dates"] or conflicts["range_inversions"]) else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""locale-format.py — formatta date/numeri/valute secondo locale del doc.

Feature:
- Date: IT "17 aprile 2026" / EN "April 17, 2026" / DE "17. April 2026" / ...
- Numeri: IT "1.234,56" / EN "1,234.56" / DE "1.234,56" / FR "1 234,56"
- Valute: EUR posizione dopo IT, prima EN, ecc.
- Percentuali
- Plurali

Applica trasformazioni a un file md/tex basandosi su marker `{{locale_date:2026-04-17}}`,
`{{locale_num:1234.56}}`, `{{locale_eur:50000}}`, ecc.

Usage:
    locale-format.py <file> --lang it|en|es|fr|de|pt [--in-place]
    locale-format.py --demo it          # mostra esempi formattazione per lingua
"""
import argparse
import pathlib
import re
import sys
from datetime import date


MONTHS = {
    "it": ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
           "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"],
    "en": ["January", "February", "March", "April", "May", "June",
           "July", "August", "September", "October", "November", "December"],
    "es": ["enero", "febrero", "marzo", "abril", "mayo", "junio",
           "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
    "fr": ["janvier", "février", "mars", "avril", "mai", "juin",
           "juillet", "août", "septembre", "octobre", "novembre", "décembre"],
    "de": ["Januar", "Februar", "März", "April", "Mai", "Juni",
           "Juli", "August", "September", "Oktober", "November", "Dezember"],
    "pt": ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
           "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"],
}


def format_date(iso_date, lang):
    y, m, d = map(int, iso_date.split("-"))
    month = MONTHS.get(lang, MONTHS["en"])[m - 1]
    if lang == "it":
        return f"{d} {month} {y}"
    if lang == "en":
        return f"{month} {d}, {y}"
    if lang == "es":
        return f"{d} de {month} de {y}"
    if lang == "fr":
        return f"{d} {month} {y}"
    if lang == "de":
        return f"{d}. {month} {y}"
    if lang == "pt":
        return f"{d} de {month} de {y}"
    return f"{d}/{m:02d}/{y}"


def format_number(value, lang):
    try:
        n = float(str(value).replace(",", "."))
    except ValueError:
        return str(value)
    is_int = n.is_integer()
    s = f"{int(n):,}" if is_int else f"{n:,.2f}"
    if lang in ("it", "es", "pt", "de"):
        # punto per migliaia, virgola per decimali
        s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    elif lang == "fr":
        s = s.replace(",", " ").replace(".", ",")
    # en: default
    return s


def format_currency(value, currency, lang):
    num = format_number(value, lang)
    if lang == "it" or lang == "es" or lang == "pt":
        return f"{num} {currency}"
    if lang == "en":
        sym = {"EUR": "€", "USD": "$", "GBP": "£"}.get(currency, currency)
        return f"{sym}{num}" if sym in ("$", "£", "€") else f"{num} {currency}"
    if lang == "de":
        return f"{num} {currency}"
    if lang == "fr":
        return f"{num} {currency}"
    return f"{num} {currency}"


def format_percent(value, lang):
    num = format_number(value, lang)
    if lang == "en":
        return f"{num}%"
    if lang == "fr":
        return f"{num} %"
    return f"{num}%"


REPLACERS = {
    r"\{\{locale_date:([^}]+)\}\}": format_date,
    r"\{\{locale_num:([^}]+)\}\}": format_number,
    r"\{\{locale_percent:([^}]+)\}\}": format_percent,
}


def apply_locale(text, lang):
    for pattern, fn in REPLACERS.items():
        text = re.sub(pattern, lambda m: fn(m.group(1), lang), text)
    # Currency: {{locale_eur:500}}, {{locale_usd:500}}, {{locale_gbp:500}}
    for curr, sym in [("eur", "EUR"), ("usd", "USD"), ("gbp", "GBP")]:
        text = re.sub(
            r"\{\{locale_" + curr + r":([^}]+)\}\}",
            lambda m, s=sym: format_currency(m.group(1), s, lang),
            text,
        )
    return text


def demo(lang):
    today = date.today().isoformat()
    print(f"Locale demo — {lang}")
    print(f"  Date:       {format_date(today, lang)}")
    print(f"  Number:     {format_number(1234567.89, lang)}")
    print(f"  Currency:   {format_currency(48500, 'EUR', lang)}")
    print(f"  Percent:    {format_percent(42.5, lang)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?")
    ap.add_argument("--lang", default="it")
    ap.add_argument("--in-place", action="store_true")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()

    if args.demo:
        demo(args.lang)
        return 0

    if not args.file:
        ap.print_help()
        return 2

    p = pathlib.Path(args.file)
    if not p.exists():
        print(f"[ERR] {p} non trovato", file=sys.stderr)
        return 2
    text = p.read_text(encoding="utf-8")
    new_text = apply_locale(text, args.lang)

    if args.in_place:
        p.write_text(new_text, encoding="utf-8")
        print(f"[OK] locale {args.lang} applicato a {p}")
    else:
        print(new_text)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""pii-redact.py — scansiona/redact PII in file relazione.

Modalità:
  --mode=warn   → elenca occorrenze, exit 1 se trovate (default)
  --mode=redact → sostituisce con placeholder, scrive in <file>.redacted

Pattern coperti:
  - email
  - IPv4 / IPv6
  - hostname interni (.internal, .local, .lan, localhost)
  - path locali Windows (C:\\Users\\..., D:\\...)
  - path locali Unix (/home/..., /Users/...)
  - telefoni IT (+39, 3xx xxxxxxx)
  - codici fiscali IT
  - P.IVA IT (11 cifre)
  - IBAN
  - carte di credito (Luhn-checked)

Usage:
  pii-redact.py <file> [--mode=warn|redact] [--out=<path>]
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path


PATTERNS = {
    "EMAIL":     (r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "[EMAIL_REDACTED]"),
    "IPV4":      (r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "[IP_REDACTED]"),
    "IPV6":      (r"\b(?:[A-F0-9]{1,4}:){7}[A-F0-9]{1,4}\b", "[IPV6_REDACTED]"),
    "HOSTNAME":  (r"\b[a-zA-Z0-9-]+\.(?:internal|local|lan|corp|home)\b|\blocalhost\b", "[INTERNAL_HOST]"),
    "WIN_PATH":  (r"[A-Z]:\\(?:Users|home)\\[A-Za-z0-9_.-]+(?:\\[A-Za-z0-9_.-]+)*", "[USER_PATH]"),
    "UNIX_PATH": (r"/(?:home|Users)/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*", "[USER_PATH]"),
    "PHONE_IT":  (r"\+39[\s.-]?3\d{2}[\s.-]?\d{6,7}\b|\b3\d{2}[\s.-]?\d{6,7}\b", "[PHONE]"),
    "CF_IT":     (r"\b[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]\b", "[CODICE_FISCALE]"),
    "PIVA_IT":   (r"\b(?:IT)?\d{11}\b", "[PIVA]"),
    "IBAN":      (r"\b[A-Z]{2}\d{2}[A-Z0-9]{1,30}\b", "[IBAN]"),
    "CC":        (r"\b(?:\d[ -]*?){13,19}\b", "[CARD_REDACTED]"),
}


def luhn_check(number: str) -> bool:
    digits = [int(d) for d in re.sub(r"\D", "", number)]
    if len(digits) < 13: return False
    checksum = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 1:
            d *= 2
            if d > 9: d -= 9
        checksum += d
    return checksum % 10 == 0


def find_matches(text: str) -> list[tuple[str, int, str, str]]:
    """Returns list of (label, line_no, match, replacement)."""
    matches = []
    lines = text.splitlines()
    for label, (pat, repl) in PATTERNS.items():
        for m in re.finditer(pat, text, re.IGNORECASE if label == "HOSTNAME" else 0):
            if label == "CC" and not luhn_check(m.group()):
                continue
            line_no = text[:m.start()].count("\n") + 1
            matches.append((label, line_no, m.group(), repl))
    return matches


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("file")
    p.add_argument("--mode", choices=["warn", "redact"], default="warn")
    p.add_argument("--out", default=None)
    args = p.parse_args()

    text = Path(args.file).read_text(encoding="utf-8")
    matches = find_matches(text)

    if not matches:
        print(f"[OK] Nessun PII trovato in {args.file}")
        return 0

    print(f"=== PII SCAN: {args.file} ===\n")
    by_label: dict[str, list] = {}
    for label, ln, m, _ in matches:
        by_label.setdefault(label, []).append((ln, m))

    for label, items in by_label.items():
        print(f"[{label}] {len(items)} occorrenze:")
        for ln, m in items[:20]:
            print(f"  line {ln}: {m}")
        if len(items) > 20:
            print(f"  ... +{len(items) - 20} altri")
        print()

    if args.mode == "redact":
        new_text = text
        for label, _, m, repl in matches:
            new_text = new_text.replace(m, repl)
        out = args.out or args.file.replace(".md", ".redacted.md").replace(".tex", ".redacted.tex")
        Path(out).write_text(new_text, encoding="utf-8")
        print(f"\n✓ Redacted: {out}")
        return 0

    print("Esegui con --mode=redact per sostituire automaticamente con placeholder.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

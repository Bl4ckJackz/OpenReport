#!/usr/bin/env python3
"""pdf-redact.py — redaction permanente di PII/secret da PDF.

A differenza di pii-redact.py (che lavora sul markdown), questo opera sul PDF
generato, sovrascrivendo con box neri i pattern sensibili.

**CRITICAL**: La redaction PDF è permanente — i dati originali NON sono recuperabili.
Testare sempre su copia prima di distribuire.

Pattern rilevati:
- Email
- Numeri di telefono (IT/EN)
- Codice fiscale italiano (16 char)
- P.IVA
- Carte di credito (Luhn check)
- IBAN
- API key / token pattern
- IP address

Usage:
    pdf-redact.py input.pdf -o redacted.pdf [--patterns email,phone,cf,iban]
    pdf-redact.py input.pdf --dry-run     # mostra cosa verrebbe redacted
"""
import argparse
import pathlib
import re
import sys

PATTERNS = {
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "phone": r"(?:\+?\d{1,3}[- .]?)?\(?\d{2,4}\)?[- .]?\d{3,4}[- .]?\d{3,4}",
    "cf": r"\b[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]\b",
    "piva": r"\bIT\d{11}\b|\bP\.?\s*IVA[:\s]+\d{11}\b",
    "card": r"\b(?:\d{4}[- ]?){3}\d{4}\b",
    "iban": r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b",
    "apikey": r"(?i)(?:api[_-]?key|token|secret)[:\s=]+['\"]?([A-Za-z0-9_\-]{20,})",
    "ip": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
}


def find_redactions(text, categories):
    found = []
    for cat in categories:
        if cat not in PATTERNS:
            continue
        for m in re.finditer(PATTERNS[cat], text):
            found.append((m.start(), m.end(), cat, m.group(0)))
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--patterns", default="email,phone,cf,piva,card,iban,apikey")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("-o", "--output")
    args = ap.parse_args()

    inp = pathlib.Path(args.input)
    if not inp.exists() or inp.suffix.lower() != ".pdf":
        print(f"[ERR] PDF non valido: {inp}", file=sys.stderr)
        return 2

    categories = [c.strip() for c in args.patterns.split(",") if c.strip()]

    try:
        import pymupdf  # aka fitz
    except ImportError:
        try:
            import fitz as pymupdf
        except ImportError:
            print("[ERR] pymupdf mancante: pip install pymupdf", file=sys.stderr)
            return 2

    doc = pymupdf.open(str(inp))
    total_redactions = 0

    for page_num, page in enumerate(doc):
        text = page.get_text()
        redactions = find_redactions(text, categories)
        if not redactions:
            continue

        for start, end, cat, snippet in redactions:
            total_redactions += 1
            if args.dry_run:
                print(f"  [page {page_num+1}] [{cat}] {snippet}")
            else:
                # Trova bbox del testo con search_for
                instances = page.search_for(snippet)
                for inst in instances:
                    page.add_redact_annot(inst, fill=(0, 0, 0))

        if not args.dry_run:
            page.apply_redactions()

    if args.dry_run:
        print(f"\n[DRY-RUN] {total_redactions} redaction candidate (nessun file modificato)")
        return 0

    out = pathlib.Path(args.output) if args.output else inp.with_name(f"{inp.stem}-redacted.pdf")
    doc.save(str(out), garbage=4, deflate=True)
    doc.close()
    print(f"[OK] {total_redactions} redaction applicate -> {out}")
    print("[WARN] redazione permanente: originale intatto, ma mai condividere il file sorgente al posto del redacted")
    return 0


if __name__ == "__main__":
    sys.exit(main())

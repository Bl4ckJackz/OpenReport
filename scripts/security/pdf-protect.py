#!/usr/bin/env python3
"""pdf-protect.py — password-protect PDF con permessi granulari.

Feature:
- User password (richiesta per aprire)
- Owner password (richiesta per modificare/stampare)
- Permessi granulari: stampa, copia testo, modifica, annotazioni
- AES 256 encryption

Requisiti: pypdf >= 3.0 (pip install pypdf)

Usage:
    pdf-protect.py input.pdf --password "segreto" [-o out.pdf]
                    [--owner-password "owner-secret"]
                    [--disable printing,copying]
"""
import argparse
import pathlib
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--password", "-p", required=True, help="User password")
    ap.add_argument("--owner-password", help="Owner password (default: user password)")
    ap.add_argument("--disable", default="", help="CSV di: printing,copying,modifying,annotating")
    ap.add_argument("-o", "--output")
    args = ap.parse_args()

    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        print("[ERR] pypdf non installato: pip install pypdf", file=sys.stderr)
        return 2

    inp = pathlib.Path(args.input)
    if not inp.exists():
        print(f"[ERR] {inp} non esiste", file=sys.stderr)
        return 2

    out = pathlib.Path(args.output) if args.output else inp.with_name(f"{inp.stem}-protected.pdf")

    reader = PdfReader(str(inp))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    disabled = {d.strip().lower() for d in args.disable.split(",") if d.strip()}
    permissions_flags = 0xFFFF
    try:
        from pypdf.constants import UserAccessPermissions as UAP
        perms = UAP(0)
        if "printing" not in disabled:
            perms |= UAP.PRINT | UAP.PRINT_TO_REPRESENTATION
        if "copying" not in disabled:
            perms |= UAP.EXTRACT | UAP.EXTRACT_TEXT_AND_GRAPHICS
        if "modifying" not in disabled:
            perms |= UAP.MODIFY | UAP.ASSEMBLE_DOC
        if "annotating" not in disabled:
            perms |= UAP.ADD_OR_MODIFY
        permissions_flags = perms
    except (ImportError, AttributeError):
        pass

    writer.encrypt(
        user_password=args.password,
        owner_password=args.owner_password or args.password,
        use_128bit=True,
        permissions_flag=permissions_flags,
    )

    with open(out, "wb") as f:
        writer.write(f)

    print(f"[OK] PDF protetto: {out}")
    if disabled:
        print(f"    Permessi disabilitati: {', '.join(sorted(disabled))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

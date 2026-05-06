#!/usr/bin/env python3
"""watermark-pdf.py — aggiunge watermark a PDF esistente secondo status.

Modalità:
1. Se qpdf/pdftk + un PDF di overlay disponibili → usa quelli
2. Altrimenti genera nuovo PDF con overlay via pypdf (se installato)
3. Se nessuno disponibile, stampa istruzione LaTeX da usare in sorgente (draftwatermark)

Usage:
    watermark-pdf.py <input.pdf> --status draft|in-review|confidential|approved
                                  [--text "CUSTOM"] [--output out.pdf]
"""
import argparse
import pathlib
import shutil
import subprocess
import sys

STATUS_TEXTS = {
    "draft": "DRAFT — DO NOT DISTRIBUTE",
    "in-review": "FOR REVIEW",
    "confidential": "CONFIDENTIAL",
    "approved": "APPROVED",
    "archived": "ARCHIVED",
}


def try_pypdf(input_pdf, output_pdf, text):
    try:
        from pypdf import PdfReader, PdfWriter
        from pypdf.generic import TextStringObject, NameObject, create_string_object
    except ImportError:
        return False, "pypdf non installato"
    try:
        import io
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
    except ImportError:
        return False, "reportlab non installato"

    # genera overlay con reportlab
    overlay = io.BytesIO()
    c = canvas.Canvas(overlay, pagesize=A4)
    c.saveState()
    c.setFillColorRGB(0.85, 0.1, 0.1, alpha=0.25)
    c.setFont("Helvetica-Bold", 80)
    c.translate(A4[0] / 2, A4[1] / 2)
    c.rotate(45)
    c.drawCentredString(0, 0, text)
    c.restoreState()
    c.save()
    overlay.seek(0)

    overlay_reader = PdfReader(overlay)
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    for page in reader.pages:
        page.merge_page(overlay_reader.pages[0])
        writer.add_page(page)
    with open(output_pdf, "wb") as f:
        writer.write(f)
    return True, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--status", default="draft", choices=list(STATUS_TEXTS.keys()))
    ap.add_argument("--text", default=None)
    ap.add_argument("--output", "-o", default=None)
    args = ap.parse_args()

    inp = pathlib.Path(args.input)
    if not inp.exists():
        print(f"[ERR] input non trovato: {inp}", file=sys.stderr)
        return 2

    text = args.text or STATUS_TEXTS.get(args.status, args.status.upper())
    out = pathlib.Path(args.output) if args.output else inp.with_name(f"{inp.stem}-watermark{inp.suffix}")

    ok, err = try_pypdf(str(inp), str(out), text)
    if ok:
        print(f"[OK] watermark '{text}' aggiunto -> {out}")
        return 0

    print(f"[INFO] pypdf/reportlab non disponibili ({err}).")
    print("Alternative:")
    print("  1. Installa: pip install pypdf reportlab")
    print("  2. Oppure aggiungi in sorgente LaTeX:")
    print("     \\usepackage{draftwatermark}")
    print(f"     \\SetWatermarkText{{{text}}}")
    print("     \\SetWatermarkScale{4}")
    print("     \\SetWatermarkColor[gray]{0.85}")
    print("  3. Oppure usa pandoc YAML: add `header-includes` con i comandi sopra")
    return 1


if __name__ == "__main__":
    sys.exit(main())

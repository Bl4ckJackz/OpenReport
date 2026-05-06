#!/usr/bin/env python3
"""user-watermark.py — watermark PDF specifico per destinatario.

Crea copia PDF con watermark discreto "For <recipient> — <date>" in footer/bg.
Tracking invisibile: se il PDF viene redistribuito, la copia originale è identificabile.

Modalità:
- `discrete` — watermark grigio chiaro in footer
- `background` — watermark diagonale 45° semi-trasparente
- `header` — banner top con nome destinatario

Usage:
    user-watermark.py input.pdf --recipient "ACME Corp" -o acme-copy.pdf
    user-watermark.py input.pdf --recipient "John Doe" --mode background
    user-watermark.py input.pdf --batch recipients.txt --output-dir copies/
"""
import argparse
import pathlib
import sys
from datetime import date


def add_watermark(input_path, output_path, recipient, mode="discrete"):
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        print("[ERR] pypdf mancante: pip install pypdf reportlab", file=sys.stderr)
        return False
    try:
        import io
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
    except ImportError:
        print("[ERR] reportlab mancante: pip install reportlab", file=sys.stderr)
        return False

    today = date.today().isoformat()
    text = f"For {recipient} — {today}"

    overlay = io.BytesIO()
    c = canvas.Canvas(overlay, pagesize=A4)
    if mode == "discrete":
        c.setFillColorRGB(0.6, 0.6, 0.6, alpha=0.8)
        c.setFont("Helvetica", 7)
        c.drawString(2*28, 0.8*28, text)  # footer-left in cm
    elif mode == "background":
        c.saveState()
        c.setFillColorRGB(0.85, 0.85, 0.85, alpha=0.2)
        c.setFont("Helvetica-Bold", 30)
        c.translate(A4[0] / 2, A4[1] / 2)
        c.rotate(45)
        c.drawCentredString(0, 0, text)
        c.restoreState()
    elif mode == "header":
        c.setFillColorRGB(0.3, 0.3, 0.3, alpha=0.7)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(2*28, A4[1] - 1.5*28, text)
    c.save()
    overlay.seek(0)

    overlay_reader = PdfReader(overlay)
    reader = PdfReader(str(input_path))
    writer = PdfWriter()
    for page in reader.pages:
        page.merge_page(overlay_reader.pages[0])
        writer.add_page(page)

    # Add recipient metadata (invisible)
    writer.add_metadata({"/Recipient": recipient, "/DistributionDate": today})

    with open(output_path, "wb") as f:
        writer.write(f)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--recipient")
    ap.add_argument("--batch", help="File con un destinatario per riga")
    ap.add_argument("--output-dir", help="Directory output per batch")
    ap.add_argument("--mode", choices=["discrete", "background", "header"], default="discrete")
    ap.add_argument("-o", "--output")
    args = ap.parse_args()

    inp = pathlib.Path(args.input)
    if not inp.exists():
        print(f"[ERR] {inp} non esiste", file=sys.stderr)
        return 2

    if args.batch:
        recipients = [l.strip() for l in pathlib.Path(args.batch).read_text(encoding="utf-8").split("\n") if l.strip()]
        out_dir = pathlib.Path(args.output_dir or "watermarked-copies")
        out_dir.mkdir(parents=True, exist_ok=True)
        success = 0
        for r in recipients:
            safe_name = r.replace("/", "_").replace(" ", "-")
            out_path = out_dir / f"{inp.stem}-{safe_name}{inp.suffix}"
            if add_watermark(inp, out_path, r, args.mode):
                success += 1
                print(f"[OK] {out_path.name}")
        print(f"\n[DONE] {success}/{len(recipients)} copie watermarked")
        return 0 if success == len(recipients) else 1

    if not args.recipient:
        print("[ERR] --recipient richiesto", file=sys.stderr)
        return 2

    out = pathlib.Path(args.output) if args.output else inp.with_name(f"{inp.stem}-{args.recipient.replace(' ', '-')}{inp.suffix}")
    if add_watermark(inp, out, args.recipient, args.mode):
        print(f"[OK] {out}")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())

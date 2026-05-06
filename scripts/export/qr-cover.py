#!/usr/bin/env python3
"""qr-cover.py — genera QR code PNG per la cover (link PDF, URL progetto, vCard).

Usage:
    qr-cover.py --url https://example.com/report.pdf -o qr.png
    qr-cover.py --vcard name="Mario Rossi" email=m@x.com tel=123 -o vcard.png
    qr-cover.py --text "Custom text" --size 300 -o qr.png

Requisiti: qrcode[pil] (pip install qrcode[pil])
"""
import argparse
import sys


def make_vcard(kv):
    lines = ["BEGIN:VCARD", "VERSION:3.0"]
    for k, v in kv.items():
        if k == "name":
            lines.append(f"FN:{v}")
        elif k == "email":
            lines.append(f"EMAIL:{v}")
        elif k == "tel":
            lines.append(f"TEL:{v}")
        elif k == "org":
            lines.append(f"ORG:{v}")
        elif k == "title":
            lines.append(f"TITLE:{v}")
        elif k == "url":
            lines.append(f"URL:{v}")
    lines.append("END:VCARD")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--url")
    g.add_argument("--text")
    g.add_argument("--vcard", nargs="+", help="Formato: name=X email=Y tel=Z")
    ap.add_argument("--size", type=int, default=300)
    ap.add_argument("--box-size", type=int, default=10)
    ap.add_argument("--border", type=int, default=4)
    ap.add_argument("--fg", default="black")
    ap.add_argument("--bg", default="white")
    ap.add_argument("-o", "--output", required=True)
    args = ap.parse_args()

    try:
        import qrcode
    except ImportError:
        print("[ERR] qrcode mancante: pip install qrcode[pil]", file=sys.stderr)
        return 2

    if args.url:
        data = args.url
    elif args.text:
        data = args.text
    elif args.vcard:
        kv = {}
        for item in args.vcard:
            if "=" in item:
                k, v = item.split("=", 1)
                kv[k.strip()] = v
        data = make_vcard(kv)
    else:
        return 2

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=args.box_size,
        border=args.border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color=args.fg, back_color=args.bg)
    if args.size:
        img = img.resize((args.size, args.size))
    img.save(args.output)
    print(f"[OK] QR -> {args.output} ({len(data)} char encoded)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

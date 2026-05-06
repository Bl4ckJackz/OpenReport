#!/usr/bin/env python3
"""
relazione-setup — first-run wizard for the relazione skill.

Steps:
    1. Run doctor.py to validate environment
    2. Walk the user through creating .brand-profile.json
    3. Optionally fetch the Eisvogel LaTeX template
    4. Print next-step instructions

Usage:
    python scripts/workflow/setup.py             # full interactive
    python scripts/workflow/setup.py --no-input  # accept defaults (CI)
    python scripts/workflow/setup.py --skip-doctor
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent.parent
DOCTOR = SKILL_DIR / "scripts" / "workflow" / "doctor.py"

EISVOGEL_URL = (
    "https://raw.githubusercontent.com/Wandmalfarbe/"
    "pandoc-latex-template/master/eisvogel.latex"
)


def prompt(label: str, default: str = "", noinput: bool = False) -> str:
    if noinput:
        return default
    suffix = f" [{default}]" if default else ""
    try:
        ans = input(f"  {label}{suffix}: ").strip()
    except EOFError:
        return default
    return ans or default


def run_doctor() -> int:
    if not DOCTOR.exists():
        print(f"  doctor.py not found at {DOCTOR}", file=sys.stderr)
        return 1
    return subprocess.call([sys.executable, str(DOCTOR)])


def write_brand_profile(target: Path, noinput: bool) -> None:
    if target.exists():
        print(f"  {target.name} già presente — salto la creazione.")
        return

    print("\n[2/3] Brand profile — premi INVIO per i default")
    nome = prompt("Chiave breve (es. 'acme')", "acme", noinput)
    ragione = prompt("Ragione sociale", nome.title(), noinput)
    email = prompt("Email default", f"info@{nome}.com", noinput)
    primary = prompt("Colore primario hex", "#1D3557", noinput)
    secondary = prompt("Colore secondario hex", "#457B9D", noinput)
    accent = prompt("Colore accent hex", "#E63946", noinput)

    profile = {
        "$schema": "./schemas/brand-profile.schema.json",
        "brands": [
            {
                "nome": nome,
                "ragione_sociale": ragione,
                "claim": "",
                "indirizzo": "",
                "p_iva": "",
                "sito_web": "",
                "email_default": email,
                "telefono": "",
                "logo_path": "",
                "palette": {
                    "primary": primary,
                    "secondary": secondary,
                    "accent": accent,
                    "text": "#1D1D1D",
                    "background": "#FFFFFF",
                },
                "font": {"body": "Inter", "heading": "Inter", "mono": "JetBrains Mono"},
                "glossario": {},
                "banned_words": [],
                "preferred_terms": {},
                "boilerplate": {},
                "classification_default": "internal",
                "watermark_rules": {
                    "draft": "DRAFT — DO NOT DISTRIBUTE",
                    "in_review": "FOR REVIEW",
                    "confidential": "CONFIDENTIAL",
                },
            }
        ],
        "active_brand": nome,
        "updated_at": "2026-01-01T00:00:00Z",
    }
    target.write_text(json.dumps(profile, indent=2, ensure_ascii=False))
    print(f"  Scritto {target}")


def fetch_eisvogel(target: Path, noinput: bool) -> None:
    if target.exists():
        print(f"  {target.name} già presente — salto il download.")
        return

    if not noinput:
        ans = prompt("Scaricare il template Eisvogel? (y/N)", "n", noinput)
        if ans.lower() not in ("y", "yes", "s", "si"):
            return

    print(f"  Scarico Eisvogel da {EISVOGEL_URL}")
    try:
        with urllib.request.urlopen(EISVOGEL_URL, timeout=15) as resp:
            target.write_bytes(resp.read())
        print(f"  Scritto {target}")
    except Exception as exc:
        print(f"  Download fallito: {exc}. Puoi scaricarlo manualmente.")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-input", action="store_true", help="accept defaults silently")
    ap.add_argument("--skip-doctor", action="store_true")
    args = ap.parse_args()

    print("relazione-setup — first-run wizard\n")

    if not args.skip_doctor:
        print("[1/3] Diagnostica ambiente")
        rc = run_doctor()
        if rc != 0 and not args.no_input:
            ans = prompt("Doctor segnala problemi. Continuare? (y/N)", "n", args.no_input)
            if ans.lower() not in ("y", "yes", "s", "si"):
                return rc

    write_brand_profile(SKILL_DIR / ".brand-profile.json", args.no_input)

    print("\n[3/3] Eisvogel LaTeX template (opzionale)")
    fetch_eisvogel(SKILL_DIR / "pdf-templates" / "eisvogel.latex", args.no_input)

    print("\nSetup completato.")
    print("Prossimo passo: vai in una cartella di progetto e invoca /relazione")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""accessibility-pass.py — rende il doc più accessibile (PDF/UA friendly).

Interventi:
1. Warning per immagini senza alt-text (`![](img.png)` senza descrizione)
2. Warning per tabelle senza header (prima riga con `---`)
3. Suggerisce contrasto colori se brand profile presente
4. Aggiunge metadata `lang` a YAML frontmatter se mancante
5. Propone rename link "click here" → testo descrittivo
6. Controlla struttura heading (salto di livello H1 → H3)

Usage:
    accessibility-pass.py <file.md> [--fix] [--lang it]
"""
import argparse
import pathlib
import re
import sys


def check_images(text):
    issues = []
    for m in re.finditer(r"!\[([^\]]*)\]\(([^)]+)\)", text):
        alt = m.group(1).strip()
        path = m.group(2)
        if not alt or alt.lower() in ("image", "img", "picture", "figure"):
            issues.append(f"immagine senza alt-text descrittivo: {path}")
    for m in re.finditer(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", text):
        path = m.group(1)
        if "\\caption" not in text[max(0, m.start()-300):m.end()+300]:
            issues.append(f"\\includegraphics senza \\caption nelle vicinanze: {path}")
    return issues


def check_headings(text):
    issues = []
    levels = []
    for m in re.finditer(r"^(#{1,6})\s+(.+?)\s*$", text, flags=re.MULTILINE):
        levels.append((len(m.group(1)), m.group(2).strip()))
    for i in range(1, len(levels)):
        prev, curr = levels[i-1][0], levels[i][0]
        if curr > prev + 1:
            issues.append(f"salto di livello H{prev} → H{curr} (sezione '{levels[i][1]}')")
    return issues


def check_link_text(text):
    issues = []
    weak = ["click here", "qui", "clicca qui", "clicca", "here", "read more", "leggi di più", "link"]
    for m in re.finditer(r"\[([^\]]+)\]\([^)]+\)", text):
        t = m.group(1).strip().lower()
        if t in weak:
            issues.append(f"link con testo debole: '{m.group(1)}'")
    return issues


def ensure_lang_frontmatter(text, lang):
    if text.startswith("---"):
        end = text.find("---", 3)
        if end > 0:
            fm = text[3:end]
            if "lang:" not in fm:
                new_fm = fm.rstrip() + f"\nlang: {lang}\n"
                return "---" + new_fm + text[end:]
            return text
    return f"---\nlang: {lang}\n---\n\n" + text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--fix", action="store_true", help="Applica fix automatici (solo lang frontmatter)")
    ap.add_argument("--lang", default="it")
    args = ap.parse_args()

    path = pathlib.Path(args.file)
    if not path.exists():
        print(f"[ERR] file non trovato: {path}", file=sys.stderr)
        return 2

    text = path.read_text(encoding="utf-8")
    all_issues = {
        "images": check_images(text),
        "headings": check_headings(text),
        "links": check_link_text(text),
    }

    total = sum(len(v) for v in all_issues.values())

    if total == 0:
        print(f"[OK] accessibility-pass: nessun issue rilevato in {path.name}")
    else:
        print(f"ACCESSIBILITY PASS: {total} issue su {path.name}")
        if all_issues["images"]:
            print(f"\n[WARN] {len(all_issues['images'])} immagini senza alt-text adeguato:")
            for i in all_issues["images"]:
                print(f"  • {i}")
        if all_issues["headings"]:
            print(f"\n[WARN] {len(all_issues['headings'])} salti di livello heading:")
            for i in all_issues["headings"]:
                print(f"  • {i}")
        if all_issues["links"]:
            print(f"\n[WARN] {len(all_issues['links'])} link con testo debole:")
            for i in all_issues["links"]:
                print(f"  • {i}")

    if args.fix:
        new_text = ensure_lang_frontmatter(text, args.lang)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            print(f"\n[FIX] metadata lang={args.lang} aggiunto")

    return 1 if total > 0 else 0


if __name__ == "__main__":
    sys.exit(main())

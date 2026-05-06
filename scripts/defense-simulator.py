#!/usr/bin/env python3
"""defense-simulator.py — genera Q&A simulata per discussione tesi.

Legge la tesi, estrae sezioni principali, genera 20 domande tipo commissione con
risposta suggerita basata sul contenuto della tesi.

Categorie domande:
- Motivazione della ricerca (perché hai scelto questo tema)
- Metodologia (scelte tecniche, alternative scartate)
- Risultati (interpretazione, validità, limiti)
- Stato dell'arte (rapporto con letteratura)
- Applicabilità (impatto, scenari reali)
- Difficoltà incontrate
- Future work

Usage:
    defense-simulator.py <tesi.md|tesi.tex> [--output defense-qa.md] [--num 20]
"""
import argparse
import pathlib
import re
import sys

DOMANDE_TEMPLATE = [
    ("Motivazione", "Qual è stata la motivazione principale nella scelta di questo argomento?"),
    ("Motivazione", "Perché ritiene questo tema rilevante per la disciplina?"),
    ("Stato dell'arte", "In che modo il suo lavoro si differenzia da [citare lavoro simile della letteratura]?"),
    ("Stato dell'arte", "Quali sono i principali contributi della letteratura che ha utilizzato come base?"),
    ("Metodologia", "Perché ha scelto questa metodologia e non altre alternative?"),
    ("Metodologia", "Come ha gestito la validità interna del suo approccio?"),
    ("Metodologia", "Quali assunzioni sono alla base del suo metodo?"),
    ("Risultati", "Come interpreta il risultato principale del suo lavoro?"),
    ("Risultati", "Quali sono le implicazioni pratiche di questi risultati?"),
    ("Risultati", "Come ha validato i risultati ottenuti?"),
    ("Limitazioni", "Quali sono i principali limiti del suo studio?"),
    ("Limitazioni", "Se avesse più tempo, cosa approfondirebbe?"),
    ("Difficoltà", "Qual è stata la difficoltà maggiore durante il lavoro?"),
    ("Difficoltà", "Ha dovuto cambiare approccio in corso d'opera? Perché?"),
    ("Etica/privacy", "Ha considerato aspetti etici o di privacy?"),
    ("Applicabilità", "In quale scenario reale si applicherebbe il suo lavoro?"),
    ("Applicabilità", "Come si potrebbe industrializzare il suo prototipo?"),
    ("Future work", "Quali sono i prossimi passi di ricerca che suggerirebbe?"),
    ("Future work", "Cosa manca al suo lavoro per essere pubblicato su una rivista?"),
    ("Discussione aperta", "Cosa ha imparato da questo percorso di tesi a livello personale?"),
]


HEADING_RE = re.compile(r"^(#{1,3})\s+(.+)$|^\\section\*?\{([^}]+)\}", flags=re.MULTILINE)


def extract_sections(text):
    sections = []
    for m in HEADING_RE.finditer(text):
        title = (m.group(2) or m.group(3) or "").strip()
        sections.append(title)
    return sections


def suggest_answer(domanda, sections, content_snippet):
    """Genera risposta-stub da includere come placeholder per l'utente."""
    return (f"_[Suggerimento — rispondere facendo riferimento alle sezioni: "
            f"{', '.join(sections[:3])}. "
            f"Includere esempi concreti dalla tesi, non generalizzare.]_")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tesi")
    ap.add_argument("--output", "-o", default=None)
    ap.add_argument("--num", type=int, default=20)
    args = ap.parse_args()

    path = pathlib.Path(args.tesi)
    if not path.exists():
        print(f"[ERR] tesi non trovata: {path}", file=sys.stderr)
        return 2

    text = path.read_text(encoding="utf-8")
    sections = extract_sections(text)

    selected = DOMANDE_TEMPLATE[:args.num]
    out = ["# Defense simulator — Domande possibili in sede di discussione\n"]
    out.append(f"Tesi: `{path.name}`  \n")
    out.append(f"Sezioni individuate: {len(sections)}\n")
    out.append("---\n")

    by_cat = {}
    for cat, q in selected:
        by_cat.setdefault(cat, []).append(q)

    for cat, questions in by_cat.items():
        out.append(f"\n## {cat}\n")
        for i, q in enumerate(questions, 1):
            out.append(f"**Q.** {q}\n")
            out.append(f"**Risposta suggerita:** {suggest_answer(q, sections, text)}\n")
            out.append("")

    out.append("\n---\n")
    out.append("## Note\n")
    out.append("- Rispondi sempre con esempi concreti dalla tesi, non generalizzare")
    out.append("- Ammetti limiti senza giustificarli, mostra consapevolezza")
    out.append("- Se una domanda va oltre la tua tesi, riporta il focus su cosa hai fatto tu")
    out.append("- Prepara 2-3 slide di backup per domande su figure/risultati chiave")

    result = "\n".join(out)
    if args.output:
        pathlib.Path(args.output).write_text(result, encoding="utf-8")
        print(f"[OK] {len(selected)} Q&A -> {args.output}")
    else:
        print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())

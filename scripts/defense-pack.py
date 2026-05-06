#!/usr/bin/env python3
"""defense-pack.py — genera materiale per discussione tesi.

Output (in directory `defense/`):
  - DOMANDE-PROBABILI.md  — domande probabili commissione (basate su weakness analysis)
  - RISPOSTE-DRAFT.md      — bozza risposta per ogni domanda (estratta dal contenuto tesi)
  - BIGLIETTINI.md         — pillole sintetiche da memorizzare
  - SLIDES-DISCUSSIONE.md  — 12-15 slide focus discussione (non l'intera tesi)
  - CHECKLIST-GIORNO.md    — cosa portare/indossare/quando arrivare

Usage:
  defense-pack.py <TESI.md> -o defense/
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path


def split_sections(text: str) -> list[tuple[str, str]]:
    sections, title, buf = [], "PROEMIO", []
    for line in text.splitlines():
        m = re.match(r"^#{1,3}\s+(.+)$", line)
        if m:
            sections.append((title, "\n".join(buf)))
            title, buf = m.group(1).strip(), []
        else:
            buf.append(line)
    sections.append((title, "\n".join(buf)))
    return [(t, b) for t, b in sections if b.strip()]


def find_weak_claims(text: str) -> list[str]:
    """Trova frasi che fanno claim non supportati, valore approssimato, generalizzazioni."""
    patterns = [
        r"[^.]*\b(probabilmente|forse|verosimilmente|tendenzialmente|circa|approssimativamente)\b[^.]*\.",
        r"[^.]*\b(la maggior parte|molti|alcuni|spesso)\b[^.]*\.",
        r"[^.]*\b(sembra|appare|risulta evidente)\b[^.]*\.",
        r"[^.]*\[(MOCK|DA COMPLETARE|RIFERIMENTO DA VERIFICARE)\][^.]*\.",
    ]
    weak = []
    for pat in patterns:
        weak.extend(re.findall(pat, text, re.IGNORECASE))
    return [w.strip()[:200] for w in weak[:20]]


def extract_method_keywords(text: str) -> list[str]:
    sections = split_sections(text)
    method_text = ""
    for t, b in sections:
        if any(k in t.lower() for k in ["metod", "approccio", "method"]):
            method_text += b
    if not method_text: return []
    capitalized = re.findall(r"\b[A-Z][a-zA-Z]{3,}\b", method_text)
    from collections import Counter
    return [w for w, _ in Counter(capitalized).most_common(15)]


def extract_results(text: str) -> list[str]:
    sections = split_sections(text)
    for t, b in sections:
        if any(k in t.lower() for k in ["risultati", "results", "outcome"]):
            bullets = re.findall(r"^[\-\*]\s+(.+)$", b, re.MULTILINE)
            if bullets: return bullets[:10]
            sents = re.split(r"(?<=[.!?])\s+", b)
            return [s.strip() for s in sents if len(s) > 30][:10]
    return []


def make_questions(weak: list[str], method_kws: list[str], results: list[str]) -> list[tuple[str, str]]:
    """Returns (question, hint-for-answer)."""
    qs = []
    qs.append(("Perché ha scelto questo argomento di tesi?",
               "Risposta personale: motivazione, interesse, opportunità di stage/ricerca"))
    qs.append(("Qual è il contributo originale della sua tesi?",
               "Distingui chiaramente: cosa esisteva prima, cosa hai aggiunto tu, perché è nuovo"))
    qs.append(("Quale alternativa metodologica ha valutato e perché l'ha scartata?",
               "Cita 1-2 alternative + motivo specifico (performance, costo, complessità)"))
    if method_kws:
        qs.append((f"Può approfondire il funzionamento di {method_kws[0]}?",
                   f"Definizione formale di {method_kws[0]}, complessità, perché adatto al tuo caso"))
        if len(method_kws) > 1:
            qs.append((f"Come ha gestito i limiti di {method_kws[1]}?",
                       "Limiti noti + workaround che hai applicato"))
    if results:
        qs.append(("I risultati sono statisticamente significativi?",
                   "Test usato (t-test, ANOVA, χ²), p-value, dimensione campione"))
        qs.append(("Come si confrontano i suoi risultati con la letteratura?",
                   f"Cita 2-3 lavori e dichiara: meglio/peggio/comparable + perché"))
    if weak:
        qs.append(("Su che base afferma che [...]?",
                   "Identifica i claim deboli, prepara fonte o ammetti limite onestamente"))
    qs.append(("Quali sono i limiti del suo lavoro?",
               "Almeno 3 limiti onesti — meglio dichiararli tu che farli scoprire alla commissione"))
    qs.append(("Come svilupperebbe questa ricerca in futuro?",
               "2-3 direzioni concrete con motivazione, non genericità"))
    qs.append(("Perché non ha usato [tecnica X più recente]?",
               "Difendi la scelta: tempi, scope tesi, trade-off"))
    qs.append(("Può spiegare la sua tesi in 30 secondi?",
               "Elevator pitch: problema → approccio → risultato chiave"))
    qs.append(("Quale è stata la difficoltà tecnica maggiore e come l'ha superata?",
               "Storia concreta: problema → tentativi → soluzione + lesson learned"))
    qs.append(("Come sceglie un baseline per il confronto?",
               "Criterio + motivazione, evita 'perché era il primo che ho trovato'"))
    qs.append(("Cosa aggiungerebbe se avesse altri 6 mesi?",
               "1-2 estensioni concrete con motivazione di valore"))
    return qs


def make_pillole(text: str, results: list[str], method_kws: list[str]) -> list[str]:
    pillole = []
    if results:
        pillole.append(f"**Risultato principale:** {results[0][:150]}")
    if method_kws:
        pillole.append(f"**Tecniche chiave:** {', '.join(method_kws[:5])}")
    sections = split_sections(text)
    for t, b in sections:
        if "dataset" in t.lower() or "data" in t.lower():
            sents = re.split(r"(?<=[.!?])\s+", b)
            if sents:
                pillole.append(f"**Dataset:** {sents[0][:150]}")
            break
    pillole.append("**Domanda di ricerca (in 1 frase):** [DA COMPLETARE]")
    pillole.append("**Bibliografia citata più volte:** [estrai dalla tesi]")
    return pillole


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("tesi")
    p.add_argument("-o", "--out", default="defense")
    args = p.parse_args()

    text = Path(args.tesi).read_text(encoding="utf-8")
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    weak = find_weak_claims(text)
    method_kws = extract_method_keywords(text)
    results = extract_results(text)
    qs = make_questions(weak, method_kws, results)
    pillole = make_pillole(text, results, method_kws)

    # DOMANDE
    out = ["# Domande probabili della commissione", "",
           f"*Generate analizzando weak claims ({len(weak)}), parole chiave metodo ({len(method_kws)}), risultati ({len(results)}).*", ""]
    for i, (q, hint) in enumerate(qs, 1):
        out += [f"### {i}. {q}", "", f"*Suggerimento risposta:* {hint}", ""]
    (out_dir / "DOMANDE-PROBABILI.md").write_text("\n".join(out), encoding="utf-8")

    # BIGLIETTINI
    bp = ["# Bigliettini per la discussione (memorizza)", ""] + pillole
    (out_dir / "BIGLIETTINI.md").write_text("\n".join(bp), encoding="utf-8")

    # CHECKLIST
    chk = """# Checklist giorno discussione

## Da preparare la sera prima
- [ ] Stampa copia tesi cartacea (per consultazione personale)
- [ ] Caricamento file presentazione in 2 formati (USB + cloud)
- [ ] Test PC + monitor + adattatore (HDMI/DisplayPort/USB-C)
- [ ] Bigliettini stampati (BIGLIETTINI.md)
- [ ] Vestito/scarpe pronte (formale: giacca, evita scarpe rumorose)
- [ ] Acqua + caramelle (gola)
- [ ] Sveglia + secondaria

## Il giorno
- [ ] Arriva 45 min prima dell'orario
- [ ] Test pratico setup tecnico (10 min)
- [ ] Bagno prima di entrare
- [ ] Respira: 4 sec inspira, 4 trattieni, 4 espira × 3 cicli
- [ ] Saluta commissione e relatore guardando in faccia

## Durante presentazione (15-20 min)
- [ ] Parla **lentamente** (consciously slower than feels natural)
- [ ] Guarda commissione, non slide
- [ ] Conferma chi parla quando ti rivolgono domande ("Mi sta chiedendo se...")
- [ ] Se non sai una risposta: "Non ho dati per rispondere con certezza, ma immagino..." è meglio di inventare
- [ ] Ringrazia relatore + commissione alla fine

## Cose che NON devi fare
- [ ] Leggere le slide
- [ ] Scusarti per limiti già dichiarati nella tesi
- [ ] Interrompere chi ti pone domande
- [ ] Difendere ostinatamente claim deboli — meglio ammettere e spiegare contesto
"""
    (out_dir / "CHECKLIST-GIORNO.md").write_text(chk, encoding="utf-8")

    print(f"✓ Defense pack scritto in {out_dir}/")
    print(f"  - DOMANDE-PROBABILI.md ({len(qs)} domande)")
    print(f"  - BIGLIETTINI.md ({len(pillole)} pillole)")
    print(f"  - CHECKLIST-GIORNO.md")
    print()
    print(f"Genera SLIDES-DISCUSSIONE separatamente:")
    print(f"  python3 slide-deck.py {args.tesi} --engine=beamer -o {out_dir}/SLIDES-DISCUSSIONE.tex")
    return 0


if __name__ == "__main__":
    sys.exit(main())

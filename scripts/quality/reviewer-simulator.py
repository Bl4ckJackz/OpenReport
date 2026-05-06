#!/usr/bin/env python3
"""reviewer-simulator.py — simula feedback di un reviewer severo.

Legge il draft e genera critiche/domande verosimili che un docente,
cliente o commissione porrebbe. Utile per anticipare obiezioni prima di consegnare.

Modalità reviewer:
- `docente` — severità tecnica, richiede evidenze, scettico
- `cliente` — domande pratiche su costi/tempi/deliverable
- `commissione` — domande di fondo su metodologia e contributo originale
- `peer` — focus su rigore metodologico, gap nel state-of-the-art

Euristiche (no LLM):
- Passaggio con claim ma senza citation → "Fonte?"
- Numero senza unità o metodologia → "Come misurato?"
- Affermazione generica → "Esempio concreto?"
- Gap nelle sezioni standard → "Manca sezione X"
- Buzzword senza definizione → "Definisci X al primo uso"

Usage:
    reviewer-simulator.py <file> --mode docente [--count 15]
"""
import argparse
import pathlib
import re
import sys


CLAIM_PATTERNS = [
    (r"secondo\s+alcun[ei]\s+studi", "Quali studi specifici? Riferimento bibliografico?"),
    (r"è\s+ampiamente\s+riconosciuto", "Da chi riconosciuto? Fonte istituzionale?"),
    (r"la\s+maggior\s+parte\s+d[eg]lie?", "Che percentuale? Dati a supporto?"),
    (r"è\s+dimostrato\s+che", "Dimostrato da chi? In quale studio?"),
    (r"è\s+evidente\s+che", "Lo è davvero? Può esserlo per te ma non per il lettore"),
]

NUMBER_NO_UNIT = re.compile(r"\b\d{2,}%?\b(?!\s*(?:utenti|persone|anni|mesi|giorni|euro|dollari|€|\$|kg|km|gb|mb|ms|secondi|ore|€|pagine|casi))", re.IGNORECASE)

BUZZ = {
    "AI-native": "Definisci concretamente — cosa rende il sistema AI-native?",
    "cloud-first": "Quale cloud? Quale strategia first?",
    "data-driven": "Quali dati? Raccolti come? Usati in quale decisione specifica?",
    "best practice": "Secondo quale standard? NIST? ISO? OWASP?",
    "holistic": "Holistic di cosa? Elenca le dimensioni.",
    "seamless": "Termine vago — specifica il flusso senza attrito",
    "innovativo": "Rispetto a cosa? Cita il baseline di confronto",
    "scalabile": "Fino a che carico? Linear o sub-linear scaling?",
}


REVIEWER_PROFILES = {
    "docente": {
        "focus": ["citazione mancante", "metodologia", "originalità", "rigore"],
        "tone": "Tecnico e scettico",
        "extra_questions": [
            "Qual è il contributo originale rispetto a <fonte più citata>?",
            "Quali ipotesi alternative hai scartato e perché?",
            "Come hai validato i risultati? Test statistico? Peer review?",
            "Quali sono i limiti del tuo approccio? Non sono elencati abbastanza",
        ],
    },
    "cliente": {
        "focus": ["ROI", "timeline", "costi", "rischi concreti"],
        "tone": "Pragmatico, orientato al business",
        "extra_questions": [
            "Quanto costa l'implementazione? Breakdown per voce?",
            "In quanto tempo vedo i primi risultati?",
            "Cosa succede se non raggiungiamo gli obiettivi?",
            "Chi è responsabile se qualcosa va male?",
            "Qual è il case study più simile al mio settore?",
        ],
    },
    "commissione": {
        "focus": ["contributo originale", "metodologia", "stato dell'arte"],
        "tone": "Accademico formale",
        "extra_questions": [
            "Come si posiziona il suo lavoro rispetto al lavoro di <autore>?",
            "La metodologia è riproducibile? Dataset pubblico?",
            "Quali ulteriori esperimenti rafforzerebbero le conclusioni?",
            "Ha considerato la controfattuale?",
        ],
    },
    "peer": {
        "focus": ["rigore metodologico", "gap nella letteratura", "validità esterna"],
        "tone": "Collegiale, costruttivo ma esigente",
        "extra_questions": [
            "Hai fatto ablation study?",
            "Il dataset è bilanciato? Come hai gestito l'overfitting?",
            "Hai confrontato con almeno 3 baseline forti?",
            "Considera l'aggiunta di un esperimento su <dominio diverso>",
        ],
    },
}


def analyze(text, mode):
    issues = []

    for pattern, question in CLAIM_PATTERNS:
        for m in re.finditer(pattern, text, flags=re.IGNORECASE):
            sentence = text[max(0, m.start()-50):min(len(text), m.end()+50)]
            issues.append({"type": "claim_unsupported", "q": question, "context": sentence.strip()})

    for m in NUMBER_NO_UNIT.finditer(text):
        start = max(0, m.start() - 80)
        end = min(len(text), m.end() + 50)
        context = text[start:end].replace("\n", " ").strip()
        if "tabella" not in context.lower() and "figura" not in context.lower():
            issues.append({"type": "number_no_unit", "q": f"Il numero '{m.group(0)}' non ha unità esplicita o metodologia di misura",
                          "context": context})

    for buzz, question in BUZZ.items():
        if buzz.lower() in text.lower():
            issues.append({"type": "buzz", "q": question, "context": f"Uso di '{buzz}'"})

    profile = REVIEWER_PROFILES[mode]
    issues.extend([{"type": "general", "q": q, "context": "Domanda generale tipica"} for q in profile["extra_questions"]])

    return issues


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--mode", choices=list(REVIEWER_PROFILES.keys()), default="docente")
    ap.add_argument("--count", type=int, default=15)
    ap.add_argument("-o", "--output")
    args = ap.parse_args()

    p = pathlib.Path(args.file)
    if not p.exists():
        print(f"[ERR] {p} non trovato", file=sys.stderr)
        return 2

    text = p.read_text(encoding="utf-8")
    issues = analyze(text, args.mode)

    profile = REVIEWER_PROFILES[args.mode]
    out = [f"# Reviewer Simulator — mode: {args.mode}\n"]
    out.append(f"**Tono reviewer:** {profile['tone']}  ")
    out.append(f"**Focus:** {', '.join(profile['focus'])}\n")
    out.append(f"**Generato da:** `reviewer-simulator.py` su `{p.name}`\n\n---\n")

    out.append("## Osservazioni puntuali sul testo\n")
    textual = [i for i in issues if i["type"] != "general"][:args.count]
    for i, item in enumerate(textual, 1):
        out.append(f"\n### {i}. [{item['type']}]\n")
        out.append(f"**Contesto:** _{item['context'][:200]}..._\n")
        out.append(f"**Reviewer chiede:** {item['q']}\n")
        out.append("**Tua risposta attesa:** _[pronta da preparare]_")

    out.append("\n\n## Domande generali attese\n")
    for q in profile["extra_questions"]:
        out.append(f"- {q}")

    out.append("\n\n## Come prepararsi\n")
    out.append("1. Per ogni issue, verifica se hai già una risposta nel doc (magari in altra sezione)")
    out.append("2. Se no, raccogli dati/fonti/esempi PRIMA della consegna")
    out.append("3. Riformula eventuali claim deboli con evidenze")
    out.append("4. Prepara 2-3 slide/note backup per le domande più probabili")

    result = "\n".join(out)
    if args.output:
        pathlib.Path(args.output).write_text(result, encoding="utf-8")
        print(f"[OK] {args.output}")
    else:
        print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())

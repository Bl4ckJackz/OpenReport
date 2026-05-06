# Step 3.5 — Ricerca online

## Gate obbligatorio

Se `answers.ricerca_online == "solo-locale"`, **salta tutto questo step**. Scrivi in `research-notes.md`:

> Ricerca online disabilitata dall'utente. Bibliografia e stato dell'arte basati esclusivamente sui file locali. Citazioni non verificate marcate `[RIFERIMENTO DA VERIFICARE]`.

Vai a Step 3.9.

Se `online`, procedi.

## Quando cercare (esempi)

- **Stato dell'arte / related work** — paper accademici, survey, benchmark
- **Algoritmi e tecniche** — definizione formale, complessità, referenza canonica
- **Librerie / framework** — docs ufficiale, changelog, performance note
- **Standard e specifiche** — RFC, ISO, W3C, IEEE, GDPR, OWASP, PCI-DSS
- **Confronti tra alternative** valutate
- **Bibliografia** — autore, titolo, anno, venue, DOI/URL
- **Termini tecnici** poco noti — definizioni autorevoli per glossario
- **Aziende / prodotti** citati — sito ufficiale, descrizione

## Fonti preferite

- arxiv.org, IEEE, ACM, Springer, Elsevier
- Documentazione ufficiale di progetto
- Wikipedia (in inglese, per panoramica)
- Standard body sites (W3.org, ietf.org)

## Query efficaci

- Specifiche, non generiche: "transformer attention paper Vaswani 2017", non "machine learning"
- Verifica data — soprattutto tech in rapida evoluzione
- Incrocia 2+ fonti per dato critico
- Tool: `WebSearch` per discovery, `WebFetch` per leggere page specifica

## Regole assolute (sempre, anche con sì-mock)

- **MAI inventare URL, DOI, autori, titoli, anni**
- Cita solo fonti effettivamente recuperate in questa sessione
- Per ogni citazione: autore/i, titolo, anno, venue, URL/DOI
- Se non trovi fonte: `[RIFERIMENTO DA VERIFICARE]`

## Budget

Per relazioni lunghe non fare 100+ ricerche. Concentra su:
- Stato dell'arte
- Algoritmi chiave
- Sezione metodologia

Riassumi internamente prima di scrivere.

## Output

Tutto va in `<output>/.session/research-notes.md` con:
- URL
- Titolo
- Autori
- Anno
- Venue
- 3-5 righe di estratto rilevante

## Tipologie con `online` raccomandato

`tesi`, `ricerca`, `progetto`, `analisi-codice` — e qualsiasi target ≥ 15 pagine dove si cita letteratura.

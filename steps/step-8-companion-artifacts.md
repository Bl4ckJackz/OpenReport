# Step 8 — Companion artifacts (output extra dallo stesso sorgente)

Eseguito **dopo Step 7 (export)**. Opzionale. `AskUserQuestion`:

> "Vuoi anche output companion dallo stesso sorgente?"

Opzioni multi-select:
- `Executive summary 1-pagina` (sempre disponibile)
- `Slide deck` (Marp markdown o Beamer LaTeX)
- `EPUB` (lettura tablet/Kindle)
- `Bundle .zip finale` (tutto pronto da inviare)
- `Defense pack` (solo per tipologia `tesi`)

## Executive summary

Script: `scripts/executive-summary.py <RELAZIONE.md> -o SUMMARY.md`

Estrae automaticamente:
- Titolo + autore + data dal frontespizio
- Abstract (se presente) o primo paragrafo dell'introduzione
- 3-5 risultati chiave (cerca sezione "Risultati", "Conclusioni", "Outcomes")
- 1 grafico/tabella più rilevante (link al sorgente)
- 3 bullet "next steps" (cerca "Sviluppi futuri", "Future work")

Output max 1 pagina A4 in markdown e PDF.

Uso: email di submission, allegato candidatura, post LinkedIn riassuntivo.

## Slide deck

Script: `scripts/slide-deck.py <RELAZIONE.md> --engine={marp|beamer} -o SLIDES.md`

**Marp** (default, più semplice):
- 1 slide titolo
- 1 slide TOC
- 1-2 slide per sezione principale (titolo + 3-5 bullet)
- 1 slide grafico per ogni figura
- 1 slide conclusioni
- 1 slide Q&A

**Beamer** (per tesi):
- Template `pdf-templates/slides-beamer.tex`
- Theme accademico (Madrid, Berkeley)
- Bibliografia gestita

Compila a PDF/PPTX:
```bash
marp SLIDES.md -o SLIDES.pdf
# oppure
marp SLIDES.md -o SLIDES.pptx
```

## EPUB

```bash
pandoc RELAZIONE.md -o RELAZIONE.epub --toc \
  --metadata title="<titolo>" --metadata author="<autore>" \
  --epub-cover-image=img/cover.png  # opzionale
```

Utile per leggere su Kindle/Boox/iPad durante revisione.

## Bundle .zip finale

Script: `scripts/bundle.sh <output_folder>`

Crea `<titolo>-<data>.zip` contenente:
- Tutti i `.md`, `.tex`, `.pdf`, `.docx`, `.epub` finali
- `references.bib`
- `img/` con tutte le immagini referenziate
- `SUMMARY.md` (se generato)
- `SLIDES.pdf` (se generato)
- `README-deliverable.md` (auto-generato): cosa contiene il bundle, ordine di lettura consigliato

**Esclude sempre:**
- `.session/` (interno, contiene state)
- `*.log`, `*.aux`, `*.toc`, `*.bbl`, `*.out` (artefatti LaTeX)
- File temporanei

Output: `<output>/relazione-{titolo-slug}-{YYYY-MM-DD}.zip`

## Defense pack (solo tesi)

Script: `scripts/defense-pack.py <TESI.md> -o defense/`

Genera:
- `defense/DOMANDE-PROBABILI.md` — analizza punti deboli (warn da self-check, sezioni con poche citazioni, claim non supportati) e formula 10-15 domande probabili della commissione
- `defense/RISPOSTE-DRAFT.md` — bozza risposta per ogni domanda, basata su contenuto della tesi
- `defense/BIGLIETTINI.md` — pillole sintetiche da memorizzare (key result, dataset, metriche, citazioni canoniche)
- `defense/SLIDES-DISCUSSIONE.md` — 10-15 slide focused sulla discussione (non l'intera tesi)
- `defense/CHECKLIST-GIORNO-DISCUSSIONE.md` — cosa portare, cosa indossare, tempistiche

## Ordine consigliato di esecuzione

1. Bundle (per congelare lo stato)
2. Executive summary (deriva facilmente)
3. Slide deck (copre il bundle)
4. EPUB (nice-to-have)
5. Defense pack (per `tesi` solo dopo bundle)

## Aggiorna session-state

Per ogni companion generato, append in `session-state.json.files_written` con tipo `companion`.

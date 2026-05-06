# Step 1 — Initial Questions (dettaglio completo)

10–11 domande in 4–5 batch. **USA SEMPRE `AskUserQuestion`**, mai testo libero.

## Batch 1 (4 domande)

1. **Tipologia** — `progetto`, `tecnica`, `tesi`, `stage` (altre 8 via "Other": laboratorio, codice, analisi-codice, bug, finale, ricerca, esperienza, custom)
2. **Lingua** — `italiano`, `inglese`
3. **Stile** — `formale accademico`, `semi-formale aziendale`, `tecnico divulgativo`, `narrativo personale`
4. **Destinatario** — `docente / commissione`, `azienda / committente`, `team interno`, `pubblico generico`

## Batch 2 (4 domande)

5. **Lunghezza** — `corta (5-15 pp)`, `media (15-40)`, `lunga (40-80)`, `molto lunga (80+)` (Other per numero esatto)
6. **Elementi visivi** (multiSelect) — `tabelle`, `schemi/diagrammi`, `grafici di dati`, `nessuno`
7. **Formato** — `md`, `latex`, `both` (suggerisci default in base a tipologia, vedi Quick Reference in `SKILL.md`)
8. **Mock data** — `no-placeholder`, `sì-mock`

## Batch 3 (1 domanda)

9. **Ricerca online** — `online (raccomandato per tesi/ricerca/progetto/analisi-codice)`, `solo-locale`

## Batch 4 (condizionale: solo se stima file > 15 o `--scan=deep`)

10. **Modalità scan** — `rapido (single-pass, default < 15 file)`, `profondo-parallelo (4 agenti + hybrid store, raccomandato per progetti grandi — vedi steps/step-2-parallel.md)`

Se < 15 file scansionabili, salta e imposta `scan_mode: "rapido"` automaticamente.

## Pre-flight code detection (prima di Batch 5)

Glob per file sorgente nella cwd:

```
**/*.{ts,tsx,js,jsx,mjs,cjs,py,go,rs,dart,java,kt,swift,rb,php,c,cpp,cc,h,hpp,scala,clj,ex,exs,vue,svelte,sql,prisma}
```

Esclusioni automatiche: `node_modules`, `.next`, `dist`, `build`, `.git`, `vendor`, `target`, `__pycache__`, `venv`, `.venv`, `coverage`.

Considera "presenza di codice" se Glob ritorna ≥ 5 file. Salva il flag `cwd_has_source_code: true|false` in memoria locale.

## Batch 5 (condizionale: solo se `cwd_has_source_code = true`)

11. **Snippet di codice nella relazione** — opzioni:
    - `no (relazione neutra, nessun code block)`
    - `sì-mirato (4-6 snippet nelle sezioni più rilevanti)`
    - `sì-estensivo (10+ snippet in tutte le sotto-sezioni rilevanti + firme TS in Appendice B)`
    - `solo-appendice (firme/snippet concentrati in Appendice B, corpo testo neutro)`

**Default per tipologia** (proponi come prima opzione "Recommended"):

| Tipologia | Default |
|---|---|
| `tecnica`, `codice`, `analisi-codice`, `bug`, `spec-tecnica`, `runbook`, `incident-postmortem` | `sì-estensivo` |
| `progetto`, `tesi`, `ricerca`, `stage`, `finale`, `whitepaper`, `case-study`, `handover` | `sì-mirato` |
| `esperienza`, `laboratorio`, `status-report` | `solo-appendice` |
| `proposta`, `rfp-response`, `sow`, `business-case`, `audit-report`, `compliance-report` | `no` |

Se `cwd_has_source_code = false`, salta Batch 5 e imposta `code_snippets: "no"` automaticamente.

## Follow-up LaTeX (se `formato ∈ {latex, both}`)

Terza chiamata aggiuntiva:

- **Classe documento**: `article`, `report`, `book`
- **Stile bibliografico**: `bibtex`, `biblatex+biber`, `nessuna`
- **Template**: `default`, `ho un template da fornire`

## Tipologia "custom"

Se "Other" su tipologia → `custom`: chiedi struttura desiderata in chat libera (NON `AskUserQuestion`).

## Mock rules

- `sì-mock`: dati realistici marcati `[MOCK]`, listati in "Nota metodologica" finale
- `no-placeholder`: `[DA COMPLETARE: <cosa>]` ovunque manca info
- **MAI mockare** (anche con sì-mock): nomi di persone reali, bibliografia, DOI/URL, dati fiscali, citazioni dirette, metriche dichiarate misurate

Dettaglio: `steps/forbidden-terms.md`.

## Online rules

- `online`: WebSearch/WebFetch attivi per stato dell'arte, algoritmi, librerie, standard, bibliografia
- `solo-locale`: ZERO chiamate web. Citazioni non recuperabili dai file → `[RIFERIMENTO DA VERIFICARE]`

Dettaglio: `steps/step-3.5-research.md`.

# Spec — Redline / Track-changes per /relazione

**Data:** 2026-05-15
**Skill:** `~/.claude/skills/relazione/`
**Versione skill al momento dello spec:** 2.3.00
**Stato:** draft per implementazione (Sub-progetto 1 di 3)

---

## 1. Contesto e problema

La skill `/relazione` produce documenti (md → docx/pdf/html/typst/epub) attraverso un workflow con stati `draft → in-review → approved`. Esistono già:

- `scripts/live-preview-draft.sh` — preview HTML auto-refresh del draft con badge per sezione (done/writing/pending). **Non mostra cosa è cambiato.**
- `scripts/diff-summary.py` + `/relazione-diff` — riassunto testuale di sezioni aggiunte/rimosse/modificate. **Solo terminale, non visuale.**
- `scripts/import-feedback.py` — parsa track-changes da docx revisionato in ingresso. **Non li produce in uscita.**

**Manca:** la possibilità di vedere le modifiche al draft (a) **visivamente nella live HTML** in tempo reale e (b) **sottolineate/barrate nei file esportati** (PDF, DOCX e altri), in stile Word.

Questo spec affronta il Sub-progetto 1 di 3 di un'iniziativa più ampia "modifiche visibili". Gli altri due (subagent di sintesi narrativa, subagent di applicazione automatica feedback) sono progetti separati che dipendono dal formato redline definito qui.

## 2. Requisiti

### Funzionali

1. Generare un file intermedio `RELAZIONE.redlined.md` in formato **CriticMarkup** (`{++ins++}` / `{--del--}` / `{~~old~>new~~}`) dato un draft corrente e una baseline.
2. Baseline selezionabile a runtime tra:
   - **ultimo backup**: file più recente in `<session>/.session/backups/` (convenzione `auto-save.sh`, formato `<timestamp>-RELAZIONE.md`).
   - **ultima versione approvata**: snapshot del draft conservato in `<session>/archive/v<version>-<YYYY-MM-DD>/RELAZIONE.md` (convenzione `/relazione-approve`, vedi `commands/relazione-approve.md` step 7). Risolto con: archivio più recente per `lexicographic sort` su nome cartella.
   - **ultima revisione importata**: path opzionale. `/relazione-import-feedback` oggi produce solo JSON con commenti/track-changes parsati, non un md applicabile. Sub-1 cerca `<session>/.session/feedback/applied-*.md` (convenzione introdotta da Sub-3 in futuro): se trovato, baseline = file più recente. Se assente, baseline `imported` non disponibile (fallback a `backup`). Non viene modificato `import-feedback.py` in questo spec.

   Default automatico: `approved` se esiste, altrimenti `backup`, altrimenti `imported`, altrimenti warning + export pulito (mai blocca).
3. Stile redline: **Word-style** — inserimenti verde sottolineato, cancellazioni rosso barrato. Coerente sui 4 formati target.
4. Formati supportati: **HTML live preview**, **PDF moderno (Typst)**, **PDF accademico (LaTeX/Eisvogel)**, **DOCX Word nativo**. EPUB/audiobook esclusi.
5. Attivazione **automatica** quando session-state ha `status === "in-review"`. Disattivazione automatica su `approved`.
6. Comando dedicato `/relazione-redline [baseline]` per attivazione on-demand fuori dal ciclo di review.
7. Flag `--redline=auto|on|off|<baseline>` su comandi di export per override esplicito.
8. Output redline **in file separati** con suffisso `-redline.*` — mai sovrascrivere il file pulito.
9. Toggle in-page nella live HTML per cambiare baseline o disattivare diff senza ricaricare manualmente.

### Non funzionali

- **Performance:** generazione redline su 50k parole < 2s; rebuild live preview < 500ms aggiuntivi.
- **Robustezza:** nessun problema di redline blocca un export. Fallback a export pulito + warning chiaro.
- **Compatibilità:** pandoc ≥ 2.x (per `markdown+critic_markup`). Check esplicito allo startup con messaggio di upgrade se mancante.
- **Audit:** ogni attivazione/disattivazione redline registrata in `audit-trail.py` con timestamp, baseline scelta, conteggio +/− parole.
- **Zero impatto** sul flusso draft normale: senza `--redline` o fuori da `in-review`, il comportamento di tutti gli export è bytes-identico al pre-feature.

### Fuori scope (esplicito)

- Sintesi narrativa LLM delle modifiche → Sub-progetto 2.
- Applicazione automatica di feedback revisore con LLM → Sub-progetto 3.
- Vector store / grafo embeddings → Sub-progetto 2.
- Track-changes su EPUB, audiobook, formati audio.
- Redline a livello carattere (solo word-level e sentence-level).
- Multi-author tracking (chi ha fatto cosa) — il pacchetto LaTeX `changes` lo supporta ma non viene esposto.

## 3. Architettura

### Flusso dati

```
[RELAZIONE.md (current)]   [.session/redline/baseline.md]
            \                      /
             \                    /
              ▼                  ▼
       ┌─────────────────────────────┐
       │  scripts/redline-generator  │  diff word-level → CriticMarkup
       └─────────────────────────────┘
                     │
                     ▼
    [.session/redline/RELAZIONE.redlined.md]
                     │
       ┌─────────────┼──────────────┬────────────┐
       ▼             ▼              ▼            ▼
   pandoc        pandoc         pandoc        pandoc
   (HTML)        (DOCX          (LaTeX        (JSON →
                  --track-       + filter      typst-filter
                  changes=all)   critic-to-    → Typst →
                                 latex)        compile)
       ▼             ▼              ▼            ▼
   *.html       *-redline.docx  *-redline.pdf  *-redline.pdf
```

### Boundary

- **`redline-generator.py`** non sa nulla di formati: input = 2 path `.md`, output = 1 path `.redlined.md`. Testabile in isolamento.
- **Filtri pandoc** (`critic-to-typst.py`, `critic-to-latex.py`) operano su AST JSON di pandoc, ognuno traduce i 3 pattern CriticMarkup nel target. Testabili con snippet AST.
- **Script di export esistenti** acquisiscono un flag `--redline` e una piccola sezione condizionale che (a) verifica esistenza `.redlined.md`, (b) lo usa al posto del `.md` pulito. Nessuna logica di diff dentro gli script di export.
- **Comandi `/relazione-review` e `/relazione-approve`** gestiscono il ciclo di vita della baseline (snapshot, archivio) e del flag `redline.enabled` nel session-state.

### Diff algorithm

- Tokenizzazione: split su whitespace + punteggiatura preservata come token separati.
- Algoritmo: `difflib.SequenceMatcher` su token, post-processato per:
  - Collassare run consecutive di insert/delete in un singolo `{++...++}` / `{--...--}`.
  - Rilevare pattern delete-poi-insert su run brevi (≤ 8 token) → emettere `{~~vecchio~>nuovo~~}` (substitution).
  - Threshold rewrite: se >70% di un blocco (paragrafo) è cambiato, emettere `{--paragrafo intero--}` + `{++paragrafo intero++}` invece di frammentare.
  - Hard cap: max 5.000 span CriticMarkup per file. Oltre → fallback automatico a `--mode sentence`.

### Stato persistito

In `session-state.json`:

```json
"redline": {
  "enabled": true,
  "baseline": "approved",
  "baseline_path": ".session/redline/baseline.md",
  "baseline_ref": "2026-05-12T10:32:00Z",
  "mode": "word"
}
```

Snapshot baseline salvati in `.session/redline/baseline.md` (corrente) e archiviati in `.session/redline/baselines/<ISO-timestamp>.md` quando il ciclo review→approve si chiude.

## 4. Componenti

### File nuovi

| Path | Ruolo | Righe stimate |
|---|---|---|
| `scripts/redline-generator.py` | CLI: `redline-generator.py <baseline.md> <current.md> -o <out.md> [--mode word\|sentence] [--threshold-rewrite 0.7] [--max-spans 5000] [--verbose]`. Output: `.redlined.md` con CriticMarkup. | ~200 |
| `scripts/critic-to-typst.py` | Filtro pandoc (stdin/stdout JSON AST). Mappa span CriticMarkup → chiamate `#ins[]`/`#del[]` Typst. | ~80 |
| `scripts/critic-to-latex.py` | Filtro pandoc. Mappa span CriticMarkup → `\added{}` / `\deleted{}` / `\replaced{}{}` del pacchetto LaTeX `changes`. | ~80 |
| `commands/relazione-redline.md` | Comando utente on-demand: `/relazione-redline [backup\|approved\|imported]`. Genera redlined.md una volta, apre live preview con diff attivo, non persiste flag. | ~40 |

### File modificati

| Path | Modifica |
|---|---|
| `scripts/live-preview-draft.sh` | Flag `--diff [baseline]`. Pre-step: invoca `redline-generator.py` quando attivo. Pandoc invocato con `--from markdown+critic_markup`. CSS esteso con stile `<ins>` (verde, `text-decoration: underline`) e `<del>` (rosso, `text-decoration: line-through`). Header sticky: toggle `Diff: OFF/backup/approved/imported` (link che ricarica con `?diff=<value>`). Counter `+N / -N parole, M paragrafi`. |
| `scripts/export-html-standalone.sh` | Flag `--redline`. Se attivo e `.redlined.md` esiste, lo usa come input pandoc. Output: `RELAZIONE-redline.html`. |
| `scripts/export-typst.sh` | Flag `--redline`. Se attivo: invoca pandoc con filter `critic-to-typst.py` per generare il `.typ`, inietta preamble con `#let ins(body) = text(fill: rgb("#2A9D8F"), underline(body))` e `#let del(body) = text(fill: rgb("#E63946"), strike(body))`. Output: `RELAZIONE-redline.pdf`. |
| `scripts/export-pdf.sh` (o equivalente Eisvogel) | Flag `--redline`. Pandoc con filter `critic-to-latex.py` + header LaTeX `\usepackage[markup=underlined,authormarkup=none]{changes}`. Fallback: se pacchetto `changes` non disponibile, usa `\sout{}` + `\uline{}` (soul). Output: `RELAZIONE-redline-tex.pdf`. |
| `scripts/export-docx.sh` (o equivalente) | Flag `--redline`. Pandoc con `--from markdown+critic_markup --track-changes=all` produce `w:ins`/`w:del` nativi Word. Output: `RELAZIONE-redline.docx`. |
| `commands/relazione-review.md` | Su transizione a `in-review`: copia `RELAZIONE.md` → `.session/redline/baseline.md` (scegliendo automaticamente la sorgente migliore: approved > backup > imported). Setta `session-state.redline.enabled = true` e `redline.baseline` di conseguenza. Log audit-trail. |
| `commands/relazione-approve.md` | Su transizione a `approved`: setta `redline.enabled = false`, archivia `baseline.md` → `.session/redline/baselines/<timestamp>.md`. Log audit-trail. |
| `commands/relazione-help.md` | Aggiungere riga per `/relazione-redline`. |
| `SKILL.md` | Sezione "Usabilità": menzionare track-changes nei formati output. Workflow review: menzionare attivazione automatica redline. |
| `CHANGELOG.md` | Voce per la versione che introduce questa feature. |

### File invariati (esplicito)

- `scripts/import-feedback.py` — continua a parsare track-changes in ingresso, comportamento identico.
- `scripts/diff-summary.py` e `/relazione-diff` — restano il tool testuale per riassunto, ortogonali al redline visuale.
- Tutti gli altri ~60 script della skill non vengono toccati.

## 5. UX e comandi

### Flusso principale (auto in-review)

1. Utente lavora normalmente in stato `draft`. Export puliti.
2. `/relazione-review` → snapshot baseline + flag attivato. Messaggio: *"Redline attivo. Modifiche da ora visibili in live preview e export. Baseline: ultima approvazione (2026-05-12)."*
3. Utente modifica `RELAZIONE.md`. Live preview (se aperta) mostra ins/del; export producono `*-redline.*`.
4. `/relazione-approve` → flag disattivato, baseline archiviata, export tornano puliti.

### Flusso on-demand

```bash
/relazione-redline                 # vs ultimo backup (default fuori da in-review)
/relazione-redline approved        # vs ultima approvata
/relazione-redline imported        # vs revisione importata da docx
```

Apre live preview con diff attivo. Non persiste flag, non altera lo status.

### Toggle in-page (live HTML)

Header sticky già esistente acquisisce:

```
┌────────────────────────────────────────────────────────────────┐
│ 12/15 sezioni done · 2 writing · 1 pending      Diff: ON ▼     │
│ 3,247 parole · ~8 pp · +340/-120 parole · 8 ¶   [vs approved]  │
└────────────────────────────────────────────────────────────────┘
```

Dropdown `Diff: ON ▼` con 4 voci (`OFF`, `vs backup`, `vs approved`, `vs imported`). Ricarica con `?diff=<value>`; server-side rigenera redlined.md.

### Flag su export

```bash
/relazione-export pdf --redline on         # forza
/relazione-export pdf --redline off        # pulito anche in-review
/relazione-export pdf --redline=approved   # baseline esplicita
# default: --redline=auto (legge da session-state)
```

## 6. Edge cases e error handling

| Caso | Comportamento |
|---|---|
| Nessuna baseline disponibile | Fallback ordine `approved` → `backup` → `imported`. Se zero: warning `[redline] nessuna baseline disponibile, redline disattivato` + export pulito. Non blocca. |
| File rinominato/spostato tra baseline e current | Baseline è sempre `.session/redline/baseline.md`. Nessuna rinominazione runtime. |
| Diff massivo | Fallback chain a soglie: se span generati in mode `word` superano 5.000 → rigenera in mode `sentence`. Se anche `sentence` produce > 5.000 span → degradazione finale: ogni paragrafo modificato marcato come singolo `{--vecchio--}{++nuovo++}` (zero granularità intra-paragrafo). Soglia di trigger della degradazione è una funzione del numero di span, non della percentuale di file cambiato. |
| Sezione interamente rimossa | Resa in coda al documento sotto heading `## Sezioni rimosse dalla baseline` con `{--blocco intero--}`. Garantisce visibilità nei formati che ignorano `\deleted`. |
| Modifica dentro fence di codice o tabella | Diff disabilitato nel blocco: marca l'intero blocco come modificato. CriticMarkup dentro code è illeggibile. |
| Live preview attiva mentre status cambia | Polling 2s rilegge `session-state.json`. Prossimo render riflette il cambio di `redline.enabled`. |
| `pandoc < 2.x` (no critic_markup) | Check startup: `pandoc --list-extensions \| grep critic_markup`. Se mancante: errore esplicito con istruzione upgrade. |
| Pacchetto LaTeX `changes` mancante | `export-pdf.sh` fallback a `\sout{}` + `\uline{}` (soul). Logga warning. |
| Baseline == current (zero diff) | Output redlined identico al source. Header: `Diff: 0 modifiche`. |
| CriticMarkup spurio nel source (es. `{++` in esempio di codice) | `redline-generator.py` escapa `\{` durante generazione redlined.md per evitare interpretazione errata di pandoc. |
| Errore durante diff (es. encoding) | Logga errore, salta redline, procede con export pulito. Mai blocca. |

**Principi error handling:**

- Mai bloccare un export per problemi di redline.
- Mai sovrascrivere il file pulito.
- Stato baseline immutabile durante un ciclo `in-review → approved`.

## 7. Testing

| Tipo | Cosa | Come |
|---|---|---|
| Unit | `redline-generator.py` produce CriticMarkup atteso su 8 fixture (small/medium/large/all-add/all-del/only-code/only-table/heading-change) | pytest, fixture in `tests/fixtures/redline/` |
| Unit | `critic-to-typst.py` e `critic-to-latex.py` traducono i 3 pattern correttamente | pytest con snippet AST pandoc |
| Integration | Pipeline 2 `.md` → 4 export → file esistono + contengono marker attesi (`<ins>`, `\added`, `#ins`, `w:ins`) | bash test che esegue export e grep dei marker |
| E2E | Sessione mock: `review` → modifica → `export` → verifica file `-redline.*` esistono | script in `tests/e2e/redline.sh` |
| Visual smoke | docx generato: apertura in Word/LibreOffice mostra ≥1 revisione | manuale, documentato in CHANGELOG |
| Regression | Export pulito senza `--redline` → output bytes-identico al pre-feature su 3 fixture di reference | hash SHA-256 di PDF/DOCX/HTML pre/post-feature |

### Performance budget

- `redline-generator.py` su 50k parole: < 2s.
- Live preview rebuild con redline attivo: < 500ms aggiuntivi sul tempo pandoc base.
- Export PDF/DOCX con redline: < 30% overhead sul tempo export pulito.

## 8. Telemetria e debug

- `redline-generator.py --verbose` stampa: N tokens baseline, N tokens current, N ins, N del, N substitutions, threshold rewrite raggiunta s/n, mode usato (word/sentence).
- Live preview espone in console del browser: baseline ref, mode, conteggio modifiche.
- `audit-trail.py` registra: `redline.enable`, `redline.disable`, `redline.baseline_change` con timestamp ISO, baseline name, +/− parole.

## 9. Dipendenze esterne

- **pandoc ≥ 2.x** (già richiesto dalla skill). Verifica `critic_markup` in `--list-extensions`.
- **Python 3** (già richiesto). `difflib` è stdlib.
- **Pacchetto LaTeX `changes`** (opzionale, fallback su `soul` che è quasi sempre presente).
- **Typst** (già richiesto da export-typst). Macro `#ins`/`#del` definite inline nel preamble, nessun pacchetto Typst esterno.
- **Niente** sentence-transformers, vector DB, LLM, embeddings. Tutto deterministico.

## 10. Migrazione e compatibilità

- Sessioni esistenti senza chiave `redline` in `session-state.json`: trattate come `redline.enabled = false`. Nessuna migrazione necessaria.
- Comandi esistenti senza `--redline`: comportamento bytes-identico (verificato dal regression test).
- Versione skill che introduce la feature: 2.4.00 (minor bump, backwards-compatible).

## 11. Sub-progetti collegati (fuori scope qui)

- **Sub-2 — Subagent "spiega i change":** LLM che produce sintesi narrativa del redline. Consumerà il `.redlined.md` definito qui. Richiede chiarimento separato su "grafo vettoriale per le notifiche" (cache embeddings? knowledge graph? event log?).
- **Sub-3 — Subagent "applica feedback":** LLM che da commenti revisore propone modifiche con track-changes. Dipende dal formato CriticMarkup definito qui. Richiede design dedicato per safety (auto-apply vs suggest, rollback, conflitti).

## 12. Domande aperte

Nessuna. Tutte le ambiguità riscontrate durante brainstorming sono state risolte:

- Baseline: selezionabile a runtime, default `approved > backup > imported`.
- Stile: Word-style ins sottolineato + del barrato.
- Formati: HTML + 2 PDF + DOCX.
- Attivazione: auto in-review + flag esplicito + comando dedicato.
- Granularità: word-level con fallback sentence-level.
- Granularità multi-author: fuori scope (no multi-author tracking).

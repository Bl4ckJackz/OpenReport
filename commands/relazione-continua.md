---
description: Riprende una sessione /relazione interrotta, caricando lo stato salvato su disco in relazioni*/.session/session-state.json
argument-hint: "[--fresh]  (opzionale: ignora eventuali sessioni salvate e forza nuovo avvio)"
---

# /relazione-continua — Resume di una sessione `/relazione`

Questo comando **riprende** una sessione precedente della skill `relazione` che era stata messa in pausa (tipicamente dopo un `/clear` invocato dal checkpoint Step 3.9).

## Cosa fare quando viene invocato

1. **Cerca tutte le cartelle con sessioni** in `cwd` (anche orphan senza state). Tre pattern da combinare:
   ```
   # Sessioni dirette
   Glob: relazioni*/.session/session-state.json
   Glob: relazioni*/

   # Sessioni dentro workspace (creati da /relazione-workspace)
   Glob: relazioni-workspaces/*/*/.session/session-state.json
   Glob: relazioni-workspaces/*/*/

   # Sessioni ricorrenti per periodo (create da /relazione-ricorrente)
   Glob: relazioni-ricorrenti/*/*/.session/session-state.json
   Glob: relazioni-ricorrenti/*/*/
   ```
   Per le sessioni dentro workspace/ricorrenti, mostra il path completo (es. `relazioni-workspaces/cliente-acme/relazione-sow/`) e include il container (`workspace=cliente-acme` o `ricorrente=acme-weekly/2026-W16`) come prefisso nell'opzione del menu.

2. **Per ogni cartella trovata**, leggi `session-state.json` se presente e classifica:
   - `"status": "in-progress"` → candidata prioritaria per resume
   - `"status": "completed"` → già chiusa (mostra comunque, può voler rivedere)
   - Nessun state → **orphan** (backup manuale, sessione interrotta senza persistence)

3. **Se trovi UNA sola sessione in sospeso** (e nessuna altra cartella):
   Mostra all'utente un riepilogo testuale estratto dal JSON:
   - Cartella (`output_folder`)
   - Tipologia (`answers.tipologia`)
   - Step corrente (`current_step`)
   - Ultima modifica (`last_updated_at`)
   - Autore cover (`cover.autore`)
   - Titolo (`cover.titolo`)

   Poi usa `AskUserQuestion` con opzioni:
   - **Riprendi da dove mi ero fermato** — carica tutto lo state e salta agli step non ancora fatti
   - **Ricomincia da capo in questa cartella** — mantiene la cartella di output ma reset dello step corrente (salva prima lo state precedente come `session-state.BACKUP-<timestamp>.json`)
   - **Abbandona questa sessione e iniziane una nuova** — archivia la cartella esistente rinominandola con timestamp (`relazioni-BACKUP-<data-ora>/`) e avvia la skill `relazione` da zero

4. **Se trovi PIÙ di una cartella `relazioni*/`** (qualsiasi combinazione di in-progress/completed/orphan):

   Presenta **UNA sola `AskUserQuestion`** con le cartelle ordinate per `last_updated_at` desc (più recenti prima). Ogni opzione in label compatta (max 1 riga):

   ```
   [IN CORSO] relazioni/              — tecnica · step-4-ready · 2026-04-15 · "Virtual Retail..."
   [IN CORSO] relazioni-2026-04-10/   — tesi · step-6-refining · 2026-04-12 · "Tesi magistrale..."
   [OK]       relazioni-2026-03-28/   — stage · completed · 2026-03-29
   [?]        relazioni-BACKUP-xxx/   — orphan (nessuno state)
   --- Azioni ---
   Avvia una nuova sessione (ignora tutte)
   Abbandona una esistente (rinomina BACKUP-<ts>)
   ```

   Icone: `[IN CORSO]` = in-progress · `[OK]` = completed · `[?]` = orphan.
   Campi mostrati (se presenti nello state): tipologia, current_step, last_updated (YYYY-MM-DD), titolo cover (tronca a 40 char).
   Se più di 4 cartelle, usa "Other" per le meno recenti.

   **Dopo la scelta:**
   - **In-progress scelta** → procedi come al punto 3 (Riprendi / Ricomincia / Abbandona)
   - **Completed scelta** → `AskUserQuestion`: Modifica in loco / Duplica in nuova cartella / Apri in lettura
   - **Orphan scelta** → `AskUserQuestion`: Ricostruisci state dai file / Rinomina in BACKUP e nuova / Ignora
   - **"Nuova sessione"** → invoca skill `relazione` da zero, le cartelle esistenti restano intatte
   - **"Abbandona una esistente"** → seconda `AskUserQuestion` per scegliere quale, rinomina con `BACKUP-<ISO>`, poi torna al menu

5. **Se NON trovi alcuna cartella `relazioni*/`**:
   Comunica: *"Nessuna sessione `/relazione` trovata nella cartella corrente."* e proponi di avviare una nuova sessione invocando la skill `relazione` dall'inizio.

## Flag `--fresh`

Se l'argomento `--fresh` è presente:
- Non cercare sessioni esistenti
- Invoca direttamente la skill `relazione` da zero
- Se esistono cartelle `relazioni*/` con state non-completed, **avvisa l'utente** che verranno ignorate (non cancellate)

## Come riprendere correttamente (step della skill da saltare vs eseguire)

La skill `relazione` è strutturata in step numerati. Il `current_step` nel JSON indica dove la sessione si era fermata. Ecco la mappa:

| `current_step` nel JSON | Cosa saltare | Riparti da |
|---|---|---|
| `step-0-resume-check` | nulla | Step 1 (domande iniziali) |
| `step-1-questions` (parziale) | domande gia' presenti in `answers` | completa domande mancanti |
| `step-2-scan-in-progress` / `step-2-scan-done` | domande iniziali | Step 2.5 persist (se non fatto) o Step 2.6 KG |
| `step-2.5-persist` | scan + persist | Step 2.6 (build knowledge graph, OBBLIGATORIO per regola 11) |
| `step-2.6-knowledge-graph` | scan + persist + KG | Step 3 (template) |
| `step-3.5-research-in-progress` | scan + KG | Step 3.5 (continua ricerca) |
| `step-3.8-skeleton-built` | scan + KG + template + research + skeleton | Step 3.9 / Step 4 |
| `step-4-ready` | scan + KG + template + ricerca + skeleton | Step 4 (riempi skeleton — NON rigenerare lo scheletro se esiste) |
| `step-4-draft-in-progress` | scan + research | Step 4 (riprendi bozza da dove si era fermato) |
| `step-4-draft-done` | scan + research + bozza | **Ciclo di raffinamento** (vedi sotto) |
| `step-5-followup` | bozza base | Step 5 (domande approfondimento), poi raffinamento |
| `step-6-refining` | bozza + follow-up | **Ciclo di raffinamento** (vedi sotto) |
| `step-6-draft-approved` | tutto fino alla bozza finale | Step 7 (export docx/pdf/compile LaTeX) |
| `step-7-conversion` | sorgenti scritti | Step 7 (export docx/pdf/compile LaTeX) |

**Aggiorna SEMPRE `last_updated_at` e `current_step`** dopo ogni transizione.

## Ciclo di raffinamento bozza (step 4-done / 5 / 6)

Quando si riprende una sessione che ha gia' una bozza scritta su disco (`step-4-draft-done`, `step-5-followup`, `step-6-refining`), il comando entra nel **ciclo di raffinamento**: l'utente puo' modificare la relazione quante volte vuole fino a quando non la approva per l'export.

### 6.1 — Carica e presenta la bozza esistente

1. **Leggi il file bozza** dalla cartella di output. Controlla quale esiste:
   ```
   Glob: <output_folder>/RELAZIONE.md
   Glob: <output_folder>/RELAZIONE.tex
   Glob: <output_folder>/*.md
   Glob: <output_folder>/*.tex
   ```
   Leggi il file con il tool Read.

2. **Mostra un riepilogo strutturato** (NON l'intero documento — solo la mappa):
   - Indice delle sezioni (titoli `#`/`##`/`###` per markdown, `\section`/`\subsection` per LaTeX)
   - Conteggio parole approssimativo e stima pagine (~400 parole/pagina)
   - Numero di `[DA COMPLETARE]` ancora presenti
   - Numero di `[MOCK]` ancora presenti
   - Numero di `[RIFERIMENTO DA VERIFICARE]` ancora presenti
   - Stato rispetto al target pagine (`answers.lunghezza_target_pagine`): "~25/40 pagine target"

3. **Segnala punti aperti**: elenca in modo compatto le sezioni con piu' placeholder/mock, cosi' l'utente sa subito dove intervenire.

### 6.2 — Menu di raffinamento (loop)

Usa `AskUserQuestion` con le seguenti opzioni (ripeti ad ogni iterazione):

**Domanda:** "Cosa vuoi fare sulla bozza?"

Opzioni (single-select):
- `Modifica una sezione` — chiedi quale sezione (per titolo o numero), poi chiedi cosa cambiare (riscrivere, espandere, accorciare, cambiare tono). Applica le modifiche con Edit sul file.
- `Espandi la relazione` — aggiungi dettaglio dove serve per avvicinarsi al target pagine. Chiedi su quali sezioni concentrarsi, oppure lascia scegliere automaticamente le piu' corte rispetto al template.
- `Sostituisci dati mock/placeholder` — mostra l'elenco dei `[MOCK]` e `[DA COMPLETARE]` presenti, chiedi all'utente i valori reali, sostituiscili nel file e aggiorna la Nota metodologica.
- `Approva e procedi all'export (Recommended)` — termina il ciclo, setta `current_step` a `step-6-draft-approved`, procedi a Step 7 (export).

**Se l'utente sceglie "Other"**, interpreta la richiesta in linguaggio libero (es. "aggiungi una sezione sulla sicurezza", "cambia tutta l'introduzione", "traduci in inglese la sezione 3") e applicala.

### 6.3 — Applica le modifiche

Per ogni modifica:
1. Leggi la sezione interessata dal file su disco (Read)
2. Applica la modifica (Edit) — mai riscrivere l'intero file se la modifica e' localizzata
3. Aggiorna `session-state.json`:
   ```json
   {
     "current_step": "step-6-refining",
     "last_updated_at": "<ISO-8601>",
     "refinement_history": [
       {"at": "<ISO-8601>", "action": "expand", "section": "Implementazione", "summary": "Aggiunto dettaglio su modulo auth"},
       {"at": "<ISO-8601>", "action": "replace-mock", "section": "Risultati", "summary": "Sostituiti 3 [MOCK] con dati reali"}
     ]
   }
   ```
4. Dopo ogni modifica, **ripresenta il riepilogo aggiornato** (conteggio parole, pagine, placeholder rimanenti) e **torna al menu** (Step 6.2)

### 6.4 — Checkpoint mid-refining

Se il contesto della conversazione sta diventando lungo (molte iterazioni di modifica), proponi un checkpoint:

> "Abbiamo fatto N modifiche in questa sessione. Vuoi continuare o preferisci fare `/clear` e riprendere dopo? Lo stato e' salvato su disco."

Opzioni:
- `Continua` — resta nel loop
- `Pausa e /clear` — salva state con `step-6-refining`, stampa istruzioni di ripresa (come Step 3.9 della skill principale)

### 6.5 — Uscita dal ciclo

Quando l'utente sceglie "Approva e procedi all'export":
1. Aggiorna `current_step` a `step-6-draft-approved`
2. Scrivi il file finale su disco (se non gia' aggiornato in-place)
3. Procedi a Step 7 della skill `relazione` (export docx/pdf/compile LaTeX)

## Comportamento atteso per il checkpoint successivo

Dopo il resume, se l'analisi e' gia' stata fatta ma la bozza non ancora generata (`step-4-ready`), **riproponi il checkpoint Step 3.9** solo se non e' stato gia' mostrato in questa sessione — in genere si procede direttamente con la ricerca online + bozza perche' il contesto e' fresco.

Se la bozza esiste gia' (`step-4-draft-done` o successivi), **salta direttamente al ciclo di raffinamento** (Step 6.1) — non rigenerare la bozza da zero a meno che l'utente non lo chieda esplicitamente.

## Invocazione della skill

Dopo aver gestito il check e caricato lo state, **invoca la skill `relazione`** (via tool Skill con `skill: "relazione"`) passando mentalmente le risposte già presenti in `answers`. La skill, trovando un JSON con status `in-progress`, dovrebbe riconoscere che sta venendo invocata in modalità resume e comportarsi di conseguenza (vedi Step 0 in `~/.claude/skills/relazione/SKILL.md`).

## Red flags (STOP)

- **Non sovrascrivere** `session-state.json` senza prima leggerlo — se il file corrotto o ha campi mancanti, chiedi all'utente prima di procedere
- **Non cancellare** cartelle `relazioni*/` — al massimo rinomina con suffisso BACKUP-timestamp
- **Non inventare** informazioni mancanti dallo state: se manca `cover.autore` o altro campo critico, richiedilo all'utente prima di proseguire
- **Non andare oltre lo step salvato** senza confermare con l'utente (potrebbe voler modificare qualche risposta precedente)
- **Non rigenerare la bozza da zero** se esiste gia' su disco — entra nel ciclo di raffinamento e modifica quella esistente. Rigenerare solo se l'utente lo chiede esplicitamente
- **Non riscrivere l'intero file** per una modifica localizzata — usa Edit sulla sezione interessata, non Write sull'intero documento
- **Non uscire dal ciclo di raffinamento** senza che l'utente abbia scelto "Approva e procedi all'export" — il loop deve essere esplicito
- **Non perdere la refinement_history** — ogni modifica va tracciata nel JSON per consentire undo e audit

## Esempio di output atteso

> Trovata 1 sessione `/relazione` in sospeso:
> 
> **Cartella:** `relazioni/`
> **Tipologia:** tecnica
> **Step corrente:** `step-4-ready` (analisi completata, pronto per ricerca online + bozza)
> **Autore:** Dominik Duda
> **Titolo:** Virtual Retail Experience Hub — Relazione Tecnica
> **Ultima modifica:** 2026-04-13 12:17:35
> **Lunghezza target:** 85 pagine
> **Formato:** md + tex + pdf
> 
> Cosa vuoi fare? [AskUserQuestion con 3 opzioni]

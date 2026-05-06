# Step 0 — Auto-resume check (dettaglio completo)

## Discovery

```
Glob: relazioni*/.session/session-state.json
Glob: relazioni*/                                  # cartelle anche senza .session/
```

Classifica i risultati:

- **In-progress** — state esiste con `"status": "in-progress"` o `"ready-for-approval"`
- **Completed** — state esiste con `"status": "completed"` o `"approved"`
- **Orphan** — cartella `relazioni*/` senza `.session/session-state.json` (es. backup manuale, sessione interrotta senza state)

## Decisione

| Situazione | Comportamento |
|---|---|
| 0 cartelle | Procedi con Step 1 (nuova sessione) |
| 1 cartella in-progress | Riepilogo + `AskUserQuestion` (Riprendi / Nuova / Abbandona) |
| ≥ 2 cartelle (qualsiasi stato) | Menu di selezione (sotto) |
| 1 cartella completed, 0 in-progress | Segnala esistenza, `AskUserQuestion` (Nuova / Apri esistente) |

## Menu di selezione (≥ 2 cartelle)

Una sola `AskUserQuestion` con cartelle ordinate per `last_updated_at` desc. Ogni opzione include:

- Icona di stato: `[IN CORSO]` / `[OK]` / `[?]` per orphan
- Nome cartella · tipologia · step corrente · ultima modifica · titolo cover (40 char max)

Esempio:

```
[IN CORSO] relazioni/              — tecnica · step-4-ready · 2026-04-15 · "Virtual Retail..."
[IN CORSO] relazioni-2026-04-10/   — tesi · step-6-refining · 2026-04-12 · "Tesi magistrale..."
[OK]       relazioni-2026-03-28/   — stage · completed · 2026-03-29 · "Relazione di stage"
[?]        relazioni-BACKUP-xxx/   — (nessuno state, orphan)
--- Azioni ---
Avvia nuova sessione (ignora esistenti)
Abbandona una sessione (rinomina BACKUP-<ts>)
```

> 4 cartelle → usa "Other" per le meno recenti.

## Dopo la selezione

1. **Sessione in-progress / ready-for-approval**: **valida** state contro `schemas/session-state.schema.json`. Se manca `skill_version`/`current_step` → state vecchio, vedi `steps/backup-and-versioning.md`. Carica `answers`, mostra menu di ripresa (sotto), poi jump a `current_step`.
2. **Sessione approved/completed**: `AskUserQuestion` (Apri in lettura / Duplica in nuova cartella / Modifica in loco — crea versione `1.x`). **Mai sovrascrivere file approved.**
3. **Orphan**: avvisa "nessuno state trovato", `AskUserQuestion` (Ricostruisci state dai file / Rinomina in BACKUP e nuova / Ignora).
4. **Nuova sessione**: procedi Step 1 (le esistenti restano intatte).
5. **Abbandona**: secondo `AskUserQuestion` per scegliere quale, rinomina con `BACKUP-<ISO>`, torna al menu.

## Menu di ripresa guidato

Subito dopo aver caricato lo state, **UNA `AskUserQuestion`** con queste opzioni (in quest'ordine):

1. **Riprendi da dove eravamo** *(default — più frequente)* — salta a `current_step` salvato
2. **Apri il file e decidiamo insieme cosa modificare** *(opzione libera)* — Read del file principale (`RELAZIONE.md` o `.tex`) + Read di `.session/scan-summary.md`, poi prompt aperto: «Ho riletto la relazione. Dimmi liberamente cosa vuoi cambiare e procediamo.» Aspetta input libero, NON una scelta strutturata
3. **Mostra dashboard sessione** — `relazione-stats` per la sessione
4. **Cambia una risposta del Step 1** — ri-apri una delle domande iniziali e ri-genera le parti dipendenti
5. **Salta a uno step specifico** *(avanzato)* — `AskUserQuestion` con elenco step (4-draft, 5-followup, 7-export, ecc.)

**Importante**: l'opzione 2 è progettata per lavoro guidato dove l'utente non sa ancora cosa cambiare. Non chiedere altre domande prima di aver fatto Read del file.

## Quick mode (entry path alternativo)

Se invocato come `/relazione-quick` o con `--profile=<nome>`:

1. Carica preset da `presets/<nome>.yaml` se presente
2. Auto-detect tipologia da nome cartella (vedi `~/.claude/commands/relazione-quick.md` per mapping)
3. Compila `answers` con default
4. Una sola `AskUserQuestion` di conferma:
   - `Conferma e procedi` → Step 2 diretto
   - `Modifica` → mostra le 9–11 domande standard
5. Resto identico al flow standard

Vedi `steps/profiles.md` per schema preset e auto-detect.

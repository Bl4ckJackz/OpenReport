# /relazione-exit

Uscita pulita dalla skill: salva lo state corrente, crea uno snapshot di backup, stampa un summary di cosa è stato fatto e il comando esatto per riprendere. È il simmetrico di `/relazione-continua`.

## Quando usarlo

- Devi chiudere il terminale o passare ad altro lavoro mentre `/relazione` è a metà
- Vuoi liberare context (`/clear`) ma assicurarti prima che lo state sia persistito
- Hai modifiche in volo (refinement, draft parziale) e vuoi cristallizzarle in un backup nominato

## Comportamento

### Sessione attiva trovata (`status` ∈ `in-progress`, `ready-for-approval`)

1. **Discovery**: `Glob: relazioni*/.session/session-state.json`. Se più di una, prendi quella con `last_updated_at` più recente con `status` non terminale. Se ambiguità reale (più sessioni concorrenti), una `AskUserQuestion` per scegliere.

2. **Forced save di `session-state.json`**:
   - Aggiorna `last_updated_at` a `now()` (ISO 8601)
   - Aggiungi/aggiorna `paused_at` a `now()` (campo informativo)
   - **Non modificare** `status` (resta `in-progress` o `ready-for-approval`)
   - **Non modificare** `current_step` (deve restare un punto di ripresa valido)
   - Validate il JSON contro `schemas/session-state.schema.json` prima del write

3. **Backup snapshot** in `<output>/.session/backups/{ISO}-pre-exit/`:
   - Copia `RELAZIONE.md` (e/o `RELAZIONE.tex`, `references.bib` se esistono)
   - Copia `session-state.json`
   - Vedi `steps/backup-and-versioning.md` § "Backup incrementale" per le convenzioni di path e retention (ultimi 10).

4. **Summary** (formato standard, modello sotto). Leggi i campi da `session-state.json` per riempire — non inventarli.

```
Sessione chiusa: relazioni-2026-05-06/
  Tipologia:     tesi · 80 pp · italiano
  Stato:         in-progress
  Step corrente: step-5-followup
  File scritti:  RELAZIONE.md (12.3 KB), references.bib (1.1 KB)
  Mock residui:  3 (vedi mock_inventory in state)
  Ultimo backup: .session/backups/2026-05-06T14-32-08-pre-exit/
  Ultima azione: refinement § 4.2 (da last_updated_at)
```

Se un campo è assente, omettere la riga (non scrivere `n/a`). Esempio: se `mock_inventory` è vuoto, salta la riga "Mock residui".

5. **Riga `→ Next:`** finale (formato standard):

```
→ Next:
   Per riprendere:        /relazione-continua    (apre menu su questa cartella)
   Per snapshot read-only: /relazione-stats
   Per ripristinare backup precedente: /relazione-rollback
```

6. **Termina il turno** — nessuna `AskUserQuestion`, nessun `Read` aggiuntivo, nessuna prosa dopo la riga `→ Next:`.

### Nessuna sessione attiva trovata

Glob restituisce 0 risultati con `status` non terminale. Stampa:

```
Nessuna sessione attiva da chiudere.

→ Next: per iniziarne una nuova lancia /relazione (oppure /relazione-quick per saltare le domande).
```

### Sessione `approved` o `completed`

La sessione più recente ha `status ∈ {approved, completed}`. Stampa:

```
La sessione <nome> è già completata (status=<status>, completed_at=<ISO>).
Versione finale archiviata in <output>/archive/v<x>/.

→ Next: per iniziare una nuova relazione lancia /relazione.
```

Non creare backup, non toccare lo state.

### Errori bloccanti

- **State JSON corrotto / non valido contro schema**: avvisa l'utente, mostra il path del file, suggerisci `/relazione-rollback` per recuperare backup precedente. Non sovrascrivere lo state corrotto.
- **Permessi di scrittura**: stampa il path che ha fallito + comando di rimedio (`chmod` o controlla disco pieno). Non terminare silenziosamente.

## Idempotenza

Eseguire `/relazione-exit` due volte di fila è sicuro: la seconda esecuzione trova `paused_at` già impostato e scrive un nuovo backup `{ISO}-pre-exit/` con timestamp diverso. La retention 10 si occupa di tagliare i vecchi.

## Non fa

- Non cambia `status` a un nuovo valore "paused" — quello richiederebbe un'estensione della state machine ad alto rischio. Semanticamente la sessione resta `in-progress` con un `paused_at` informativo.
- Non chiude Claude Code né esegue `/clear`. L'utente decide se proseguire con `/clear` o aprire altro.
- Non genera artifact né esporta. Per uno snapshot read-only usa `/relazione-stats`.
- Non rimuove file dalla cartella di output. La cartella `relazioni*/` resta intatta — `/relazione-continua` la riprende.

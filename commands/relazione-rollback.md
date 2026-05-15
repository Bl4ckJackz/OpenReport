---
description: Ripristina una versione precedente della relazione da backup automatico
allowed-tools: Bash, Read, Write, Glob, AskUserQuestion
---

# /relazione-rollback — Ripristino da backup

## Argomenti

`$ARGUMENTS` può contenere:
- vuoto — auto-detect cartella `relazioni*/` nella cwd, mostra lista backup
- `--last` — ripristina automaticamente l'ultimo backup senza chiedere
- `--folder=<path>` — specifica cartella esplicitamente

## Comportamento

1. **Trova cartella attiva** (Glob `relazioni*/.session/backups/`).

2. **Lista backup** ordinati per timestamp:

   ```
   === BACKUP DISPONIBILI ===
   Cartella: relazioni-2026-04-16/
   
   #  | Timestamp           | Step              | Size  | Note
   ---|---------------------|-------------------|-------|-------------
   1  | 2026-04-16T14:32:18 | step-4-draft      | 18 KB | (più recente)
   2  | 2026-04-16T13:45:02 | step-4-draft      | 17 KB |
   3  | 2026-04-16T11:20:15 | step-3.9-checkpoint| 0 KB  | (pre-draft)
   4  | 2026-04-15T18:30:00 | step-2-scan       | 0 KB  | (pre-research)
   ```

3. **`AskUserQuestion`** se `--last` non è passato:
   - "Quale backup vuoi ripristinare?" — opzioni dei più recenti
   - "Mostra dettagli (diff vs corrente)" → esegue `/relazione-diff` poi richiede

4. **Pre-rollback safety — MOVE (non copy):**
   Sposta i file CORRENTI in `.session/backups/_pre-rollback-{ISO}/`. Mai cancellare senza salvare.
   ```bash
   PRE="$OUTPUT/.session/backups/_pre-rollback-$(date -u +%Y%m%dT%H%M%SZ)"
   mkdir -p "$PRE"
   # Sposta TUTTI i file di lavoro, incluso lo state corrente
   mv "$OUTPUT/RELAZIONE.md"            "$PRE/" 2>/dev/null || true
   mv "$OUTPUT/RELAZIONE.tex"           "$PRE/" 2>/dev/null || true
   mv "$OUTPUT/references.bib"          "$PRE/" 2>/dev/null || true
   mv "$OUTPUT/.session/session-state.json" "$PRE/" 2>/dev/null || true
   ```

5. **Esegue rollback** — ora puoi copiare dal backup scelto (la copia di sicurezza è in `_pre-rollback-`):
   ```bash
   cp ".session/backups/<scelto>/RELAZIONE.md"        "$OUTPUT/RELAZIONE.md"
   cp ".session/backups/<scelto>/RELAZIONE.tex"       "$OUTPUT/RELAZIONE.tex" 2>/dev/null || true
   cp ".session/backups/<scelto>/references.bib"      "$OUTPUT/references.bib" 2>/dev/null || true
   cp ".session/backups/<scelto>/session-state.json"  "$OUTPUT/.session/session-state.json"
   ```

6. **Aggiorna session-state:**
   - `current_step` → quello del backup ripristinato
   - `last_updated_at` → ora
   - Aggiunge entry in `backups[]` con tag "rollback-restore"

7. **Conferma:**
   ```
   ✓ Ripristinato backup #2 (2026-04-16T13:45:02, step-4-draft)
   ✓ File correnti salvati in .session/backups/_pre-rollback-2026-04-16T16-12/
   ✓ Step impostato a: step-4-draft
   
   Per riprendere: /relazione (riprenderà da step-4-draft)
   ```

## Casi limite

- **Nessun backup disponibile**: messaggio + suggerisci di proseguire normalmente.
- **Backup corrotto** (file mancanti / size 0 sui critici): WARN, mostra cosa manca, chiedi conferma.
- **Multiple cartelle relazioni*/**: chiedi quale.
- **`--last` ma backup vuoto**: errore, esci.

## Note

Tutto sotto `.session/backups/_pre-rollback-*/` può essere ripristinato a sua volta — il sistema è ricorsivo. Per cleanup vecchi backup: `rm -rf relazioni*/.session/backups/_pre-rollback-*` (manuale, mai automatico).

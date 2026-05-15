---
description: Genera una vista redline (track-changes) del draft corrente vs una baseline, senza alterare lo status di review.
argument-hint: "[baseline: backup|approved|imported] [--no-open]"
---

# /relazione-redline — Vista redline on-demand

Genera `<session>/.session/redline/.redlined-RELAZIONE.md` e apre la live preview con i diff attivi. **Non modifica `cover.status` né `state.status`.** Non persiste il flag in session-state (a differenza di `/relazione-review` che lo attiva automaticamente).

## Argomenti

- `backup` (default): confronta vs file più recente in `.session/backups/`.
- `approved`: confronta vs `archive/<latest>/RELAZIONE.md`.
- `imported`: confronta vs `.session/feedback/applied-*.md` più recente (se assente, fallback a `backup` con warning).
- `--no-open`: non aprire il browser.

## Cosa fare

1. **Trova la sessione** (Glob `relazioni*/.session/session-state.json`, come `/relazione-continua`).
2. **Risolvi baseline** secondo l'argomento (vedi `scripts/_resolve-baseline.sh`).
3. **Avvia live-preview con `--diff`**:
   ```bash
   bash ~/.claude/skills/relazione/scripts/workflow/live-preview-draft.sh <session> \
     --diff <baseline> --port 8766
   ```
   Se `--no-open` passato dall'utente, aggiungi `--no-open`.
4. **Output**:
   > Redline view: http://localhost:8766/.preview-RELAZIONE.html
   > Baseline: `<approved 2026-04-12 | backup 2026-05-14T09-12-44>`
   > Note: questa è una vista on-demand. Non viene esportato nessun file. Per redline negli export usa `/relazione-export --redline` o passa a `/relazione-review`.

## Red flags

- Mai modificare `session-state.json` da questo comando.
- Mai sovrascrivere file pulito di export.
- Se nessuna baseline trovata: errore esplicito, non avviare la preview.

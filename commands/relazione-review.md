---
description: Cambia status della relazione a 'in-review', aggiunge banner/watermark, registra audit trail
argument-hint: "[cartella relazione] --reviewers \"Nome, Ruolo; Nome2, Ruolo2\""
---

# /relazione-review — Invia relazione in review

Cambia **`cover.status`** della sessione da `draft` a `in-review`, aggiunge watermark "FOR REVIEW", registra nell'audit trail.

> **Nota sui due status.** `cover.status` è il valore *visualizzato* sul frontespizio e nel watermark (`draft` / `in-review` / `approved`). `state.status` è il valore della state machine canonica (`in-progress → ready-for-approval → approved → completed`). Questo comando **modifica solo `cover.status`** — la lifecycle resta `in-progress` (o `ready-for-approval` se Step 8 è già stato completato). La promozione lifecycle ad `approved` avviene solo via `/relazione-approve`.

## Cosa fare

1. **Trova la sessione** (Glob `relazioni*/.session/session-state.json`)
   - Più di una → `AskUserQuestion` menu (vedi `/relazione-continua`)
2. **Leggi state e controlli preliminari**:
   - `cover.status` deve essere `draft` (altrimenti warn: "review già fatto / in approvazione")
   - `state.status` deve essere `in-progress` o `ready-for-approval` (altrimenti rifiuta: la sessione è già `approved` o `completed`)
   - `self_check_results` deve avere `[OK]` globale (altrimenti `AskUserQuestion`: "Self-check non pulito, procedere comunque?")
3. **Raccogli reviewers** da `--reviewers` o interattivamente:
   - `AskUserQuestion`: "Chi sono i reviewer? (formato: Nome Cognome, Ruolo — separati da `;`)"
   - Valida e salva in `cover.reviewers[]`
4. **Aggiorna solo `cover.*`** (display) — **NON toccare `state.status`**:
   ```json
   {
     "status": "in-review",
     "versione": "<patch+1>",
     "reviewers": [...]
   }
   ```
5. **Snapshot redline baseline** (nuovo dalla v2.6.0):
   - Risolvi baseline source in ordine:
     1. `<session>/archive/` — sottocartella più recente per nome (es. `v1.0-2026-04-12`). Usa `<session>/archive/<latest>/RELAZIONE.md` come baseline.
     2. Se nessun archive → file più recente in `<session>/.session/backups/`.
     3. Se nemmeno backup → salta lo snapshot, warn `[redline] nessuna baseline disponibile, redline disattivato`.
   - Copia la baseline in `<session>/.session/redline/baseline.md` (mkdir -p `.session/redline/`).
   - Aggiorna `session-state.json`:
     ```json
     "redline": {
       "enabled": true,
       "baseline": "approved",
       "baseline_path": ".session/redline/baseline.md",
       "baseline_ref": "<ISO-8601 della baseline source>",
       "mode": "word"
     }
     ```
     Imposta `baseline = approved` se sorgente da `archive/`, `backup` se sorgente da `.session/backups/`.
   - Log audit-trail:
     ```bash
     python3 ~/.claude/skills/relazione/scripts/workflow/audit-trail.py log \
       --state <state.json> --action redline_enabled --by <user> \
       --note "baseline=<approved|backup>, ref=<ISO>"
     ```
6. **Rigenera PDF (se esiste) con watermark**:
   ```bash
   python3 ~/.claude/skills/relazione/scripts/watermark-pdf.py \
     <output_folder>/RELAZIONE.pdf --status in-review
   ```
   Se pypdf/reportlab mancanti, mostra istruzione LaTeX header.
7. **Audit trail**:
   ```bash
   python3 ~/.claude/skills/relazione/scripts/audit-trail.py log \
     --state <state.json> --action review_requested --by <user> \
     --from-status draft --to-status in-review \
     --note "Reviewers: <elenco nomi>"
   ```
8. **(Opzionale) notifica**: se brand profile ha `integrations.slack_channel` o email reviewers, proponi `AskUserQuestion`: "Inviare notifica (Slack / email / no)?"
9. **Output**:
   > Sessione `relazioni-2026-04-17/` in review.
   > Versione: 0.2 · Status: IN REVIEW · Reviewers: M. Rossi (PM), A. Bianchi (Tech Lead)
   > PDF watermarked: relazioni-2026-04-17/RELAZIONE-watermark.pdf
   > Audit trail aggiornato (.session/audit-trail.jsonl)
   > Redline attivo, baseline: <approved YYYY-MM-DD | backup ISO-timestamp>

## Red flags

- Non passare mai a `in-review` se ci sono `[FAIL]` nel self-check senza conferma utente
- Non sovrascrivere il PDF originale: il watermarked va in file separato `-watermark.pdf`
- Aggiorna sempre versione (patch bump) al cambio status
- Non procedere senza almeno 1 reviewer
- **Mai toccare `state.status`** in questo comando — solo `/relazione-approve` può promuovere ad `approved` (regola 10 SKILL.md)
- Mai marcare `cover.status: in-review` se `state.status` è già `approved` o `completed` — è regressione

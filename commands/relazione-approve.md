---
description: Approva la relazione, timbra data di approvazione, salva versione archive, registra audit trail
argument-hint: "[cartella] --approver \"Nome, Ruolo\""
---

# /relazione-approve — Approva e archivia la relazione

Cambia `cover.status` a `approved`, rimuove il watermark DRAFT/REVIEW, aggiunge pagina di approvazione, crea snapshot immutabile in `archive/`.

## Cosa fare

1. **Trova la sessione** come `/relazione-review`
2. **Verifica preconditions** — distingui i due status:
   - **HARD (bloccante)**: `state.status == "ready-for-approval"` — la sessione DEVE essere arrivata a fine Step 8. Se è ancora `in-progress` rifiuta con: «Sessione non ancora pronta per approvazione (state.status=`<x>`). Completa il flow `/relazione` fino a Step 8.»
   - **HARD (bloccante)**: `layout_check.force_overridden != true` (regola 10 in SKILL.md). Se true, rifiuta: «Layout-check è stato forzato — approvazione bloccata per design.»
   - **HARD (bloccante)**: `self_check_results.fail_count == 0`. Se >0, rifiuta.
   - **SOFT (warn)**: `cover.status == "in-review"` (con reviewer definiti). Se `cover.status == "draft"`, `AskUserQuestion`: «Approvo direttamente da draft, saltando la fase di review formale?»
3. **Raccogli approver(s)** da `--approver` o `AskUserQuestion`:
   - Nome, ruolo, data approvazione (default oggi)
   - Più approver? Raccogli tutti
4. **Aggiorna cover + state** (entrambi):
   `cover.*` (display sul frontespizio):
   ```json
   {
     "status": "approved",
     "versione": "1.0",
     "data_approvazione": "<YYYY-MM-DD>",
     "approvers": [{"nome": "...", "ruolo": "...", "firma_placeholder": true}]
   }
   ```
   `state.status` (lifecycle):
   ```json
   { "status": "approved", "approved_at": "<ISO-8601>" }
   ```
   Se la versione era < 1.0, promuovi a 1.0. Altrimenti incrementa major (1.0 → 2.0).
   **Importante:** `cover.status` e `state.status` sono campi distinti — il primo è ciò che appare sulla cover/watermark, il secondo è lo stato della state machine canonica (`in-progress → ready-for-approval → approved → completed`). Vanno aggiornati entrambi e devono rimanere in sync dopo questa operazione.
5. **Genera pagina di approvazione** da prependere al doc finale:
   ```markdown
   ## Approvazione

   Il presente documento (Doc ID: {{doc_id}}, Versione: {{doc_version}}) è stato
   approvato in data {{today}} dai seguenti approver:

   | Nome | Ruolo | Data | Firma |
   |---|---|---|---|
   | {{approver_1_name}} | {{approver_1_role}} | __________ | __________ |

   Status: APPROVED
   ```
   Inseriscila dopo il control sheet.
6. **Rigenera PDF pulito** (senza watermark DRAFT/REVIEW):
   - `python3 ~/.claude/skills/relazione/scripts/resolve-variables.py <file> --state <state> --in-place`
   - `bash ~/.claude/skills/relazione/scripts/parallel-export.sh <file> --pdf`
   - Applica watermark APPROVED (più discreto, grigio chiaro):
     `python3 ~/.claude/skills/relazione/scripts/watermark-pdf.py <pdf> --status approved --text "APPROVED — {{today}}"`
7. **Crea snapshot archive/**:
   ```bash
   ARCHIVE_DIR="<output>/archive/v<version>-<YYYY-MM-DD>"
   mkdir -p "$ARCHIVE_DIR"
   cp <output>/RELAZIONE.{md,tex,pdf,docx} "$ARCHIVE_DIR/"
   cp <output>/references.bib "$ARCHIVE_DIR/" 2>/dev/null
   ```
8. **Audit trail**:
   ```bash
   python3 ~/.claude/skills/relazione/scripts/audit-trail.py log \
     --state <state> --action approval_granted \
     --by "<approver>" --from-status in-review --to-status approved \
     --note "Version 1.0, archived in archive/v1.0-<date>"
   ```
9. **Output**:
   > ✓ Relazione APPROVATA.
   > Versione: 1.0 · Status: APPROVED · Data: 2026-04-17
   > Approver: Mario Rossi (CTO)
   > Snapshot: relazioni/archive/v1.0-2026-04-17/
   > Audit trail integro (ultimo hash: xxx)

## Red flags

- Mai cancellare la versione draft/review — archiviala in `archive/` non sovrascriverla
- Mai approvare se `self_check_results` ha FAIL attivi
- Mai approvare se `state.status != "ready-for-approval"` — manca Step 8
- Mai approvare se `layout_check.force_overridden == true` (Step 6.7 forzato)
- `cover.status` e `state.status` immutabili dopo `approved` (solo transition `approved → completed` via Step 10)
- Ogni approvazione deve passare da audit-trail (compliance)
- Dopo l'approvazione, Step 10 (Delivered) auto-promuove `state.status: completed` — non farlo manualmente

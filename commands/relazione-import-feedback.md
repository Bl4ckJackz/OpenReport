---
description: Importa commenti/track-changes da un docx revisionato, propone fix per ciascuno
argument-hint: "<path al feedback.docx>"
---

# /relazione-import-feedback — Applica feedback docx al draft

Legge un docx contenente commenti e track-changes (tipico workflow: il cliente/docente apre il docx, commenta, ti rimanda), estrae tutti i commenti, poi guida il fix one-by-one.

## Cosa fare

1. **Verifica input**:
   - Arg deve essere path a `.docx` esistente
   - Se mancante, `AskUserQuestion`: "Incolla il path al docx di feedback"
2. **Trova sessione attiva** (Glob, menu se multiple)
3. **Estrai feedback**:
   ```bash
   python3 ~/.claude/skills/relazione/scripts/import-feedback.py \
     <feedback.docx> --output <output>/.session/feedback-imported.json
   ```
4. **Mostra riepilogo**:
   > Importati da feedback.docx:
   > - 12 commenti (3 da M. Rossi, 9 da A. Bianchi)
   > - 5 inserimenti proposti
   > - 8 cancellazioni proposte
5. **Loop di applicazione** — per ogni item (commento, insertion, deletion):
   - Mostra contesto (frase originale nel draft) + proposta feedback
   - `AskUserQuestion` con 4 opzioni:
     - **Accetta come proposto** — applica modifica via Edit
     - **Accetta con modifica** — chiedi versione rivista
     - **Rifiuta** — nessuna modifica, nota come "rifiutato" nel log
     - **Posticipa** — lascia per review manuale dopo
   - Aggiorna `session-state.refinement_history` con azione
6. **Audit trail**:
   ```bash
   python3 ~/.claude/skills/relazione/scripts/audit-trail.py log \
     --state <state> --action feedback_imported \
     --by "<reviewer>" --note "<N commenti applicati, M rifiutati>"
   ```
7. **Rerun self-check** dopo applicazione:
   ```bash
   bash ~/.claude/skills/relazione/scripts/self-check.sh <file> --state=<state>
   ```
8. **Proponi step successivo**:
   - Se tutte le modifiche applicate → `AskUserQuestion`: "Riavvia ciclo di revisione (/relazione-review) o approva (/relazione-approve)?"

## Red flags

- Non applicare cambiamenti in batch senza conferma utente (rischio override)
- Mantieni traccia di commenti "rifiutati" con motivazione — utile se reviewer chiede perché
- Se feedback contiene richiesta di contenuto non verificabile (es. "aggiungi dato X"), non inventare: flag "CHIEDI ALL'UTENTE"
- Backup pre-apply: `.session/backups/pre-feedback-<ts>/`

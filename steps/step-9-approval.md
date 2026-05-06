# Step 9 — Approval workflow (state machine STRETTA)

**Una sessione non può andare in `completed` senza il comando esplicito `/relazione-approve`.**

## State machine canonica

```
in-progress  →  ready-for-approval  →  approved  →  completed
                       │
                       └─→ rejected → in-progress (ripartenza con feedback)

abandoned (ramo terminale, manuale)
```

| Stato | Set da | Significato |
|---|---|---|
| `in-progress` | Step 0 / Step 2.5 | Sessione attiva, work in progress |
| `ready-for-approval` | Step 8 al termine | Tutto generato, in attesa di approvazione |
| `approved` | `/relazione-approve` | Utente ha confermato l'output finale |
| `completed` | Step 10 (auto, dopo `approved`) | Bundle/archive finalizzato |
| `rejected` | `/relazione-import-feedback` con esito reject | Torna a `in-progress` con feedback |
| `abandoned` | Step 0 menu o `/relazione-rollback --abandon` | Rimossa dalla rotazione |

**Regola d'oro:** Step 8 NON imposta più `status: "completed"`. Imposta `status: "ready-for-approval"`.

## Transizioni vietate (BLOCCATE da validazione schema + orchestratore)

| Da | A | Vietato? |
|---|---|---|
| `in-progress` | `completed` | SÌ — manca `ready-for-approval` |
| `in-progress` | `approved` | SÌ |
| `ready-for-approval` | `completed` | SÌ — manca `approved` |
| `approved` | `in-progress` | SÌ — usare nuova sessione |
| `completed` | qualsiasi | SÌ — sessione chiusa |

Le transizioni proibite generano errore `INVALID_STATE_TRANSITION` e abortiscono il save.

## Pre-requisiti per `ready-for-approval`

Step 8 può impostare `ready-for-approval` SOLO se:
1. Step 4.5 self-check con 0 FAIL (WARN tollerati con flag esplicito)
2. Step 6.5 PII/secret check OK (no secret residui)
3. Step 6.7 layout coherence OK (no `force_overridden: true`)
4. Step 7 export riuscito: DOCX presente, modern PDF presente, LaTeX-PDF presente se formato include latex
5. Tutti i `[MOCK]` listati in "Nota metodologica" o sostituiti
6. `cover.versione` e `cover.status: in-review`

Se manca anche solo un requisito → resta `in-progress`, mostra checklist mancante.

## Comando `/relazione-approve`

### Pre-check

Carica `session-state.json`. Se `status != "ready-for-approval"` → ABORT con messaggio:
```
Impossibile approvare: lo stato corrente è "<stato>".
Prima di approvare, completare Step 8 fino a "ready-for-approval".
```

### Domande utente (`AskUserQuestion`)

1. **Conferma approvazione** — `Approva e finalizza` / `Approva con riserva (note)` / `Rifiuta (rejected)` / `Annulla`
2. **Versione finale** — default `1.0`, modificabile (`1.0-rc`, `2.0` ecc.)
3. **Approver** — chi sta approvando (nome + ruolo, multi-row se più approvers nello state)
4. **Data approvazione** — default oggi, modificabile per backdate giustificato

### Azioni su `Approva e finalizza`

1. Update `cover.status` → `approved`
2. Update `cover.versione` → versione scelta
3. Append a `cover.approvers[]` con timestamp e firma_placeholder=false
4. Append in `.session/audit-trail.jsonl`:
   ```json
   {"at":"<ISO>","actor":"<approver>","action":"approve","version":"1.0","note":""}
   ```
5. Esegui `python3 scripts/workflow/audit-trail.py append` con la riga sopra
6. Esegui `python3 scripts/export/watermark-pdf.py` per togliere il banner DRAFT/IN-REVIEW
7. Crea `<output>/archive/v<versione>/` e copia tutti i file finali
8. Update `session-state.json`:
   ```json
   {
     "status": "approved",
     "approved_at": "<ISO>",
     "approved_by": "<approver name>",
     "final_version": "1.0",
     "current_step": "step-10-delivered"
   }
   ```
9. **Procedi automaticamente a Step 10** (delivery)

### Azioni su `Rifiuta (rejected)`

1. `AskUserQuestion`: chiedi motivo + sezioni da rivedere
2. Append audit trail con action="reject"
3. Update `status: "in-progress"`, `current_step: "step-5-followup"`
4. Crea `feedback-import.md` con il motivo, importabile da `/relazione-import-feedback`

## Step 10 — Delivered (auto dopo approve)

Eseguito automaticamente dopo `approved`:

1. Genera companion artifacts mancanti (executive summary, slide deck, bundle .zip)
2. Aggiorna `cover.versione` → versione approvata
3. Esegui integrity hash su tutti i file finali:
   ```bash
   bash scripts/security/integrity-hash.sh <output>/archive/v<versione>/
   ```
4. (Opzionale, su `AskUserQuestion`) firma GPG: `bash scripts/security/gpg-sign.sh`
5. Update `session-state.json`:
   ```json
   { "status": "completed", "completed_at": "<ISO>" }
   ```
6. Stampa riepilogo:
   ```
   [APPROVED] Relazione finalizzata
   Versione: 1.0
   Approver: <nome>
   Files: <output>/archive/v1.0/...
   Hash: <output>/archive/v1.0/SHA256SUMS
   ```

## Audit trail

`.session/audit-trail.jsonl` (append-only, immutabile dopo `approved`):

```jsonl
{"at":"2026-05-05T10:12:00Z","actor":"system","action":"draft-complete","step":"step-8"}
{"at":"2026-05-05T10:14:00Z","actor":"system","action":"export-complete","files":["RELAZIONE.docx","RELAZIONE.pdf","RELAZIONE.tex","RELAZIONE-tex.pdf"]}
{"at":"2026-05-05T10:15:00Z","actor":"system","action":"layout-check","result":"OK"}
{"at":"2026-05-05T10:16:00Z","actor":"system","action":"ready-for-approval"}
{"at":"2026-05-05T10:30:00Z","actor":"M.Rossi","action":"approve","version":"1.0","note":""}
{"at":"2026-05-05T10:30:05Z","actor":"system","action":"completed"}
```

Ogni transizione di stato genera UNA riga.

## Schema

`session-state.schema.json` aggiornato:
- `status` enum: `["in-progress", "ready-for-approval", "approved", "completed", "rejected", "abandoned"]`
- nuovi campi: `approved_at`, `approved_by`, `final_version`, `rejected_reason`

## Red flags

- Step 8 che imposta `status: "completed"` direttamente — VIETATO
- Manualmente editare `session-state.json` per saltare `ready-for-approval` — VIETATO
- Eseguire `/relazione-approve` quando `layout_check.force_overridden: true` — BLOCCATO
- Eseguire `/relazione-approve` con FAIL residui in self-check — BLOCCATO
- Modificare l'audit trail dopo `approved` — è append-only e immutabile

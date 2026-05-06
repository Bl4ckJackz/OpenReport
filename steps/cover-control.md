# Step — Document Control Sheet (cover estesa)

Dettaglio modulo cover control per documenti enterprise. Usato da:
- Tipologie business (`proposta`, `sow`, `business-case`, `spec-funzionale`, `spec-tecnica`, `incident-postmortem`, `status-report`, `whitepaper`, `handover`, `runbook`, `audit-report`, `compliance-report`, `rfp-response`, `case-study`)
- Qualsiasi tipologia con `cover.classificazione != "public"` oppure `cover.status != "draft"`

## Campi cover control

| Campo | Fonte | Obbligatorio quando | Esempio |
|---|---|---|---|
| `doc_id` | Genera `<PRJ>-<YYYY>-<NNN>` o chiedi | enterprise | `RFP-2026-042` |
| `protocollo` | Chiedi all'utente | classificazione ≥ internal | `2026/ABC/001` |
| `versione` | Default `0.1` → `1.0` a approved | sempre | `1.0`, `1.1-rc` |
| `classificazione` | Brand default o chiedi | sempre | `internal` |
| `status` | Default `draft` | sempre | `draft` |
| `approvers[]` | Chiedi (nome, ruolo) | status `in-review` o `approved` | `[{nome:"M.Rossi", ruolo:"CTO"}]` |
| `reviewers[]` | Chiedi (nome, ruolo) | status ≥ `in-review` | `[{nome:"A.Bianchi", ruolo:"PM"}]` |
| `stakeholders[]` | Chiedi opzionale | `status-report`, `proposta`, `sow` | `[{nome:"Cliente X", ruolo:"Sponsor"}]` |
| `cliente` | Chiedi | tipologie con committente esterno | `ACME S.p.A.` |
| `progetto_codice` | Chiedi | progetto/sow/proposta/status | `ACME-PRJ-042` |
| `contratto_id` | Chiedi opzionale | sow/proposta | `CTR-2026-018` |
| `logo_path` | Brand profile o chiedi | se brand attivo | `~/logos/example-brand.png` |

## Domanda aggiuntiva Step 1 (solo tipologie business)

Usa **UNA** `AskUserQuestion` aggiuntiva con 4 opzioni principali:

1. **Brand profile attivo** → carica `.brand-profile.json` attivo, precompila logo/palette/classification default
2. **Brand profile custom** → chiedi quale brand se ce ne sono più d'uno
3. **Nessun brand** → no logo, stile neutro
4. **Configura ora un nuovo brand** → wizard interattivo, salva in `.brand-profile.json`

Poi una seconda `AskUserQuestion` per la **classification**:
- `public` (pubblicabile), `internal` (uso interno), `confidential` (riservato), `restricted` (accesso limitato)
- Default = `brand.classification_default` se presente, altrimenti `internal`

## Control sheet (seconda pagina PDF)

Dopo la cover page, inserisci una pagina "Document Control" con:

```markdown
## Document Control

| | |
|---|---|
| **Doc ID** | {{doc_id}} |
| **Protocollo** | {{protocollo}} |
| **Versione** | {{doc_version}} |
| **Status** | {{doc_status}} |
| **Classificazione** | {{classification}} |
| **Autore** | {{author}} |
| **Data** | {{today}} |
| **Cliente** | {{client_name}} |
| **Progetto** | {{project_code}} |

### Approvazioni

| Nome | Ruolo | Data | Firma |
|---|---|---|---|
| {{approver_1_name}} | {{approver_1_role}} | __________ | __________ |

### Revisione

| Versione | Data | Autore | Descrizione modifiche |
|---|---|---|---|
| 0.1 | {{today}} | {{author}} | Prima stesura |
```

Equivalente LaTeX con `\begin{tabular}` o package `booktabs`.

## Regole

1. **Status `draft`** → banner grande "DRAFT" in cover + watermark pagina (vedi Fase 9)
2. **Status `in-review`** → banner "FOR REVIEW" + highlight sezioni con `[TODO]`/`[MOCK]`/`[DA COMPLETARE]`
3. **Status `approved`** → pulisci banner, timbro data approvazione, PDF finale in `archive/` sottocartella
4. **Classificazione `confidential`/`restricted`** → header/footer con classification su ogni pagina
5. **Ogni update a cover** → aggiorna `cover.versione` (patch +0.1) e aggiungi riga a changelog

## Integrazione con `resolve-variables.py`

Tutti i campi sono risolti via placeholder. Esempio in template LaTeX:

```latex
\newcommand{\docid}{{\{\{doc_id\}\}}}
\newcommand{\classlabel}{{\{\{classification\}\}}}
\newcommand{\version}{{\{\{doc_version\}\}}}
```

Poi, alla fine del Step 6, esegui:

```bash
python3 scripts/workflow/resolve-variables.py <file> --state <state> --in-place
```

## Quando saltare il control sheet

- Tipologie accademiche (`tesi`, `ricerca`, `stage` universitario, `laboratorio`, `esperienza`) NON hanno control sheet — usano frontespizio accademico standard
- `bug` / `codice` / `analisi-codice` → solo se `cover.classificazione != "public"`
- Tipologie enterprise → **sempre** control sheet

# LAYOUTS — Schemi visivi per categoria di relazione

Riferimento **bloccante** per Step 3.8 (skeleton materialization) e Step 4 (draft).

Lo Step 3.8 legge questo file in base a `answers.tipologia`, materializza lo scheletro vuoto su `.session/skeleton.md`, e lo Step 4 si limita a **riempire i placeholder** — mai aggiungere, rimuovere o riordinare heading.

Regola d'oro: **se una sezione non è nel layout, non esiste. Se è nel layout, esiste sempre nell'ordine indicato.**

---

## Mappa tipologia → categoria

| Tipologia | Categoria | Schema |
|---|---|---|
| `tesi`, `ricerca`, `laboratorio` (long) | ACCADEMICO | §1 |
| `proposta`, `rfp-response`, `sow`, `business-case`, `whitepaper`, `case-study`, `handover`, `progetto` (>30 pp) | AZIENDALE | §2 |
| `tecnica`, `codice`, `analisi-codice`, `spec-funzionale`, `spec-tecnica`, `runbook` | TECNICO | §3 |
| `bug`, `incident-postmortem`, `audit-report`, `compliance-report` | POSTMORTEM | §4 |
| `esperienza`, `stage`, `finale`, `laboratorio` (short) | NARRATIVO | §5 |
| `status-report` (ricorrente) | STATUS | §6 |
| `custom` | ASK USER | — |

---

## §1 — ACCADEMICO

Per: `tesi`, `ricerca`, `laboratorio` (>15 pp), paper scientifici.

```
┌─────────────────────────────────────────────┐
│  1. FRONTESPIZIO                            │
│     └─ titolo, autore, relatore, ente, data │
├─────────────────────────────────────────────┤
│  2. ABSTRACT (lingua principale)            │
│  3. ABSTRACT (inglese)            [se IT]   │
├─────────────────────────────────────────────┤
│  4. INDICE                                  │
│  5. ELENCO FIGURE                 [se ≥ 3]  │
│  6. ELENCO TABELLE                [se ≥ 3]  │
│  7. ELENCO ACRONIMI               [se ≥ 5]  │
├─────────────────────────────────────────────┤
│  8. INTRODUZIONE                            │
│  9. STATO DELL'ARTE                         │
│ 10. METODOLOGIA                             │
│ 11. IMPLEMENTAZIONE / SVILUPPO              │
│ 12. RISULTATI                               │
│ 13. DISCUSSIONE                             │
│ 14. CONCLUSIONI E SVILUPPI FUTURI           │
├─────────────────────────────────────────────┤
│ 15. NOTA METODOLOGICA              [se mock]│
│ 16. BIBLIOGRAFIA                            │
├─────────────────────────────────────────────┤
│ 17. APPENDICE A: dati estesi      [opz]     │
│ 18. APPENDICE B: codice / firme   [opz]     │
│ 19. APPENDICE C: questionari      [opz]     │
└─────────────────────────────────────────────┘
```

**Bloccante:**
- Abstract PRIMA dell'indice
- Indice nel blocco 2 (dopo frontespizio + abstract)
- Elenchi figure/tabelle/acronimi DOPO l'indice e PRIMA dell'introduzione
- Bibliografia PRIMA delle appendici
- Conclusioni PRIMA della bibliografia
- Nessuna appendice prima della bibliografia

**Scaling per pagine:**
- 40-60 pp: scheletro completo, sezioni ~3-5 pp ciascuna
- 60-100 pp: aggiungi sottosezioni (§9.1, §9.2 …)
- 100-150 pp (tesi magistrali): includi appendici complete e dataset

---

## §2 — AZIENDALE

Per: `proposta`, `rfp-response`, `sow`, `business-case`, `whitepaper`, `case-study`, `handover`, `progetto` (>30 pp).

```
┌─────────────────────────────────────────────┐
│  1. COVER + DOCUMENT CONTROL                │
│     └─ titolo, cliente, doc-id, versione,   │
│        classification, autori, approvers    │
├─────────────────────────────────────────────┤
│  2. EXECUTIVE SUMMARY              [1 pag]  │
├─────────────────────────────────────────────┤
│  3. INDICE                                  │
├─────────────────────────────────────────────┤
│  4. CONTESTO E OBIETTIVI                    │
│  5. STAKEHOLDER E PERIMETRO                 │
│  6. SOLUZIONE PROPOSTA                      │
│  7. APPROCCIO / METODOLOGIA                 │
│  8. ROADMAP / TIMELINE                      │
│  9. DELIVERABLE                             │
│ 10. ECONOMICS                     [se appl] │
│ 11. RISCHI E MITIGAZIONI                    │
│ 12. ASSUNZIONI E DIPENDENZE                 │
├─────────────────────────────────────────────┤
│ 13. NEXT STEPS                              │
│ 14. CONTATTI / RESPONSABILI                 │
├─────────────────────────────────────────────┤
│ 15. NOTA METODOLOGICA              [se mock]│
│ 16. GLOSSARIO                     [opz]     │
│ 17. APPENDICE A: dettagli tecnici [opz]     │
│ 18. APPENDICE B: SLA / contratto  [opz]     │
└─────────────────────────────────────────────┘
```

**Bloccante:**
- Executive summary PRIMA dell'indice (cliente legge prima quello)
- Document control nella cover (mai pagina separata)
- Economics PRIMA di rischi (ordine narrativo: cosa offro → quanto costa → cosa può andare storto)
- Next steps come ULTIMA sezione del corpo
- Glossario PRIMA delle appendici

**Varianti per tipologia:**
- `rfp-response`: aggiungi §3.5 "Matrice di conformità RFP" (mappa requirement → risposta)
- `sow`: §10 diventa "Pricing + Pagamenti", §11 diventa "SLA"
- `business-case`: aggiungi §10.5 "Analisi ROI" e §11.5 "Scenari (best/expected/worst)"
- `whitepaper`: rimuovi §10 (economics), §13 (next steps); aggiungi §6.5 "Evidenze"
- `case-study`: §4 → "Sfida del cliente", §6 → "Cosa abbiamo fatto", §7 → "Risultati misurati"
- `handover`: §6 → "Stato attuale del sistema", §8 → "Cosa resta da fare", §9 → "Runbook operativo"

---

## §3 — TECNICO

Per: `tecnica`, `codice`, `analisi-codice`, `spec-funzionale`, `spec-tecnica`, `runbook`.

```
┌─────────────────────────────────────────────┐
│  1. INTESTAZIONE                            │
│     └─ titolo, doc-id, versione, autori,    │
│        ultimo aggiornamento                 │
├─────────────────────────────────────────────┤
│  2. SCOPO E AUDIENCE              [1 par]   │
├─────────────────────────────────────────────┤
│  3. INDICE                                  │
├─────────────────────────────────────────────┤
│  4. CONTESTO E REQUISITI                    │
│  5. ARCHITETTURA                            │
│  6. STACK TECNOLOGICO                       │
│  7. MODELLO DATI                  [se appl] │
│  8. IMPLEMENTAZIONE PER MODULO              │
│     ├─ 8.1 Modulo X                         │
│     ├─ 8.2 Modulo Y                         │
│     └─ 8.N …                                │
│  9. CONFIGURAZIONE E DEPLOY                 │
│ 10. SICUREZZA                                │
│ 11. TESTING E QUALITÀ                       │
│ 12. PERFORMANCE                   [opz]     │
│ 13. OSSERVABILITÀ                 [opz]     │
├─────────────────────────────────────────────┤
│ 14. LIMITAZIONI NOTE                        │
│ 15. RIFERIMENTI                             │
├─────────────────────────────────────────────┤
│ 16. APPENDICE A: firme interfaccia [se code]│
│ 17. APPENDICE B: schema completo  [opz]     │
└─────────────────────────────────────────────┘
```

**Bloccante:**
- Scopo+audience PRIMA dell'indice (lettore sa subito se è il doc giusto)
- Architettura PRIMA di stack (concetto prima della tecnologia)
- Modello dati PRIMA di implementazione (se applicabile)
- Sicurezza è SEZIONE DEDICATA, mai sparpagliata
- Limitazioni note PRIMA dei riferimenti
- Code snippet dentro le sotto-sezioni di pertinenza (§8.x), non in appendice obbligatoria

**Varianti per tipologia:**
- `analisi-codice`: §5 → "Mappa del codebase", §6 → "Pattern e anti-pattern rilevati", §8 → "Hotspot per modulo"
- `spec-funzionale`: §5 → "User stories e use case", §8 → "Specifiche funzionali per area", rimuovi §9-13
- `spec-tecnica`: estendi §5 con diagrammi C4, §11 → "Strategia di test (unit/integration/e2e)"
- `runbook`: §8 → "Procedure operative (start, stop, restart, restore)", §9 → "Troubleshooting", §10 → "Escalation"
- `codice`: §8 → "Walkthrough del codice file-per-file", §11 → "Come eseguire i test"

---

## §4 — POSTMORTEM

Per: `bug`, `incident-postmortem`, `audit-report`, `compliance-report`.

```
┌─────────────────────────────────────────────┐
│  1. INTESTAZIONE                            │
│     └─ incident-id, severity, data,         │
│        autori, status (open/resolved)       │
├─────────────────────────────────────────────┤
│  2. TL;DR                          [3-5 r]  │
│     └─ cosa è successo, impatto, risolto?   │
├─────────────────────────────────────────────┤
│  3. INDICE                                  │
├─────────────────────────────────────────────┤
│  4. TIMELINE                                │
│     └─ ISO datetime, evento, attore         │
│  5. IMPATTO                                 │
│     └─ utenti, revenue, SLA breach          │
│  6. ROOT CAUSE                              │
│     └─ 5 perché, contributing factors       │
│  7. AZIONI DI MITIGAZIONE (immediate)       │
│  8. AZIONI DI REMEDIATION (lungo termine)   │
│  9. COSA HA FUNZIONATO                      │
│ 10. COSA NON HA FUNZIONATO                  │
├─────────────────────────────────────────────┤
│ 11. ACTION ITEMS                            │
│     └─ owner, deadline, status              │
│ 12. LESSONS LEARNED                         │
├─────────────────────────────────────────────┤
│ 13. RIFERIMENTI                             │
│     └─ ticket, log, dashboard, PR           │
│ 14. APPENDICE: log estratti       [opz]     │
└─────────────────────────────────────────────┘
```

**Bloccante:**
- TL;DR PRIMA dell'indice (chi legge la mattina deve capire in 30 sec)
- Timeline PRIMA di root cause (i fatti prima dell'interpretazione)
- Root cause PRIMA delle azioni (non puoi fixare ciò che non hai capito)
- Action items SEMPRE con owner+deadline (mai action item orfani)
- Niente "blameful" naming — solo ruoli ("on-call", "deploy bot"), mai persone

**Varianti per tipologia:**
- `bug`: rimuovi §9-12 (sproporzionati per bug singoli), mantieni §1-8, §13
- `incident-postmortem`: schema completo, severity ≥ S2
- `audit-report`: §4 → "Scope dell'audit", §6 → "Findings (con severity)", §7-8 → "Raccomandazioni"
- `compliance-report`: §4 → "Framework di riferimento (GDPR/SOC2/...)", §6 → "Gap analysis", §11 → "Piano di rimediazione con milestone"

---

## §5 — NARRATIVO

Per: `esperienza`, `stage`, `finale`, `laboratorio` (5-15 pp).

```
┌─────────────────────────────────────────────┐
│  1. FRONTESPIZIO                            │
│     └─ titolo, autore, ente, periodo, data  │
├─────────────────────────────────────────────┤
│  2. INDICE                                  │
├─────────────────────────────────────────────┤
│  3. INTRODUZIONE / CONTESTO                 │
│     └─ chi sono, cosa ho fatto, dove        │
│  4. OBIETTIVI                               │
│  5. ATTIVITÀ SVOLTE                         │
│     ├─ 5.1 Periodo 1                        │
│     ├─ 5.2 Periodo 2                        │
│     └─ 5.N …                                │
│  6. COMPETENZE ACQUISITE                    │
│  7. DIFFICOLTÀ INCONTRATE                   │
│  8. RIFLESSIONE PERSONALE                   │
│  9. CONCLUSIONI                             │
├─────────────────────────────────────────────┤
│ 10. NOTA METODOLOGICA              [se mock]│
│ 11. RIFERIMENTI                   [opz]     │
│ 12. APPENDICE: artefatti prodotti [opz]     │
└─────────────────────────────────────────────┘
```

**Bloccante:**
- Frontespizio + indice prima del corpo (anche per doc brevi)
- Attività svolte ORGANIZZATE per periodo o per tema (sceglie l'utente in Step 5)
- Riflessione PRIMA delle conclusioni (sono distinte: riflessione = "cosa ho imparato di me", conclusioni = "cosa è stato fatto")
- Mai pagine di "ringraziamenti" qui (vanno in tesi accademiche, non in stage/esperienza)

**Varianti per tipologia:**
- `stage`/`tirocinio`: §3 → "Azienda ospitante e settore", §6 → "Competenze tecniche e trasversali", aggiungi §9.5 "Valutazione tutor aziendale" (placeholder)
- `finale`: §5 → "Sintesi del progetto", §6 → "Risultati", rimuovi §7-8
- `esperienza`: schema completo, più libero

---

## §6 — STATUS REPORT (per `/relazione-ricorrente`)

Per: `status-report` (weekly, biweekly, monthly).

```
┌─────────────────────────────────────────────┐
│  1. INTESTAZIONE                            │
│     └─ progetto, periodo (es. W16/2026),    │
│        data emissione, autore               │
├─────────────────────────────────────────────┤
│  2. TL;DR                          [3 r]    │
│     └─ stato semaforico (verde/giallo/rosso)│
├─────────────────────────────────────────────┤
│  3. INDICE                        [se ≥ 3pp]│
├─────────────────────────────────────────────┤
│  4. COSA È STATO FATTO QUESTA SETTIMANA     │
│  5. COSA È IN CORSO                         │
│  6. COSA È PIANIFICATO PROSSIMA SETTIMANA   │
│  7. BLOCCANTI E RISCHI                      │
│  8. METRICHE CHIAVE                [opz]    │
│  9. DECISIONI RICHIESTE                     │
├─────────────────────────────────────────────┤
│ 10. VARIAZIONI DAL PERIODO PRECEDENTE       │
│     └─ auto-generato da diff-summary.py     │
├─────────────────────────────────────────────┤
│ 11. APPENDICE: ticket chiusi      [opz]     │
└─────────────────────────────────────────────┘
```

**Bloccante:**
- TL;DR sempre con stato semaforico esplicito
- Variazioni dal periodo precedente sempre come ULTIMA sezione del corpo (consumer reader)
- Niente "lessons learned" qui (vanno in retrospettive sprint, non in status weekly)
- Decisioni richieste come elenco numerato con owner+deadline

---

## Convenzioni del file skeleton

Lo Step 3.8 produce `.session/skeleton.md` con questo formato:

```markdown
<!-- LAYOUT-VERSION: 1 -->
<!-- TIPOLOGIA: tesi -->
<!-- CATEGORIA: ACCADEMICO -->

<!-- SECTION: frontespizio | ORDER: 1 | REQUIRED -->
# {{titolo}}

{{autore}} · {{ente}}
Relatore: {{relatore}}
{{data}}

<!-- SECTION: abstract-it | ORDER: 2 | REQUIRED -->
## Abstract

[DA RIEMPIRE: 150-250 parole. Sintesi del problema, metodo, risultato chiave.]

<!-- SECTION: abstract-en | ORDER: 3 | REQUIRED if lingua=italiano -->
## Abstract (English)

[DA RIEMPIRE: translation of §2.]

<!-- SECTION: indice | ORDER: 4 | REQUIRED -->
## Indice

[TOC AUTO-GENERATA]

...
```

**Regole per Step 4:**
- Mai cancellare un commento `<!-- SECTION: ... -->`
- Mai modificare l'ordine (`ORDER:`)
- Mai aggiungere heading non listati nello skeleton
- Sostituire ogni `[DA RIEMPIRE: ...]` con contenuto reale
- Sostituire ogni `{{placeholder}}` con valore da `state.answers` o `cover.*`
- Se un blocco è marcato `REQUIRED if <condizione>` e la condizione è falsa, rimuovere l'intero blocco (commento incluso)

**Validation downstream:**
- Step 6.7 `layout-coherence.py` verifica che ogni `<!-- SECTION: x | ORDER: N -->` sia presente e nell'ordine giusto
- Se manca o è fuori ordine → FAIL bloccante (regola 9 SKILL.md)

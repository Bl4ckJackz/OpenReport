---
title: "Status Report — Settimana 18 / 2026"
subtitle: "Progetto Atlas — Migrazione piattaforma di pagamento"
author: "Team Atlas"
date: "2026-05-04"
classification: "internal"
status: "approved"
version: "1.0"
---

# Sommario esecutivo

La settimana 18 ha consolidato l'integrazione del nuovo gateway con l'ambiente di staging. Sono stati chiusi 14 ticket su 17 pianificati; i 3 residui sono rinviati alla settimana 19 senza impatto sul go-live previsto per il 2026-06-30.

## Highlights

- Throughput in staging: 1.240 tx/min (+18% rispetto alla baseline)
- Errori 5xx in staging: 0,03% (target <0,1%)
- Riduzione latenza media checkout: 312 ms → 247 ms

# Avanzamento

| Workstream | Stato | Δ vs scorsa settimana |
|---|---|---|
| Gateway integration | 92% | +14 punti |
| Reconciliation engine | 71% | +6 punti |
| Compliance PSD2 | 88% | +2 punti |
| Migration tooling | 60% | +12 punti |

# Rischi e blocchi

1. **Certificato eIDAS in scadenza il 2026-06-15** — rinnovo in corso, owner: Team Security. Mitigation: chiavi tampone già emesse.
2. **Capacity planning peak Black Friday** — analisi a partire dalla settimana 22.

# Decisioni della settimana

- Adottato algoritmo di retry esponenziale con jitter (RFC 7231) sul reconciliation engine.
- Scartata l'opzione di fallback sincrono al vecchio gateway in caso di failure: aggiunge complessità senza guadagno misurabile.

# Prossima settimana

- Stress test con profilo di carico Black Friday 2025 replay
- Rilascio in pre-prod del modulo di reconciliation
- Audit compliance interno (giovedì 2026-05-15)

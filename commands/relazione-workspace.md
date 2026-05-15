---
description: Gestisce workspace multi-sessione per /relazione (più relazioni attive in parallelo)
argument-hint: "[list|switch|create|archive|status] [nome]"
---

# /relazione-workspace — Multi-sessione

Un workspace è un contenitore logico che raggruppa più sessioni `/relazione` correlate (es. "Cliente-ACME-2026", "Tesi-Magistrale", "Proposte-Q2"). Permette di:

- Avere N sessioni attive in parallelo, ciascuna in cartella propria
- Switch rapido fra workspace senza perdere contesto
- Archiviare workspace completi quando milestone raggiunta
- Stats aggregati (totale relazioni, tempo speso, tipologie più usate)

## Struttura

```
relazioni-workspaces/
├── .index.json                     # meta: workspace attivo, lista, stats
├── cliente-acme-2026/
│   ├── relazione-proposta-iniziale/
│   ├── relazione-sow-dettagliato/
│   └── relazione-status-w16/
├── tesi-magistrale/
│   └── relazione-tesi/
└── proposte-q2/
    ├── relazione-acme/
    ├── relazione-beta/
    └── relazione-gamma/
```

## Sub-comandi

### `/relazione-workspace list`

Elenca tutti i workspace con:
- Nome · numero relazioni · data ultima modifica · stato (attivo/archiviato)
- Workspace attivo marcato con `*`

### `/relazione-workspace create <nome>`

Crea nuovo workspace `relazioni-workspaces/<nome>/`, lo imposta attivo.

### `/relazione-workspace switch <nome>`

Cambia workspace attivo. Da questo momento:
- Nuove sessioni `/relazione` vanno dentro `relazioni-workspaces/<nome>/`
- `/relazione-continua` cerca solo dentro questo workspace

### `/relazione-workspace status`

Mostra workspace attivo + elenco relazioni interne (status, tipologia, ultima modifica).

### `/relazione-workspace archive <nome>`

Rinomina `relazioni-workspaces/<nome>/` → `relazioni-workspaces/archived/<nome>-<YYYY-MM>/`. Aggiorna `.index.json` status=archived. Mantiene tutti i dati.

### `/relazione-workspace stats`

Statistiche aggregate:
- Totale relazioni create
- Distribuzione per tipologia
- Tempo medio da start a approved
- Top tag (vedi `/relazione-tag`)

## Storage

`.index.json`:
```json
{
  "active": "cliente-acme-2026",
  "workspaces": [
    {
      "nome": "cliente-acme-2026",
      "created_at": "2026-04-01T10:00:00Z",
      "status": "active",
      "last_activity_at": "2026-04-17T14:30:00Z",
      "relazioni_count": 3,
      "tags": ["cliente", "acme", "2026"]
    }
  ]
}
```

## Red flags

- **Non cambiare workspace mentre una sessione è in-progress** senza fare prima `/relazione-continua` o save point
- **Non archiviare workspace con relazioni `in-review`** o `draft` senza conferma utente
- **Non nominare workspace con caratteri speciali** (solo `[a-z0-9-]`)
- **Sync check**: prima di archive, verifica che tutte le sessioni abbiano backup in `.session/backups/`

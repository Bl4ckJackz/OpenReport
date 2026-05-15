---
description: Configura il brand profile aziendale per /relazione (logo, colori, font, claim, glossario, banned/preferred words).
argument-hint: "[list|add|edit|activate|show] [nome-brand]"
---

# /relazione-brand — Setup brand profile per /relazione

Wizard interattivo per gestire `~/.claude/skills/relazione/.brand-profile.json`.

## Sub-comandi

### `/relazione-brand list`

Elenca i brand configurati:
```bash
python3 ~/.claude/skills/relazione/scripts/brand-loader.py --list
```

### `/relazione-brand show [nome]`

Mostra i dettagli (JSON) del brand attivo o del brand specificato:
```bash
python3 ~/.claude/skills/relazione/scripts/brand-loader.py --info [--brand <nome>]
```

### `/relazione-brand add`

Wizard interattivo per aggiungere un nuovo brand. Usa `AskUserQuestion` sequenziali:

**Batch 1 — anagrafica:**
1. Nome breve del brand (chiave, es. `mindsmart`) — testo libero
2. Ragione sociale completa (es. `Mindsmart S.r.l.`) — testo libero
3. P.IVA / VAT — testo libero (può restare vuoto)
4. Claim / payoff — testo libero
5. Sito web — testo libero

**Batch 2 — contatti:**
6. Email default — testo libero
7. Telefono — testo libero
8. PEC — testo libero
9. SDI — testo libero

**Batch 3 — identity:**
10. Path logo (es. `~/logos/marchio.png`) — chiedi e verifica esistenza con Glob
11. Colore primary (hex, es. `#1D3557`) — testo libero
12. Colore secondary — testo libero
13. Colore accent — testo libero
14. Font body (es. `Inter`) — testo libero
15. Font heading — testo libero

**Batch 4 — governance:**
16. Classificazione default (`public`/`internal`/`confidential`/`restricted`) — `AskUserQuestion`
17. Banned words (termini vietati in documenti) — testo libero separato da virgole
18. Preferred terms (sostituzioni, formato `generic1=aziendale1, generic2=aziendale2`) — testo libero

Dopo la raccolta, **leggi** `.brand-profile.json`, **aggiungi** un oggetto in `brands[]`, **scrivi** con Write. Aggiorna `updated_at`.

Infine `AskUserQuestion`: "Imposta questo brand come attivo?" — se sì, aggiorna `active_brand`.

### `/relazione-brand edit [nome]`

Leggi il brand esistente, mostra i campi, chiedi quali modificare. Applica modifiche preservando il resto.

### `/relazione-brand activate <nome>`

Cambia `active_brand` nel JSON. Verifica che il brand esista prima.

### Senza argomenti

Mostra menu con `AskUserQuestion`:
- `Elenca brand` → sub-comando list
- `Mostra attivo` → sub-comando show
- `Aggiungi nuovo brand` → sub-comando add
- `Modifica brand` → sub-comando edit (chiedi quale)
- `Attiva brand diverso` → sub-comando activate

## Red flags

- **Mai** includere secret/credenziali nel brand profile (key API, password)
- **Mai** scrivere path assoluti Windows con backslash — usa forward slash o `~/`
- **Valida** hex colors contro regex `^#[0-9a-fA-F]{6}$` prima di salvare
- **Verifica** che il path logo esista prima di salvare (Glob), se no avvisa ma permetti comunque (utente può fornirlo dopo)
- **Backup** del file esistente prima di riscriverlo: copia in `.brand-profile.json.bak-<ISO>`

## Output atteso

Conferma testuale con nome brand creato/modificato e `active_brand` corrente. Esempio:

> Brand `mindsmart` salvato. Active brand: `mindsmart`.
> Per usarlo: `--brand=mindsmart` nei comandi /relazione o settando `answers.brand_profile` in session-state.

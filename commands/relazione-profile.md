---
description: Configura il profilo utente persistente di /relazione (nome, stile, voice profile, preferenze output, banned/preferred words personali)
argument-hint: "[show|edit|reset|set-voice-from <path>]"
---

# /relazione-profile — Gestisci `.user-profile.json`

Wizard interattivo per `~/.claude/skills/relazione/.user-profile.json`. Mirror di `/relazione-brand` ma orientato all'individuo, non all'azienda.

Il profilo seeda voice/stile/preferenze ad ogni nuova sessione `/relazione`, riducendo le domande iniziali.

## Sub-comandi

### Senza argomenti o `show`

Stampa il profilo corrente in formato leggibile (non JSON crudo):

```
Profilo utente
──────────────
Nome:            Dominik Duda
Email:           dominik.duda@coinsafe.it
Ruolo default:   founder / consulente
Ente default:    Coinsafe
Lingua:          italiano
Stile:           formale-accademico

Voice profile (da N relazioni passate)
──────────────────────────────────────
Persona:         prima-plurale
Tempo dominante: presente
Lunghezza frase media: 22.4 parole
Marker lessicali:  in particolare, ovvero, quindi, di seguito
Aperture tipiche:  "Il presente documento", "Nel corso di"

Preferenze output
─────────────────
Formato default: md
PDF style:       moderno
Executive summary auto: no
Slide deck auto: no

Personalizzazioni
─────────────────
Banned words:     (nessuna)
Preferred terms:  customer → cliente
```

Esegui:
```bash
PROFILE="$HOME/.claude/skills/relazione/.user-profile.json"
test -f "$PROFILE" || { echo "Nessun profilo. Esegui /relazione-profile edit"; exit 0; }
python3 -c "
import json
p = json.load(open('$PROFILE'))
# pretty print formattato come sopra
"
```

### `edit`

Wizard `AskUserQuestion` sequenziale. Ogni batch ha la sua schermata.

**Batch 1 — anagrafica:**
1. Nome completo — testo libero (default: valore corrente)
2. Email — testo libero
3. Ruolo default (es. `studente magistrale`, `founder`, `consulente`) — testo libero
4. Ente default (università/azienda) — testo libero

**Batch 2 — preferenze linguistiche:**
5. Lingua preferita — `italiano`, `inglese`
6. Stile preferito — `formale-accademico`, `semi-formale-aziendale`, `tecnico-divulgativo`, `narrativo-personale`

**Batch 3 — voice profile (opzionale, default skip):**
7. Persona — `prima-singolare`, `prima-plurale`, `impersonale`, `terza`
8. Lunghezza frase media (parole) — numero (default 20)
9. Marker lessicali — testo libero separato da virgole
10. Aperture tipiche di sezione — testo libero separato da `;`

**Batch 4 — preferenze output:**
11. Formato default — `md`, `latex`, `both`
12. PDF style default — `accademico`, `moderno`, `brand`
13. Includi executive summary di default — `sì` / `no`
14. Includi slide deck di default — `sì` / `no`

**Batch 5 — sostituzioni personali:**
15. Banned words personali — testo libero separato da virgole
16. Preferred terms — testo libero formato `generic1=preferito1, generic2=preferito2`

**Dopo la raccolta:**
1. Leggi `.user-profile.json` corrente
2. Backup in `.user-profile.json.bak-<ISO>`
3. Aggiorna campi modificati (preserva quelli non toccati)
4. Setta `updated_at` a ora
5. Validate contro `schemas/user-profile.schema.json`
6. Write

### `reset`

`AskUserQuestion`: "Reset a profilo vuoto? Backup salvato in `.user-profile.json.bak-<ISO>`."
Se conferma:
```bash
PROFILE="$HOME/.claude/skills/relazione/.user-profile.json"
cp "$PROFILE" "$PROFILE.bak-$(date -u +%Y%m%dT%H%M%SZ)"
# riscrivi con template vuoto (vedi .user-profile.json originale)
```

### `set-voice-from <path>`

Distilla voice profile da una relazione esistente (es. precedente lavoro dell'utente):

```bash
python3 ~/.claude/skills/relazione/scripts/voice-lock.py extract <path> --to-profile
```

Lo script aggiorna `voice_profile.*` nel `.user-profile.json` e aggiunge il path a `relazioni_precedenti[]` (FIFO, max 10).

## Red flags

- **Mai** salvare credenziali (`password`, `api_key`, `token`) nel profile
- **Valida** email contro regex `^[^@]+@[^@]+\.[^@]+$` prima di salvare
- **Backup** del file esistente prima di ogni `edit` o `reset`
- **Mai** sovrascrivere `created_at`
- Banned words personali si **sommano** a quelle del brand attivo (`/relazione-brand`), non le sostituiscono

## Differenza vs `/relazione-brand`

| Aspetto | `/relazione-brand` | `/relazione-profile` |
|---|---|---|
| Scope | Azienda / cliente | Singolo utente |
| Storage | `.brand-profile.json` (lista `brands[]`) | `.user-profile.json` (singolo profilo) |
| Tipico contenuto | Logo, palette, claim, ragione sociale | Voice, stile, preferenze output, ruolo |
| Quando viene applicato | Quando `answers.brand_profile` è settato | SEMPRE all'avvio di `/relazione` |

I due profili si sommano. Il brand vince per identity visiva (palette/logo). L'utente vince per voice/stile.

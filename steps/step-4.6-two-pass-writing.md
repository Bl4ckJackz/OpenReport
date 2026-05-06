# Step 4.6 — Two-pass writing (per relazioni lunghe)

Attivato automaticamente quando `answers.lunghezza_target_pagine >= 30` o quando l'utente passa `--two-pass`.

Riduce drift di tono e ripetizioni in documenti lunghi separando "scheletro" e "espansione".

## Pass 1 — Scheletro completo

Genera **solo struttura** del documento:
- Tutti i titoli e sottotitoli (livelli `#`, `##`, `###`)
- Per ogni sezione: 3-7 bullet con i punti che andranno trattati
- Frontespizio compilato (autore, titolo, data)
- TOC stub
- Lista figure/tabelle pianificata
- Bibliografia: chiavi pianificate (placeholder)

Output: `<output>/.session/draft-pass-1-skeleton.md`

**Stop e checkpoint:** mostra scheletro all'utente con `AskUserQuestion`:
- `Procedi all'espansione` → Pass 2
- `Modifica struttura` → utente edita inline
- `Aggiungi/rimuovi sezioni` → batch update
- `Pausa e /clear` → salva state, riprende dopo

## Pass 2 — Espansione sezione per sezione

**Ordine sequenziale**, una sezione alla volta:

Per ogni sezione del Pass 1:
1. Carica voice profile (se locked dalla prima sezione)
2. Espandi i bullet in prosa
3. Inserisci `[MOCK]` o `[DA COMPLETARE]` dove mancano dati
4. Verifica che la lunghezza espansa rispetti la quota della sezione (target_pagine × 400 / num_sezioni × peso_sezione)
5. Salva sezione singola in `<output>/.session/draft-pass-2-section-{N}.md`
6. Append a `RELAZIONE.md` accumulando

**Voice profile lock dopo prima sezione:**
- Estrai marker stilistici da Pass 2 sezione 1: lunghezza media frase, persona dominante, tempo verbale, lessico ricorrente, densità subordinate
- Salva in `session-state.json.voice_profile`
- Riapplica come constraint a tutte le sezioni successive del Pass 2

## Vantaggi

- Stato salvato dopo ogni sezione → safe interruption
- Voice consistency garantita (no drift tra capitoli)
- Permette modifiche strutturali senza buttare prosa
- Scheletro riutilizzabile per slide deck companion

## Quando NON usare

- Target < 30 pagine: bozza monolitica è più veloce
- Tipologie discorsive (`esperienza`, `bug`): lo scheletro perde naturalezza
- L'utente ha esplicitamente passato `--monolithic`

## Backup automatico

Prima di ogni nuova sezione del Pass 2:
- Copia `RELAZIONE.md` corrente in `.session/backups/{ISO-timestamp}-pre-section-{N}.md`
- Se la nuova sezione è peggiore (l'utente lo dice), `/relazione-rollback` la ripristina

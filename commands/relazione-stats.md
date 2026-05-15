---
description: Mostra statistiche e diagnostica delle sessioni /relazione (passate e correnti)
allowed-tools: Bash, Read, Glob, Grep
---

# /relazione-stats — Dashboard sessioni /relazione

## Argomenti

`$ARGUMENTS` può essere:
- vuoto — riepilogo globale
- `--current` — solo sessione attiva nella cwd
- `--all` — anche sessioni completate
- `--html` — genera **dashboard HTML** con progress ring SVG, sezioni, metriche, quick actions, e la apre nel browser (delega a `render-stats-dashboard.py`, vedi `/relazione-visual dashboard`)

## Modalità `--html`

Se `$ARGUMENTS` contiene `--html`, **non stampare l'output testuale sotto**. Invece:

```bash
python3 ~/.claude/skills/relazione/scripts/render-stats-dashboard.py --open
```

Lo script auto-detect la sessione più recente (incluse `relazioni-workspaces/*/*/` e `relazioni-ricorrenti/*/*/`), genera `<session>/.session/dashboard.html` e lo apre cross-OS via `_browser-open.sh`.

Per specificare una sessione precisa: `--html --session relazioni-2026-04-16/`

## Output: Sessione corrente (se presente)

Se trovi `relazioni*/.session/session-state.json` nella cwd:

```
=== SESSIONE ATTIVA ===
Cartella: relazioni-2026-04-16/
Tipologia: tesi
Status: in-progress
Step corrente: step-4-draft
Età: 2 giorni (creata 2026-04-14T15:23)
Skill version: <da `cat ~/.claude/skills/relazione/VERSION`>

Progresso:
  ✓ Domande iniziali (9/9)
  ✓ Scan cartella (47 file)
  ✓ Ricerca online (12 fonti in research-notes.md)
  ⟳ Bozza (3247/12000 parole — 27%)
  ☐ Self-check
  ☐ Refinement
  ☐ Write output finale
  ☐ Export PDF/EPUB

Token budget:
  Stimato: 65k token
  Usato (approx): 28k (~43%)
  Margine: 37k disponibili — OK

Backup disponibili: 4 (più recente: 2 ore fa)
Mock inseriti: 7 (tutti listati in Nota metodologica draft)

File scritti:
  - RELAZIONE.md (3247 parole)
  - references.bib (12 entry)

Per riprendere: /relazione (auto-detect) oppure /relazione-continua
```

## Output: Riepilogo globale

```
=== STATISTICHE GLOBALI /relazione ===
Skill version: <da `cat ~/.claude/skills/relazione/VERSION`>
Path skill: ~/.claude/skills/relazione/

Sessioni totali (cwd ricorsivo, max-depth 4):
  In progress: 2
  Completate:  8
  Abbandonate: 1

Per tipologia (ultime 11):
  tesi:        3
  progetto:    4
  tecnica:     2
  bug:         1
  esperienza:  1

Tempo medio per tipologia (created → completed):
  tesi:      14 giorni
  progetto:  3 giorni
  tecnica:   1 giorno
  bug:       2 ore

Lunghezza media output (parole):
  tesi:      35,000 (~85 pagine)
  progetto:  12,500
  tecnica:   8,000
  bug:       1,200

Dipendenze rilevate:
  ✓ pandoc 3.1.2
  ✓ xelatex (MiKTeX)
  ✓ biber
  ✓ Eisvogel template installato
  ✗ mermaid-filter (non trovato)
  ✗ pygmentize (non trovato)

Preset più usati:
  1. mindsmart-tecnica (7 volte)
  2. tesi-magistrale (2 volte)
```

## Comportamento

1. **Leggi skill version**: `cat ~/.claude/skills/relazione/VERSION` — mai hardcodare (la versione cambia con `git pull` o update). Se il file manca o è vuoto, mostra `unknown` e segnala.
2. **Trova sessioni:** `Glob` per:
   - `**/relazioni*/.session/session-state.json` (max-depth 4)
   - `**/relazioni-workspaces/*/*/.session/session-state.json`
   - `**/relazioni-ricorrenti/*/*/.session/session-state.json`
3. **Leggi e parse** ogni JSON state
4. **Aggrega stats** per tipologia, durata, dimensione (raggruppando per container quando applicabile)
5. **Verifica dipendenze:** chiama tutti i comandi `--version` con timeout breve
6. **Mostra preset** dalla cartella `~/.claude/skills/relazione/presets/`

## Note

Solo lettura. Nessuna modifica. Output solo a console.

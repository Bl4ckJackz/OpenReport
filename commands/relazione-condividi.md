---
description: Comprime e condivide una sessione /relazione perché altri possano continuarla con /relazione-continua. Chiede l'OS del destinatario, comprime nel formato corretto, e apre il file manager per la condivisione.
argument-hint: "[cartella]  (opzionale: percorso della cartella relazioni/ da condividere)"
---

# /relazione-condividi — Comprimi e condividi una sessione

Crea un archivio portatile di una sessione `/relazione` (stato `.session/` + bozze + bibliografia) e apre il file manager per condividerlo. Chi riceve potra' estrarre l'archivio e continuare con `/relazione-continua`.

## Step 1 — Individua la sessione da condividere

**Se l'utente ha passato un argomento** (es. `/relazione-condividi relazioni-2026-04-13`): verifica che la cartella esista e contenga `.session/session-state.json`. Se non esiste o manca lo state, segnala errore e termina.

**Altrimenti**, cerca le sessioni nella cwd:

```
Glob: relazioni*/.session/session-state.json
```

Per ogni file trovato, leggi `session-state.json` ed estrai: `status`, `answers.tipologia`, `current_step`, `last_updated_at`, `cover.titolo`.

- **Nessuna trovata** — comunica: *"Nessuna sessione /relazione trovata nella cartella corrente. Avvia prima `/relazione`."* e termina.
- **Una sola** — mostra riepilogo (cartella, tipologia, step, titolo, data) e procedi direttamente a Step 2.
- **Piu' di una** — usa `AskUserQuestion` per far scegliere quale condividere (max 4 opzioni + Other). Per ciascuna mostra: nome cartella, tipologia, step corrente.

## Step 2 — Domande

Usa **una singola `AskUserQuestion`** con 2 domande:

**Domanda 1 — OS del destinatario** (single-select):
- `Windows (Recommended)` — genera `.zip` (compatibilita' nativa)
- `macOS` — genera `.zip`
- `Linux` — genera `.tar.gz`
- `Non lo so / Universale` — genera `.zip`

**Domanda 2 — Includere istruzioni per chi riceve?** (single-select):
- `Si, includi istruzioni (Recommended)` — aggiunge `ISTRUZIONI-CONDIVISIONE.md` nella cartella prima della compressione
- `No, solo i file`

## Step 3 — Genera file istruzioni (se richiesto)

Se l'utente ha scelto "Si", scrivi `<cartella>/ISTRUZIONI-CONDIVISIONE.md` nella lingua della relazione (`answers.lingua` da session-state.json; default: italiano).

**Contenuto (versione italiana — traduci se `answers.lingua = "inglese"`):**

```markdown
# Come continuare questa relazione

## Prerequisiti
- Claude Code installato (https://claude.ai/claude-code)
- Skill /relazione installata (~/.claude/skills/relazione/SKILL.md)
- Comando /relazione-continua (~/.claude/commands/relazione-continua.md)

## Procedura
1. Estrai l'archivio in una cartella di lavoro
2. Apri Claude Code in quella cartella
3. Scrivi `/relazione` oppure `/relazione-continua`
4. La sessione verra' rilevata e ripresa automaticamente

## Contenuto dell'archivio
- `.session/session-state.json` — stato della sessione (risposte, step corrente)
- `.session/scan-summary.md` — elenco file analizzati dal codebase originale
- `.session/codebase-notes.md` — note su architettura e stack tecnologico
- `.session/research-notes.md` — fonti e ricerche web effettuate
- `RELAZIONE.*` — bozza della relazione (se gia' generata)
- `references.bib` — bibliografia (se presente)

## Note importanti
- Il codebase originale NON e' incluso nell'archivio
- L'analisi del codebase e' salvata in `.session/codebase-notes.md` e `.session/scan-summary.md`
- Se vuoi rieseguire la scansione, dovrai avere i file sorgente nella cartella padre
- Stato attuale della sessione: {{current_step}}
- Tipologia: {{tipologia}}
```

Sostituisci `{{current_step}}` e `{{tipologia}}` con i valori reali da `session-state.json`.

## Step 4 — Comprimi

### 4.1 — Nome archivio

```
<nome-cartella>-share.<ext>
```

Esempi: `relazioni-share.zip`, `relazioni-2026-04-13-share.tar.gz`

**Destinazione:** cwd (stessa directory che contiene la cartella relazioni/).

**Verifica che il file non esista gia'** con Glob. Se esiste, aggiungi suffisso numerico: `relazioni-share-2.zip`, `-3`, ecc.

### 4.2 — Rileva OS corrente

```bash
case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*) OS_CORRENTE="windows" ;;
  Darwin)                OS_CORRENTE="macos" ;;
  *)                     OS_CORRENTE="linux" ;;
esac
```

### 4.3 — Comandi di compressione

| OS corrente | .zip | .tar.gz |
|---|---|---|
| **Windows (bash)** | `powershell.exe -NoProfile -Command "Compress-Archive -Path '<CARTELLA>' -DestinationPath '<OUTPUT>.zip' -Force"` | `tar -czf "<OUTPUT>.tar.gz" "<CARTELLA>"` |
| **macOS** | `zip -r "<OUTPUT>.zip" "<CARTELLA>"` | `tar -czf "<OUTPUT>.tar.gz" "<CARTELLA>"` |
| **Linux** | `zip -r "<OUTPUT>.zip" "<CARTELLA>"` | `tar -czf "<OUTPUT>.tar.gz" "<CARTELLA>"` |

**Su Linux**, se `zip` non e' disponibile e serve `.zip`, prova `tar -cf "<OUTPUT>.zip" --format=zip "<CARTELLA>"` come fallback. Se anche questo fallisce, segnala all'utente di installare `zip` (`sudo apt install zip`).

### 4.4 — Verifica

```bash
ls -lh "<OUTPUT>"
```

Se il file non esiste o ha dimensione 0, **segnala l'errore** e mostra stderr/stdout del comando di compressione. Non proseguire.

Salva la dimensione del file per il riepilogo finale.

## Step 5 — Apri file manager con il file selezionato

Rileva l'OS corrente (gia' determinato in Step 4.2) e apri il file manager:

| OS corrente | Comando |
|---|---|
| **Windows (bash)** | `explorer.exe /select,"$(cygpath -w "$(pwd)/<OUTPUT>")"` |
| **macOS** | `open -R "<OUTPUT>"` |
| **Linux** | `xdg-open "$(pwd)"` |

**Fallback Windows** (se `cygpath` non disponibile):
```bash
WINPATH=$(echo "$(pwd)/<OUTPUT>" | sed 's|^/\([a-z]\)/|\U\1:\\|' | sed 's|/|\\|g')
explorer.exe /select,"$WINPATH"
```

Se il comando di apertura fallisce (es. ambiente headless, SSH), comunica il percorso completo del file e suggerisci all'utente di aprirlo manualmente.

## Step 6 — Aggiorna state e mostra riepilogo

Aggiorna `session-state.json` aggiungendo il campo `shared`:

```json
{
  "shared": {
    "at": "<ISO-8601>",
    "format": "zip|tar.gz",
    "archive_name": "<nome file archivio>"
  }
}
```

Stampa il riepilogo finale:

> **Archivio creato:** `<OUTPUT>` (<dimensione>)
>
> File manager aperto con il file selezionato — condividilo come preferisci (email, cloud, USB, chat...).
>
> **Istruzioni per chi riceve:**
> 1. Estrarre l'archivio in una cartella di lavoro
> 2. Aprire Claude Code in quella cartella
> 3. Scrivere `/relazione` o `/relazione-continua`
> 4. La sessione verra' rilevata e ripresa automaticamente
>
> Stato sessione: `<current_step>` | Tipologia: `<tipologia>` | Target: `<lunghezza_target_pagine>` pagine

Se la dimensione dell'archivio supera 25 MB, aggiungi un avviso:

> **Nota:** l'archivio pesa piu' di 25 MB — potrebbe non essere inviabile via email. Considera un servizio cloud (OneDrive, Google Drive, WeTransfer) per la condivisione.

## Red Flags — STOP

- **Non comprimere file esterni** alla cartella relazioni/ selezionata — solo il suo contenuto
- **Non cancellare la cartella originale** dopo la compressione — e' ancora la copia di lavoro dell'utente
- **Non inventare il percorso** dell'archivio — verifica con `ls` che esista e abbia dimensione > 0
- **Non usare path Unix con `explorer.exe`** — converti SEMPRE con `cygpath -w` o il fallback sed
- **Non includere `node_modules/`, `.git/`, o altri artefatti** — ma questi non dovrebbero trovarsi dentro `relazioni*/` comunque
- Se la compressione fallisce (spazio disco, permessi, tool mancante), **mostra l'errore testuale** e non fingere che l'archivio esista
- **Non proseguire a Step 5** se Step 4.4 ha fallito

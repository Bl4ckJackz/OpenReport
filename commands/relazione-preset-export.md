---
description: Esporta un preset locale di /relazione come gist GitHub (pubblico/privato) o stdout, per condivisione
argument-hint: "<nome-preset> [--public|--private|--stdout]"
---

# /relazione-preset-export — Comando inverso di preset-import

Esporta un preset YAML da `~/.claude/skills/relazione/presets/<nome>.yaml` verso:
- **gist pubblico** (default se `gh` disponibile)
- **gist privato** (con `--private`)
- **stdout** (con `--stdout`, per copia-incolla manuale)

## Cosa fare

1. **Parse argomenti** da `$ARGUMENTS`:
   - Primo positional: `<nome-preset>` (obbligatorio)
   - Flag opzionale: `--public` (default), `--private`, `--stdout`
2. **Verifica esistenza** preset:
   ```bash
   PRESET="$HOME/.claude/skills/relazione/presets/${NAME}.yaml"
   test -f "$PRESET" || { echo "Preset $NAME non trovato. Usa 'ls ~/.claude/skills/relazione/presets/'."; exit 1; }
   ```
3. **Sanity-check pre-export** (no credenziali):
   ```bash
   if grep -E '(api[_-]?key|token|password|secret)' "$PRESET" >/dev/null 2>&1; then
     # AskUserQuestion: trovata stringa sospetta, proseguire?
   fi
   ```
4. **Esegui export**:

   ### Caso `--stdout`
   ```bash
   cat "$PRESET"
   ```
   Stampa anche un messaggio: "Copia il contenuto sopra e incollalo come `presets/<nome>.yaml` sul sistema di destinazione."

   ### Caso gist (default `--public`, o `--private`)
   Verifica che `gh` sia disponibile:
   ```bash
   command -v gh >/dev/null || { echo "Installa GitHub CLI: https://cli.github.com/"; exit 1; }
   gh auth status >/dev/null 2>&1 || { echo "Autentica gh: gh auth login"; exit 1; }
   ```
   Crea gist:
   ```bash
   FLAG="--public"
   [ "$VISIBILITY" = "private" ] && FLAG=""   # gh gist create senza flag = privato
   URL=$(gh gist create "$PRESET" $FLAG --desc "Preset /relazione: $NAME")
   ```
5. **Output finale**:
   > Preset `<nome>` esportato.
   > URL: <gist-url>
   >
   > Importazione su altra macchina:
   > `/relazione-preset-import <gist-url>`

## Red flags

- **Mai** esportare preset che contengono path assoluti utente (`/home/<user>/...`, `C:\Users\<user>\...`) — sostituisci con `~/` o avvisa
- **Mai** esportare se trovi pattern simili a credenziali — chiedi conferma esplicita
- **Mai** esportare senza prima validare il YAML (`python3 -c "import yaml; yaml.safe_load(open('<file>'))"`)
- Dimensione massima preset 100KB — preset non devono contenere dati, solo metadati

## Esempi

```
/relazione-preset-export status-report-weekly
→ gist pubblico, URL stampato

/relazione-preset-export mindsmart-tecnica --private
→ gist privato (solo accessibile via URL)

/relazione-preset-export bug-postmortem-rapido --stdout
→ stampa YAML, utente copia/incolla manualmente
```

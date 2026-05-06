# Profile presets system

I preset risparmiano le 9 domande iniziali quando hai pattern ricorrenti.

## Uso

```bash
/relazione --profile=mindsmart-tecnica
/relazione --profile=tesi-magistrale
```

La skill carica `presets/<nome>.yaml` e usa quei valori come risposte default. Salta lo Step 1 (questions) interamente o per i campi presenti. I campi mancanti vengono ancora chiesti.

## Schema preset YAML

```yaml
# presets/mindsmart-tecnica.yaml
profile_name: "Mindsmart — Relazione tecnica cliente"
description: "Default per relazioni tecniche di progetto consegnate ai clienti Mindsmart"
answers:
  tipologia: "tecnica"
  lingua: "italiano"
  stile: "semi-formale aziendale"
  destinatario: "cliente / committente"
  lunghezza_target_pagine: 25
  elementi_visivi: ["tabelle", "schemi", "grafici"]
  formato: "both"
  mock: "no-placeholder"
  ricerca_online: "online"
  classe_latex: "article"
  bibliografia: "biblatex"
cover_defaults:
  autore: "Dominik Duda"
  ente: "Mindsmart"
pdf_template: "mindsmart-eisvogel.yaml"  # vedi pdf-templates/
post_actions:
  - bundle
  - executive-summary
```

## Preset disponibili

Vedi cartella `presets/`:

- `mindsmart-tecnica.yaml`
- `tesi-magistrale.yaml`
- `progetto-aziendale.yaml`
- `bug-postmortem-rapido.yaml`
- `paper-ricerca-italiano.yaml`

L'utente può aggiungerne propri.

## Auto-detect dal nome cartella

Se l'utente non specifica `--profile`, prova auto-detect dal nome cwd:
- `tesi-*`, `thesis-*` → suggerisci `tesi-magistrale`
- `progetto-*`, `project-*` → suggerisci `progetto-aziendale`
- `bug-*`, `incident-*`, `postmortem-*` → suggerisci `bug-postmortem-rapido`
- `mindsmart-*` → suggerisci `mindsmart-tecnica`

`AskUserQuestion`:
> "Cartella suggerisce profilo `tesi-magistrale`. Uso questo o preferisci configurare manualmente?"

## Override singolo

Anche con preset attivo, l'utente può override singoli campi via flag:
```bash
/relazione --profile=mindsmart-tecnica --pages=50 --mock=si
```

I flag override il preset; campi non specificati restano dal preset; il resto viene chiesto.

## File-based answers

Alternativa al preset: utente edita `<output>/.session/answers.yaml` con tutte le risposte e poi lancia `/relazione`. La skill carica answers.yaml se presente.

Schema = stesso `answers:` block del preset.

Utile per lavoro non-interattivo: prepari il file in calma, poi fai partire la skill che esegue tutto in sequenza senza domande.

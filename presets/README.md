# Profile presets

Preset risparmiano le 9 domande iniziali con scelte pre-configurate.

## Uso

```bash
/relazione --profile=<nome>
/relazione-quick --profile=<nome>
```

## Schema

```yaml
profile_name: "Display name"
description: "Quando usarlo"
answers:                  # tutte le 9 risposte di Step 1
  tipologia: "..."
  lingua: "italiano|inglese"
  stile: "..."
  destinatario: "..."
  lunghezza_target_pagine: NN
  elementi_visivi: ["..."]
  formato: "md|latex|both"
  mock: "si-mock|no-placeholder"
  ricerca_online: "online|solo-locale"
  classe_latex: "..."     # solo se latex/both
  bibliografia: "..."     # solo se latex/both
cover_defaults:           # opzionale
  autore: "..."
  ente: "..."
pdf_template: "..."       # path a yaml in pdf-templates/
post_actions:             # companion artifacts da generare in Step 8
  - bundle
  - executive-summary
  - slides
```

## Preset inclusi

| File | Descrizione |
|---|---|
| `mindsmart-tecnica.yaml` | Relazione tecnica per cliente Mindsmart |
| `tesi-magistrale.yaml`   | Tesi magistrale italiana, latex+biblatex |
| `progetto-aziendale.yaml`| Progetto aziendale 30-50 pp, both |
| `bug-postmortem-rapido.yaml` | Post-mortem 5pp, md, no-online |
| `paper-ricerca-italiano.yaml` | Paper IMRaD per rivista italiana |

## Aggiungere preset

Crea `<nome>.yaml` in questa cartella. Schema sopra. Auto-discovered al prossimo `/relazione --profile=<nome>`.

## Override

Flag CLI hanno precedenza sul preset:
```bash
/relazione --profile=mindsmart-tecnica --pages=50 --mock
```

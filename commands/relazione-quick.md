---
description: Esegue /relazione saltando le 9 domande con default intelligenti basati sul contesto (auto-detect tipologia da nome cartella)
allowed-tools: Read, Glob, Bash, Write, Edit
---

# /relazione-quick — Modalità rapida senza domande

## Argomenti

`$ARGUMENTS` può contenere flag override:
- `--tipologia=<tipo>` — forza tipologia (default: auto-detect dal nome cartella)
- `--lang=it|en` (default: it)
- `--pages=<N>` (default: dipende dalla tipologia)
- `--format=md|latex|both` (default: md)
- `--mock` o `--no-mock` (default: --no-mock)
- `--online` o `--locale` (default: --online se tipologia accademica)
- `--profile=<nome>` — usa preset da `presets/<nome>.yaml`

## Comportamento

**Skip Step 1 (questions)** della skill /relazione. Compila `answers` automaticamente:

### Auto-detect tipologia dal nome cartella

| Pattern nome cwd | Tipologia |
|---|---|
| `tesi-*`, `thesis-*`, `dissertation-*` | `tesi` |
| `progetto-*`, `project-*` | `progetto` |
| `bug-*`, `incident-*`, `postmortem-*` | `bug` |
| `lab-*`, `laboratorio-*`, `experiment-*` | `laboratorio` |
| `stage-*`, `internship-*`, `tirocinio-*` | `stage` |
| `paper-*`, `research-*`, `ricerca-*` | `ricerca` |
| `relazione-*` | `progetto` (fallback) |
| `mindsmart-*` | profilo `mindsmart-tecnica` |
| altro | chiedi conferma con `AskUserQuestion` |

### Default per tipologia

```yaml
tesi:
  lingua: italiano
  stile: "formale accademico"
  destinatario: "commissione di laurea"
  pages: 80
  formato: latex
  mock: no-placeholder
  ricerca_online: online
  classe_latex: report
  bibliografia: biblatex

progetto:
  lingua: italiano
  stile: "semi-formale aziendale"
  destinatario: "committente"
  pages: 30
  formato: md
  mock: no-placeholder
  ricerca_online: online

tecnica:
  lingua: italiano
  stile: "tecnico divulgativo"
  destinatario: "team interno"
  pages: 15
  formato: md
  mock: no-placeholder
  ricerca_online: online

bug:
  lingua: italiano
  stile: "fattuale"
  destinatario: "team interno"
  pages: 5
  formato: md
  mock: no-placeholder
  ricerca_online: solo-locale
```

### Flusso

1. Auto-detect tipologia (o usa flag/preset)
2. Compila `answers` con default
3. Mostra all'utente le scelte fatte in 1 schermata + `AskUserQuestion`:
   > "Procedo con questi default? `[Conferma]` `[Modifica]` `[Annulla]`"
4. Se Conferma → vai direttamente a Step 2 (scan)
5. Se Modifica → mostra le 9 domande standard (ricade su flusso normale)
6. Resto del flusso identico a `/relazione` standard

## Esempi

```
$ cd /home/dom/tesi-magistrale-RAG-evaluation
$ /relazione-quick --pages=120

→ Auto-detect: tipologia=tesi (da prefisso "tesi-")
→ Lingua: italiano, Formato: latex, Pages: 120
→ Procedo? [Conferma]
→ [scan + draft + ...]
```

```
$ /relazione-quick --profile=mindsmart-tecnica

→ Carico preset presets/mindsmart-tecnica.yaml
→ Tipologia: tecnica, Stile: semi-formale aziendale, Pages: 25
→ Procedo? [Conferma]
```

## Note

- `--profile` ha precedenza su auto-detect.
- Flag CLI hanno precedenza sul preset.
- Se nessun match auto-detect, NON procede silenziosamente — chiede tipologia.

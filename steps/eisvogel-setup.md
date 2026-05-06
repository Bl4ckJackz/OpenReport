# Eisvogel — setup template pandoc per PDF moderno

Eisvogel è un template pandoc per produrre PDF stile business/report (title page grafica, TOC dedicato, header/footer, tabelle a righe alternate, code blocks stilizzati).

## Verifica presenza

```bash
pandoc -D eisvogel > /dev/null 2>&1 && echo OK || echo MISSING
```

## Installazione (una sola volta per macchina)

**Windows (PowerShell o Git Bash):**
```bash
mkdir -p "$APPDATA/pandoc/templates"
curl -L "https://raw.githubusercontent.com/Wandmalfarbe/pandoc-latex-template/master/eisvogel.latex" \
  -o "$APPDATA/pandoc/templates/eisvogel.latex"
```

**macOS/Linux:**
```bash
mkdir -p "$HOME/.pandoc/templates"
curl -L "https://raw.githubusercontent.com/Wandmalfarbe/pandoc-latex-template/master/eisvogel.latex" \
  -o "$HOME/.pandoc/templates/eisvogel.latex"
```

## YAML header per sfruttare Eisvogel

Inserire in testa al file `.md`:

```yaml
---
title: "Titolo Relazione"
subtitle: "Sottotitolo opzionale"
author: ["Nome Autore"]
date: "Data"
lang: it-IT
titlepage: true
titlepage-color: "1E3A8A"
titlepage-text-color: "FFFFFF"
titlepage-rule-color: "FFFFFF"
titlepage-rule-height: 2
toc: true
toc-own-page: true
colorlinks: true
linkcolor: NavyBlue
urlcolor: NavyBlue
citecolor: NavyBlue
listings: true
listings-disable-line-numbers: false
book: false
header-right: "\\hspace{1cm}"
footer-left: "Nome Relazione"
---
```

I parametri possono essere passati anche come `-V key=value` da CLI.

## Preset disponibili

Vedi `presets/` per YAML preconfigurati:
- `example-brand-tecnica.yaml` — brand Example Brand blu/azzurro
- `tesi-default.yaml` — sobrio, accademico ma colorato
- `progetto-aziendale.yaml` — corporate, neutro

Applica un preset prependendo il YAML al markdown:
```bash
cat presets/example-brand-tecnica.yaml RELAZIONE.md > RELAZIONE-eisvogel.md
pandoc RELAZIONE-eisvogel.md -o RELAZIONE.pdf --template=eisvogel ...
```

## Fallback senza Eisvogel

Se l'utente rifiuta l'install, look moderno con sole opzioni standard pandoc:

```yaml
---
documentclass: scrartcl
geometry: a4paper,margin=2cm
fontsize: 11pt
linestretch: 1.2
colorlinks: true
linkcolor: [RGB]{30,64,175}
urlcolor: [RGB]{30,64,175}
citecolor: [RGB]{30,64,175}
toc: true
numbersections: true
---
```

Non è perfetto ma evita install. Va in `RELAZIONE.pdf` con classe KOMA-Script (più curata di `article` default).

## Naming output (evita collisioni)

Quando si producono entrambi i PDF (formato `both`):
- PDF da markdown via Eisvogel → `RELAZIONE.pdf`
- PDF da LaTeX classico → `RELAZIONE-tex.pdf`

`xelatex` produce `<basename>.pdf` di default — **rinomina sempre** dopo compilazione tex per non sovrascrivere.

Compila prima il LaTeX (e rinomina), poi il markdown.

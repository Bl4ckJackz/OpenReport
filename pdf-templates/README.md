# PDF Templates

YAML preset per pandoc + Eisvogel template. Vengono prepended al markdown prima della compilazione.

## File

### Eisvogel YAML (per sorgente `.md`)

| File | Stile | `pdf_style` | Quando usarlo |
|---|---|---|---|
| `eisvogel-relazione.yaml` | Moderno colorato (blu+ambra, callout, tabelle alternate) | `moderno` | **Default** per progetti/stage/finale/tecnica/bug/esperienza |
| `eisvogel-example-brand.yaml` | Brand Example Brand (blu/cyan) | `brand` | Relazioni cliente con branding Example Brand |
| `eisvogel-default-it.yaml` | Default italiano sobrio | `accademico` | Generale quando serve stile neutro e formale |
| `eisvogel-tesi-modern.yaml` | Accademico modernizzato (navy+amber, KOMA-Script report) | `accademico` | Tesi/paper che vogliono un look meno "muro di testo" |

### LaTeX preamble (per sorgente `.tex`)

| File | Stile | `pdf_style` | Quando usarlo |
|---|---|---|---|
| `relazione-moderna-preamble.tex` | Moderno colorato (titlesec, tcolorbox, fancyhdr, minted) | `moderno` | Quando scrivi in LaTeX ma vuoi PDF da "relazione aziendale" anziché accademico B/N |

Inserire con `\input{preamble-moderna.tex}` subito dopo `\documentclass{...}`. Richiede compilazione con `xelatex --shell-escape` (per `minted`).

## Uso (manuale)

```bash
cd <output_folder>
cat <skill_dir>/pdf-templates/eisvogel-example-brand.yaml RELAZIONE.md > _temp.md
pandoc _temp.md -o RELAZIONE.pdf --template=eisvogel --pdf-engine=xelatex --listings
rm _temp.md
```

## Uso (automatico via post_actions del preset)

I preset in `presets/<name>.yaml` puntano a uno di questi file via campo `pdf_template`. La skill applica automaticamente in Step 7.

## Customizzare

Copia `eisvogel-example-brand.yaml` come base. Modifica:
- `titlepage-color`: colore HEX della title page
- `titlepage-rule-color`: colore della linea sottotitolo
- `header-includes`: per aggiungere logo (`\\logo{path/to/logo.png}`)
- `footer-left`/`footer-right`: testo footer pagine

## Eisvogel parametri completi

Vedi `~/.claude/skills/relazione/steps/eisvogel-setup.md` per setup template + lista parametri YAML disponibili.

Reference upstream: https://github.com/Wandmalfarbe/pandoc-latex-template

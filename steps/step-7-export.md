# Step 7 — Export to docx / pdf / compile LaTeX

Eseguito **dopo Step 6.7 (layout coherence)** ed esclusivamente se quel check è OK (no `force_overridden`).

## REGOLA FERMA — Output minimo garantito

| Output | Quando si produce | Stile |
|---|---|---|
| `RELAZIONE.docx` | **SEMPRE** (no eccezioni) | Moderno (mirror del PDF moderno) |
| `RELAZIONE.pdf` (modern) | **SEMPRE** | Moderno (eisvogel-relazione o brand) |
| `RELAZIONE.tex` | Se `formato ∈ {latex, both}` | Sorgente LaTeX |
| `RELAZIONE-tex.pdf` | Se `formato ∈ {latex, both}` | Accademico (classico) |

**Conseguenza:** quando `formato` include LaTeX, si producono **2 stili grafici differenti**:
- **Stile A — Accademico**: `RELAZIONE.tex` + `RELAZIONE-tex.pdf` (sobrio, serif, BibLaTeX, classe `article`/`report`/`book`)
- **Stile B — Moderno**: `RELAZIONE.docx` + `RELAZIONE.pdf` (eisvogel colorato, mirror reciproco, identica impaginazione)

DOCX è SEMPRE prodotto e DEVE rispecchiare il PDF moderno. La sorgente del DOCX e del PDF moderno è SEMPRE il markdown (anche se l'utente ha scelto `latex` puro: in quel caso pandoc converte `.tex → .md` come passaggio intermedio per generare il moderno + docx).

Nessuna domanda di "vuoi anche docx?" — il DOCX si produce sempre.

## Step 7.0 — Scelta del preset MODERNO (Stile B)

`pdf_style` (in `session-state.json.answers`) ora controlla **solo il preset dello stile moderno** (Stile B). Lo stile A (LaTeX) è sempre accademico per definizione.

**`AskUserQuestion`** con 2 opzioni:

1. **Moderno relazione** *(default)* — eisvogel-relazione (blu profondo + ambra), callout, tabelle a righe alternate, code highlight
2. **Brand aziendale** — preset custom (es. `eisvogel-example-brand.yaml`). Se nessun brand attivo, ricade su moderno

Valori in schema: `moderno` | `brand`. Il valore `accademico` resta consentito per retro-compatibilità ma è ridondante (lo Stile A copre già l'accademico).

### Default per tipologia (Stile B)

| Tipologia | Default Stile B |
|---|---|
| tesi, ricerca, stage accademico | moderno (oppure brand se attivo) |
| enterprise (proposta, sow, ...) | brand se attivo, altrimenti moderno |
| altre | moderno |

## Tabella riassuntiva degli output (REGOLA FERMA)

| Formato richiesto | DOCX | PDF moderno | LaTeX | LaTeX-PDF (acc.) | # stili |
|---|---|---|---|---|---|
| `md` | ✓ | ✓ | — | — | 1 |
| `latex` | ✓ (da pandoc tex→md→docx) | ✓ (da pandoc tex→md→pdf eisvogel) | ✓ | ✓ | **2** |
| `both` | ✓ (da md) | ✓ (da md) | ✓ | ✓ | **2** |

In tutte le righe DOCX e PDF moderno usano lo stesso `pdf_style` (Stile B) e devono apparire come "lo stesso documento in due formati". Il LaTeX-PDF è sempre accademico (Stile A).

**REGOLA NAMING:** PDF da LaTeX si chiama SEMPRE `RELAZIONE-tex.pdf` (anche se non c'è collisione, per chiarezza visiva).

**REGOLA COERENZA:** i due stili devono essere **visivamente distinguibili a colpo d'occhio**. Se Stile B viene sovrascritto in modalità sobria (es. brand grigio/serif), riallinea palette o avvisa l'utente — mai due output identici.

## Step 7.1 — Setup preamble moderno per LaTeX

Se `pdf_style == "moderno"` e sorgente è `.tex`:

1. Copia `<skill_dir>/pdf-templates/relazione-moderna-preamble.tex` nella cartella di output (come `preamble-moderna.tex`)
2. Verifica che `RELAZIONE.tex` includa `\input{preamble-moderna.tex}` **subito dopo** `\documentclass{...}`. Se assente, inseriscilo.
3. Verifica presenza pacchetti richiesti in MiKTeX/TeXLive: `titlesec`, `tcolorbox`, `fancyhdr`, `minted`, `xcolor`, `colortbl`, `booktabs`, `enumitem`, `caption`. MiKTeX auto-installa, TeXLive potrebbe richiedere `tlmgr install`.
4. Compila con `--shell-escape` (richiesto da `minted`).

## Dipendenze richieste

| Azione | Tool | Verifica |
|---|---|---|
| docx/pdf da markdown | `pandoc` | `pandoc --version` |
| pdf via xelatex | `xelatex` (MiKTeX/TeXLive) | `xelatex --version` |
| PDF moderno Eisvogel | template Eisvogel | `pandoc -D eisvogel > /dev/null 2>&1 && echo OK` |
| Mermaid in pdf/docx | `mermaid-filter` (npm) + Node | `mermaid-filter --version` |
| Bibliografia BibTeX | `bibtex` | `bibtex --version` |
| Bibliografia biblatex | `biber` | `biber --version` |
| Code colorato minted | Python + Pygments + `xelatex --shell-escape` | `pygmentize -V` |
| Grafici `pgfplots` | pacchetto LaTeX | auto-install in MiKTeX |
| `.md` → `.tex` | `pandoc` | `pandoc --version` |

## Procedura mancante dipendenze

1. Elenca tool mancanti + ragione (1 riga ciascuno)
2. `AskUserQuestion` con 3 opzioni:
   - `Installa tutto ora` (autorizza esecuzione comandi)
   - `Solo alternative online/manuali`
   - `Salta export, lascia .md/.tex`
3. Se autorizzato install (Windows con winget):

```bash
winget install --id JohnMacFarlane.Pandoc --accept-source-agreements --accept-package-agreements
winget install --id MiKTeX.MiKTeX --accept-source-agreements --accept-package-agreements
winget install --id OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements
npm install -g mermaid-filter
winget install --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements && pip install --upgrade Pygments
```

4. Dopo ogni `winget install`: verifica con il comando di check. Se PATH stale → avvisa utente di riaprire terminale, salva state, termina.
5. Aggiorna `session-state.json` `deps_installed`.

## Comandi di conversione

**IMPORTANTE:** tutti dentro la cartella di output (`cd <DIR>`). Sostituisci `<DIR>` col path effettivo.

### Da Markdown

```bash
cd <DIR>

# md → docx (semplice)
pandoc RELAZIONE.md -o RELAZIONE.docx --toc

# md → docx con Mermaid
pandoc RELAZIONE.md -o RELAZIONE.docx --toc --filter mermaid-filter

# md → pdf MODERNO COLORATO (eisvogel-relazione preset) — pdf_style="moderno"
# Prepone il YAML al sorgente per configurare palette/callout/titoli colorati.
cat <skill_dir>/pdf-templates/eisvogel-relazione.yaml RELAZIONE.md > _temp.md
pandoc _temp.md -o RELAZIONE.pdf --toc --pdf-engine=xelatex \
  --template=eisvogel --listings --filter mermaid-filter \
  --bibliography=references.bib --citeproc
rm _temp.md

# md → pdf ACCADEMICO SOBRIO (eisvogel-default-it o eisvogel-tesi-modern) — pdf_style="accademico"
cat <skill_dir>/pdf-templates/eisvogel-default-it.yaml RELAZIONE.md > _temp.md
pandoc _temp.md -o RELAZIONE.pdf --toc --pdf-engine=xelatex \
  --template=eisvogel --listings --filter mermaid-filter \
  --bibliography=references.bib --citeproc
rm _temp.md

# md → pdf BRAND AZIENDALE (eisvogel-example-brand o preset utente) — pdf_style="brand"
cat <skill_dir>/pdf-templates/eisvogel-example-brand.yaml RELAZIONE.md > _temp.md
pandoc _temp.md -o RELAZIONE.pdf --toc --pdf-engine=xelatex \
  --template=eisvogel --listings --filter mermaid-filter \
  --bibliography=references.bib --citeproc
rm _temp.md

# md → pdf fallback senza Eisvogel
pandoc RELAZIONE.md -o RELAZIONE.pdf --toc --pdf-engine=xelatex \
  -V documentclass=scrartcl -V geometry:margin=2cm -V colorlinks \
  --filter mermaid-filter --bibliography=references.bib --citeproc

# md → tex (per "both" via pandoc)
pandoc RELAZIONE.md -o RELAZIONE.tex --standalone

# md → EPUB (lettura tablet/Kindle)
pandoc RELAZIONE.md -o RELAZIONE.epub --toc --metadata title="Titolo" --metadata author="Autore"
```

### Da LaTeX (BibTeX classico)

```bash
cd <DIR>
xelatex RELAZIONE.tex
bibtex RELAZIONE
xelatex RELAZIONE.tex
xelatex RELAZIONE.tex
mv RELAZIONE.pdf RELAZIONE-tex.pdf  # sempre!
```

### Da LaTeX (biblatex + biber)

```bash
cd <DIR>
xelatex RELAZIONE.tex
biber RELAZIONE
xelatex RELAZIONE.tex
xelatex RELAZIONE.tex
mv RELAZIONE.pdf RELAZIONE-tex.pdf
```

### Con minted (code colorato)

```bash
cd <DIR>
xelatex --shell-escape RELAZIONE.tex
```

### Da LaTeX con preamble moderno colorato (`pdf_style="moderno"`)

```bash
cd <DIR>
cp <skill_dir>/pdf-templates/relazione-moderna-preamble.tex preamble-moderna.tex
# Assicurati che RELAZIONE.tex abbia \input{preamble-moderna.tex} dopo \documentclass
xelatex --shell-escape RELAZIONE.tex
biber RELAZIONE    # oppure bibtex se BibTeX classico
xelatex --shell-escape RELAZIONE.tex
xelatex --shell-escape RELAZIONE.tex
mv RELAZIONE.pdf RELAZIONE-tex.pdf
```

## Sequenza canonica di build (eseguila SEMPRE in questo ordine)

Indipendentemente da `formato` scelto, segui questa pipeline. Salta solo gli step che non si applicano.

```
0. Verifica pre-condizioni:
   - Step 6.7 layout-coherence → fail_count == 0 e force_overridden == false
   - Step 6.5 PII/secret → OK
   - Self-check → 0 FAIL
   Altrimenti: ABORT, non produrre nulla.

1. Se formato == "latex": pandoc tex→md (intermediate)
   pandoc RELAZIONE.tex -o _modern_source.md --wrap=preserve

   Se formato == "md" o "both": _modern_source.md = RELAZIONE.md (link)

2. STILE B — DOCX (SEMPRE)
   pandoc <_modern_source> -o RELAZIONE.docx --toc --reference-doc=<brand-docx-template>

3. STILE B — PDF moderno (SEMPRE)
   cat <preset-yaml> <_modern_source> > _temp.md
   pandoc _temp.md -o RELAZIONE.pdf --toc --pdf-engine=xelatex \
     --template=eisvogel --listings --filter mermaid-filter \
     --bibliography=references.bib --citeproc
   rm _temp.md

4. STILE A — LaTeX-PDF accademico (solo se formato ∈ {latex, both})
   cd <DIR>
   xelatex --shell-escape RELAZIONE.tex
   biber RELAZIONE  # o bibtex se classico
   xelatex --shell-escape RELAZIONE.tex
   xelatex --shell-escape RELAZIONE.tex
   mv RELAZIONE.pdf RELAZIONE-tex.pdf   # IMMEDIATAMENTE per evitare collisione

5. Verifica finale:
   - RELAZIONE.docx esiste, size > 5 KB
   - RELAZIONE.pdf esiste, size > 5 KB
   - Se applicabile: RELAZIONE.tex e RELAZIONE-tex.pdf esistono
   - Diff visivo: hash dei thumbnail prima pagina di RELAZIONE.pdf vs RELAZIONE-tex.pdf
     deve essere DIVERSO (i 2 stili devono essere distinguibili)
```

**Mai sovrascrivere `RELAZIONE.pdf` con il PDF di LaTeX** — rinomina subito (step 4).

**Sequenza specifica per ogni formato:**

| Formato | Step eseguiti | File finali |
|---|---|---|
| `md` | 0, 2, 3 | `.md`, `.docx`, `.pdf` (moderno) |
| `latex` | 0, 1, 2, 3, 4 | `.tex`, `.docx`, `.pdf` (moderno), `-tex.pdf` (accademico) |
| `both` | 0, 2, 3, 4 | `.md`, `.tex`, `.docx`, `.pdf` (moderno), `-tex.pdf` (accademico) |

## Verifica post-compilazione

Dopo ogni comando:
- Verifica file output esiste e size > 0
- Se errore: leggi `RELAZIONE.log` (LaTeX) o stderr (pandoc)
- Mostra errore esatto all'utente
- **Mai claimare successo se non lo è**

## Companion artifacts (Step 8)

Vedi `steps/step-8-companion-artifacts.md` per:
- Slide deck (Marp/Beamer) dallo stesso sorgente
- Executive summary 1-pagina
- Bundle `.zip` finale
- Defense pack (per tesi)

## Riepilogo finale

`ls -la <DIR>` per mostrare contenuto finale.

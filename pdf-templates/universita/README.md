# Template tesi università italiane

Frontespizi LaTeX conformi (per quanto noto pubblicamente) ai regolamenti delle principali università italiane.

**Disclaimer:** I template sono basati su layout pubblici e indicazioni regolamentari note al 2026. Verifica sempre con la segreteria/dipartimento di destinazione prima della consegna — i regolamenti cambiano e ogni dipartimento può avere variazioni interne.

## File inclusi

| File | Università | Tipologia |
|---|---|---|
| `polimi-tesi.tex` | Politecnico di Milano | Triennale/magistrale/dottorato |
| `polito-tesi.tex` | Politecnico di Torino | Triennale/magistrale |
| `sapienza-tesi.tex` | Sapienza Università di Roma | Triennale/magistrale/dottorato |
| `bocconi-tesi.tex` | Università Bocconi | Triennale/magistrale |
| `unina-tesi.tex` | Università Federico II di Napoli | Triennale/magistrale |
| `unibo-tesi.tex` | Alma Mater Studiorum Università di Bologna | Triennale/magistrale/dottorato |

## Uso

1. Copia il file `<univ>-tesi.tex` nella cartella di output della tesi (rinomina in `TESI.tex` se vuoi)
2. Sostituisci tutti i placeholder marcati `[...]` con i tuoi dati
3. Aggiungi `\usepackage{...}` extra se servono (graphicx, hyperref, listings, ecc.)
4. Aggiungi sezioni dopo `\maketitle` / `\frontespizio`
5. Compila con `xelatex TESI.tex && biber TESI && xelatex TESI.tex && xelatex TESI.tex`

## Logo

Ogni template referenzia `logo.pdf` o `logo.png` nella stessa cartella. Scarica il logo ufficiale del tuo ateneo dal sito brand/identità visiva e mettilo accanto al `.tex`.

## Personalizzazione

Tutti i campi tra `[...]` sono placeholder. Cerca con grep:
```bash
grep -nE "\[[^]]+\]" <univ>-tesi.tex
```

Per font specifici richiesti dall'ateneo, aggiungi nel preamble:
```latex
\usepackage{fontspec}
\setmainfont{Times New Roman}      % o quanto richiesto
```

# Step — Multi-lingua parallelo (IT + EN)

Usato quando l'utente sceglie `answers.lingua = "italiano+inglese"` in Step 1.

## Flow

1. **Step 1 — domanda lingua** estesa con `italiano+inglese` (richiede Step-7 bilingual-generator).
2. **Step 2-4** — genera sezioni IT prima (lingua primaria), poi EN come traduzione.
   - Dopo ogni sezione IT, genera versione EN nello stesso turn
   - Mantieni glossario in `.session/glossary.json` per coerenza term tecnici
3. **Step 4.5 self-check** — esegui su entrambi i file (`--lang=it` poi `--lang=en`)
4. **Step 6 output**:
   - `RELAZIONE-it.md` (primary)
   - `RELAZIONE-en.md` (secondary)
   - `.session/glossary.json` (termini tecnici condivisi)
5. **Step 7 export**:
   - 2 PDF separati: `RELAZIONE-it.pdf`, `RELAZIONE-en.pdf`
   - (Opzionale) bilingual side-by-side: `scripts/generators/bilingual-generator.py --mode split-page`
   - (Opzionale) bilingual sequential: sezione IT + EN alternate in un solo doc

## Regole

1. **Glossario term tecnici**: identifica term ricorrenti in Step 3.5 research, mantieni mapping IT↔EN in `.session/glossary.json`. Riapplicalo in ogni refinement.
2. **Citazioni e fonti**: identiche in entrambe le lingue (stesso .bib).
3. **Figure e tabelle**: stesse immagini, caption tradotte. Numerazione coerente.
4. **Unità di misura e formattazione numeri**:
   - IT: `1.234,56 €` (punto migliaia, virgola decimali, simbolo dopo)
   - EN: `$1,234.56` o `1,234.56 EUR` (virgola migliaia, punto decimali, simbolo prima per USD/GBP)
5. **Date**:
   - IT: `17 aprile 2026` o `17/04/2026`
   - EN: `April 17, 2026` o `2026-04-17` (ISO)
6. **Non tradurre automaticamente con traduzione black-box**: rigenera ogni sezione nella target language, non tradurre frase-per-frase.
7. **Voice profile separato**: `voice_profile_it` + `voice_profile_en` in state se long-form.

## Quando usare split-page vs sequential

- **split-page** (LaTeX minipage side-by-side) → contratti, doc legali, quick reference bilingue. Richiede landscape A4.
- **sequential** (MD/tex con IT seguito da EN) → whitepaper, case study, material marketing internazionale. Portrait A4, più leggibile su mobile.

## Integrazioni

- `resolve-variables.py` applicato a entrambi i file (stesse variabili)
- `forbidden-check.sh` eseguito con `--lang=it` su IT, `--lang=en` su EN (tells diverse)
- `readability.py`: Gulpease per IT, Flesch per EN
- `cross-ref-lint.py`: label/cite keys devono essere identici in entrambi

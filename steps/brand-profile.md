# Brand Profile — uso all'interno della skill

Il brand profile (`.brand-profile.json`) è il contenitore di identità aziendale: logo, colori, font, claim, glossario, banned/preferred words, boilerplate, classification default.

## Quando viene caricato

1. **Step 1** — se l'utente sceglie tipologia enterprise, offri "Usa brand profile attivo?" come prima domanda (vedi `steps/cover-control.md`).
2. **Step 6** — cover page include logo e ragione sociale da brand.
3. **Step 7** — se `pdf_style=brand`, genera `eisvogel-brand.yaml` dinamicamente con `scripts/brand-to-eisvogel.py`.
4. **Step 4.5** — self-check estende forbidden-check con `--brand=<nome>` per includere banned_words aziendali.
5. **Refinement Step 5** — `apply_preferred_terms` può essere invocato per sostituire termini generici con quelli aziendali.

## Multi-brand

Il file supporta più brand in `brands[]`. `active_brand` indica quale è il default. Altri brand accessibili via `--brand=<nome>`.

Esempio use case: consulente che lavora per 3 clienti, ciascuno con proprio stile. Un solo `.brand-profile.json`, tre voci in `brands[]`, switch via CLI.

## Utility

| Script | Scopo |
|---|---|
| `scripts/brand-loader.py --list` | Elenca brand disponibili |
| `scripts/brand-loader.py --info --brand <nome>` | Dump JSON del brand |
| `scripts/brand-loader.py --apply-preferred-terms <file> --brand <nome> --in-place` | Sostituisce termini generici → aziendali |
| `scripts/brand-loader.py --banned-words --brand <nome>` | Lista banned words (una per riga) |
| `scripts/brand-to-eisvogel.py --brand <nome> -o eisvogel-auto.yaml` | Genera preset eisvogel da brand |
| `scripts/forbidden-check.sh <file> --brand <nome>` | Self-check esteso con banned words brand |

## Comando interattivo

`/relazione-brand` — wizard interattivo per setup/edit brand profile (vedi `~/.claude/commands/relazione-brand.md`).

## Regole

1. **Un brand può essere `public`** (whitepaper, case study) o **`internal`/`confidential`/`restricted`** (proposte, SOW, audit). Il brand definisce il default via `classification_default`, l'utente può override.
2. **Logo path deve esistere** — se specificato ma file mancante, warn in Step 7 e chiedi come procedere.
3. **Palette hex validate** contro regex `^#[0-9a-fA-F]{6}$` dal schema JSON.
4. **preferred_terms case-insensitive in match**, case-preserving in output (`Customer` → `Cliente`, `customer` → `cliente`).
5. **boilerplate paths relativi o assoluti** — risolvibili da `resolve-variables.py` come blocchi di testo citati.

## Integrazione con user profile

Se entrambi presenti, le regole si sommano:
- `banned_words` = union(user, brand)
- `preferred_terms` = merge(user, brand) con brand priority
- `voice_profile` = user profile (il brand non vincola voice)
- `formato_default` = user profile
- `classificazione_default` = brand profile

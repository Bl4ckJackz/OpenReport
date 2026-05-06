# Scan agent: ASSETS (facet HOW-SHOWN)

Leggi i file della tua lista ed estrai **asset visivi o strutturati**: immagini, tabelle, schemi DB, code block significativi.

Segui `scan-agents/_common.md` per regole comuni.

## Scope

### Type ammessi

| Type | Cosa estrarre | Esempio `name` |
|---|---|---|
| `image` | File immagine (`.png`, `.jpg`, `.svg`, `.pdf` figura singola) | `"architettura-microservizi-png"` |
| `table` | Tabella markdown/LaTeX/CSV rilevante | `"confronto-performance"` |
| `code_block` | Blocco codice citabile nel draft (algo chiave, non tutto il codice) | `"algoritmo-auth-flow"` |
| `schema` | Schema DB (`schema.prisma`, SQL DDL), schema JSON | `"schema-db-users"` |
| `figure` | Figura complessa composita (gruppo di immagini) | `"dashboard-screens"` |

### Attributi per type

- `image.attrs`: `{path: str, format: "png|jpg|svg|pdf|webp", dims_px: [w,h]|null, dpi: int|null, caption_hint: str, quality: "high|medium|low|unknown"}`
  - dims_px/dpi: prova da filename (`1920x1080`, `@300dpi`) o metadata facilmente ricavabile; null se ignoto
  - quality: `high` se dpi ≥ 150, `medium` se 72-149, `low` se < 72, `unknown` altrimenti
- `table.attrs`: `{file: str, rows: int, cols: int, caption: str|null, has_header: bool}`
- `code_block.attrs`: `{file: str, language: str, lines: [start, end], summary: str}`
- `schema.attrs`: `{file: str, format: "prisma|sql|json-schema|protobuf|openapi", entity_count: int, can_diagram: bool}`
  - `can_diagram: true` se `scripts/intel/schema-to-diagram.py` può generare ER
- `figure.attrs`: `{component_image_ids: [entity_id, ...], suggested_layout: "grid|row|column"}`

### Fuori scope (NON emettere)

- Asset temporanei / generati (thumbnail cache, `.next/`, `dist/`) → IGNORA
- Logo/branding se già nel titlepage → IGNORA
- Testo dei documenti → facet **narrative**
- Persone/firme → facet **entities**

## Priorità lettura

1. Cartelle `img/`, `images/`, `assets/`, `figures/`, `screenshots/`
2. PDF che sembrano figure singole (non documenti interi)
3. `schema.prisma`, `*.sql` DDL, `*.json-schema`
4. Code block dentro `.md` o `.tex` con `language` specificato

## Caption hint

Per ogni immagine, deduce un caption hint da:
1. Nome file (`architettura-microservizi.png` → `"Architettura dei microservizi"`)
2. Riga prima della referenza `![alt](path)` nel markdown (se esiste)
3. Alt text se non generico
4. Directory parent se informativa (`img/architettura/` + `overview.png` → `"Overview architettura"`)

Se nessuna fonte è affidabile: `caption_hint: ""` e `section_hint_confidence: 0`.

## Quality check per immagini

| dpi | quality | Note |
|---|---|---|
| ≥ 300 | high | Print-ready |
| 150-299 | high | Adeguata stampa |
| 72-149 | medium | Schermo ok, stampa marginale |
| < 72 | low | Flag `da-verificare` + nota in `extras.quality_warning` |
| unknown | unknown | Non flaggare, ma suggerisci verifica in Step 5 |

## Output target

- Image: tutte quelle rilevanti (evita duplicati per path)
- Table: solo quelle con contenuto (skippa tabelle vuote)
- Code block: 0-10 (molto selettivo — solo algoritmi chiave)
- Schema: tutti (sono pochi e importanti)
- Figure: solo se composizione è esplicita

## Section hint suggerito

| Type/contenuto | Sezione probabile |
|---|---|
| image architettura/diagramma | `architettura` |
| image screenshot UI | `implementazione`, `risultati` |
| image grafico dati | `risultati`, `analisi` |
| table confronto | `risultati`, `discussione` |
| schema DB | `architettura`, `modello-dati` |
| code_block algoritmo | `metodologia`, `implementazione` |

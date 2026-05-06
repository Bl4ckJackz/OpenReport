# Step 2-parallel — Deep scan via 4 parallel subagents (scan_mode=profondo-parallelo)

Alternativa a Step 2 single-pass. Attivata quando `answers.scan_mode == "profondo-parallelo"` o auto-suggerita se file scansionabili > 15 o dimensione totale > 500 KB.

Produce una **hybrid store** normalizzata in `.session/scan/`:
- `entities.jsonl` — source of truth (una riga per entity, append-only)
- `index/{by-facet,by-file,by-section,by-date}.json` — indici derivati per lookup O(1)
- `graph.json` — archi tipizzati (provenance + relazioni)
- `merge_candidates.json` — match fuzzy non risolti, review umana in Step 5
- `scan-summary.md` — overview human-readable
- `scan-tree-meta.json` — metadati top-level validati contro `schemas/scan-tree.schema.json`

## Quando usarlo

| Condizione | Azione |
|---|---|
| `answers.scan_mode == "profondo-parallelo"` | Esegui |
| File scansionabili > 15 **e** `scan_mode` non definito | AskUserQuestion suggerisci upgrade |
| File scansionabili < 15 **e** entità stimate < 20 | Fallback a Step 2 single-pass |
| Cartella vuota o irrilevante | Stessa gestione Step 2 standard |

## Architettura (parallel fan-out + merge)

```dot
digraph step2_parallel {
  orchestrator [shape=box, label="Orchestrator (main)\nglob → partition → dispatch"];
  a1 [shape=box, label="Agent: Narrative\nWHAT — topic, tech, excerpts"];
  a2 [shape=box, label="Agent: Entities\nWHO — person, email, org, url"];
  a3 [shape=box, label="Agent: Temporal\nWHEN — date, task, milestone"];
  a4 [shape=box, label="Agent: Assets\nHOW-SHOWN — image, table, code, schema"];
  merge [shape=box, label="Merge + dedup\ncross-agent entity resolution"];
  indexes [shape=box, label="Build indexes\nby-facet/file/section/date"];
  graph [shape=box, label="Build graph\ntyped edges with weights"];
  validate [shape=diamond, label="Round-trip check\n(bloccante su FAIL)"];
  out [shape=doublecircle, label=".session/scan/ + state"];

  orchestrator -> a1;
  orchestrator -> a2;
  orchestrator -> a3;
  orchestrator -> a4;
  a1 -> merge;
  a2 -> merge;
  a3 -> merge;
  a4 -> merge;
  merge -> indexes;
  merge -> graph;
  indexes -> validate;
  graph -> validate;
  validate -> out [label="OK"];
  validate -> merge [label="FAIL → re-merge"];
}
```

## Protocollo

### 2-par.1 — Partition file

Glob escludendo le directory standard (`node_modules`, `.git`, `dist`, build, `__pycache__`, `venv`, etc.). Classifica ogni file per **lead facet**:

| Pattern file | Lead facet | Note |
|---|---|---|
| `*.md`, `*.txt`, `*.tex`, `README*`, `CHANGELOG*` | narrative + temporal | Narrativa legge; temporal scansiona date |
| `package.json`, `*.toml`, `requirements*.txt`, `Gemfile`, `go.mod` | narrative | Tech stack |
| `mail*`, `*.eml`, `contacts*`, `AUTHORS*`, `CODEOWNERS*` | entities | Contatti espliciti |
| `TODO*`, `ROADMAP*`, `*.todo`, issues dumps, frontmatter con date | temporal | Task & milestone |
| `*.png`, `*.jpg`, `*.svg`, `*.pdf` (figure) | assets | Image inventory |
| `*.prisma`, `schema.sql`, `*.sql` DDL | assets | Schema extraction |
| `*.py`, `*.js`, `*.ts`, `*.go`, etc. | narrative + assets | Narrativa per topic; assets per code blocks significativi |

Ogni file finisce in **almeno 1** lista. La lista `narrative` riceve tutto, ma con hint di priorità.

### 2-par.2 — Dispatch 4 subagents (parallelo)

Usa `Agent` tool, `subagent_type: Explore`, con **un solo messaggio con 4 tool_use in parallelo**. Ogni agente riceve:

- Prompt template da `steps/scan-agents/<facet>.md`
- Lista file di pertinenza
- Schema JSON Schema di output (`$defs/entity` da `scan-tree.schema.json`)
- Path di scrittura: `.session/scan/raw/<facet>.jsonl`
- Budget: max 20k tokens input, max 3k tokens output

Output atteso per ogni agente: JSONL con una entity per riga, conforme a `$defs/entity`, campo `provenance[0].agent == "<facet>"`.

**Regole agenti (comuni):**
1. Mai inventare. Solo ciò che esiste nei file.
2. `raw_string` obbligatorio in ogni mention (testo originale, non normalizzato).
3. Confidence ≤ 0.75 se single-source.
4. Flag `da-verificare` su confidence < 0.6.
5. Usa `extras{}` per campi non previsti invece di droppare.

### 2-par.3 — Merge + entity resolution

Orchestratore legge i 4 `.jsonl` e produce `entities.jsonl` unico.

**Regole merge (conservativo):**

1. **Match esatto** (post-normalizzazione lowercase + strip diacritics + punctuation):
   - Stesso `type` + stesso `name` normalizzato → merge automatico
   - Unisci `mentions[]` (concatenation)
   - Unisci `provenance[]` (concatenation)
   - Confidence ricalcolata: `1 - Π(1 - ci)` su tutte le provenance
   - Mantieni il primo `id` cronologicamente

2. **Match fuzzy** (edit distance ≤ 2 su name normalizzato, o sottostringa):
   - NON merge automatico
   - Aggiungi in `merge_candidates.json` con entrambi gli ID + similarity score
   - Flag `merge-candidate` su entrambi
   - Review umana in Step 5 (`AskUserQuestion` sui candidati)

3. **Nessun match** → nuova entity con ID generato: `<facet>:<slug(name)>[:<disambiguator>]`

**Non-negotiable:**
- Mai cancellare mentions[] o provenance[] durante merge
- Mai sovrascrivere raw_string (append-only in mentions)
- Mai dedurre relazioni non esplicite nei file

### 2-par.4 — Build indexes (derivati)

Da `entities.jsonl` genera 4 file in `.session/scan/index/`:

```json
// by-facet.json
{
  "narrative": ["narrative:topic-auth-flow", "narrative:tech-nextjs", ...],
  "entities":  ["entities:person-marco-rossi", ...],
  "temporal":  ["temporal:event-2025-03-14", ...],
  "assets":    ["assets:image-architecture-png", ...]
}

// by-file.json
{
  "src/auth/login.ts": ["narrative:topic-auth-flow", "assets:code-login-ts"],
  "README.md":         ["narrative:tech-nextjs", ...]
}

// by-section.json (raggruppato per section_hint)
{
  "architettura":    ["narrative:topic-auth-flow", "assets:image-architecture-png"],
  "cronologia":      ["temporal:event-2025-03-14"],
  "ringraziamenti":  ["entities:person-marco-rossi"]
}

// by-date.json (solo temporal entities)
{
  "2025-03-14": ["temporal:event-2025-03-14", "temporal:task-deploy-auth"]
}
```

Indexes sono **rigenerabili** da entities.jsonl. Se si corrompono → rebuild, non perdita dati.

### 2-par.5 — Build graph

`.session/scan/graph.json`:

```json
{
  "nodes_ref": "entities.jsonl",
  "edges": [
    {"from_id": "entities:person-marco-rossi", "to_id": "narrative:topic-auth-flow", "rel": "authored_by", "weight": 0.9},
    {"from_id": "temporal:event-2025-03-14", "to_id": "narrative:topic-deploy", "rel": "occurred_on", "weight": 1.0},
    {"from_id": "assets:image-architecture-png", "to_id": "narrative:topic-auth-flow", "rel": "shown_in", "weight": 1.0}
  ]
}
```

Relazioni derivate solo da co-occurrenze esplicite nei file (stesso file + prossimità). Mai inferite.

### 2-par.6 — Round-trip check (bloccante)

Esegui:

```bash
bash scripts/scan-rebuild-check.sh .session/scan/
```

Lo script:
1. Legge i 4 raw `.jsonl` degli agenti
2. Legge `entities.jsonl` merged
3. Per ogni raw entry, verifica che esista in merged o sia fusa in un merge-candidate documentato
4. Verifica che tutte le `mentions[].raw_string` raw siano preservate nel merged
5. Verifica che gli indici puntino solo a ID esistenti
6. Exit 0 = OK, exit 1 = FAIL con diff

**Se FAIL:** blocca, mostra diff all'utente, proponi rerun merge con soglia più conservativa.

**Se OK:** setta `meta.round_trip_ok = true` in `scan-tree-meta.json`.

### 2-par.7 — Write scan-summary.md

Sintesi human-readable in `.session/scan/scan-summary.md`:

```markdown
# Scan summary

## Meta
- Files scanned: 42
- Entities total: 58
- Mode: profondo-parallelo
- Round-trip: OK
- Confidence avg: 0.83
- Low-confidence flagged: 4

## By facet
- Narrative: 18 (topic: 7, glossary: 4, tech: 5, excerpts: 2)
- Entities: 14 (person: 6, email: 4, org: 2, url: 2)
- Temporal: 19 (event: 9, task: 8, milestone: 2)
- Assets: 7 (image: 4, table: 1, schema: 2)

## Low confidence — DA VERIFICARE
- `temporal:event-fine-febbraio` (0.52) — data vaga in CHANGELOG.md:17
- `entities:person-m-rossi` (0.58) — possibile duplicato di `person-marco-rossi`
...

## Merge candidates (review in Step 5)
- `entities:person-m-rossi` ↔ `entities:person-marco-rossi` (similarity 0.87)
```

### 2-par.8 — Aggiorna state

In `session-state.json`:
- `current_step`: `step-2.5-persist`
- `token_budget.tokens_subagents`: somma
- `answers.scan_mode`: conferma
- Append a `files_written`: tutti i file sotto `.session/scan/`

## Lookup API (usata da Step 4 e 5)

Durante draft/refine, l'orchestratore usa pattern:

```
# Per sezione
entries = read(index/by-section.json)["architettura"]
entities = [read_jsonl(entities.jsonl, id=e) for e in entries]

# Per data
events = read(index/by-date.json)["2025-03-14"]

# Per persona (via graph)
edges = [e for e in graph.edges if e.from_id == "entities:person-marco-rossi"]
related = [e.to_id for e in edges]
```

Questo evita di ricaricare i file sorgente in main context.

## Failure modes & mitigations

| Failure | Mitigazione |
|---|---|
| Subagent crash durante scan | Retry max 2 volte, poi fallback a Step 2 single-pass per quel facet |
| Merge conflict (stesso ID fra agenti diversi) | Auto-disambiguator suffix: `:agent-<name>` |
| Round-trip check FAIL | Blocca, mostra diff, re-merge con soglia più conservativa |
| Tokens subagent > budget | Sample files per priority (README/docs prima), avvisa utente |
| entities.jsonl corrotto | Backup pre-merge in `.session/backups/{ISO}-pre-merge/`; rollback |

## Token budget atteso

Per 40 file / 50 entità (relazione tipo progetto/stage):
- Subagenti (isolato): ~110-130k tokens totali (parallelo)
- Main (merge + index + graph): ~15-20k tokens
- Step 4/5 riutilizzo: ~5-10k per sezione/refine invece di re-read

Vedi `docs/SKILL-GUIDE.md` per confronto quantitativo vs scan single-pass.

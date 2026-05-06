# Scan agent: TEMPORAL (facet WHEN)

Leggi i file della tua lista ed estrai **cosa è successo quando**: date, scadenze, milestone, task (open/done), cronologia.

Segui `scan-agents/_common.md` per regole comuni.

## Scope

### Type ammessi

| Type | Cosa estrarre | Esempio `name` |
|---|---|---|
| `event` | Evento datato (meeting, deploy, inizio/fine attività) | `"deploy-auth-service"` |
| `task` | Attività con stato (TODO/DONE/WIP) | `"integrare-stripe"` |
| `milestone` | Traguardo significativo (release, beta, handoff) | `"v1-0-release"` |

### Attributi per type

- `event.attrs`: `{date_iso: "YYYY-MM-DD", date_precision: "day|month|year|fuzzy", raw_date_string: str, related_topic_id: entity_id|null}`
- `task.attrs`: `{status: "open|done|wip|blocked", due_iso: "YYYY-MM-DD"|null, due_precision: "day|month|year|fuzzy", owner_hint: str|null}`
- `milestone.attrs`: `{date_iso: str, milestone_type: "release|beta|handoff|deadline|start|end"}`

### Date precision

- `"day"`: data completa (`2025-03-14`)
- `"month"`: solo mese/anno (`marzo 2025` → `2025-03-01` con `precision: month`)
- `"year"`: solo anno (`2025` → `2025-01-01` con `precision: year`)
- `"fuzzy"`: vaga (`fine febbraio`, `inizio estate`) → prova a normalizzare ma metti `precision: fuzzy` e `raw_date_string` originale, flag `da-verificare`

**Mai** inventare precisione che non c'è. Preferisci `fuzzy` a una data precisa fabbricata.

### Fuori scope (NON emettere)

- Date di copyright/generate files → IGNORA
- Timestamp interni codice (logger output) → IGNORA
- Persone/org → facet **entities**
- Topic/tech → facet **narrative**

## Priorità lettura

1. `CHANGELOG*`, `HISTORY*`, `RELEASES*` → autoritativi per event/milestone
2. `TODO*`, `ROADMAP*`, `*.todo` → task
3. Issue tracker dumps (`issues.json`, export Linear/Jira)
4. Git log output (se fornito come file, NON eseguire git)
5. Frontmatter YAML `date:`, `created:`, `updated:`, `published:`, `due:`
6. Markdown checklist `- [ ]` / `- [x]` → task con status

## Pattern riconoscimento date (italiano + inglese)

| Input | Output date_iso | precision |
|---|---|---|
| `14/03/2025`, `2025-03-14`, `March 14, 2025` | `2025-03-14` | day |
| `marzo 2025`, `03/2025`, `March 2025` | `2025-03-01` | month |
| `2025`, `anno 2025` | `2025-01-01` | year |
| `fine febbraio 2025`, `late Feb 2025` | `2025-02-25` | fuzzy |
| `inizio 2025` | `2025-01-15` | fuzzy |
| `prossima settimana`, `ieri` | IGNORA (relative senza reference) | — |

## Output target

- Event: 3-20 (dipende da lunghezza CHANGELOG e cronologia)
- Task: 5-50 (se presenti TODO/ROADMAP)
- Milestone: 1-8

## Section hint suggerito

| Type | Sezione probabile |
|---|---|
| event | `cronologia`, `attivita-svolte` |
| task status=done | `attivita-svolte`, `risultati` |
| task status=open/wip | `lavori-futuri`, `limitazioni` |
| milestone | `cronologia`, `risultati-chiave` |

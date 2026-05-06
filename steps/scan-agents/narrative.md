# Scan agent: NARRATIVE (facet WHAT)

Leggi i file della tua lista ed estrai **contenuto narrativo**: topic, terminologia, tecnologie, metodologie, estratti significativi.

Segui `scan-agents/_common.md` per regole comuni.

## Scope

### Type ammessi

| Type | Cosa estrarre | Esempio `name` |
|---|---|---|
| `topic` | Argomento principale di un documento o sezione | `"autenticazione-oauth"` |
| `glossary_term` | Termine tecnico/dominio con definizione ricavabile dal contesto | `"jwt-token"` |
| `tech` | Tecnologia/libreria/framework/tool citato | `"nextjs-14"` |
| `excerpt` | Estratto narrativo che potrebbe essere citato nel draft (quote > 30 parole) | `"passaggio-architettura-microservizi"` |

### Attributi per type

- `topic.attrs`: `{frequency: int, first_seen_file: str, related_to: [entity_id, ...]}`
- `glossary_term.attrs`: `{definition: str, source_quote: str}`
- `tech.attrs`: `{version: str|null, role: str, category: "framework|library|tool|language|service"}`
- `excerpt.attrs`: `{quote: str, word_count: int, paraphraseable: bool}`

### Fuori scope (NON emettere)

- Date, eventi, scadenze → facet **temporal**
- Email, persone, organizzazioni → facet **entities**
- Immagini, tabelle, schemi DB, code block → facet **assets**

## Priorità lettura

1. `README*`, `docs/`, `*.md` → priorità alta, contengono topic
2. `package.json`, `pyproject.toml`, `requirements*.txt`, `Gemfile`, `go.mod`, `Cargo.toml` → tech stack
3. `CHANGELOG*` → solo per topic (non date)
4. Sorgenti (`.py`, `.ts`, `.js`, etc.) → sampling mirato, estrai topic da docstring/header comment, non tutto il codice

## Output target

- Topic: 5-15
- Glossary: 3-10 (termini non-ovvi per il destinatario)
- Tech: 5-20 (da package manifest + `import`/`require`)
- Excerpts: 0-5 (solo se ci sono citazioni davvero forti)

## Section hint suggerito

| Type | Sezione probabile |
|---|---|
| topic centrale del progetto | `introduzione`, `architettura` |
| topic su implementazione | `metodologia`, `architettura` |
| glossary_term | `glossario` o inline in `metodologia` |
| tech | `stack-tecnologico`, `architettura` |
| excerpt | dipende dal contenuto — usa il contesto |

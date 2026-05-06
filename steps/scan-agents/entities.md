# Scan agent: ENTITIES (facet WHO)

Leggi i file della tua lista ed estrai **chi è coinvolto**: persone, email, organizzazioni, URL, domini, prodotti citati per nome.

Segui `scan-agents/_common.md` per regole comuni.

## Scope

### Type ammessi

| Type | Cosa estrarre | Esempio `name` |
|---|---|---|
| `person` | Nome di persona (autore, collaboratore, docente, tutor, cliente) | `"Marco Rossi"` |
| `email` | Indirizzo email (standalone o associato a persona) | `"marco.rossi@example.com"` |
| `org` | Azienda, università, ente, team | `"Politecnico di Milano"` |
| `url` | URL esterno rilevante (non asset interno, non bibliografia) | `"https://nextjs.org"` |

### Attributi per type

- `person.attrs`: `{role: str, email_id: entity_id|null, org_id: entity_id|null, is_author: bool}`
- `email.attrs`: `{domain: str, person_id: entity_id|null, mx_verified: false}` (mx_verified sempre false, non fare DNS)
- `org.attrs`: `{type: "university|company|team|public-body|other", country: str|null}`
- `url.attrs`: `{domain: str, category: "documentation|tool|paper|social|other", http_status: null}` (mai fare HTTP)

### Regole speciali persone

- Match pattern: nome+cognome con maiuscola (`^[A-Z][a-zà-ù]+\s+[A-Z][a-zà-ù]+`)
- Forme abbreviate (`M. Rossi`) → emetti comunque, confidence 0.60-0.70, sarà merge-candidate
- Se la persona ha email associata (stesso file, prossimità ≤ 3 righe) → link in `attrs.email_id` + edge `authored_by`/`contacted_at` nel graph
- Skippa nomi comuni ambigui senza cognome (`Marco`, `Luca`) — confidence < 0.5 → non emettere

### Fuori scope (NON emettere)

- Nomi di tecnologie/prodotti software → facet **narrative** (`type: tech`)
- Date di nascita/assunzione → facet **temporal**
- Firma in immagine → facet **assets**

## Priorità lettura

1. `AUTHORS*`, `CODEOWNERS*`, `CONTRIBUTORS*`, `CREDITS*` → autoritativi
2. README "Team" / "Autori" / "Ringraziamenti"
3. Email footer signature in file `*.eml`, `*.msg`, `mail*`
4. Frontmatter YAML di `.md` con `author:`, `authors:`
5. git `Co-authored-by:` in COMMIT_* se rilevanti

## Pattern email

Regex: `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`. Skippa ovvi placeholder (`user@example.com`, `test@test.com`, `your-email@domain.com`).

## Section hint suggerito

| Type | Sezione probabile |
|---|---|
| person con role author | `frontespizio`, `ringraziamenti` |
| person con role tutor/supervisor | `frontespizio`, `ringraziamenti` |
| person con role stakeholder/cliente | `stakeholder`, `contesto` |
| org | `frontespizio`, `contesto-aziendale` |
| url | `bibliografia` (se paper) o `riferimenti-web` |

# Common rules for scan agents

Tutti e 4 gli agenti (narrative, entities, temporal, assets) devono rispettare queste regole.

## Output format (STRICT)

JSONL, una entity per riga, schema conforme a `$defs/entity` in `schemas/scan-tree.schema.json`:

```json
{"id":"<facet>:<slug>","facet":"<facet>","type":"<type>","name":"...","attrs":{...},"mentions":[{"file":"...","line_start":N,"line_end":M,"raw_string":"...","context":"..."}],"confidence":0.85,"provenance":[{"agent":"<facet>","agent_confidence":0.85,"timestamp":"ISO8601","raw_output_excerpt":"..."}],"section_hint":"...","section_hint_confidence":0.7,"flags":[],"extras":{}}
```

Scrivi in `.session/scan/raw/<facet>.jsonl`.

## Regole non negoziabili

1. **Mai inventare.** Se non c'è nei file, non esiste. Confidence 0 = non emettere.
2. **Raw string obbligatoria.** Ogni mention deve contenere la stringa testuale originale, prima di qualsiasi normalizzazione.
3. **Single-source cap:** confidence ≤ 0.75 se solo il tuo agente ha trovato l'entity. La confidence finale sale via merge se altri agenti la confermano.
4. **Flag `da-verificare`** automaticamente su confidence < 0.6.
5. **Campi non previsti** in `extras{}`, mai droppare.
6. **Normalizzazione in `name`, raw in `mentions[].raw_string`.** Esempio: `name: "Marco Rossi"`, `mention.raw_string: "M. Rossi"`.
7. **ID stabile e unico:** `<facet>:<slug>[:disambiguator]`. Slug = lowercase + strip diacritics + replace spaces with `-`.
8. **Context:** ±50 caratteri attorno alla mention nel file.
9. **Non leggere file fuori lista.** Il tuo scope è la lista ricevuta.
10. **Non overlap con altri facet.** Se trovi un'entità che appartiene chiaramente a un altro facet, NON emetterla. (Esempio: narrative non emette date; temporal non emette topic.)

## Confidence guidelines

| Evidenza | Confidence suggerita |
|---|---|
| Match esatto + pattern forte (es. email formato valido) | 0.90-0.95 |
| Contesto chiaro + multipla occorrenza | 0.80-0.90 |
| Inferenza ragionevole + 1 occorrenza | 0.65-0.75 |
| Ambigua / contesto debole | 0.50-0.65 |
| Sotto 0.5: non emettere |

## Budget

- Input: max 20k tokens (file content tuo subset)
- Output JSONL: max 3k tokens
- Se supera budget: priorità a entità con confidence ≥ 0.7, skippa il resto con nota in `extras.skipped_reason`

## Section hint

Cerca segnali per suggerire in quale sezione del draft l'entity servirà:
- `introduzione`, `architettura`, `metodologia`, `risultati`, `cronologia`, `stakeholder`, `ringraziamenti`, `bibliografia`, `appendice`, `discussione`, `conclusioni`

Se non sei sicuro, lascia vuoto (`""`) con `section_hint_confidence: 0`.

# Step — Knowledge Graph (vectorized, lightweight)

**Sostituisce dump raw + re-read** in `Step 4/5` con uno store leggero e cercabile per similarità.

## Quando si costruisce

- **Sempre, dopo Step 2** (sia `rapido` sia `profondo-parallelo`)
- Output in `<output>/.session/knowledge/`
- Costo tipico: 50–200 KB su disco, ~2–8 s build per 50 file

## File prodotti

```
.session/knowledge/
├── nodes.jsonl       # 1 riga = 1 nodo {id,type,name,summary,embed_b64,file_refs,section_hints}
├── edges.jsonl       # 1 riga = 1 arco {from,to,rel,weight}
├── manifest.json     # {dim, model, built_at, nodes_count, edges_count}
└── query.py          # helper standalone (incluso nel build, eseguibile a parte)
```

`embed_b64` è un vettore float16 base64 (default 128 dim, hash-projection deterministica). Niente dipendenze esterne. Se è installato `sentence-transformers`, viene preferito automaticamente con `--use-st`.

## Comandi

### Build da scratch (Step 2 `rapido`)

```bash
python3 scripts/knowledge-graph.py build \
  --root <cwd> \
  --out <output>/.session/knowledge
```

### Build da scan profondo (Step 2 `profondo-parallelo`)

Riusa `entities.jsonl` + `graph.json` esistenti:

```bash
python3 scripts/knowledge-graph.py from-scan \
  --scan <output>/.session/scan \
  --out  <output>/.session/knowledge
```

### Query (usato in Step 4 e 5)

```bash
python3 <output>/.session/knowledge/query.py "auth jwt refresh token" 5
# oppure
python3 scripts/knowledge-graph.py query \
  --out <output>/.session/knowledge \
  --text "auth jwt refresh" --topk 5
```

Output: top-K nodi per cosine similarity, ognuno con `score | type | name | summary`.

## Quando interrogarlo

| Step | Uso |
|---|---|
| Step 3 (load template) | `query "<sezione del template>"` per sapere quali file referenziare |
| Step 4 (draft) | Per ogni sezione, query del titolo e dei concetti chiave → file_refs guidano cosa leggere |
| Step 5 (refine) | Domande utente → query → recupera contesto pertinente senza re-read di tutti i sorgenti |
| Step 6.7 (layout) | Verifica presenza nodi `section:bibliografia`, `section:abstract` ecc. |

## Vantaggi rispetto a re-read raw

- **−60–80% token nel main context** sui draft di sezioni successive alla prima
- **Lookup O(N) su vettori compatti** (~256B/nodo) invece di re-Read di file MB
- **Provenance preservata**: ogni nodo punta ai `file_refs` originali — quando serve il testo intero, leggi il file una sola volta e cache locale
- **Aggiornabile incrementalmente**: re-build su un singolo file con `--root <file>` o re-run completo (~secondi)

## Aggiorna state

In `session-state.json`:

```json
"knowledge_graph_ref": "relative/path/to/.session/knowledge",
"knowledge_graph_built_at": "<ISO>",
"knowledge_graph_nodes": <int>
```

## Failure modes

| Failure | Mitigazione |
|---|---|
| `nodes.jsonl` corrotto | Rebuild idempotente — comando `build` o `from-scan` rifà tutto |
| Embedding mismatch (dim differente fra build e query) | Helper `query.py` è auto-generato dal build, allineato per definizione |
| Sentence-transformers non installato ma `--use-st` passato | Fallback automatico a hash-projection, model field aggiornato |
| Cwd vuota | `nodes.jsonl` vuoto, manifest con `nodes_count: 0`. Step 2 emette warning. |

## Regola di disciplina

Mai citare/usare contenuto che non sia attestato in `nodes.jsonl` (file_refs) o in WebSearch. Se il KG non ha il dato, leggere il file sorgente o chiedere all'utente — **mai inventare**.

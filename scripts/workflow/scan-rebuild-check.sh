#!/usr/bin/env bash
# scan-rebuild-check.sh
# Round-trip validation for Step 2-parallel hybrid scan store.
# Verifica che il merge sia loss-preserving: ogni entry raw dei 4 agenti
# deve essere presente (o fusa in un merge-candidate documentato) nel
# entities.jsonl consolidato.
#
# Usage: bash scan-rebuild-check.sh <scan_dir>
#   <scan_dir> = path a .session/scan/ (contiene entities.jsonl, raw/, index/, graph.json)
#
# Exit codes:
#   0 — PASS (round-trip OK, store è loss-preserving)
#   1 — FAIL (mentions mancanti, ID dangling in indici, o struttura corrotta)
#   2 — error di invocazione / file mancanti
set -u

SCAN_DIR="${1:-}"
if [[ -z "$SCAN_DIR" || ! -d "$SCAN_DIR" ]]; then
  echo "ERROR: scan dir mancante o non esistente: $SCAN_DIR" >&2
  echo "Usage: $0 <scan_dir>" >&2
  exit 2
fi

ENTITIES="$SCAN_DIR/entities.jsonl"
RAW_DIR="$SCAN_DIR/raw"
INDEX_DIR="$SCAN_DIR/index"
GRAPH="$SCAN_DIR/graph.json"
MERGE_CAND="$SCAN_DIR/merge_candidates.json"

# Verifica presenza file obbligatori
for f in "$ENTITIES" "$GRAPH"; do
  if [[ ! -f "$f" ]]; then
    echo "ERROR: file obbligatorio mancante: $f" >&2
    exit 2
  fi
done

if [[ ! -d "$RAW_DIR" ]]; then
  echo "ERROR: raw/ directory mancante: $RAW_DIR" >&2
  exit 2
fi

# Esegui controlli via python (per parsing JSON robusto)
python3 - "$ENTITIES" "$RAW_DIR" "$INDEX_DIR" "$GRAPH" "$MERGE_CAND" <<'PYEOF'
import json, os, sys

entities_path, raw_dir, index_dir, graph_path, merge_cand_path = sys.argv[1:6]

failures = []
warnings = []

def load_jsonl(path):
    if not os.path.isfile(path):
        return []
    entries = []
    with open(path, "r", encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError as e:
                failures.append(f"{path}:{ln} JSON invalido: {e}")
    return entries

def load_json(path):
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        failures.append(f"{path}: JSON invalido: {e}")
        return None

merged = load_jsonl(entities_path)
merged_ids = {e.get("id") for e in merged if e.get("id")}

# Raccogli tutte le mentions raw_string dal merged (source of truth)
merged_mention_strings = set()
merged_raw_outputs = set()
for e in merged:
    for m in e.get("mentions", []):
        rs = m.get("raw_string")
        if rs:
            merged_mention_strings.add((m.get("file", ""), rs))
    for p in e.get("provenance", []):
        ex = p.get("raw_output_excerpt", "")
        if ex:
            merged_raw_outputs.add(ex[:100])

# Controlla ogni raw agent file: ogni mention deve essere presente nel merged
for facet in ("narrative", "entities", "temporal", "assets"):
    raw_path = os.path.join(raw_dir, f"{facet}.jsonl")
    raw_entries = load_jsonl(raw_path)
    for re_ in raw_entries:
        rid = re_.get("id", "<no-id>")
        for m in re_.get("mentions", []):
            key = (m.get("file", ""), m.get("raw_string", ""))
            if key not in merged_mention_strings:
                failures.append(
                    f"MENTION PERSA: agent={facet} id={rid} file={key[0]} raw={key[1][:50]!r}"
                )

# Controlla indici: ogni ID referenziato deve esistere in merged
if os.path.isdir(index_dir):
    for idx_name in ("by-facet.json", "by-file.json", "by-section.json", "by-date.json"):
        idx_path = os.path.join(index_dir, idx_name)
        idx = load_json(idx_path)
        if idx is None:
            continue
        for key, ids in idx.items():
            if not isinstance(ids, list):
                failures.append(f"INDEX MALFORMED: {idx_name}[{key}] non è lista")
                continue
            for eid in ids:
                if eid not in merged_ids:
                    failures.append(
                        f"DANGLING INDEX: {idx_name}[{key}] punta a id inesistente: {eid}"
                    )
else:
    warnings.append(f"Index directory assente: {index_dir}")

# Controlla graph: edges devono referenziare ID esistenti
graph = load_json(graph_path)
if graph:
    edges = graph.get("edges", [])
    for i, edge in enumerate(edges):
        for side in ("from_id", "to_id"):
            eid = edge.get(side)
            if eid and eid not in merged_ids:
                failures.append(
                    f"DANGLING EDGE[{i}]: graph.edges[{i}].{side} = {eid} non esiste"
                )

# Merge candidates: se esistono, devono referenziare ID esistenti
if os.path.isfile(merge_cand_path):
    mc = load_json(merge_cand_path)
    if mc and isinstance(mc, dict):
        for pair in mc.get("candidates", []):
            for side in ("id_a", "id_b"):
                eid = pair.get(side)
                if eid and eid not in merged_ids:
                    failures.append(
                        f"MERGE-CAND DANGLING: {pair.get(side)} non esiste in entities.jsonl"
                    )

# Report
print(f"entities.jsonl: {len(merged)} entries, {len(merged_ids)} unique IDs")
print(f"raw mentions verificate: {len(merged_mention_strings)}")

if warnings:
    print(f"\n[WARN] {len(warnings)}:")
    for w in warnings:
        print(f"  - {w}")

if failures:
    print(f"\n[FAIL] {len(failures)} round-trip failures:")
    for f in failures[:30]:
        print(f"  - {f}")
    if len(failures) > 30:
        print(f"  ... e altri {len(failures) - 30}")
    sys.exit(1)

print("\n[PASS] round-trip OK — store è loss-preserving")
sys.exit(0)
PYEOF

rc=$?
exit $rc

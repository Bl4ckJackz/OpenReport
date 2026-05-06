#!/usr/bin/env python3
"""
knowledge-graph.py - Build a lightweight vectorized knowledge graph for relazione.

Produces .session/knowledge/ with:
  nodes.jsonl     - {id, type, name, summary, embed_b64, file_refs[], section_hints[]}
  edges.jsonl     - {from, to, rel, weight}
  manifest.json   - {dim, model, built_at, files_scanned, nodes_count, edges_count}
  query.py        - small CLI helper for nearest-neighbor lookup

Embedding: hash-based 128-dim sparse projection (deterministic, dependency-free).
Optional: if `sentence-transformers` is installed, use it (better quality).

Usage:
  python3 knowledge-graph.py build --root <cwd> --out <.session/knowledge>
  python3 knowledge-graph.py query --out <.session/knowledge> --text "auth flow" --topk 5
  python3 knowledge-graph.py from-scan --scan <.session/scan> --out <.session/knowledge>

Designed for: O(1) lookup by id, O(N) cosine search over compact vectors,
~50-200KB on disk for typical project (vs MB of raw scan content).
"""
import argparse
import base64
import hashlib
import json
import math
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

DIM = 128
EMBED_MODEL = "hash-projection-v1"

EXCLUDE_DIRS = {
    "node_modules", ".git", "dist", "build", ".next", "out", ".cache",
    "coverage", "__pycache__", "venv", ".venv", "target", "vendor",
    ".session", "relazioni", "img"
}
TEXT_EXT = {
    ".md", ".txt", ".tex", ".rst", ".org",
    ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".kt",
    ".swift", ".rb", ".php", ".c", ".cpp", ".h", ".hpp", ".cs", ".scala",
    ".clj", ".ex", ".exs", ".vue", ".svelte", ".sql", ".prisma",
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg",
}

WORD_RE = re.compile(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ0-9_\-]{2,}")
SECTION_HINTS = [
    "introduzione", "abstract", "metodologia", "architettura", "implementazione",
    "risultati", "conclusioni", "bibliografia", "appendice", "ringraziamenti",
    "frontespizio", "sommario", "stato dell'arte", "obiettivi", "test",
    "deploy", "auth", "database", "sicurezza", "performance"
]


def embed_hash(text: str, dim: int = DIM) -> list[float]:
    """Deterministic hash-based embedding. No external dependencies."""
    vec = [0.0] * dim
    if not text:
        return vec
    tokens = WORD_RE.findall(text.lower())
    if not tokens:
        return vec
    for tok in tokens:
        h = hashlib.blake2b(tok.encode("utf-8"), digest_size=8).digest()
        idx = int.from_bytes(h[:4], "little") % dim
        sign = 1.0 if (h[4] & 1) else -1.0
        vec[idx] += sign
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [x / norm for x in vec]
    return vec


def try_embed_st(text: str) -> list[float] | None:
    """Try sentence-transformers if available. Returns None if not installed."""
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore
        global _ST
        try:
            _ST  # noqa
        except NameError:
            _ST = SentenceTransformer("all-MiniLM-L6-v2")
        v = _ST.encode([text or ""], normalize_embeddings=True)[0]
        return v.tolist()
    except Exception:
        return None


def embed(text: str, prefer_st: bool = False) -> tuple[list[float], str]:
    if prefer_st:
        v = try_embed_st(text)
        if v is not None:
            return v, "sentence-transformers/all-MiniLM-L6-v2"
    return embed_hash(text), EMBED_MODEL


def vec_to_b64(vec: list[float]) -> str:
    """Pack as float16 little-endian → base64. ~25% size of float32."""
    import struct
    raw = b"".join(struct.pack("<e", v) for v in vec)
    return base64.b64encode(raw).decode("ascii")


def b64_to_vec(s: str) -> list[float]:
    import struct
    raw = base64.b64decode(s)
    return [struct.unpack_from("<e", raw, i)[0] for i in range(0, len(raw), 2)]


def cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXT


def walk_files(root: Path) -> list[Path]:
    out = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(part in EXCLUDE_DIRS for part in p.parts):
            continue
        if not is_text_file(p):
            continue
        try:
            if p.stat().st_size > 500_000:
                continue
        except OSError:
            continue
        out.append(p)
    return out


def summarize(text: str, max_chars: int = 240) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars]


def detect_section_hints(text: str) -> list[str]:
    low = text.lower()
    return [h for h in SECTION_HINTS if h in low]


def slugify(s: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "-", s.lower()).strip("-")
    return s[:60] or "node"


def build_from_root(root: Path, out: Path, prefer_st: bool = False) -> None:
    out.mkdir(parents=True, exist_ok=True)
    files = walk_files(root)
    nodes = []
    edges = []
    seen_ids = set()
    used_model = EMBED_MODEL

    for f in files:
        try:
            txt = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = str(f.relative_to(root)).replace("\\", "/")
        node_id = f"file:{slugify(rel)}"
        if node_id in seen_ids:
            continue
        seen_ids.add(node_id)
        vec, model = embed(txt[:8000], prefer_st=prefer_st)
        used_model = model
        hints = detect_section_hints(txt)
        node = {
            "id": node_id,
            "type": "file",
            "name": rel,
            "summary": summarize(txt),
            "embed_b64": vec_to_b64(vec),
            "file_refs": [rel],
            "section_hints": hints,
        }
        nodes.append(node)

        for h in hints:
            sec_id = f"section:{slugify(h)}"
            if sec_id not in seen_ids:
                seen_ids.add(sec_id)
                vh, _ = embed(h, prefer_st=prefer_st)
                nodes.append({
                    "id": sec_id, "type": "section", "name": h,
                    "summary": h, "embed_b64": vec_to_b64(vh),
                    "file_refs": [], "section_hints": [h],
                })
            edges.append({"from": node_id, "to": sec_id, "rel": "mentions_section", "weight": 0.7})

    write_jsonl(out / "nodes.jsonl", nodes)
    write_jsonl(out / "edges.jsonl", edges)
    manifest = {
        "dim": DIM if used_model == EMBED_MODEL else len(b64_to_vec(nodes[0]["embed_b64"])) if nodes else DIM,
        "model": used_model,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "files_scanned": len(files),
        "nodes_count": len(nodes),
        "edges_count": len(edges),
        "root": str(root),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    write_query_helper(out)
    print(f"[knowledge-graph] {len(nodes)} nodes, {len(edges)} edges → {out}")


def build_from_scan(scan_dir: Path, out: Path, prefer_st: bool = False) -> None:
    """Convert .session/scan/entities.jsonl + graph.json into a vectorized graph."""
    out.mkdir(parents=True, exist_ok=True)
    entities_path = scan_dir / "entities.jsonl"
    graph_path = scan_dir / "graph.json"
    if not entities_path.exists():
        print(f"[knowledge-graph] {entities_path} not found", file=sys.stderr)
        sys.exit(2)

    nodes = []
    used_model = EMBED_MODEL
    with entities_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            text_for_embed = " ".join(filter(None, [
                e.get("name", ""),
                " ".join(m.get("raw_string", "") for m in e.get("mentions", [])[:3]),
            ]))
            vec, model = embed(text_for_embed, prefer_st=prefer_st)
            used_model = model
            nodes.append({
                "id": e.get("id"),
                "type": e.get("type") or e.get("facet") or "entity",
                "name": e.get("name") or "",
                "summary": summarize(text_for_embed),
                "embed_b64": vec_to_b64(vec),
                "file_refs": [m.get("file") for m in e.get("mentions", []) if m.get("file")][:5],
                "section_hints": list(set(filter(None, [m.get("section_hint") for m in e.get("mentions", [])]))),
            })
    write_jsonl(out / "nodes.jsonl", nodes)

    edges = []
    if graph_path.exists():
        try:
            g = json.loads(graph_path.read_text(encoding="utf-8"))
            for e in g.get("edges", []):
                edges.append({
                    "from": e.get("from_id") or e.get("from"),
                    "to": e.get("to_id") or e.get("to"),
                    "rel": e.get("rel", "related_to"),
                    "weight": e.get("weight", 0.5),
                })
        except json.JSONDecodeError:
            pass
    write_jsonl(out / "edges.jsonl", edges)

    manifest = {
        "dim": DIM,
        "model": used_model,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "source": "scan",
        "nodes_count": len(nodes),
        "edges_count": len(edges),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    write_query_helper(out)
    print(f"[knowledge-graph] from-scan: {len(nodes)} nodes, {len(edges)} edges → {out}")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False))
            fh.write("\n")


def write_query_helper(out: Path) -> None:
    helper = out / "query.py"
    helper.write_text(
        "#!/usr/bin/env python3\n"
        "# Auto-generated by knowledge-graph.py — minimal nearest-neighbor query.\n"
        "import json, sys, base64, struct, math, hashlib, re\n"
        "from pathlib import Path\n"
        f"DIM = {DIM}\n"
        'WORD_RE = re.compile(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ0-9_\\-]{2,}")\n'
        "def embed(text):\n"
        "    v=[0.0]*DIM\n"
        "    for tok in WORD_RE.findall((text or '').lower()):\n"
        "        h=hashlib.blake2b(tok.encode('utf-8'),digest_size=8).digest()\n"
        "        v[int.from_bytes(h[:4],'little')%DIM] += 1.0 if (h[4]&1) else -1.0\n"
        "    n=math.sqrt(sum(x*x for x in v));\n"
        "    return [x/n for x in v] if n>0 else v\n"
        "def b64v(s):\n"
        "    raw=base64.b64decode(s); return [struct.unpack_from('<e',raw,i)[0] for i in range(0,len(raw),2)]\n"
        "def cos(a,b): return sum(x*y for x,y in zip(a,b))\n"
        "def main():\n"
        "    here=Path(__file__).parent; q=sys.argv[1] if len(sys.argv)>1 else ''; k=int(sys.argv[2]) if len(sys.argv)>2 else 5\n"
        "    qv=embed(q); rows=[]\n"
        "    for line in (here/'nodes.jsonl').read_text(encoding='utf-8').splitlines():\n"
        "        if not line: continue\n"
        "        n=json.loads(line); rows.append((cos(qv,b64v(n['embed_b64'])), n))\n"
        "    rows.sort(key=lambda r: -r[0])\n"
        "    for s,n in rows[:k]: print(f\"{s:+.3f}  [{n['type']}]  {n['name']}  — {n.get('summary','')[:80]}\")\n"
        "if __name__=='__main__': main()\n",
        encoding="utf-8",
    )


def cmd_query(out: Path, text: str, topk: int) -> None:
    qv = embed_hash(text)
    nodes_path = out / "nodes.jsonl"
    if not nodes_path.exists():
        print(f"[knowledge-graph] {nodes_path} missing", file=sys.stderr); sys.exit(2)
    rows = []
    with nodes_path.open(encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            n = json.loads(line)
            rows.append((cosine(qv, b64_to_vec(n["embed_b64"])), n))
    rows.sort(key=lambda r: -r[0])
    for score, n in rows[:topk]:
        print(f"{score:+.3f}  [{n['type']}]  {n['name']}  — {n.get('summary','')[:90]}")


def main() -> int:
    ap = argparse.ArgumentParser(prog="knowledge-graph")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--root", required=True)
    b.add_argument("--out", required=True)
    b.add_argument("--use-st", action="store_true", help="prefer sentence-transformers if installed")
    s = sub.add_parser("from-scan")
    s.add_argument("--scan", required=True)
    s.add_argument("--out", required=True)
    s.add_argument("--use-st", action="store_true")
    q = sub.add_parser("query")
    q.add_argument("--out", required=True)
    q.add_argument("--text", required=True)
    q.add_argument("--topk", type=int, default=5)
    args = ap.parse_args()

    if args.cmd == "build":
        build_from_root(Path(args.root), Path(args.out), prefer_st=args.use_st)
    elif args.cmd == "from-scan":
        build_from_scan(Path(args.scan), Path(args.out), prefer_st=args.use_st)
    elif args.cmd == "query":
        cmd_query(Path(args.out), args.text, args.topk)
    return 0


if __name__ == "__main__":
    sys.exit(main())

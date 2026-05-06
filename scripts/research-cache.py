#!/usr/bin/env python3
"""research-cache.py — cache locale per URL fetched durante Step 3.5.

Evita di ri-scaricare le stesse fonti tra retry/resume/rigenerazioni.
Struttura: .session/research-cache/index.json + file per hash.

Usage:
    research-cache.py get <url>                      # legge da cache, exit 0 se hit
    research-cache.py put <url> <file>               # salva contenuto file in cache
    research-cache.py list                           # elenca URL in cache
    research-cache.py prune --older-than 30          # rimuove entry > 30 giorni
    research-cache.py stats                          # hit/miss count, size totale

Variabile env: RELAZIONE_CACHE_DIR (default: .session/research-cache/ relativo a cwd)
"""
import argparse
import hashlib
import json
import os
import pathlib
import shutil
import sys
from datetime import datetime, timedelta


def cache_dir():
    d = os.environ.get("RELAZIONE_CACHE_DIR") or ".session/research-cache"
    return pathlib.Path(d)


def url_hash(url):
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]


def load_index(d):
    p = d / "index.json"
    if not p.exists():
        return {"entries": {}, "stats": {"hits": 0, "misses": 0}}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {"entries": {}, "stats": {"hits": 0, "misses": 0}}


def save_index(d, idx):
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.json").write_text(json.dumps(idx, indent=2, ensure_ascii=False), encoding="utf-8")


def cmd_get(args):
    d = cache_dir()
    idx = load_index(d)
    h = url_hash(args.url)
    entry = idx.get("entries", {}).get(h)
    if not entry:
        idx.setdefault("stats", {"hits": 0, "misses": 0})["misses"] += 1
        save_index(d, idx)
        print(f"[MISS] {args.url}", file=sys.stderr)
        return 1
    path = d / entry["file"]
    if not path.exists():
        idx["stats"]["misses"] += 1
        save_index(d, idx)
        print(f"[MISS] {args.url} (file mancante)", file=sys.stderr)
        return 1
    idx["stats"]["hits"] = idx["stats"].get("hits", 0) + 1
    save_index(d, idx)
    sys.stdout.write(path.read_text(encoding="utf-8", errors="ignore"))
    return 0


def cmd_put(args):
    d = cache_dir()
    d.mkdir(parents=True, exist_ok=True)
    idx = load_index(d)
    h = url_hash(args.url)
    src = pathlib.Path(args.file)
    if not src.exists():
        print(f"[ERR] file non trovato: {src}", file=sys.stderr)
        return 2
    dest_name = f"{h}.txt"
    dest = d / dest_name
    shutil.copy(src, dest)
    idx.setdefault("entries", {})[h] = {
        "url": args.url,
        "file": dest_name,
        "cached_at": datetime.now().isoformat(),
        "size": dest.stat().st_size,
    }
    save_index(d, idx)
    print(f"[OK] cached {args.url} -> {dest_name}")
    return 0


def cmd_list(args):
    d = cache_dir()
    idx = load_index(d)
    for h, entry in sorted(idx.get("entries", {}).items(), key=lambda kv: kv[1]["cached_at"], reverse=True):
        print(f"  [{entry['cached_at'][:10]}] {entry['url']} ({entry.get('size', 0)} bytes)")
    return 0


def cmd_prune(args):
    d = cache_dir()
    idx = load_index(d)
    cutoff = datetime.now() - timedelta(days=args.older_than)
    removed = 0
    keep = {}
    for h, entry in idx.get("entries", {}).items():
        cached_at = datetime.fromisoformat(entry["cached_at"])
        if cached_at < cutoff:
            fp = d / entry["file"]
            if fp.exists():
                fp.unlink()
            removed += 1
        else:
            keep[h] = entry
    idx["entries"] = keep
    save_index(d, idx)
    print(f"[OK] rimosse {removed} entry più vecchie di {args.older_than} giorni")
    return 0


def cmd_stats(args):
    d = cache_dir()
    idx = load_index(d)
    entries = idx.get("entries", {})
    stats = idx.get("stats", {})
    total_size = sum(e.get("size", 0) for e in entries.values())
    print(f"Cache dir: {d}")
    print(f"Entries: {len(entries)}")
    print(f"Size: {total_size / 1024:.1f} KB")
    print(f"Hits: {stats.get('hits', 0)}")
    print(f"Misses: {stats.get('misses', 0)}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("get"); g.add_argument("url")
    p = sub.add_parser("put"); p.add_argument("url"); p.add_argument("file")
    sub.add_parser("list")
    pr = sub.add_parser("prune"); pr.add_argument("--older-than", type=int, default=30)
    sub.add_parser("stats")
    args = ap.parse_args()
    return {"get": cmd_get, "put": cmd_put, "list": cmd_list, "prune": cmd_prune, "stats": cmd_stats}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())

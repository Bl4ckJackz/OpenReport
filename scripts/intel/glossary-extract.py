#!/usr/bin/env python3
"""glossary-extract.py — estrae termini tecnici ricorrenti dal codebase + relazione.

Strategia:
  1. Trova parole tecniche (CamelCase, snake_case, sigle MAIUSCOLE, parole inglesi
     in testo italiano) ricorrenti nei file scansionati e nella relazione.
  2. Cerca definizione: prima occorrenza in commento, docstring, o paragrafo.
  3. Filtra: tieni solo termini con > N occorrenze.
  4. Genera glossario markdown ordinato alfabeticamente.

Usage:
  glossary-extract.py <relazione.md> --src=<src-dir> -o GLOSSARIO.md [--min-occurrences=3]
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path
from collections import Counter


# Stopword italiane comuni — non sono termini tecnici
COMMON_IT = {
    "Per", "Con", "Una", "Della", "Delle", "Degli", "Sono", "Questo",
    "Questa", "Quello", "Quella", "Anche", "Solo", "Più", "Meno",
}

ENGLISH_TECH_HINTS = {
    "API", "REST", "HTTP", "HTTPS", "JSON", "XML", "SQL", "NoSQL", "ORM",
    "JWT", "OAuth", "TLS", "SSL", "CRUD", "MVC", "MVVM", "DDD", "TDD",
    "CI", "CD", "DNS", "CDN", "VPN", "IDE", "SDK", "CLI", "GUI", "UI", "UX",
    "PWA", "SPA", "SSR", "CSR", "AOT", "JIT", "GC", "OOM", "RPC", "gRPC",
    "WebSocket", "GraphQL", "Kubernetes", "Docker", "Redis", "Postgres",
    "MongoDB", "Elasticsearch", "Kafka", "RabbitMQ",
}


def find_tech_terms(text: str) -> Counter:
    """Trova termini candidati: CamelCase, snake_case, MAIUSCOLE, hint inglesi."""
    candidates = Counter()
    for tok in re.findall(r"\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b", text):       # CamelCase
        candidates[tok] += 1
    for tok in re.findall(r"\b[a-z]+(?:_[a-z]+)+\b", text):                  # snake_case
        candidates[tok] += 1
    for tok in re.findall(r"\b[A-Z]{2,8}\b", text):                          # SIGLE
        if tok not in COMMON_IT:
            candidates[tok] += 1
    for tok in ENGLISH_TECH_HINTS:                                            # hint
        n = len(re.findall(rf"\b{re.escape(tok)}\b", text))
        if n: candidates[tok] += n
    return candidates


def find_definition(term: str, files: list[Path]) -> str:
    """Cerca prima definizione: 'X è ...', '`X` is ...', commento /** X: ... */."""
    patterns = [
        rf"`?{re.escape(term)}`?\s+è\s+(?:un[ao]?|il|la|lo|i|le|gli)?\s*([^.]+\.)",
        rf"`?{re.escape(term)}`?\s+is\s+(?:an?|the)?\s*([^.]+\.)",
        rf"/\*\*?\s*{re.escape(term)}[:\s].*?\*/",
        rf"//\s*{re.escape(term)}\s*[:\-]\s*([^\n]+)",
        rf"#\s*{re.escape(term)}\s*[:\-]\s*([^\n]+)",
    ]
    for f in files:
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            for pat in patterns:
                m = re.search(pat, content)
                if m:
                    return m.group(1).strip()[:200] if m.lastindex else m.group(0).strip()[:200]
        except Exception:
            continue
    return ""


def collect_files(src_dir: Path) -> list[Path]:
    if not src_dir.exists(): return []
    excludes = {"node_modules", ".git", "dist", "build", ".next", "out", "__pycache__",
                "venv", ".venv", "target", ".cache", "coverage"}
    files = []
    for f in src_dir.rglob("*"):
        if f.is_file() and not any(p in excludes for p in f.parts):
            if f.suffix in {".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs",
                            ".rb", ".php", ".cs", ".kt", ".swift", ".cpp", ".c", ".h",
                            ".md", ".txt", ".rst"}:
                files.append(f)
    return files[:200]  # cap


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("relazione", help="Path al file relazione (.md o .tex)")
    p.add_argument("--src", default=".", help="Directory codice sorgente da scansionare")
    p.add_argument("-o", "--out", default="GLOSSARIO.md")
    p.add_argument("--min-occurrences", type=int, default=3)
    args = p.parse_args()

    rel_text = Path(args.relazione).read_text(encoding="utf-8")
    src_files = collect_files(Path(args.src))
    src_text = "\n".join(f.read_text(encoding="utf-8", errors="ignore") for f in src_files)

    counts = find_tech_terms(rel_text + "\n" + src_text)
    candidates = {t: c for t, c in counts.items() if c >= args.min_occurrences}

    out = ["# Glossario", "",
           f"*Generato automaticamente da {len(src_files)} file sorgente + relazione. Soglia: ≥{args.min_occurrences} occorrenze.*",
           ""]

    for term in sorted(candidates, key=str.lower):
        n = candidates[term]
        defn = find_definition(term, [Path(args.relazione)] + src_files[:30])
        if defn:
            out.append(f"**{term}** ({n} occ.) — {defn}")
        else:
            out.append(f"**{term}** ({n} occ.) — *[DA COMPLETARE: definizione]*")
        out.append("")

    Path(args.out).write_text("\n".join(out), encoding="utf-8")
    print(f"Glossario scritto in {args.out} ({len(candidates)} termini)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

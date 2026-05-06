#!/usr/bin/env python3
"""plagio-lite.py — scan locale frasi del draft vs research-notes.

Per ogni frase del draft (min 8 parole), calcola n-gram overlap con research-notes.
Flag >= threshold (default 0.70) come "troppo simile a fonte — riformulare".

Non sostituisce un plagio-check professionale ma cattura copy/paste dall'online research.

Usage:
    plagio-lite.py <draft> --research research-notes.md [--threshold 0.70] [--min-words 8]
"""
import argparse
import pathlib
import re
import sys


def sentences(text):
    text = re.sub(r"\s+", " ", text)
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def ngrams(words, n=4):
    return set(tuple(words[i:i+n]) for i in range(len(words) - n + 1))


def similarity(s1_words, s2_words, n=4):
    if len(s1_words) < n or len(s2_words) < n:
        return 0.0
    ng1 = ngrams(s1_words, n)
    ng2 = ngrams(s2_words, n)
    if not ng1:
        return 0.0
    inter = ng1 & ng2
    return len(inter) / len(ng1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("draft")
    ap.add_argument("--research", required=True)
    ap.add_argument("--threshold", type=float, default=0.70)
    ap.add_argument("--min-words", type=int, default=8)
    ap.add_argument("--ngram", type=int, default=4)
    args = ap.parse_args()

    draft_path = pathlib.Path(args.draft)
    res_path = pathlib.Path(args.research)
    if not draft_path.exists() or not res_path.exists():
        print("[ERR] draft o research mancanti", file=sys.stderr)
        return 2

    draft = draft_path.read_text(encoding="utf-8")
    research = res_path.read_text(encoding="utf-8")

    draft_sentences = sentences(draft)
    research_sentences = sentences(research)
    research_words_list = [re.findall(r"\w+", s.lower()) for s in research_sentences]

    hits = []
    for ds in draft_sentences:
        d_words = re.findall(r"\w+", ds.lower())
        if len(d_words) < args.min_words:
            continue
        best = 0.0
        best_res = ""
        for rs, r_words in zip(research_sentences, research_words_list):
            if len(r_words) < args.min_words:
                continue
            sim = similarity(d_words, r_words, n=args.ngram)
            if sim > best:
                best = sim
                best_res = rs
                if best >= 0.95:
                    break
        if best >= args.threshold:
            hits.append((best, ds, best_res))

    if not hits:
        print(f"[OK] plagio-lite: nessuna frase > {args.threshold:.0%} simile a research-notes")
        return 0

    print(f"[WARN] {len(hits)} frasi sopra soglia {args.threshold:.0%} — considera riformulazione")
    print("=" * 60)
    for sim, draft_sent, res_sent in sorted(hits, key=lambda x: -x[0])[:20]:
        print(f"\nSimilarità: {sim:.0%}")
        print(f"  DRAFT:    {draft_sent[:200]}")
        print(f"  RESEARCH: {res_sent[:200]}")
    return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""clarity-score.py — score di chiarezza del testo, sezione per sezione.

Metriche:
- Frasi troppo lunghe (>35 parole)
- Parole complesse (>4 sillabe)
- Densità subordinate (virgole per frase)
- Voce passiva (approssimata)
- Ambiguità (parole vaghe: 'cosa', 'questo', 'qualcosa', 'determinato')

Output: score 0-100 per sezione + raccomandazioni.

Usage:
    clarity-score.py <file> [--threshold 60] [--per-section]
"""
import argparse
import pathlib
import re
import sys


VAGUE_WORDS_IT = {"cosa", "cose", "questo", "questa", "quello", "qualcosa", "determinato",
                  "certi", "alcuni", "diversi", "vari", "quanto", "quanti"}
VAGUE_WORDS_EN = {"thing", "things", "something", "several", "various", "certain", "some"}

PASSIVE_IT = re.compile(r"\b(è|sono|è stato|sono stati|viene|vengono|veniva)\s+\w+(ato|ito|uto)\b", re.IGNORECASE)
PASSIVE_EN = re.compile(r"\b(is|are|was|were|be|been|being)\s+\w+(ed|en)\b", re.IGNORECASE)

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", flags=re.MULTILINE)


def syllable_count(word):
    word = word.lower()
    vowels = "aeiouàèéìòùáéíóú"
    count = sum(1 for c in word if c in vowels)
    return max(1, count)


def analyze(text, lang="it"):
    text_clean = re.sub(r"```[\s\S]*?```", " ", text)
    text_clean = re.sub(r"[!@#$%^&*()\[\]{}|\\/:;\"',<>]", " ", text_clean)

    sentences = re.split(r"(?<=[.!?])\s+", text_clean)
    sentences = [s for s in sentences if len(s.split()) >= 3]

    if not sentences:
        return {"score": 0, "words": 0, "sentences": 0}

    long_sentences = [s for s in sentences if len(s.split()) > 35]

    all_words = [w for s in sentences for w in re.findall(r"\b[a-zA-Zà-ú]+\b", s)]
    complex_words = [w for w in all_words if syllable_count(w) > 4]

    subordinate_per_sentence = sum(s.count(",") for s in sentences) / len(sentences)

    passive_re = PASSIVE_IT if lang == "it" else PASSIVE_EN
    passive_matches = len(passive_re.findall(text_clean))
    passive_rate = passive_matches / len(sentences) if sentences else 0

    vague = VAGUE_WORDS_IT if lang == "it" else VAGUE_WORDS_EN
    vague_matches = sum(1 for w in all_words if w.lower() in vague)
    vague_rate = vague_matches / max(1, len(all_words)) * 100

    score = 100
    if long_sentences:
        score -= min(25, len(long_sentences) / len(sentences) * 100)
    if complex_words:
        score -= min(20, len(complex_words) / len(all_words) * 200)
    if subordinate_per_sentence > 3:
        score -= min(15, (subordinate_per_sentence - 3) * 5)
    if passive_rate > 0.3:
        score -= min(15, (passive_rate - 0.3) * 50)
    if vague_rate > 2:
        score -= min(10, (vague_rate - 2) * 2)
    score = max(0, min(100, int(score)))

    return {
        "score": score,
        "words": len(all_words),
        "sentences": len(sentences),
        "long_sentences": len(long_sentences),
        "complex_words": len(complex_words),
        "subordinate_per_sentence": round(subordinate_per_sentence, 1),
        "passive_rate": round(passive_rate * 100),
        "vague_rate": round(vague_rate, 1),
    }


def split_by_sections(text):
    matches = list(HEADING_RE.finditer(text))
    if not matches:
        return [("Documento intero", text)]
    result = []
    for i, m in enumerate(matches):
        title = m.group(2)
        start = m.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        result.append((title, text[start:end]))
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--lang", default="it", choices=["it", "en"])
    ap.add_argument("--threshold", type=int, default=60)
    ap.add_argument("--per-section", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    p = pathlib.Path(args.file)
    if not p.exists():
        print(f"[ERR] {p} non trovato", file=sys.stderr)
        return 2

    text = p.read_text(encoding="utf-8")

    if args.per_section:
        sections = split_by_sections(text)
    else:
        sections = [("Documento", text)]

    results = []
    for title, body in sections:
        a = analyze(body, args.lang)
        a["title"] = title
        results.append(a)

    if args.json:
        import json
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return 0

    print(f"CLARITY SCORE — {p.name} (lang: {args.lang}, threshold: {args.threshold})")
    print("=" * 70)
    below_threshold = 0
    for r in results:
        emoji = "✓" if r["score"] >= args.threshold else "⚠"
        print(f"\n{emoji} [{r['score']:3d}/100] {r['title'][:50]}")
        print(f"    {r['words']} parole, {r['sentences']} frasi")
        if r["long_sentences"]:
            print(f"    • {r['long_sentences']} frasi troppo lunghe (>35 parole) — spezza")
        if r["complex_words"] > r["words"] * 0.08:
            print(f"    • {r['complex_words']} parole complesse (>4 sillabe) — semplifica")
        if r["subordinate_per_sentence"] > 3:
            print(f"    • {r['subordinate_per_sentence']} subordinate/frase — riduci le virgole")
        if r["passive_rate"] > 30:
            print(f"    • voce passiva al {r['passive_rate']}% — preferisci attiva")
        if r["vague_rate"] > 2:
            print(f"    • {r['vague_rate']}% parole vaghe — specifica")
        if r["score"] < args.threshold:
            below_threshold += 1

    avg = sum(r["score"] for r in results) / len(results) if results else 0
    print(f"\n{'=' * 70}")
    print(f"Media: {avg:.0f}/100  •  {below_threshold} sezioni sotto soglia {args.threshold}")
    return 1 if below_threshold else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""abstract-generator.py — estrae abstract candidato dal doc completo.

Strategia (euristica, no LLM):
1. Seleziona introduzione + conclusioni (primi 2 e ultimi 2 paragrafi sostanziali)
2. Estrae prima frase di ogni sezione top-level (topic sentences)
3. Combina + trim a target word count (default 250 parole)
4. Rimuove stop-word iniziali e chiusure inutili

Usage:
    abstract-generator.py <draft.md> [--words 250] [--keywords] [-o abstract.md]
"""
import argparse
import pathlib
import re
import sys


HEADING_RE = re.compile(r"^(#{1,3})\s+(.+?)\s*$", flags=re.MULTILINE)
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+(?=[A-ZÀ-Ú])")


def extract_sections(text):
    sections = []
    matches = list(HEADING_RE.finditer(text))
    for i, m in enumerate(matches):
        title = m.group(2).strip()
        start = m.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        sections.append((title, text[start:end].strip()))
    return sections


def first_sentence(text):
    text = re.sub(r"^\s*[-*]\s+", "", text.split("\n\n")[0]).strip()
    parts = SENTENCE_RE.split(text, maxsplit=1)
    return parts[0] if parts else text


def extract_keywords(text, n=7):
    from collections import Counter
    # Estrae sostantivi tecnici (parole >5 char, capitalize o tecnici)
    words = re.findall(r"\b[A-Za-zà-ú]{5,}\b", text)
    # Remove common stopwords IT/EN
    stop = {"della", "dello", "delle", "degli", "questo", "questa", "questi", "queste",
            "essere", "avere", "fare", "andare", "dovere", "potere", "volere",
            "the", "this", "that", "which", "these", "those", "with", "from",
            "their", "there", "when", "where", "whose", "would", "could", "should",
            "about", "because", "between", "however", "therefore"}
    filtered = [w.lower() for w in words if w.lower() not in stop and not w.lower().startswith("http")]
    return [k for k, _ in Counter(filtered).most_common(n)]


def trim_to_words(text, max_words):
    words = re.findall(r"\S+", text)
    if len(words) <= max_words:
        return text
    truncated = " ".join(words[:max_words])
    m = re.match(r"^(.*[.!?])[^.!?]*$", truncated)
    return m.group(1) if m else truncated + "…"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--words", type=int, default=250)
    ap.add_argument("--keywords", action="store_true")
    ap.add_argument("--keywords-n", type=int, default=7)
    ap.add_argument("-o", "--output")
    args = ap.parse_args()

    p = pathlib.Path(args.file)
    if not p.exists():
        print(f"[ERR] {p} non trovato", file=sys.stderr)
        return 2

    text = p.read_text(encoding="utf-8")
    sections = extract_sections(text)

    intro = ""
    concl = ""
    topic_sentences = []

    for title, body in sections:
        tl = title.lower()
        if any(k in tl for k in ("introduzione", "introduction", "abstract")):
            intro = " ".join(first_sentence(p_) for p_ in body.split("\n\n")[:2] if p_.strip())
        elif any(k in tl for k in ("conclusion", "conclusioni")):
            paragraphs = [p_ for p_ in body.split("\n\n") if p_.strip()]
            concl = " ".join(first_sentence(p_) for p_ in paragraphs[:2])
        else:
            topic_sentences.append(first_sentence(body))

    parts = [intro] if intro else []
    parts.extend(topic_sentences[:5])
    if concl:
        parts.append(concl)
    combined = " ".join(p_ for p_ in parts if p_).strip()
    abstract = trim_to_words(combined, args.words)

    out_lines = ["## Abstract\n", abstract, ""]
    if args.keywords:
        keywords = extract_keywords(text, args.keywords_n)
        out_lines.append(f"**Parole chiave:** {', '.join(keywords)}")

    result = "\n".join(out_lines)
    if args.output:
        pathlib.Path(args.output).write_text(result, encoding="utf-8")
        print(f"[OK] {args.output}")
    else:
        print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())

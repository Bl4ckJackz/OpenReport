#!/usr/bin/env python3
"""readability.py — calcola Gulpease (IT) e Flesch (EN) per ogni sezione di un .md/.tex.

Usage:
  readability.py <file> [--lang=it|en] [--per-section]

Output: tabella sezione → score → giudizio.
Exit: 0 sempre (informational, non bloccante). Il consumer (self-check.sh) decide.
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path


VOWELS_IT = set("aeiouàèéìòùAEIOUÀÈÉÌÒÙ")
VOWELS_EN = set("aeiouAEIOU")


def split_sections(text: str) -> list[tuple[str, str]]:
    """Split markdown by H1/H2 headings; LaTeX by \\section/\\subsection."""
    sections = []
    current_title = "PROEMIO"
    current_buf: list[str] = []
    for line in text.splitlines():
        m_md = re.match(r"^(#{1,3})\s+(.+)$", line)
        m_tex = re.match(r"^\\(section|subsection|chapter)\*?\{(.+?)\}", line)
        if m_md or m_tex:
            sections.append((current_title, "\n".join(current_buf)))
            current_title = (m_md.group(2) if m_md else m_tex.group(2))[:60]
            current_buf = []
        else:
            current_buf.append(line)
    sections.append((current_title, "\n".join(current_buf)))
    return [(t, b) for t, b in sections if b.strip()]


def count_syllables_it(word: str) -> int:
    """Approssimazione: gruppi vocalici contigui."""
    word = word.lower()
    syl, prev_v = 0, False
    for ch in word:
        is_v = ch in VOWELS_IT
        if is_v and not prev_v:
            syl += 1
        prev_v = is_v
    return max(syl, 1)


def count_syllables_en(word: str) -> int:
    word = word.lower().strip(".,;:!?()[]\"'")
    if not word:
        return 0
    syl, prev_v = 0, False
    for ch in word:
        is_v = ch in VOWELS_EN
        if is_v and not prev_v:
            syl += 1
        prev_v = is_v
    if word.endswith("e") and syl > 1:
        syl -= 1
    return max(syl, 1)


def gulpease(text: str) -> float:
    """Indice Gulpease per italiano. Range 0-100. Target adulti formali: 50-70."""
    sentences = re.split(r"[.!?]+", text)
    sentences = [s for s in sentences if s.strip()]
    words = re.findall(r"\b\w+\b", text)
    if not words:
        return 0.0
    n_chars = sum(len(w) for w in words)
    n_words = len(words)
    n_sent = max(len(sentences), 1)
    return 89 + (300 * n_sent - 10 * n_chars) / n_words


def flesch_reading_ease(text: str) -> float:
    """Flesch Reading Ease per inglese. Range 0-100. Target accademico: 30-50."""
    sentences = re.split(r"[.!?]+", text)
    sentences = [s for s in sentences if s.strip()]
    words = re.findall(r"\b[a-zA-Z']+\b", text)
    if not words or not sentences:
        return 0.0
    syllables = sum(count_syllables_en(w) for w in words)
    n_words = len(words)
    n_sent = len(sentences)
    return 206.835 - 1.015 * (n_words / n_sent) - 84.6 * (syllables / n_words)


def grade_it(score: float) -> str:
    if score < 40: return "MOLTO DIFFICILE"
    if score < 60: return "FORMALE / ACCADEMICO"
    if score < 80: return "DIVULGATIVO"
    return "TROPPO SEMPLICE"


def grade_en(score: float) -> str:
    if score < 30: return "VERY DIFFICULT (academic)"
    if score < 50: return "DIFFICULT (formal)"
    if score < 70: return "STANDARD"
    return "EASY"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("file")
    p.add_argument("--lang", choices=["it", "en"], default="it")
    p.add_argument("--per-section", action="store_true", default=True)
    args = p.parse_args()

    text = Path(args.file).read_text(encoding="utf-8")
    sections = split_sections(text)

    print(f"=== READABILITY: {args.file} ({args.lang.upper()}) ===\n")
    print(f"{'Sezione':<50} {'Parole':>8} {'Score':>8}  Giudizio")
    print("-" * 100)

    fn = gulpease if args.lang == "it" else flesch_reading_ease
    grade_fn = grade_it if args.lang == "it" else grade_en

    for title, body in sections:
        n_words = len(re.findall(r"\b\w+\b", body))
        if n_words < 30:
            continue
        score = fn(body)
        print(f"{title[:50]:<50} {n_words:>8} {score:>8.1f}  {grade_fn(score)}")

    overall = fn(text)
    print("-" * 100)
    print(f"{'OVERALL':<50} {len(re.findall(r'\b\w+\b', text)):>8} {overall:>8.1f}  {grade_fn(overall)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

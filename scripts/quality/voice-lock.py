#!/usr/bin/env python3
"""voice-lock.py — estrae voice profile dalla prima sezione e salva in session-state.

Modalità:
  --extract  → legge file e prima sezione, salva profilo in session-state.json
  --verify   → confronta ogni sezione vs profilo locked, ritorna WARN se drift

Usage:
  voice-lock.py extract <file> --state <session-state.json>
  voice-lock.py verify  <file> --state <session-state.json> [--threshold=0.30]
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path
from collections import Counter


PERSON_PATTERNS = {
    "prima-singolare": [r"\b(ho|sono|mio|mia|mi)\b", r"\b(faccio|vado|penso)\b"],
    "prima-plurale":  [r"\b(abbiamo|siamo|nostro|nostra|ci)\b", r"\b(facciamo|andiamo|pensiamo)\b"],
    "impersonale":    [r"\bsi (è|sono|sta|stanno)\b", r"\bè (stato|stata)\b"],
    "terza":          [r"\b(esso|essa|loro)\b"],
}


def split_sections(text: str) -> list[tuple[str, str]]:
    sections, title, buf = [], "PROEMIO", []
    for line in text.splitlines():
        m = re.match(r"^(#{1,3})\s+(.+)$", line) or re.match(
            r"^\\(section|subsection|chapter)\*?\{(.+?)\}", line)
        if m:
            sections.append((title, "\n".join(buf)))
            title, buf = (m.group(2)[:60]), []
        else:
            buf.append(line)
    sections.append((title, "\n".join(buf)))
    return [(t, b) for t, b in sections if b.strip() and len(re.findall(r"\b\w+\b", b)) > 100]


def dominant_person(text: str) -> str:
    counts = {k: sum(len(re.findall(p, text, re.IGNORECASE)) for p in v)
              for k, v in PERSON_PATTERNS.items()}
    if max(counts.values()) == 0: return "impersonale"
    return max(counts, key=counts.get)


def avg_sentence_len(text: str) -> float:
    sents = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    if not sents: return 0
    return sum(len(re.findall(r"\b\w+\b", s)) for s in sents) / len(sents)


def lexical_markers(text: str, top_n: int = 20) -> list[str]:
    """Parole tematiche ricorrenti (esclude stopword IT)."""
    stop = {"il", "lo", "la", "i", "gli", "le", "un", "uno", "una", "di", "a", "da", "in", "con",
            "su", "per", "tra", "fra", "e", "o", "ma", "che", "non", "è", "sono", "ho", "ha", "si",
            "del", "della", "dei", "delle", "al", "alla", "alle", "ai", "agli", "nel", "nella",
            "questo", "questa", "quello", "quella", "come", "anche", "più", "meno", "molto", "essere",
            "stato", "stata", "stati", "state", "essendo"}
    words = [w.lower() for w in re.findall(r"\b[a-zàèéìòù]{4,}\b", text)]
    common = [w for w, _ in Counter(w for w in words if w not in stop).most_common(top_n)]
    return common


def subordinate_density(text: str) -> float:
    sents = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    if not sents: return 0
    return text.count(",") / len(sents)


def extract_profile(text: str) -> dict:
    return {
        "avg_sentence_length": round(avg_sentence_len(text), 2),
        "person": dominant_person(text),
        "lexical_markers": lexical_markers(text),
        "subordinate_density": round(subordinate_density(text), 2),
    }


def load_state(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def save_state(path: Path, state: dict) -> None:
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def cmd_extract(args) -> int:
    text = Path(args.file).read_text(encoding="utf-8")
    sections = split_sections(text)
    if not sections:
        print("ERROR: nessuna sezione abbastanza lunga (>100 parole)", file=sys.stderr)
        return 2
    title, body = sections[0]
    profile = extract_profile(body)
    state = load_state(Path(args.state))
    state["voice_profile"] = profile
    save_state(Path(args.state), state)
    print(f"Voice profile estratto da '{title}':")
    print(json.dumps(profile, indent=2, ensure_ascii=False))
    return 0


def cmd_verify(args) -> int:
    state = load_state(Path(args.state))
    profile = state.get("voice_profile")
    if not profile:
        print("ERROR: nessun voice_profile in state. Esegui prima 'extract'.", file=sys.stderr)
        return 2

    text = Path(args.file).read_text(encoding="utf-8")
    sections = split_sections(text)
    print(f"=== VOICE LOCK VERIFY (baseline: avg-sent={profile['avg_sentence_length']}, persona={profile['person']}) ===\n")

    warns = 0
    for title, body in sections:
        m = extract_profile(body)
        flags = []
        delta_sent = abs(m["avg_sentence_length"] - profile["avg_sentence_length"]) / max(profile["avg_sentence_length"], 1)
        if delta_sent > args.threshold:
            flags.append(f"avg-sent {m['avg_sentence_length']} (locked {profile['avg_sentence_length']}, Δ{delta_sent*100:.0f}%)")
        if m["person"] != profile["person"]:
            flags.append(f"persona '{m['person']}' (locked '{profile['person']}')")
        delta_sub = abs(m["subordinate_density"] - profile["subordinate_density"]) / max(profile["subordinate_density"], 1)
        if delta_sub > args.threshold + 0.1:
            flags.append(f"sub-density Δ{delta_sub*100:.0f}%")

        if flags:
            warns += 1
            print(f"[WARN] '{title}': " + "; ".join(flags))
        else:
            print(f"[OK]   '{title}'")

    print(f"\nTotale WARN: {warns}/{len(sections)}")
    return 1 if warns > 0 else 0


def main() -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    pe = sub.add_parser("extract")
    pe.add_argument("file")
    pe.add_argument("--state", required=True)
    pv = sub.add_parser("verify")
    pv.add_argument("file")
    pv.add_argument("--state", required=True)
    pv.add_argument("--threshold", type=float, default=0.30)
    args = p.parse_args()
    return cmd_extract(args) if args.cmd == "extract" else cmd_verify(args)


if __name__ == "__main__":
    sys.exit(main())

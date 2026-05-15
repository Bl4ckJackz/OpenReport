"""Tests for scripts/workflow/redline-generator.py CLI."""
from __future__ import annotations

import subprocess
from pathlib import Path

FIXTURES_REL = Path("tests/fixtures/redline")


def _run(python: str, repo_root: Path, baseline: Path, current: Path, out: Path, mode: str = "word", max_spans: int | None = None) -> subprocess.CompletedProcess:
    script = repo_root / "scripts" / "workflow" / "redline-generator.py"
    cmd = [python, str(script), str(baseline), str(current), "-o", str(out), "--mode", mode]
    if max_spans is not None:
        cmd.extend(["--max-spans", str(max_spans)])
    return subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)


def test_word_insertion_produces_critic_ins(tmp_path, repo_root, python):
    baseline = repo_root / FIXTURES_REL / "simple_baseline.md"
    current = repo_root / FIXTURES_REL / "simple_current.md"
    out = tmp_path / "out.md"
    _run(python, repo_root, baseline, current, out)
    text = out.read_text(encoding="utf-8")
    # word-level insert can land as {++nuovo ++}, {++nuovo++}, or {++ nuovo++} depending on
    # whether the adjacent space is grouped before or after the inserted word or not at all.
    assert "{++nuovo " in text or "{++nuovo++}" in text or "{++ nuovo" in text
    assert "{++molto " in text or "{++molto++}" in text or "{++ molto" in text
    assert "Il" in text and "prodotto" in text


def test_short_replace_collapses_to_substitution(tmp_path, repo_root, python):
    baseline = tmp_path / "b.md"
    current = tmp_path / "c.md"
    baseline.write_text("La casa è grande.", encoding="utf-8")
    current.write_text("La villa è grande.", encoding="utf-8")
    out = tmp_path / "out.md"
    _run(python, repo_root, baseline, current, out)
    text = out.read_text(encoding="utf-8")
    assert "{~~casa~>villa~~}" in text
    assert "{--casa--}" not in text
    assert "{++villa++}" not in text


def test_long_replace_stays_as_del_plus_ins(tmp_path, repo_root, python):
    # Replace 1 word with 9 completely unique words: new_token_count > SUBSTITUTION_MAX_TOKENS=8
    # so difflib emits a single replace opcode that exceeds the threshold.
    baseline = tmp_path / "b.md"
    current = tmp_path / "c.md"
    baseline.write_text("parola.", encoding="utf-8")
    current.write_text(
        "aaabbb cccddd eeefff ggghhh iiijjj kkkmmm nnnppp qqqrrr sssttt.", encoding="utf-8"
    )
    out = tmp_path / "out.md"
    _run(python, repo_root, baseline, current, out)
    text = out.read_text(encoding="utf-8")
    assert "{--" in text
    assert "{++" in text
    assert "{~~" not in text


# --- A3: Paragraph-level block rewrite threshold ---

def test_paragraph_70pct_changed_becomes_block_rewrite(tmp_path, repo_root, python):
    baseline = tmp_path / "b.md"
    current = tmp_path / "c.md"
    baseline.write_text(
        "Alfa beta gamma delta epsilon zeta eta theta iota kappa.\n",
        encoding="utf-8",
    )
    current.write_text(
        "Uno due tre quattro cinque sei sette otto nove dieci.\n",
        encoding="utf-8",
    )
    out = tmp_path / "out.md"
    _run(python, repo_root, baseline, current, out)
    text = out.read_text(encoding="utf-8")
    # 70%+ changed: entire paragraph is deleted + inserted as a block (exactly one {-- and one {++)
    assert text.count("{--") == 1
    assert text.count("{++") == 1


def test_paragraph_30pct_changed_keeps_granular_diff(tmp_path, repo_root, python):
    baseline = tmp_path / "b.md"
    current = tmp_path / "c.md"
    baseline.write_text(
        "Alfa beta gamma delta epsilon zeta eta theta iota kappa.\n",
        encoding="utf-8",
    )
    current.write_text(
        "Alfa beta gamma delta NUOVO zeta eta theta iota kappa.\n",
        encoding="utf-8",
    )
    out = tmp_path / "out.md"
    _run(python, repo_root, baseline, current, out)
    text = out.read_text(encoding="utf-8")
    # Only ~10% changed: granular diff should mark just the changed word
    assert "{--epsilon--}" in text or "{~~epsilon~>NUOVO~~}" in text


# --- A4: Sentence-mode fallback ---

def test_sentence_mode_does_not_emit_intra_sentence_spans(tmp_path, repo_root, python):
    baseline = tmp_path / "b.md"
    current = tmp_path / "c.md"
    baseline.write_text("Frase uno. Frase due originale.\n", encoding="utf-8")
    current.write_text("Frase uno. Frase due modificata.\n", encoding="utf-8")
    out = tmp_path / "out.md"
    _run(python, repo_root, baseline, current, out, mode="sentence")
    text = out.read_text(encoding="utf-8")
    # Sentence mode: entire changed sentence is deleted + inserted (no intra-sentence spans)
    assert "{--Frase due originale.--}" in text
    assert "{++Frase due modificata.++}" in text
    assert "{--originale--}" not in text
    assert "{++modificata++}" not in text

"""Tests for scripts/workflow/redline-generator.py CLI."""
from __future__ import annotations

import subprocess
from pathlib import Path

FIXTURES_REL = Path("tests/fixtures/redline")


def _run(python: str, repo_root: Path, baseline: Path, current: Path, out: Path, mode: str = "word") -> subprocess.CompletedProcess:
    script = repo_root / "scripts" / "workflow" / "redline-generator.py"
    return subprocess.run(
        [python, str(script), str(baseline), str(current), "-o", str(out), "--mode", mode],
        capture_output=True, text=True, check=True, timeout=30,
    )


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

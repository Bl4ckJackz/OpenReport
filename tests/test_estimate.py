"""Smoke test for scripts/workflow/estimate.py."""
from __future__ import annotations

import json
import subprocess


def test_estimate_human_runs(repo_root, python):
    script = repo_root / "scripts" / "workflow" / "estimate.py"
    assert script.exists(), f"estimate.py not found at {script}"

    res = subprocess.run(
        [python, str(script), "--tipologia", "tecnica", "--pages", "30"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert res.returncode == 0, f"estimate failed: {res.stderr}"
    assert "Token usage" in res.stdout
    assert "Context-window pressure" in res.stdout


def test_estimate_json_runs(repo_root, python):
    script = repo_root / "scripts" / "workflow" / "estimate.py"
    res = subprocess.run(
        [python, str(script), "--pages", "50", "--online", "--json"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert res.returncode == 0, f"estimate --json failed: {res.stderr}"

    payload = json.loads(res.stdout)
    assert {"input", "tokens", "context_pressure", "minutes", "recommendations"} <= payload.keys()

    tokens = payload["tokens"]
    assert tokens["input_tokens"] > 0
    assert tokens["output_tokens"] > 0
    assert tokens["total_tokens"] == tokens["input_tokens"] + tokens["output_tokens"]

    pressure = payload["context_pressure"]
    assert 0 < pressure["peak_percent"] <= 100
    assert pressure["verdict"] in {
        "comfortable", "moderate",
        "tight — consider Pausa + /clear at checkpoints",
        "over budget — split in 2 sessions or use --draft-only",
    }


def test_estimate_outline_first_reduces_output(repo_root, python):
    """Outline-first should reduce output tokens for pages >= 30."""
    script = repo_root / "scripts" / "workflow" / "estimate.py"

    def run(args: list[str]) -> dict:
        res = subprocess.run(
            [python, str(script), "--pages", "60", "--json", *args],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert res.returncode == 0
        return json.loads(res.stdout)

    baseline = run([])
    with_outline = run(["--outline-first"])

    assert with_outline["tokens"]["output_tokens"] < baseline["tokens"]["output_tokens"], (
        "outline-first should reduce output tokens for pages >= 30"
    )


def test_estimate_pages_required(repo_root, python):
    script = repo_root / "scripts" / "workflow" / "estimate.py"
    res = subprocess.run(
        [python, str(script)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert res.returncode != 0, "estimate should fail without --pages"


def test_estimate_pages_must_be_positive(repo_root, python):
    script = repo_root / "scripts" / "workflow" / "estimate.py"
    res = subprocess.run(
        [python, str(script), "--pages", "0"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert res.returncode != 0, "estimate should reject pages=0"

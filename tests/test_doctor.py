"""Smoke test for scripts/workflow/doctor.py."""
from __future__ import annotations

import json
import subprocess


def test_doctor_json_runs(repo_root, python):
    script = repo_root / "scripts" / "workflow" / "doctor.py"
    assert script.exists(), f"doctor.py not found at {script}"

    res = subprocess.run(
        [python, str(script), "--json"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    # exit code may be 1 if a required tool is missing — that's still a valid run
    assert res.returncode in (0, 1), f"unexpected exit code: {res.stderr}"

    payload = json.loads(res.stdout)
    assert isinstance(payload, list) and payload, "doctor produced empty result"

    expected_keys = {"name", "kind", "category", "found", "version", "install_hint"}
    for entry in payload:
        assert expected_keys <= entry.keys(), f"missing keys in {entry}"
        assert entry["kind"] in {"required", "recommended", "optional"}


def test_doctor_human_runs(repo_root, python):
    script = repo_root / "scripts" / "workflow" / "doctor.py"
    res = subprocess.run(
        [python, str(script)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert "relazione-doctor" in res.stdout
    assert res.returncode in (0, 1)

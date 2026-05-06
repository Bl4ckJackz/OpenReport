"""All Python scripts must at least import cleanly (no syntax / collect errors).

This is a smoke test that catches scripts broken by a refactor. It does NOT
execute the scripts — it parses them.
"""
from __future__ import annotations

import ast
from pathlib import Path

SCRIPTS_DIR = "scripts"


def _python_scripts(repo_root: Path) -> list[Path]:
    return sorted((repo_root / SCRIPTS_DIR).rglob("*.py"))


def test_all_scripts_have_shebang(repo_root):
    missing: list[str] = []
    for f in _python_scripts(repo_root):
        first_line = f.read_text(errors="ignore").splitlines()[:1]
        if not first_line or not first_line[0].startswith("#!"):
            missing.append(str(f.relative_to(repo_root)))
    assert not missing, f"missing shebang in: {missing}"


def test_all_scripts_parse(repo_root):
    errors: list[str] = []
    for f in _python_scripts(repo_root):
        try:
            ast.parse(f.read_text(errors="ignore"), filename=str(f))
        except SyntaxError as e:
            errors.append(f"{f.relative_to(repo_root)}: {e.msg} (line {e.lineno})")
    assert not errors, "syntax errors:\n  " + "\n  ".join(errors)

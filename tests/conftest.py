"""Shared pytest fixtures."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def python() -> str:
    return sys.executable


@pytest.fixture(scope="session")
def bash_exe() -> str:
    """Return the path to bash, preferring Git Bash on Windows."""
    exe = shutil.which("bash")
    if exe is None:
        pytest.skip("bash not found on PATH")
    return exe

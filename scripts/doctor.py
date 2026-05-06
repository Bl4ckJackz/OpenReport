#!/usr/bin/env python3
"""
relazione-doctor — diagnose environment for the relazione skill.

Checks required and optional dependencies, prints a status table, and
exits non-zero if any REQUIRED tool is missing.

Usage:
    python scripts/doctor.py            # human-readable
    python scripts/doctor.py --json     # machine-readable
    python scripts/doctor.py --fix      # print install hints for missing tools
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass, asdict
from typing import Callable


@dataclass
class Check:
    name: str
    kind: str           # "required" | "recommended" | "optional"
    category: str       # "core" | "export" | "quality" | "integration"
    found: bool
    version: str | None
    install_hint: str


def run(cmd: list[str]) -> tuple[bool, str]:
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        return out.returncode == 0, (out.stdout or out.stderr).strip().splitlines()[0] if (out.stdout or out.stderr) else ""
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False, ""


def has(binary: str) -> bool:
    return shutil.which(binary) is not None


def py_module(name: str) -> tuple[bool, str]:
    try:
        mod = __import__(name)
        return True, getattr(mod, "__version__", "installed")
    except ImportError:
        return False, ""


def check_python() -> Check:
    v = sys.version_info
    ok = v >= (3, 10)
    return Check(
        "Python >= 3.10", "required", "core", ok,
        f"{v.major}.{v.minor}.{v.micro}",
        "Install Python 3.10+ from https://python.org",
    )


def check_binary(name: str, kind: str, category: str, hint: str, version_flag: str = "--version") -> Check:
    if not has(name):
        return Check(name, kind, category, False, None, hint)
    ok, ver = run([name, version_flag])
    return Check(name, kind, category, True, ver or "found", hint)


def check_pymod(name: str, kind: str, category: str, hint: str) -> Check:
    ok, ver = py_module(name)
    return Check(f"python:{name}", kind, category, ok, ver, hint)


CHECKS: list[Callable[[], Check]] = [
    check_python,
    lambda: check_binary("pandoc", "recommended", "export",
                         "https://pandoc.org/installing.html"),
    lambda: check_binary("git", "recommended", "core",
                         "https://git-scm.com/downloads"),
    lambda: check_binary("xelatex", "optional", "export",
                         "Install TeX Live (https://tug.org/texlive/)"),
    lambda: check_binary("wkhtmltopdf", "optional", "export",
                         "https://wkhtmltopdf.org/downloads.html"),
    lambda: check_binary("ffmpeg", "optional", "export",
                         "https://ffmpeg.org/download.html"),
    lambda: check_binary("hunspell", "optional", "quality",
                         "apt install hunspell  /  brew install hunspell"),
    lambda: check_binary("languagetool", "optional", "quality",
                         "https://languagetool.org/download/"),
    lambda: check_pymod("yaml", "required", "core", "pip install pyyaml"),
    lambda: check_pymod("jsonschema", "required", "core", "pip install jsonschema"),
    lambda: check_pymod("requests", "recommended", "integration", "pip install requests"),
    lambda: check_pymod("docx", "optional", "export", "pip install python-docx"),
    lambda: check_pymod("pypdf", "optional", "export", "pip install pypdf"),
    lambda: check_pymod("reportlab", "optional", "export", "pip install reportlab"),
]


KIND_GLYPH = {"required": "REQ", "recommended": "REC", "optional": "OPT"}


def render_human(checks: list[Check]) -> int:
    by_cat: dict[str, list[Check]] = {}
    for c in checks:
        by_cat.setdefault(c.category, []).append(c)

    print("relazione-doctor — environment check\n")
    missing_required = 0
    for cat, items in by_cat.items():
        print(f"== {cat.upper()} ==")
        for c in items:
            mark = "OK " if c.found else "-- "
            ver = f" ({c.version})" if c.version else ""
            print(f"  {mark} [{KIND_GLYPH[c.kind]}] {c.name}{ver}")
            if not c.found and c.kind == "required":
                missing_required += 1
            if not c.found:
                print(f"        hint: {c.install_hint}")
        print()

    if missing_required:
        print(f"FAIL — {missing_required} required tool(s) missing.")
        return 1
    print("OK — all required tools available.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="emit JSON instead of human output")
    args = ap.parse_args()

    results = [c() for c in CHECKS]

    if args.json:
        json.dump([asdict(r) for r in results], sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0 if all(r.found for r in results if r.kind == "required") else 1

    return render_human(results)


if __name__ == "__main__":
    sys.exit(main())

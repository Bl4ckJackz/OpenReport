"""Tests for scripts/export/critic-to-latex.py and critic-to-typst.py filters."""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

import pytest


def _critic_md_to_json(md: str) -> str:
    """Convert CriticMarkup markdown to pandoc JSON AST.

    Pandoc 3.x does not support the critic_markup extension for markdown.
    We pre-convert CriticMarkup syntax to pandoc native bracketed_spans so
    that the Span nodes with critic-add / critic-del classes appear in the AST
    exactly as the filters expect them.

    Substitution {~~old~>new~~} is emitted as adjacent critic-del + critic-add
    spans, which matches the adjacent-pair pattern the filters collapse into
    replaced / #repl.
    """
    # {~~old~>new~~} must be converted before the simpler patterns
    md = re.sub(r"\{~~(.+?)~>(.+?)~~\}", r"[\1]{.critic-del}[\2]{.critic-add}", md, flags=re.DOTALL)
    md = re.sub(r"\{\+\+(.+?)\+\+\}", r"[\1]{.critic-add}", md, flags=re.DOTALL)
    md = re.sub(r"\{--(.+?)--\}", r"[\1]{.critic-del}", md, flags=re.DOTALL)
    return subprocess.run(
        ["pandoc", "-f", "markdown", "-t", "json"],
        input=md, capture_output=True, text=True, check=True,
    ).stdout


def _run_filter(python: str, filter_path: Path, ast_json: str, env=None) -> str:
    return subprocess.run(
        [python, str(filter_path)],
        input=ast_json, capture_output=True, text=True, check=True, env=env,
    ).stdout


def _pandoc_json_to(fmt: str, ast_json: str) -> str:
    return subprocess.run(
        ["pandoc", "-f", "json", "-t", fmt],
        input=ast_json, capture_output=True, text=True, check=True,
    ).stdout


def test_latex_filter_emits_added_deleted_replaced(repo_root, python):
    filter_path = repo_root / "scripts" / "export" / "critic-to-latex.py"
    md = "Pre {++inserito++} medio {--cancellato--} {~~vecchio~>nuovo~~} fine.\n"
    ast = _critic_md_to_json(md)
    filtered = _run_filter(python, filter_path, ast)
    latex = _pandoc_json_to("latex", filtered)
    assert "\\added{inserito}" in latex
    assert "\\deleted{cancellato}" in latex
    assert "\\replaced{nuovo}{vecchio}" in latex


def test_latex_filter_soul_fallback(repo_root, python):
    filter_path = repo_root / "scripts" / "export" / "critic-to-latex.py"
    md = "Pre {++inserito++} medio {--cancellato--} fine.\n"
    ast = _critic_md_to_json(md)
    env = {**os.environ, "REDLINE_LATEX_FALLBACK": "soul"}
    filtered = _run_filter(python, filter_path, ast, env=env)
    latex = _pandoc_json_to("latex", filtered)
    assert "\\uline{inserito}" in latex
    assert "\\sout{cancellato}" in latex


def test_typst_filter_emits_ins_del_repl(repo_root, python):
    filter_path = repo_root / "scripts" / "export" / "critic-to-typst.py"
    md = "Pre {++inserito++} medio {--cancellato--} {~~vecchio~>nuovo~~} fine.\n"
    ast = _critic_md_to_json(md)
    filtered = _run_filter(python, filter_path, ast)
    typst = _pandoc_json_to("typst", filtered)
    assert "#ins[inserito]" in typst
    assert "#del[cancellato]" in typst
    assert "#repl[nuovo][vecchio]" in typst

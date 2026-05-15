# Relazione Redline (Track-Changes) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Word-style track-changes (`<ins>` underlined / `<del>` strikethrough) to /relazione live HTML preview and to the four canonical export formats (HTML, Typst PDF, LaTeX PDF, DOCX) using CriticMarkup as the single intermediate format.

**Architecture:** A deterministic Python diff engine (`redline-generator.py`) emits CriticMarkup spans (`{++ins++}` / `{--del--}` / `{~~old~>new~~}`) from two markdown files. Two pandoc filters translate CriticMarkup into LaTeX (`changes` package) and Typst (`#ins[]`/`#del[]`) macros. Pandoc consumes CriticMarkup natively for HTML and produces native Word revisions for DOCX. Export scripts gain a `--redline` flag that swaps the input from clean to redlined; lifecycle commands (`/relazione-review`, `/relazione-approve`) manage baseline snapshots and a `redline` block in `session-state.json`.

**Tech Stack:** Python 3 (stdlib `difflib`, `argparse`, `re`, `json`, `pathlib`), pandoc ≥ 2.x (`markdown+critic_markup`, JSON AST filters), LaTeX `changes` package (with `soul` fallback), Typst, bash. Tests with pytest (added by Task 1).

**Spec:** `docs/specs/2026-05-15-relazione-redline-design.md`

**Repo conventions (read before implementing):**
- Scripts use `kebab-case.py` filenames — they are CLI entry points, not importable modules. Tests invoke them via `subprocess.run([python, str(script), ...])` (pattern: `tests/test_doctor.py`). Do **not** rename to `snake_case.py` and do **not** add `scripts/` to `sys.path`.
- Existing `tests/conftest.py` provides `repo_root` and `python` session fixtures. Use them. Do **not** add a second conftest that mutates `sys.path`.
- Tests in this plan that show `import redline_generator as rg` etc. are simplified — actual implementation must use `subprocess.run` invocations against the CLI and assert on stdout/stderr/output files.
- Sourced helpers at `scripts/_check-pandoc-critic.sh` and `scripts/_resolve-baseline.sh` are referenced from subdirs as `$(dirname "${BASH_SOURCE[0]}")/../_*.sh`. Verify this works after every script edit.
- The `redline-generator.py` CLI lives in `scripts/workflow/`. Other-subdir callers (e.g. `scripts/export/parallel-export.sh`) invoke it via `$(dirname "${BASH_SOURCE[0]}")/../workflow/redline-generator.py`.

---

## File Structure

**New files:**

| Path | Responsibility |
|---|---|
| `scripts/workflow/redline-generator.py` | Word/sentence-level diff of two `.md` → CriticMarkup output. Pure function over file paths, no format knowledge. |
| `scripts/export/critic-to-latex.py` | Pandoc JSON-AST filter: `{++X++}` → `\added{X}`, `{--Y--}` → `\deleted{Y}`, `{~~A~>B~~}` → `\replaced{B}{A}` (with `soul` fallback). |
| `scripts/export/critic-to-typst.py` | Pandoc JSON-AST filter: same three patterns → `#ins[]` / `#del[]` / `#repl[][]` Typst calls. |
| `scripts/_check-pandoc-critic.sh` | Sourced helper at `scripts/` root: verifies pandoc supports `critic_markup`. Callers in subdirs use `$(dirname BASH_SOURCE)/../_check-pandoc-critic.sh`. |
| `scripts/_resolve-baseline.sh` | Sourced helper at `scripts/` root: resolves baseline path for a session. Callers in subdirs use `$(dirname BASH_SOURCE)/../_resolve-baseline.sh`. |
| `commands/relazione-redline.md` | User-facing command for on-demand redline outside the review cycle. |
| `tests/conftest.py` | Pytest config: sets `sys.path` to include `scripts/`. |
| `tests/__init__.py` | Empty marker. |
| `tests/fixtures/redline/*.md` | Test fixtures (baseline + current pairs). |
| `tests/test_redline_generator.py` | Unit tests for diff engine. |
| `tests/test_critic_filters.py` | Unit tests for the two pandoc filters. |
| `tests/test_regression_clean_export.py` | Regression: clean export byte-identity. |
| `tests/e2e/test_redline_pipeline.sh` | End-to-end test of full export pipeline. |

**Modified files:**

| Path | Change |
|---|---|
| `scripts/workflow/live-preview-draft.sh` | Add `--diff [baseline]` flag, dropdown header toggle, CSS for ins/del. (File ported from local working copy in setup commit; first repo presence.) |
| `scripts/export/export-html-standalone.sh` | Add `--redline` flag, consume `.redlined.md` when active. |
| `scripts/export/export-typst.sh` | Add `--redline` flag, inject Typst preamble, use `critic-to-typst.py` filter. |
| `scripts/export/parallel-export.sh` | Add `--redline` flag, route PDF through LaTeX `changes`, DOCX through `--track-changes=all`. |
| `commands/relazione-review.md` | Snapshot baseline, set `redline.enabled=true` in session-state. |
| `commands/relazione-approve.md` | Archive baseline, set `redline.enabled=false`. |
| `commands/relazione-help.md` | Add row for `/relazione-redline`. |
| `SKILL.md` | Document track-changes in Usability section. |
| `CHANGELOG.md` | Entry for new minor version. |
| `VERSION` | Bump from current to `2.6.0` (next minor after `2.5.1`). |

**Phase order:** A (core engine) → B (filters) → C (lifecycle) → D (exports) → E (docs+CLI) → F (regression).

---

## Phase A — Diff Engine (`redline-generator.py`)

### Task A0: Pytest scaffolding

**Files:**
- Create: `tests/conftest.py`
- Create: `tests/__init__.py`
- Create: `tests/fixtures/redline/` (directory)

- [ ] **Step 1: Create conftest.py to make scripts importable from tests**

`tests/conftest.py`:
```python
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
```

`tests/__init__.py`: empty file.

- [ ] **Step 2: Verify pytest discovers the directory**

Run: `cd ~/.claude/skills/relazione && python -m pytest tests/ -v`
Expected: `no tests ran` (exit code 5) — confirms discovery works without errors.

- [ ] **Step 3: Commit**

```bash
cd ~/.claude/skills/relazione
git add tests/conftest.py tests/__init__.py
git commit -m "test: add pytest scaffolding for relazione skill"
```

---

### Task A1: Tokenizer + minimal word-level diff producing CriticMarkup

**Files:**
- Create: `scripts/workflow/redline-generator.py`
- Create: `tests/test_redline_generator.py`
- Create: `tests/fixtures/redline/simple_baseline.md`, `tests/fixtures/redline/simple_current.md`

- [ ] **Step 1: Create simple fixtures**

`tests/fixtures/redline/simple_baseline.md`:
```
Il prodotto funziona bene.
```

`tests/fixtures/redline/simple_current.md`:
```
Il nuovo prodotto funziona molto bene.
```

- [ ] **Step 2: Write the failing test**

`tests/test_redline_generator.py`:
```python
from pathlib import Path
import redline_generator as rg

FIXTURES = Path(__file__).parent / "fixtures" / "redline"


def test_word_insertion_produces_critic_ins(tmp_path):
    baseline = FIXTURES / "simple_baseline.md"
    current = FIXTURES / "simple_current.md"
    out = tmp_path / "out.md"
    rg.generate(str(baseline), str(current), str(out), mode="word")
    text = out.read_text(encoding="utf-8")
    assert "{++nuovo ++}" in text or "{++nuovo++}" in text
    assert "{++molto ++}" in text or "{++molto++}" in text
    assert "Il" in text
    assert "prodotto" in text
```

- [ ] **Step 3: Run test, confirm failure**

Run: `python -m pytest tests/test_redline_generator.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'redline_generator'`.

- [ ] **Step 4: Write minimal implementation**

`scripts/workflow/redline-generator.py`:
```python
#!/usr/bin/env python3
"""redline-generator.py — word-level diff of two markdown files → CriticMarkup."""
from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

TOKEN_RE = re.compile(r"(\s+|[^\s\w]|\w+)")


def tokenize(text: str) -> list[str]:
    return [t for t in TOKEN_RE.findall(text) if t]


def diff_to_critic(baseline_tokens: list[str], current_tokens: list[str]) -> str:
    sm = difflib.SequenceMatcher(a=baseline_tokens, b=current_tokens, autojunk=False)
    out: list[str] = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        old = "".join(baseline_tokens[i1:i2])
        new = "".join(current_tokens[j1:j2])
        if tag == "equal":
            out.append(new)
        elif tag == "insert":
            out.append(f"{{++{new}++}}")
        elif tag == "delete":
            out.append(f"{{--{old}--}}")
        elif tag == "replace":
            out.append(f"{{--{old}--}}{{++{new}++}}")
    return "".join(out)


def generate(baseline_path: str, current_path: str, out_path: str, mode: str = "word") -> dict:
    baseline = Path(baseline_path).read_text(encoding="utf-8")
    current = Path(current_path).read_text(encoding="utf-8")
    b_tokens = tokenize(baseline)
    c_tokens = tokenize(current)
    redlined = diff_to_critic(b_tokens, c_tokens)
    Path(out_path).write_text(redlined, encoding="utf-8")
    return {
        "baseline_tokens": len(b_tokens),
        "current_tokens": len(c_tokens),
        "mode": mode,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("baseline")
    ap.add_argument("current")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--mode", choices=["word", "sentence"], default="word")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args(argv)
    stats = generate(args.baseline, args.current, args.output, mode=args.mode)
    if args.verbose:
        print(f"[redline] mode={stats['mode']} baseline={stats['baseline_tokens']} current={stats['current_tokens']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Run test, confirm pass**

Run: `python -m pytest tests/test_redline_generator.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add scripts/workflow/redline-generator.py tests/test_redline_generator.py tests/fixtures/redline/simple_baseline.md tests/fixtures/redline/simple_current.md
git commit -m "feat(redline): word-level diff to CriticMarkup (minimal)"
```

---

### Task A2: Substitution collapse `{~~old~>new~~}`

**Files:**
- Modify: `scripts/workflow/redline-generator.py`
- Modify: `tests/test_redline_generator.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_redline_generator.py`:
```python
def test_short_replace_collapses_to_substitution(tmp_path):
    baseline = tmp_path / "b.md"
    current = tmp_path / "c.md"
    baseline.write_text("La casa è grande.", encoding="utf-8")
    current.write_text("La villa è grande.", encoding="utf-8")
    out = tmp_path / "out.md"
    rg.generate(str(baseline), str(current), str(out), mode="word")
    text = out.read_text(encoding="utf-8")
    assert "{~~casa~>villa~~}" in text
    assert "{--casa--}" not in text
    assert "{++villa++}" not in text


def test_long_replace_stays_as_del_plus_ins(tmp_path):
    baseline = tmp_path / "b.md"
    current = tmp_path / "c.md"
    baseline.write_text(
        "Uno due tre quattro cinque sei sette otto nove dieci.", encoding="utf-8"
    )
    current.write_text(
        "Alfa beta gamma delta epsilon zeta eta theta iota kappa.", encoding="utf-8"
    )
    out = tmp_path / "out.md"
    rg.generate(str(baseline), str(current), str(out), mode="word")
    text = out.read_text(encoding="utf-8")
    assert "{--" in text
    assert "{++" in text
    assert "{~~" not in text
```

- [ ] **Step 2: Run tests, confirm new ones fail**

Run: `python -m pytest tests/test_redline_generator.py -v`
Expected: 1 pass (Task A1), 2 fail (new tests).

- [ ] **Step 3: Implement substitution detection**

In `scripts/workflow/redline-generator.py`, replace the `diff_to_critic` function:
```python
SUBSTITUTION_MAX_TOKENS = 8


def diff_to_critic(baseline_tokens: list[str], current_tokens: list[str]) -> str:
    sm = difflib.SequenceMatcher(a=baseline_tokens, b=current_tokens, autojunk=False)
    out: list[str] = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        old = "".join(baseline_tokens[i1:i2])
        new = "".join(current_tokens[j1:j2])
        if tag == "equal":
            out.append(new)
        elif tag == "insert":
            out.append(f"{{++{new}++}}")
        elif tag == "delete":
            out.append(f"{{--{old}--}}")
        elif tag == "replace":
            old_token_count = i2 - i1
            new_token_count = j2 - j1
            if old_token_count <= SUBSTITUTION_MAX_TOKENS and new_token_count <= SUBSTITUTION_MAX_TOKENS:
                out.append(f"{{~~{old.strip()}~>{new.strip()}~~}}")
            else:
                out.append(f"{{--{old}--}}{{++{new}++}}")
    return "".join(out)
```

- [ ] **Step 4: Run tests, confirm all pass**

Run: `python -m pytest tests/test_redline_generator.py -v`
Expected: 3 pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/workflow/redline-generator.py tests/test_redline_generator.py
git commit -m "feat(redline): collapse short replacements to {~~old~>new~~}"
```

---

### Task A3: Span counter + paragraph-level block rewrite threshold

**Files:**
- Modify: `scripts/workflow/redline-generator.py`
- Modify: `tests/test_redline_generator.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_redline_generator.py`:
```python
def test_paragraph_70pct_changed_becomes_block_rewrite(tmp_path):
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
    rg.generate(str(baseline), str(current), str(out), mode="word")
    text = out.read_text(encoding="utf-8")
    assert text.count("{--") == 1
    assert text.count("{++") == 1


def test_paragraph_30pct_changed_keeps_granular_diff(tmp_path):
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
    rg.generate(str(baseline), str(current), str(out), mode="word")
    text = out.read_text(encoding="utf-8")
    assert "{--epsilon--}" in text or "{~~epsilon~>NUOVO~~}" in text
```

- [ ] **Step 2: Run tests, confirm new ones fail**

Run: `python -m pytest tests/test_redline_generator.py -v`
Expected: 3 pass, 1 fail (`test_paragraph_70pct_changed_becomes_block_rewrite`).

- [ ] **Step 3: Implement block-level threshold**

In `scripts/workflow/redline-generator.py`, add constants and a paragraph-split layer. Replace `generate` with:
```python
BLOCK_REWRITE_THRESHOLD = 0.7
PARAGRAPH_SPLIT_RE = re.compile(r"(\n\s*\n)")


def _diff_paragraph(b_text: str, c_text: str) -> str:
    b_tokens = tokenize(b_text)
    c_tokens = tokenize(c_text)
    sm = difflib.SequenceMatcher(a=b_tokens, b=c_tokens, autojunk=False)
    matching = sum(size for _, _, size in sm.get_matching_blocks())
    total = max(len(b_tokens), len(c_tokens))
    if total > 0 and (1.0 - matching / total) >= BLOCK_REWRITE_THRESHOLD:
        return f"{{--{b_text}--}}{{++{c_text}++}}"
    return diff_to_critic(b_tokens, c_tokens)


def generate(baseline_path: str, current_path: str, out_path: str, mode: str = "word") -> dict:
    baseline = Path(baseline_path).read_text(encoding="utf-8")
    current = Path(current_path).read_text(encoding="utf-8")
    b_parts = PARAGRAPH_SPLIT_RE.split(baseline)
    c_parts = PARAGRAPH_SPLIT_RE.split(current)
    b_paras = [p for p in b_parts if p and not PARAGRAPH_SPLIT_RE.fullmatch(p)]
    c_paras = [p for p in c_parts if p and not PARAGRAPH_SPLIT_RE.fullmatch(p)]
    b_seps = [p for p in b_parts if PARAGRAPH_SPLIT_RE.fullmatch(p)]
    sm = difflib.SequenceMatcher(a=b_paras, b=c_paras, autojunk=False)
    out_parts: list[str] = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for p in c_paras[j1:j2]:
                out_parts.append(p)
        elif tag == "insert":
            for p in c_paras[j1:j2]:
                out_parts.append(f"{{++{p}++}}")
        elif tag == "delete":
            for p in b_paras[i1:i2]:
                out_parts.append(f"{{--{p}--}}")
        elif tag == "replace":
            for b_para, c_para in zip(b_paras[i1:i2], c_paras[j1:j2]):
                out_parts.append(_diff_paragraph(b_para, c_para))
            extra_b = b_paras[i1 + (j2 - j1) : i2]
            extra_c = c_paras[j1 + (i2 - i1) : j2]
            for p in extra_b:
                out_parts.append(f"{{--{p}--}}")
            for p in extra_c:
                out_parts.append(f"{{++{p}++}}")
    sep = b_seps[0] if b_seps else "\n\n"
    redlined = sep.join(out_parts)
    Path(out_path).write_text(redlined, encoding="utf-8")
    n_ins = redlined.count("{++")
    n_del = redlined.count("{--")
    n_sub = redlined.count("{~~")
    return {
        "baseline_tokens": sum(len(tokenize(p)) for p in b_paras),
        "current_tokens": sum(len(tokenize(p)) for p in c_paras),
        "mode": mode,
        "ins_count": n_ins,
        "del_count": n_del,
        "sub_count": n_sub,
        "total_spans": n_ins + n_del + n_sub,
    }
```

- [ ] **Step 4: Run all tests**

Run: `python -m pytest tests/test_redline_generator.py -v`
Expected: 5 pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/workflow/redline-generator.py tests/test_redline_generator.py
git commit -m "feat(redline): paragraph-level block rewrite at 70% change threshold"
```

---

### Task A4: Sentence-mode fallback

**Files:**
- Modify: `scripts/workflow/redline-generator.py`
- Modify: `tests/test_redline_generator.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_redline_generator.py`:
```python
def test_sentence_mode_does_not_emit_intra_sentence_spans(tmp_path):
    baseline = tmp_path / "b.md"
    current = tmp_path / "c.md"
    baseline.write_text("Frase uno. Frase due originale.\n", encoding="utf-8")
    current.write_text("Frase uno. Frase due modificata.\n", encoding="utf-8")
    out = tmp_path / "out.md"
    rg.generate(str(baseline), str(current), str(out), mode="sentence")
    text = out.read_text(encoding="utf-8")
    assert "{--Frase due originale.--}" in text
    assert "{++Frase due modificata.++}" in text
    assert "{--originale--}" not in text
    assert "{++modificata++}" not in text
```

- [ ] **Step 2: Run test, confirm failure**

Run: `python -m pytest tests/test_redline_generator.py::test_sentence_mode_does_not_emit_intra_sentence_spans -v`
Expected: FAIL (current impl ignores `mode`).

- [ ] **Step 3: Add sentence splitter and route on mode**

In `scripts/workflow/redline-generator.py`, add after `PARAGRAPH_SPLIT_RE`:
```python
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def _diff_paragraph_sentence(b_text: str, c_text: str) -> str:
    b_sents = SENTENCE_SPLIT_RE.split(b_text)
    c_sents = SENTENCE_SPLIT_RE.split(c_text)
    sm = difflib.SequenceMatcher(a=b_sents, b=c_sents, autojunk=False)
    out: list[str] = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            out.extend(c_sents[j1:j2])
        elif tag == "insert":
            out.extend(f"{{++{s}++}}" for s in c_sents[j1:j2])
        elif tag == "delete":
            out.extend(f"{{--{s}--}}" for s in b_sents[i1:i2])
        elif tag == "replace":
            for b_s, c_s in zip(b_sents[i1:i2], c_sents[j1:j2]):
                out.append(f"{{--{b_s}--}}{{++{c_s}++}}")
            extra_b = b_sents[i1 + (j2 - j1) : i2]
            extra_c = c_sents[j1 + (i2 - i1) : j2]
            out.extend(f"{{--{s}--}}" for s in extra_b)
            out.extend(f"{{++{s}++}}" for s in extra_c)
    return " ".join(out)
```

Modify the per-paragraph replace branch in `generate` to dispatch on mode:
```python
        elif tag == "replace":
            for b_para, c_para in zip(b_paras[i1:i2], c_paras[j1:j2]):
                if mode == "sentence":
                    out_parts.append(_diff_paragraph_sentence(b_para, c_para))
                else:
                    out_parts.append(_diff_paragraph(b_para, c_para))
```

- [ ] **Step 4: Run all tests**

Run: `python -m pytest tests/test_redline_generator.py -v`
Expected: 6 pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/workflow/redline-generator.py tests/test_redline_generator.py
git commit -m "feat(redline): sentence-mode fallback for coarser diffs"
```

---

### Task A5: Hard-cap span escalation chain

**Files:**
- Modify: `scripts/workflow/redline-generator.py`
- Modify: `tests/test_redline_generator.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_redline_generator.py`:
```python
def test_escalation_word_to_sentence_when_cap_exceeded(tmp_path):
    baseline = tmp_path / "b.md"
    current = tmp_path / "c.md"
    b_lines = [f"Riga {i} con parole originali distinte qui." for i in range(200)]
    c_lines = [f"Riga {i} con vocaboli mutati differenti là." for i in range(200)]
    baseline.write_text("\n\n".join(b_lines), encoding="utf-8")
    current.write_text("\n\n".join(c_lines), encoding="utf-8")
    out = tmp_path / "out.md"
    stats = rg.generate(str(baseline), str(current), str(out), mode="word", max_spans=300)
    assert stats["mode"] in {"sentence", "block"}
    assert stats["total_spans"] <= 1200
```

- [ ] **Step 2: Run test, confirm failure**

Run: `python -m pytest tests/test_redline_generator.py::test_escalation_word_to_sentence_when_cap_exceeded -v`
Expected: FAIL (`max_spans` kwarg unknown, no escalation).

- [ ] **Step 3: Add escalation in generate()**

In `scripts/workflow/redline-generator.py`, replace the `generate` function signature and add the escalation wrapper. Rename the body of current `generate` to `_generate_once`:
```python
MAX_SPANS_DEFAULT = 5000


def _generate_once(baseline_path: str, current_path: str, mode: str) -> tuple[str, dict]:
    baseline = Path(baseline_path).read_text(encoding="utf-8")
    current = Path(current_path).read_text(encoding="utf-8")
    b_parts = PARAGRAPH_SPLIT_RE.split(baseline)
    c_parts = PARAGRAPH_SPLIT_RE.split(current)
    b_paras = [p for p in b_parts if p and not PARAGRAPH_SPLIT_RE.fullmatch(p)]
    c_paras = [p for p in c_parts if p and not PARAGRAPH_SPLIT_RE.fullmatch(p)]
    b_seps = [p for p in b_parts if PARAGRAPH_SPLIT_RE.fullmatch(p)]
    sm = difflib.SequenceMatcher(a=b_paras, b=c_paras, autojunk=False)
    out_parts: list[str] = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for p in c_paras[j1:j2]:
                out_parts.append(p)
        elif tag == "insert":
            for p in c_paras[j1:j2]:
                out_parts.append(f"{{++{p}++}}")
        elif tag == "delete":
            for p in b_paras[i1:i2]:
                out_parts.append(f"{{--{p}--}}")
        elif tag == "replace":
            for b_para, c_para in zip(b_paras[i1:i2], c_paras[j1:j2]):
                if mode == "block":
                    out_parts.append(f"{{--{b_para}--}}{{++{c_para}++}}")
                elif mode == "sentence":
                    out_parts.append(_diff_paragraph_sentence(b_para, c_para))
                else:
                    out_parts.append(_diff_paragraph(b_para, c_para))
            extra_b = b_paras[i1 + (j2 - j1) : i2]
            extra_c = c_paras[j1 + (i2 - i1) : j2]
            for p in extra_b:
                out_parts.append(f"{{--{p}--}}")
            for p in extra_c:
                out_parts.append(f"{{++{p}++}}")
    sep = b_seps[0] if b_seps else "\n\n"
    redlined = sep.join(out_parts)
    n_ins = redlined.count("{++")
    n_del = redlined.count("{--")
    n_sub = redlined.count("{~~")
    stats = {
        "baseline_tokens": sum(len(tokenize(p)) for p in b_paras),
        "current_tokens": sum(len(tokenize(p)) for p in c_paras),
        "mode": mode,
        "ins_count": n_ins,
        "del_count": n_del,
        "sub_count": n_sub,
        "total_spans": n_ins + n_del + n_sub,
    }
    return redlined, stats


def generate(
    baseline_path: str,
    current_path: str,
    out_path: str,
    mode: str = "word",
    max_spans: int = MAX_SPANS_DEFAULT,
) -> dict:
    escalation = ["word", "sentence", "block"]
    if mode not in escalation:
        raise ValueError(f"invalid mode: {mode}")
    start_idx = escalation.index(mode)
    last_redlined = ""
    last_stats: dict = {}
    for current_mode in escalation[start_idx:]:
        redlined, stats = _generate_once(baseline_path, current_path, current_mode)
        last_redlined = redlined
        last_stats = stats
        if stats["total_spans"] <= max_spans:
            break
    Path(out_path).write_text(last_redlined, encoding="utf-8")
    return last_stats
```

Add `--max-spans` to the CLI in `main`:
```python
    ap.add_argument("--max-spans", type=int, default=MAX_SPANS_DEFAULT)
```

And pass it through:
```python
    stats = generate(args.baseline, args.current, args.output, mode=args.mode, max_spans=args.max_spans)
```

- [ ] **Step 4: Run all tests**

Run: `python -m pytest tests/test_redline_generator.py -v`
Expected: 7 pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/workflow/redline-generator.py tests/test_redline_generator.py
git commit -m "feat(redline): escalate word→sentence→block when span cap exceeded"
```

---

### Task A6: Skip diff inside code fences and tables

**Files:**
- Modify: `scripts/workflow/redline-generator.py`
- Modify: `tests/test_redline_generator.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_redline_generator.py`:
```python
def test_code_fence_is_marked_as_whole_block(tmp_path):
    baseline = tmp_path / "b.md"
    current = tmp_path / "c.md"
    baseline.write_text(
        "Intro.\n\n```python\nx = 1\ny = 2\n```\n\nOutro.\n",
        encoding="utf-8",
    )
    current.write_text(
        "Intro.\n\n```python\nx = 1\ny = 99\n```\n\nOutro.\n",
        encoding="utf-8",
    )
    out = tmp_path / "out.md"
    rg.generate(str(baseline), str(current), str(out), mode="word")
    text = out.read_text(encoding="utf-8")
    assert "{++99++}" not in text
    assert "{++" in text and "```python" in text
    assert "Outro." in text


def test_table_row_change_marks_whole_table(tmp_path):
    baseline = tmp_path / "b.md"
    current = tmp_path / "c.md"
    baseline.write_text(
        "Pre.\n\n| A | B |\n|---|---|\n| 1 | 2 |\n\nPost.\n",
        encoding="utf-8",
    )
    current.write_text(
        "Pre.\n\n| A | B |\n|---|---|\n| 1 | 9 |\n\nPost.\n",
        encoding="utf-8",
    )
    out = tmp_path / "out.md"
    rg.generate(str(baseline), str(current), str(out), mode="word")
    text = out.read_text(encoding="utf-8")
    assert "{++9++}" not in text
    assert "Post." in text
```

- [ ] **Step 2: Run tests, confirm failure**

Run: `python -m pytest tests/test_redline_generator.py -v`
Expected: 7 pass, 2 fail (new code/table tests).

- [ ] **Step 3: Detect code fences and tables as opaque paragraphs**

In `scripts/workflow/redline-generator.py`, replace `_diff_paragraph` to short-circuit on opaque blocks:
```python
CODE_FENCE_RE = re.compile(r"^\s*```", re.MULTILINE)
TABLE_LINE_RE = re.compile(r"^\s*\|.*\|\s*$", re.MULTILINE)


def _is_opaque_block(text: str) -> bool:
    if CODE_FENCE_RE.search(text):
        return True
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if lines and all(TABLE_LINE_RE.match(ln) for ln in lines):
        return True
    return False


def _diff_paragraph(b_text: str, c_text: str) -> str:
    if _is_opaque_block(b_text) or _is_opaque_block(c_text):
        return f"{{--{b_text}--}}{{++{c_text}++}}"
    b_tokens = tokenize(b_text)
    c_tokens = tokenize(c_text)
    sm = difflib.SequenceMatcher(a=b_tokens, b=c_tokens, autojunk=False)
    matching = sum(size for _, _, size in sm.get_matching_blocks())
    total = max(len(b_tokens), len(c_tokens))
    if total > 0 and (1.0 - matching / total) >= BLOCK_REWRITE_THRESHOLD:
        return f"{{--{b_text}--}}{{++{c_text}++}}"
    return diff_to_critic(b_tokens, c_tokens)
```

- [ ] **Step 4: Run all tests**

Run: `python -m pytest tests/test_redline_generator.py -v`
Expected: 9 pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/workflow/redline-generator.py tests/test_redline_generator.py
git commit -m "feat(redline): treat code fences and tables as opaque blocks"
```

---

### Task A7: Escape spurious CriticMarkup in source

**Files:**
- Modify: `scripts/workflow/redline-generator.py`
- Modify: `tests/test_redline_generator.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_redline_generator.py`:
```python
def test_source_braces_escaped_to_avoid_pandoc_interpretation(tmp_path):
    baseline = tmp_path / "b.md"
    current = tmp_path / "c.md"
    baseline.write_text("Esempio: usa `{++` come marker.\n", encoding="utf-8")
    current.write_text("Esempio: usa `{++` come marker.\n", encoding="utf-8")
    out = tmp_path / "out.md"
    rg.generate(str(baseline), str(current), str(out), mode="word")
    text = out.read_text(encoding="utf-8")
    assert "\\{++" in text or "\\{ ++" in text
```

- [ ] **Step 2: Run test, confirm failure**

Run: `python -m pytest tests/test_redline_generator.py::test_source_braces_escaped_to_avoid_pandoc_interpretation -v`
Expected: FAIL.

- [ ] **Step 3: Add post-processing escape pass**

In `scripts/workflow/redline-generator.py`, add at module level:
```python
CRITIC_MARKERS = ("{++", "++}", "{--", "--}", "{~~", "~~}", "~>")


def _escape_spurious_critic(text: str, span_runs: list[tuple[int, int]]) -> str:
    """Escape `{++`, `{--`, `{~~` that appear OUTSIDE generated span ranges."""
    out_chars = list(text)
    in_span = [False] * len(text)
    for start, end in span_runs:
        for i in range(start, min(end, len(text))):
            in_span[i] = True
    for marker in CRITIC_MARKERS:
        for m in re.finditer(re.escape(marker), text):
            if not in_span[m.start()]:
                out_chars[m.start()] = "\\" + out_chars[m.start()]
    return "".join(out_chars)
```

Then in `_generate_once`, after building `redlined`, compute span runs and escape outside them. Replace the tail of `_generate_once` (after `redlined = sep.join(out_parts)`) with:
```python
    span_runs: list[tuple[int, int]] = []
    for m in re.finditer(r"\{(?:\+\+|--|~~).+?(?:\+\+|--|~~)\}", redlined, flags=re.DOTALL):
        span_runs.append((m.start(), m.end()))
    redlined = _escape_spurious_critic(redlined, span_runs)
    n_ins = redlined.count("{++")
    n_del = redlined.count("{--")
    n_sub = redlined.count("{~~")
```

- [ ] **Step 4: Run all tests**

Run: `python -m pytest tests/test_redline_generator.py -v`
Expected: 10 pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/workflow/redline-generator.py tests/test_redline_generator.py
git commit -m "feat(redline): escape spurious CriticMarkup markers in source"
```

---

### Task A8: Verbose telemetry on stderr

**Files:**
- Modify: `scripts/workflow/redline-generator.py`

- [ ] **Step 1: Enhance `--verbose` output**

In `scripts/workflow/redline-generator.py`, replace the verbose block in `main`:
```python
    if args.verbose:
        print(
            f"[redline] mode={stats['mode']} "
            f"baseline_tokens={stats['baseline_tokens']} "
            f"current_tokens={stats['current_tokens']} "
            f"ins={stats['ins_count']} del={stats['del_count']} sub={stats['sub_count']} "
            f"total_spans={stats['total_spans']} max_spans={args.max_spans}",
            file=sys.stderr,
        )
```

- [ ] **Step 2: Smoke-test the CLI**

Run from the skill root:
```bash
echo "Il vecchio testo." > /tmp/b.md
echo "Il nuovo testo." > /tmp/c.md
python scripts/workflow/redline-generator.py /tmp/b.md /tmp/c.md -o /tmp/r.md --verbose
cat /tmp/r.md
```
Expected stderr line containing `mode=word ins=1 del=1`. Expected /tmp/r.md content includes `{~~vecchio~>nuovo~~}`.

- [ ] **Step 3: Commit**

```bash
git add scripts/workflow/redline-generator.py
git commit -m "feat(redline): structured verbose telemetry"
```

---

## Phase B — Pandoc Filters

### Task B1: `critic-to-latex.py` filter

**Files:**
- Create: `scripts/export/critic-to-latex.py`
- Create: `tests/test_critic_filters.py`

- [ ] **Step 1: Write the failing test**

`tests/test_critic_filters.py`:
```python
import json
import subprocess
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def _pandoc_md_to_json(md: str) -> str:
    return subprocess.run(
        ["pandoc", "-f", "markdown+critic_markup", "-t", "json"],
        input=md, capture_output=True, text=True, check=True,
    ).stdout


def _run_filter(filter_path: Path, ast_json: str) -> str:
    return subprocess.run(
        ["python", str(filter_path)],
        input=ast_json, capture_output=True, text=True, check=True,
    ).stdout


def _pandoc_json_to_latex(ast_json: str) -> str:
    return subprocess.run(
        ["pandoc", "-f", "json", "-t", "latex"],
        input=ast_json, capture_output=True, text=True, check=True,
    ).stdout


def test_latex_filter_emits_added_deleted_replaced():
    md = "Pre {++inserito++} medio {--cancellato--} {~~vecchio~>nuovo~~} fine.\n"
    ast = _pandoc_md_to_json(md)
    filtered = _run_filter(SCRIPTS / "critic-to-latex.py", ast)
    latex = _pandoc_json_to_latex(filtered)
    assert "\\added{inserito}" in latex
    assert "\\deleted{cancellato}" in latex
    assert "\\replaced{nuovo}{vecchio}" in latex
```

- [ ] **Step 2: Run test, confirm failure**

Run: `python -m pytest tests/test_critic_filters.py::test_latex_filter_emits_added_deleted_replaced -v`
Expected: FAIL (`critic-to-latex.py` missing).

- [ ] **Step 3: Implement the filter**

`scripts/export/critic-to-latex.py`:
```python
#!/usr/bin/env python3
"""critic-to-latex.py — pandoc JSON-AST filter: CriticMarkup → LaTeX `changes` package."""
from __future__ import annotations

import json
import sys


def raw_latex(s: str) -> dict:
    return {"t": "RawInline", "c": ["latex", s]}


def transform_inlines(inlines: list) -> list:
    out: list = []
    i = 0
    while i < len(inlines):
        node = inlines[i]
        if node.get("t") == "Span":
            attrs, children = node["c"]
            classes = attrs[1] if len(attrs) >= 2 else []
            text = _inline_to_text(children)
            if "critic-add" in classes or "ins" in classes:
                out.append(raw_latex(f"\\added{{{text}}}"))
                i += 1
                continue
            if "critic-del" in classes or "del" in classes:
                out.append(raw_latex(f"\\deleted{{{text}}}"))
                i += 1
                continue
        # Pandoc emits {~~old~>new~~} as adjacent del+ins; collapse here.
        if (
            node.get("t") == "Span"
            and _span_has_class(node, ("critic-del", "del"))
            and i + 1 < len(inlines)
            and inlines[i + 1].get("t") == "Span"
            and _span_has_class(inlines[i + 1], ("critic-add", "ins"))
        ):
            old = _inline_to_text(node["c"][1])
            new = _inline_to_text(inlines[i + 1]["c"][1])
            out.append(raw_latex(f"\\replaced{{{new}}}{{{old}}}"))
            i += 2
            continue
        if isinstance(node.get("c"), list):
            node = {**node, "c": _recurse(node["c"])}
        out.append(node)
        i += 1
    return out


def _span_has_class(span: dict, classes_to_check: tuple) -> bool:
    attrs = span["c"][0]
    classes = attrs[1] if len(attrs) >= 2 else []
    return any(c in classes for c in classes_to_check)


def _inline_to_text(inlines: list) -> str:
    parts: list[str] = []
    for n in inlines:
        t = n.get("t")
        c = n.get("c")
        if t == "Str":
            parts.append(c)
        elif t == "Space":
            parts.append(" ")
        elif t == "SoftBreak" or t == "LineBreak":
            parts.append(" ")
        elif isinstance(c, list):
            parts.append(_inline_to_text(c))
    return "".join(parts)


def _recurse(c):
    if isinstance(c, list):
        if c and isinstance(c[0], dict) and "t" in c[0]:
            return transform_inlines(c)
        return [_recurse(x) for x in c]
    if isinstance(c, dict):
        return {k: _recurse(v) for k, v in c.items()}
    return c


def main() -> int:
    doc = json.load(sys.stdin)
    doc["blocks"] = _recurse(doc.get("blocks", []))
    json.dump(doc, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run test**

Run: `python -m pytest tests/test_critic_filters.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/export/critic-to-latex.py tests/test_critic_filters.py
git commit -m "feat(redline): pandoc filter CriticMarkup → LaTeX changes"
```

---

### Task B2: `critic-to-typst.py` filter

**Files:**
- Create: `scripts/export/critic-to-typst.py`
- Modify: `tests/test_critic_filters.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_critic_filters.py`:
```python
def test_typst_filter_emits_ins_del_repl():
    md = "Pre {++inserito++} medio {--cancellato--} {~~vecchio~>nuovo~~} fine.\n"
    ast = _pandoc_md_to_json(md)
    filtered = _run_filter(SCRIPTS / "critic-to-typst.py", ast)
    typst = subprocess.run(
        ["pandoc", "-f", "json", "-t", "typst"],
        input=filtered, capture_output=True, text=True, check=True,
    ).stdout
    assert "#ins[inserito]" in typst
    assert "#del[cancellato]" in typst
    assert "#repl[nuovo][vecchio]" in typst
```

- [ ] **Step 2: Run test, confirm failure**

Run: `python -m pytest tests/test_critic_filters.py::test_typst_filter_emits_ins_del_repl -v`
Expected: FAIL.

- [ ] **Step 3: Implement the filter**

`scripts/export/critic-to-typst.py`:
```python
#!/usr/bin/env python3
"""critic-to-typst.py — pandoc JSON-AST filter: CriticMarkup → Typst macros."""
from __future__ import annotations

import json
import sys


def raw_typst(s: str) -> dict:
    return {"t": "RawInline", "c": ["typst", s]}


def _span_has_class(span: dict, classes_to_check: tuple) -> bool:
    attrs = span["c"][0]
    classes = attrs[1] if len(attrs) >= 2 else []
    return any(c in classes for c in classes_to_check)


def _inline_to_text(inlines: list) -> str:
    parts: list[str] = []
    for n in inlines:
        t = n.get("t")
        c = n.get("c")
        if t == "Str":
            parts.append(c)
        elif t in ("Space", "SoftBreak", "LineBreak"):
            parts.append(" ")
        elif isinstance(c, list):
            parts.append(_inline_to_text(c))
    return "".join(parts)


def transform_inlines(inlines: list) -> list:
    out: list = []
    i = 0
    while i < len(inlines):
        node = inlines[i]
        if (
            node.get("t") == "Span"
            and _span_has_class(node, ("critic-del", "del"))
            and i + 1 < len(inlines)
            and inlines[i + 1].get("t") == "Span"
            and _span_has_class(inlines[i + 1], ("critic-add", "ins"))
        ):
            old = _inline_to_text(node["c"][1])
            new = _inline_to_text(inlines[i + 1]["c"][1])
            out.append(raw_typst(f"#repl[{new}][{old}]"))
            i += 2
            continue
        if node.get("t") == "Span" and _span_has_class(node, ("critic-add", "ins")):
            text = _inline_to_text(node["c"][1])
            out.append(raw_typst(f"#ins[{text}]"))
            i += 1
            continue
        if node.get("t") == "Span" and _span_has_class(node, ("critic-del", "del")):
            text = _inline_to_text(node["c"][1])
            out.append(raw_typst(f"#del[{text}]"))
            i += 1
            continue
        if isinstance(node.get("c"), list):
            node = {**node, "c": _recurse(node["c"])}
        out.append(node)
        i += 1
    return out


def _recurse(c):
    if isinstance(c, list):
        if c and isinstance(c[0], dict) and "t" in c[0]:
            return transform_inlines(c)
        return [_recurse(x) for x in c]
    if isinstance(c, dict):
        return {k: _recurse(v) for k, v in c.items()}
    return c


def main() -> int:
    doc = json.load(sys.stdin)
    doc["blocks"] = _recurse(doc.get("blocks", []))
    json.dump(doc, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run all filter tests**

Run: `python -m pytest tests/test_critic_filters.py -v`
Expected: 2 pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/export/critic-to-typst.py tests/test_critic_filters.py
git commit -m "feat(redline): pandoc filter CriticMarkup → Typst macros"
```

---

## Phase C — Session State & Lifecycle Commands

### Task C1: Document `redline` schema in session-state

**Files:**
- Modify: `schemas/session-state.schema.json` (if it exists; otherwise add inline doc in SKILL.md)

- [ ] **Step 1: Check for existing schema**

Run: `ls ~/.claude/skills/relazione/schemas/`
If `session-state.schema.json` exists, modify it; otherwise document the new section in `SKILL.md` under "Stato di sessione".

- [ ] **Step 2: Add `redline` block to schema**

If schema file exists, add to its `properties`:
```json
"redline": {
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "enabled": {"type": "boolean", "default": false},
    "baseline": {"type": "string", "enum": ["backup", "approved", "imported"]},
    "baseline_path": {"type": "string"},
    "baseline_ref": {"type": "string", "format": "date-time"},
    "mode": {"type": "string", "enum": ["word", "sentence"], "default": "word"}
  },
  "required": ["enabled"]
}
```

If schema file does not exist, append to `SKILL.md` under a new subsection `### redline (state)`:
```markdown
### `redline` (state)

Tracks whether track-changes are produced on export.

| Field | Type | Notes |
|---|---|---|
| `enabled` | bool | Auto-true during `in-review`, auto-false on `approve`. |
| `baseline` | `backup` \| `approved` \| `imported` | Source for diff comparison. |
| `baseline_path` | string | Resolved path on disk, set when `enabled=true`. |
| `baseline_ref` | ISO-8601 | Timestamp of baseline snapshot. |
| `mode` | `word` \| `sentence` | Diff granularity. |
```

- [ ] **Step 3: Commit**

```bash
git add schemas/session-state.schema.json SKILL.md
git commit -m "docs(redline): document redline block in session-state schema"
```

---

### Task C2: Modify `/relazione-review` to snapshot baseline + enable redline

**Files:**
- Modify: `commands/relazione-review.md`

- [ ] **Step 1: Add baseline-resolution and snapshot step to the command**

In `commands/relazione-review.md`, insert a new step between the existing steps 4 (state update) and 5 (regenerate PDF). Numbering shifts accordingly.

New step text to insert (verbatim):
```markdown
5. **Snapshot redline baseline** (nuovo dalla v2.6.0):
   - Risolvi baseline source in ordine:
     1. `<session>/archive/` — sottocartella più recente per nome (es. `v1.0-2026-04-12`). Usa `<session>/archive/<latest>/RELAZIONE.md` come baseline.
     2. Se nessun archive → file più recente in `<session>/.session/backups/`.
     3. Se nemmeno backup → salta lo snapshot, warn `[redline] nessuna baseline disponibile, redline disattivato`.
   - Copia la baseline in `<session>/.session/redline/baseline.md` (mkdir -p `.session/redline/`).
   - Aggiorna `session-state.json`:
     ```json
     "redline": {
       "enabled": true,
       "baseline": "approved",
       "baseline_path": ".session/redline/baseline.md",
       "baseline_ref": "<ISO-8601 della baseline source>",
       "mode": "word"
     }
     ```
     Imposta `baseline = approved` se sorgente da `archive/`, `backup` se sorgente da `.session/backups/`.
   - Log audit-trail:
     ```bash
     python3 ~/.claude/skills/relazione/scripts/audit-trail.py log \
       --state <state.json> --action redline_enabled --by <user> \
       --note "baseline=<approved|backup>, ref=<ISO>"
     ```
```

Then renumber the subsequent steps (old 5 → 6, etc.) and add a one-line note in the "Output" section: `> Redline attivo, baseline: <approved 2026-04-12 | backup 2026-05-14T09-12-44>`.

- [ ] **Step 2: Commit**

```bash
git add commands/relazione-review.md
git commit -m "feat(redline): /relazione-review snapshots baseline and enables redline"
```

---

### Task C3: Modify `/relazione-approve` to archive baseline + disable redline

**Files:**
- Modify: `commands/relazione-approve.md`

- [ ] **Step 1: Add cleanup step after archive creation**

In `commands/relazione-approve.md`, after step 7 (Crea snapshot archive/), add a new step 7.5:
```markdown
7.5. **Disable redline** (nuovo dalla v2.6.0):
   - Se `session-state.redline.enabled` è `true`:
     - Sposta `<session>/.session/redline/baseline.md` → `<session>/.session/redline/baselines/<approval-timestamp>.md` (mkdir -p baselines).
     - Setta in `session-state.json`:
       ```json
       "redline": { "enabled": false }
       ```
       (lascia gli altri campi per audit storico)
     - Log audit-trail:
       ```bash
       python3 ~/.claude/skills/relazione/scripts/audit-trail.py log \
         --state <state.json> --action redline_disabled --by <user> \
         --note "Approval; baseline archived to baselines/<timestamp>.md"
       ```
```

- [ ] **Step 2: Commit**

```bash
git add commands/relazione-approve.md
git commit -m "feat(redline): /relazione-approve archives baseline and disables redline"
```

---

## Phase D — Export Scripts

### Task D0: Pandoc capability check helper

**Files:**
- Create: `scripts/_check-pandoc-critic.sh`

- [ ] **Step 1: Create the helper script**

`scripts/_check-pandoc-critic.sh`:
```bash
#!/usr/bin/env bash
# _check-pandoc-critic.sh — sourced helper. Defines check_pandoc_critic().
# Exits with status 3 and a clear error if pandoc lacks critic_markup support.

check_pandoc_critic() {
  if ! command -v pandoc >/dev/null 2>&1; then
    echo "[redline] ERR: pandoc non installato. Installa pandoc ≥ 2.x e riprova." >&2
    return 3
  fi
  if ! pandoc --list-extensions 2>/dev/null | grep -q critic_markup; then
    echo "[redline] ERR: pandoc non supporta critic_markup. Aggiorna a pandoc ≥ 2.x." >&2
    return 3
  fi
  return 0
}
```

Make executable:
```bash
chmod +x scripts/_check-pandoc-critic.sh
```

- [ ] **Step 2: Smoke test**

```bash
source scripts/_check-pandoc-critic.sh && check_pandoc_critic && echo OK
```
Expected: `OK` on systems with pandoc ≥ 2.x.

- [ ] **Step 3: Commit**

```bash
git add scripts/_check-pandoc-critic.sh
git commit -m "feat(redline): pandoc critic_markup capability check helper"
```

---

### Task D0.5: Baseline resolution helper

**Files:**
- Create: `scripts/_resolve-baseline.sh`

- [ ] **Step 1: Create the shared baseline path resolver**

`scripts/_resolve-baseline.sh`:
```bash
#!/usr/bin/env bash
# _resolve-baseline.sh — shared baseline path resolver for redline-aware exports.
# Sourced, not executed. Defines resolve_baseline_path().

resolve_baseline_path() {
  local session="$1"
  local kind="$2"
  case "$kind" in
    auto)
      if [ -f "$session/.session/redline/baseline.md" ]; then
        echo "$session/.session/redline/baseline.md"; return
      fi
      ls -d "$session"/archive/*/ 2>/dev/null | sort | tail -n1 | while read -r d; do
        [ -f "${d}RELAZIONE.md" ] && echo "${d}RELAZIONE.md"
      done
      ;;
    approved)
      local latest
      latest=$(ls -d "$session"/archive/*/ 2>/dev/null | sort | tail -n1)
      [ -n "$latest" ] && [ -f "${latest}RELAZIONE.md" ] && echo "${latest}RELAZIONE.md"
      ;;
    backup)
      ls -t "$session"/.session/backups/*.md 2>/dev/null | head -n1
      ;;
    imported)
      ls -t "$session"/.session/feedback/applied-*.md 2>/dev/null | head -n1
      ;;
  esac
}
```

Make executable:
```bash
chmod +x scripts/_resolve-baseline.sh
```

- [ ] **Step 2: Smoke-test the function**

```bash
mkdir -p /tmp/baselinetest/.session/backups
touch /tmp/baselinetest/.session/backups/2026-05-14-RELAZIONE.md
source scripts/_resolve-baseline.sh
resolve_baseline_path /tmp/baselinetest backup
```
Expected output: `/tmp/baselinetest/.session/backups/2026-05-14-RELAZIONE.md`.

- [ ] **Step 3: Commit**

```bash
git add scripts/_resolve-baseline.sh
git commit -m "feat(redline): shared baseline path resolver helper"
```

---

### Task D1: `live-preview-draft.sh` — `--diff` flag + dropdown header

**Files:**
- Modify: `scripts/workflow/live-preview-draft.sh`

- [ ] **Step 1: Add `--diff` arg parsing**

In `scripts/workflow/live-preview-draft.sh`, in the `while` arg-parse loop, add a case:
```bash
    --diff)
      DIFF_BASELINE="${2:-auto}"
      shift 2
      ;;
```

And initialize at top with the other defaults:
```bash
DIFF_BASELINE=""
```

- [ ] **Step 2: Resolve baseline path when `--diff` is set**

After the existing `DRAFT` resolution block (around line 68), append:
```bash
BASELINE_PATH=""
source "$SCRIPT_DIR/../_resolve-baseline.sh"
if [ -n "$DIFF_BASELINE" ]; then
  source "$SCRIPT_DIR/../_check-pandoc-critic.sh"
  check_pandoc_critic || exit $?
  BASELINE_PATH=$(resolve_baseline_path "$SESSION" "$DIFF_BASELINE")
  if [ -z "$BASELINE_PATH" ] || [ ! -f "$BASELINE_PATH" ]; then
    echo "[redline] WARN: baseline '$DIFF_BASELINE' non trovata, diff disattivato" >&2
    DIFF_BASELINE=""
  fi
fi
```

The `SCRIPT_DIR` variable is already defined at the top of `live-preview-draft.sh`.

- [ ] **Step 3: Add redline pre-step inside `render()`**

Modify the `render()` function to generate `.redlined.md` when `BASELINE_PATH` is set, and use it as pandoc input. Replace the body of `render()`:
```bash
render() {
  python3 "$PREPROCESS_PY" "$DRAFT" "$PROCESSED"
  local PANDOC_INPUT="$PROCESSED"
  local PANDOC_FORMAT="markdown"
  if [ -n "$BASELINE_PATH" ]; then
    local REDLINED="$WORK_DIR/_redlined-$NAME.md"
    python3 "$SCRIPT_DIR/redline-generator.py" "$BASELINE_PATH" "$PROCESSED" -o "$REDLINED" --mode word 2>/dev/null || true
    if [ -f "$REDLINED" ]; then
      PANDOC_INPUT="$REDLINED"
      PANDOC_FORMAT="markdown+critic_markup"
    fi
  fi
  pandoc "$PANDOC_INPUT" -f "$PANDOC_FORMAT" -o "$HTML" --standalone --toc --metadata title="Live: $NAME" \
    --css="data:text/css,$(echo "$EXTRA_CSS" | tr '\n' ' ')" 2>&1 | head -3
  python3 - <<'POSTPY' "$HTML"
import re, sys
p = sys.argv[1]
with open(p, 'r', encoding='utf-8') as f:
    h = f.read()
h = re.sub(r"\[DA RIEMPIRE[^\]]*\]", lambda m: f'<span class="preview-placeholder">{m.group(0)}</span>', h)
h = re.sub(r"\[MOCK\]", '<span class="preview-mock">[MOCK]</span>', h)
with open(p, 'w', encoding='utf-8') as f:
    f.write(h)
POSTPY
  printf '<meta http-equiv="refresh" content="3">\n' >> "$HTML"
}
```

- [ ] **Step 4: Extend `EXTRA_CSS` with ins/del styles**

In `scripts/workflow/live-preview-draft.sh`, append to the `EXTRA_CSS` string (just before the closing `'`):
```css
ins{background:rgba(42,157,143,.12);color:#2A9D8F;text-decoration:underline;text-decoration-thickness:2px}
del{background:rgba(230,57,70,.10);color:#E63946;text-decoration:line-through;text-decoration-thickness:2px}
.redline-banner{position:sticky;top:0;background:#FFF3CD;border-bottom:2px solid #F4A261;padding:6px 12px;font-size:.85em;text-align:center;z-index:99}
```

- [ ] **Step 5: Smoke-test manually**

Create two test markdown files and run:
```bash
mkdir -p /tmp/rel/.session/backups
echo "# Test\n\nProdotto originale." > /tmp/rel/RELAZIONE.md
cp /tmp/rel/RELAZIONE.md /tmp/rel/.session/backups/2026-05-14-RELAZIONE.md
echo "# Test\n\nProdotto modificato." > /tmp/rel/RELAZIONE.md
bash scripts/workflow/live-preview-draft.sh /tmp/rel --diff backup --no-open --port 8767 &
sleep 3
curl -s http://localhost:8767/.preview-RELAZIONE.html | grep -E "(<ins>|<del>)" | head -3
kill %1
```
Expected: `<ins>` and `<del>` tags present in output.

- [ ] **Step 6: Commit**

```bash
git add scripts/workflow/live-preview-draft.sh
git commit -m "feat(redline): --diff flag in live-preview-draft with baseline resolution"
```

---

### Task D1.5: Live preview interactive baseline toggle

**Files:**
- Modify: `scripts/workflow/live-preview-draft.sh`

- [ ] **Step 1: Parse `?diff=` query param via a tiny request handler**

The current `python3 -m http.server` serves static files only — to react to `?diff=`, replace it with a thin custom handler in the script. Add this Python snippet at the end of `live-preview-draft.sh` (replace the existing `python3 -m http.server "$PORT" --bind 127.0.0.1 ...` invocation):

```bash
python3 - "$PORT" "$WORK_DIR" "$DRAFT" "$SESSION" "$NAME" <<'PYSRV' >/dev/null 2>&1 &
import os, sys, subprocess, urllib.parse, threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

port = int(sys.argv[1])
work_dir = sys.argv[2]
draft = sys.argv[3]
session = sys.argv[4]
name = sys.argv[5]
state_path = os.path.join(work_dir, "_diff_baseline.txt")

if not os.path.exists(state_path):
    open(state_path, "w").write(os.environ.get("DIFF_BASELINE", ""))

os.chdir(work_dir)

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        if "diff" in qs:
            value = qs["diff"][0]
            with open(state_path, "w") as f:
                f.write(value)
            # Trigger render via touch of marker file (main loop watches mtimes)
            marker = os.path.join(work_dir, "_force_rerender")
            open(marker, "w").write(value)
            self.send_response(303)
            self.send_header("Location", parsed.path)
            self.end_headers()
            return
        return super().do_GET()

HTTPServer(("127.0.0.1", port), Handler).serve_forever()
PYSRV
SERVER_PID=$!
```

- [ ] **Step 2: Watch the marker file in the polling loop**

In the watch loop at the bottom of `live-preview-draft.sh`, change the condition to also re-render when `_force_rerender` is touched:
```bash
  LAST_MTIME=0
  LAST_MARKER=0
  MARKER="$WORK_DIR/_force_rerender"
  STATE_FILE="$WORK_DIR/_diff_baseline.txt"
  while true; do
    if [ -f "$DRAFT" ]; then
      MTIME=$(stat -c %Y "$DRAFT" 2>/dev/null || stat -f %m "$DRAFT" 2>/dev/null)
      MMTIME=0
      [ -f "$MARKER" ] && MMTIME=$(stat -c %Y "$MARKER" 2>/dev/null || stat -f %m "$MARKER" 2>/dev/null)
      if [ "$MTIME" != "$LAST_MTIME" ] || [ "$MMTIME" != "$LAST_MARKER" ]; then
        if [ -f "$STATE_FILE" ]; then
          NEW_BASELINE=$(cat "$STATE_FILE")
          if [ "$NEW_BASELINE" = "off" ] || [ -z "$NEW_BASELINE" ]; then
            BASELINE_PATH=""
          else
            BASELINE_PATH=$(resolve_baseline_path "$SESSION" "$NEW_BASELINE")
          fi
        fi
        render >/dev/null 2>&1
        LAST_MTIME="$MTIME"
        LAST_MARKER="$MMTIME"
        echo "[reload] $(date +%H:%M:%S)"
      fi
    fi
    sleep 2
  done
```

- [ ] **Step 3: Inject the dropdown into rendered HTML**

In the `render()` function, after the existing POSTPY block, append a second post-processing block that prepends a control bar:
```bash
  python3 - <<'POSTBAR' "$HTML" "$WORK_DIR/_diff_baseline.txt"
import sys, pathlib
html_p = pathlib.Path(sys.argv[1])
state_p = pathlib.Path(sys.argv[2])
current = state_p.read_text().strip() if state_p.exists() else ""
options = [("", "OFF"), ("backup", "vs backup"), ("approved", "vs approved"), ("imported", "vs imported")]
opts_html = "".join(
    f'<option value="{v}" {"selected" if v == current else ""}>{label}</option>'
    for v, label in options
)
bar = (
    '<div style="position:sticky;top:0;background:#FFF3CD;border-bottom:2px solid #F4A261;'
    'padding:6px 12px;font-size:.85em;display:flex;justify-content:flex-end;gap:8px;z-index:200">'
    '<form method="get" style="margin:0">Diff: '
    f'<select name="diff" onchange="this.form.submit()">{opts_html}</select>'
    '</form></div>'
)
h = html_p.read_text(encoding="utf-8")
h = h.replace("<body>", "<body>" + bar, 1)
html_p.write_text(h, encoding="utf-8")
POSTBAR
```

- [ ] **Step 4: Smoke test**

```bash
mkdir -p /tmp/relt/.session/backups
echo "Originale" > /tmp/relt/RELAZIONE.md
cp /tmp/relt/RELAZIONE.md /tmp/relt/.session/backups/2026-05-14-RELAZIONE.md
echo "Modificato" > /tmp/relt/RELAZIONE.md
bash scripts/workflow/live-preview-draft.sh /tmp/relt --no-open --port 8768 &
sleep 2
curl -s "http://localhost:8768/.preview-RELAZIONE.html" | grep -q '<select name="diff"' && echo "OK toggle in DOM"
curl -s "http://localhost:8768/.preview-RELAZIONE.html?diff=backup" -o /dev/null -w "%{http_code}\n" | grep -q "303" && echo "OK redirect"
kill %1
```
Expected: both `OK` lines.

- [ ] **Step 5: Commit**

```bash
git add scripts/workflow/live-preview-draft.sh
git commit -m "feat(redline): in-page dropdown to switch diff baseline live"
```

---

### Task D2: `export-html-standalone.sh` — `--redline` flag

**Files:**
- Modify: `scripts/export/export-html-standalone.sh`

- [ ] **Step 1: Read existing file to understand structure**

Run: `cat ~/.claude/skills/relazione/scripts/export/export-html-standalone.sh`
Identify the pandoc invocation line and the input file variable.

- [ ] **Step 2: Add `--redline` flag and conditional input swap**

At the top of the arg-parse block (before the main loop), add:
```bash
REDLINE_MODE="off"
REDLINE_BASELINE="auto"
```

In the arg-parse `case` block, add:
```bash
    --redline)
      REDLINE_MODE="on"
      if [[ "${2:-}" =~ ^(backup|approved|imported|auto)$ ]]; then
        REDLINE_BASELINE="$2"; shift 2
      else
        shift
      fi
      ;;
    --redline=*)
      REDLINE_MODE="on"
      REDLINE_BASELINE="${1#--redline=}"
      shift
      ;;
```

Before the pandoc invocation, add input-swap logic. Replace the input variable usage so it goes through `$PANDOC_INPUT`:
```bash
PANDOC_INPUT="$INPUT"
PANDOC_FROM="markdown"
OUT_SUFFIX=""
if [ "$REDLINE_MODE" = "on" ]; then
  source "$(dirname "${BASH_SOURCE[0]}")/../_check-pandoc-critic.sh"
  check_pandoc_critic || exit $?
  SESSION_DIR=$(dirname "$INPUT")
  source "$(dirname "${BASH_SOURCE[0]}")/../_resolve-baseline.sh"
  BASELINE=$(resolve_baseline_path "$SESSION_DIR" "$REDLINE_BASELINE")
  if [ -n "$BASELINE" ] && [ -f "$BASELINE" ]; then
    REDLINED="$SESSION_DIR/.session/redline/.redlined-$(basename "$INPUT")"
    mkdir -p "$(dirname "$REDLINED")"
    python3 "$(dirname "${BASH_SOURCE[0]}")/../workflow/redline-generator.py" "$BASELINE" "$INPUT" -o "$REDLINED" --mode word
    PANDOC_INPUT="$REDLINED"
    PANDOC_FROM="markdown+critic_markup"
    OUT_SUFFIX="-redline"
  else
    echo "[redline] WARN: baseline non trovata, export pulito" >&2
  fi
fi
```

Update the output filename to use `$OUT_SUFFIX`: change `${BASE}.html` to `${BASE}${OUT_SUFFIX}.html` and update the pandoc call to use `$PANDOC_INPUT` and `-f $PANDOC_FROM`.

- [ ] **Step 3: Smoke-test the HTML export**

```bash
mkdir -p /tmp/relhtml/.session/backups
echo "Originale" > /tmp/relhtml/RELAZIONE.md
cp /tmp/relhtml/RELAZIONE.md /tmp/relhtml/.session/backups/2026-05-14-RELAZIONE.md
echo "Modificato" > /tmp/relhtml/RELAZIONE.md
bash scripts/export/export-html-standalone.sh /tmp/relhtml/RELAZIONE.md --redline backup
grep -E "<ins>|<del>" /tmp/relhtml/RELAZIONE-redline.html
```
Expected: `<ins>` and `<del>` tags present.

- [ ] **Step 4: Commit**

```bash
git add scripts/export/export-html-standalone.sh
git commit -m "feat(redline): --redline flag for export-html-standalone"
```

---

### Task D3: `export-typst.sh` — `--redline` flag + Typst preamble + filter

**Files:**
- Modify: `scripts/export/export-typst.sh`

- [ ] **Step 1: Read existing file**

Run: `cat ~/.claude/skills/relazione/scripts/export/export-typst.sh`
Note the input variable name and the typst-compile command.

- [ ] **Step 2: Add flag parsing**

Apply the same `--redline` flag pattern as Task D2: add `REDLINE_MODE`/`REDLINE_BASELINE` vars, parse `--redline [value]` and `--redline=value`, source `_resolve-baseline.sh`.

- [ ] **Step 3: Pre-step before pandoc → typst**

Replace the call that produces the `.typ` file. The new pattern:
```bash
PANDOC_INPUT="$INPUT"
PANDOC_FROM="markdown"
TYPST_PREAMBLE=""
OUT_SUFFIX=""
if [ "$REDLINE_MODE" = "on" ]; then
  source "$(dirname "${BASH_SOURCE[0]}")/../_check-pandoc-critic.sh"
  check_pandoc_critic || exit $?
  SESSION_DIR=$(dirname "$INPUT")
  source "$(dirname "${BASH_SOURCE[0]}")/../_resolve-baseline.sh"
  BASELINE=$(resolve_baseline_path "$SESSION_DIR" "$REDLINE_BASELINE")
  if [ -n "$BASELINE" ] && [ -f "$BASELINE" ]; then
    REDLINED="$SESSION_DIR/.session/redline/.redlined-$(basename "$INPUT")"
    mkdir -p "$(dirname "$REDLINED")"
    python3 "$(dirname "${BASH_SOURCE[0]}")/../workflow/redline-generator.py" "$BASELINE" "$INPUT" -o "$REDLINED" --mode word
    PANDOC_INPUT="$REDLINED"
    PANDOC_FROM="markdown+critic_markup"
    OUT_SUFFIX="-redline"
    TYPST_PREAMBLE='#let ins(body) = text(fill: rgb("#2A9D8F"))[#underline(body)]
#let del(body) = text(fill: rgb("#E63946"))[#strike(body)]
#let repl(new, old) = [#del[#old]#ins[#new]]
'
  else
    echo "[redline] WARN: baseline non trovata, export pulito" >&2
  fi
fi
```

Then in the pandoc → typst command, add the filter when redline is on:
```bash
PANDOC_FILTERS=()
if [ "$REDLINE_MODE" = "on" ] && [ -n "$OUT_SUFFIX" ]; then
  PANDOC_FILTERS=(--filter "$(dirname "${BASH_SOURCE[0]}")/critic-to-typst.py")
fi
pandoc "$PANDOC_INPUT" -f "$PANDOC_FROM" -t typst "${PANDOC_FILTERS[@]}" -o "${BASE}${OUT_SUFFIX}.typ"
```

After the `.typ` is produced, inject the preamble at the top:
```bash
if [ -n "$TYPST_PREAMBLE" ]; then
  TMPF=$(mktemp)
  printf '%s\n' "$TYPST_PREAMBLE" > "$TMPF"
  cat "${BASE}${OUT_SUFFIX}.typ" >> "$TMPF"
  mv "$TMPF" "${BASE}${OUT_SUFFIX}.typ"
fi
```

Update the typst compile command to use `${BASE}${OUT_SUFFIX}`:
```bash
typst compile "${BASE}${OUT_SUFFIX}.typ" "${BASE}${OUT_SUFFIX}.pdf"
```

- [ ] **Step 4: Smoke test**

```bash
mkdir -p /tmp/reltyp/.session/backups
echo "# T\n\nOriginale" > /tmp/reltyp/RELAZIONE.md
cp /tmp/reltyp/RELAZIONE.md /tmp/reltyp/.session/backups/2026-05-14-RELAZIONE.md
echo "# T\n\nModificato" > /tmp/reltyp/RELAZIONE.md
bash scripts/export/export-typst.sh /tmp/reltyp/RELAZIONE.md --redline backup
test -f /tmp/reltyp/RELAZIONE-redline.pdf && echo OK
```
Expected: `OK`.

- [ ] **Step 5: Commit**

```bash
git add scripts/export/export-typst.sh
git commit -m "feat(redline): --redline flag for export-typst"
```

---

### Task D4: `parallel-export.sh` — `--redline` flag for PDF + DOCX paths

**Files:**
- Modify: `scripts/export/parallel-export.sh`

- [ ] **Step 1: Add flag parsing**

In `scripts/export/parallel-export.sh`, add to defaults block:
```bash
REDLINE_MODE="off"
REDLINE_BASELINE="auto"
```

Add to arg-parse `case`:
```bash
    --redline) REDLINE_MODE="on"; if [[ "${2:-}" =~ ^(backup|approved|imported|auto)$ ]]; then REDLINE_BASELINE="$2"; shift 2; else shift; fi ;;
    --redline=*) REDLINE_MODE="on"; REDLINE_BASELINE="${1#--redline=}"; shift ;;
```

- [ ] **Step 2: Pre-compute redline input**

After the input validation block (after `if [ -z "$INPUT" ]...exit 2`), add:
```bash
PANDOC_INPUT="$INPUT"
PANDOC_FROM_BASE=()
OUT_SUFFIX=""
PDF_EXTRA=()
DOCX_EXTRA=()
LATEX_HEADER=""

if [ "$REDLINE_MODE" = "on" ]; then
  source "$(dirname "${BASH_SOURCE[0]}")/../_check-pandoc-critic.sh"
  check_pandoc_critic || exit $?
  SESSION_DIR=$(dirname "$INPUT")
  source "$(dirname "${BASH_SOURCE[0]}")/../_resolve-baseline.sh"
  BASELINE=$(resolve_baseline_path "$SESSION_DIR" "$REDLINE_BASELINE")
  if [ -n "$BASELINE" ] && [ -f "$BASELINE" ]; then
    REDLINED="$SESSION_DIR/.session/redline/.redlined-$(basename "$INPUT")"
    mkdir -p "$(dirname "$REDLINED")"
    python3 "$(dirname "${BASH_SOURCE[0]}")/../workflow/redline-generator.py" "$BASELINE" "$INPUT" -o "$REDLINED" --mode word
    PANDOC_INPUT="$REDLINED"
    PANDOC_FROM_BASE=(-f markdown+critic_markup)
    OUT_SUFFIX="-redline"
    # PDF route: LaTeX changes package + critic-to-latex filter
    LATEX_HEADER=$(mktemp --suffix=.tex)
    cat > "$LATEX_HEADER" <<'TEX'
\usepackage[markup=underlined,authormarkup=none]{changes}
TEX
    PDF_EXTRA=(--filter "$(dirname "${BASH_SOURCE[0]}")/critic-to-latex.py" -H "$LATEX_HEADER")
    # DOCX route: native pandoc track-changes
    DOCX_EXTRA=(--track-changes=all)
  else
    echo "[redline] WARN: baseline non trovata, export pulito" >&2
  fi
fi
```

Add cleanup of the temp header to the existing `trap`:
```bash
trap 'rm -rf "$TMPDIR"; [ -n "$LATEX_HEADER" ] && rm -f "$LATEX_HEADER"' EXIT
```

- [ ] **Step 3: Wire PDF and DOCX jobs to use the redline input**

Change the PDF job (currently at ~line 72) to:
```bash
if [ $DO_PDF -eq 1 ]; then
  PDF_ARGS=(pandoc "$PANDOC_INPUT" "${PANDOC_FROM_BASE[@]}" -o "${BASE}${OUT_SUFFIX}.pdf" "${PANDOC_COMMON[@]}" --pdf-engine=xelatex "${PDF_EXTRA[@]}")
  [ -n "$TEMPLATE" ] && [ -f "$TEMPLATE" ] && PDF_ARGS+=(--template="$TEMPLATE")
  run_job "pdf" "${PDF_ARGS[@]}"
fi
```

Change DOCX job:
```bash
if [ $DO_DOCX -eq 1 ]; then
  run_job "docx" pandoc "$PANDOC_INPUT" "${PANDOC_FROM_BASE[@]}" -o "${BASE}${OUT_SUFFIX}.docx" "${PANDOC_COMMON[@]}" "${DOCX_EXTRA[@]}"
fi
```

Leave `epub` and `tex` jobs unchanged (epub excluded from redline per spec §2.4).

- [ ] **Step 4: Smoke test PDF + DOCX redline**

```bash
mkdir -p /tmp/relpar/.session/backups
echo "# T\n\nUno." > /tmp/relpar/RELAZIONE.md
cp /tmp/relpar/RELAZIONE.md /tmp/relpar/.session/backups/2026-05-14-RELAZIONE.md
echo "# T\n\nDue." > /tmp/relpar/RELAZIONE.md
bash scripts/export/parallel-export.sh /tmp/relpar/RELAZIONE.md --pdf --docx --redline backup
test -f /tmp/relpar/RELAZIONE-redline.pdf && test -f /tmp/relpar/RELAZIONE-redline.docx && echo OK
```
Expected: `OK`.

Inspect docx for revisions:
```bash
unzip -p /tmp/relpar/RELAZIONE-redline.docx word/document.xml | grep -E "w:ins|w:del" | head -1
```
Expected: at least one `w:ins` or `w:del` element.

- [ ] **Step 5: Commit**

```bash
git add scripts/export/parallel-export.sh
git commit -m "feat(redline): --redline flag for parallel-export (PDF+DOCX)"
```

---

### Task D5: LaTeX fallback when `changes` package missing

**Files:**
- Modify: `scripts/export/critic-to-latex.py`
- Modify: `scripts/export/parallel-export.sh`

- [ ] **Step 1: Write a test for the fallback**

Add to `tests/test_critic_filters.py`:
```python
def test_latex_filter_with_fallback_uses_sout_uline(tmp_path, monkeypatch):
    monkeypatch.setenv("REDLINE_LATEX_FALLBACK", "soul")
    md = "Pre {++inserito++} medio {--cancellato--} fine.\n"
    ast = _pandoc_md_to_json(md)
    filtered = _run_filter(SCRIPTS / "critic-to-latex.py", ast)
    latex = _pandoc_json_to_latex(filtered)
    assert "\\uline{inserito}" in latex
    assert "\\sout{cancellato}" in latex
```

- [ ] **Step 2: Run, confirm failure**

Run: `python -m pytest tests/test_critic_filters.py::test_latex_filter_with_fallback_uses_sout_uline -v`
Expected: FAIL.

- [ ] **Step 3: Add env-driven fallback to the filter**

In `scripts/export/critic-to-latex.py`, near the top add:
```python
import os

_FALLBACK = os.environ.get("REDLINE_LATEX_FALLBACK") == "soul"


def _ins_macro(text: str) -> str:
    if _FALLBACK:
        return f"\\uline{{{text}}}"
    return f"\\added{{{text}}}"


def _del_macro(text: str) -> str:
    if _FALLBACK:
        return f"\\sout{{{text}}}"
    return f"\\deleted{{{text}}}"


def _repl_macro(new: str, old: str) -> str:
    if _FALLBACK:
        return f"\\sout{{{old}}}\\uline{{{new}}}"
    return f"\\replaced{{{new}}}{{{old}}}"
```

Replace the three places that build the LaTeX strings in `transform_inlines` with calls to these helpers.

- [ ] **Step 4: Add package detection in `parallel-export.sh`**

In `scripts/export/parallel-export.sh`, just before the `LATEX_HEADER` heredoc creation, replace the header block with:
```bash
    LATEX_HEADER=$(mktemp --suffix=.tex)
    if kpsewhich changes.sty >/dev/null 2>&1; then
      cat > "$LATEX_HEADER" <<'TEX'
\usepackage[markup=underlined,authormarkup=none]{changes}
TEX
    else
      cat > "$LATEX_HEADER" <<'TEX'
\usepackage{soul}
\usepackage[normalem]{ulem}
TEX
      export REDLINE_LATEX_FALLBACK=soul
      echo "[redline] LaTeX 'changes' package non disponibile, fallback a soul+ulem" >&2
    fi
```

- [ ] **Step 5: Run all tests**

Run: `python -m pytest tests/ -v`
Expected: all green (current count + new fallback test).

- [ ] **Step 6: Commit**

```bash
git add scripts/export/critic-to-latex.py scripts/export/parallel-export.sh tests/test_critic_filters.py
git commit -m "feat(redline): LaTeX soul fallback when 'changes' package missing"
```

---

## Phase E — Command + Documentation

### Task E1: Create `/relazione-redline` on-demand command

**Files:**
- Create: `commands/relazione-redline.md`

- [ ] **Step 1: Write the command file**

`commands/relazione-redline.md`:
```markdown
---
description: Genera una vista redline (track-changes) del draft corrente vs una baseline, senza alterare lo status di review.
argument-hint: "[baseline: backup|approved|imported] [--no-open]"
---

# /relazione-redline — Vista redline on-demand

Genera `<session>/.session/redline/.redlined-RELAZIONE.md` e apre la live preview con i diff attivi. **Non modifica `cover.status` né `state.status`.** Non persiste il flag in session-state (a differenza di `/relazione-review` che lo attiva automaticamente).

## Argomenti

- `backup` (default): confronta vs file più recente in `.session/backups/`.
- `approved`: confronta vs `archive/<latest>/RELAZIONE.md`.
- `imported`: confronta vs `.session/feedback/applied-*.md` più recente (se assente, fallback a `backup` con warning).
- `--no-open`: non aprire il browser.

## Cosa fare

1. **Trova la sessione** (Glob `relazioni*/.session/session-state.json`, come `/relazione-continua`).
2. **Risolvi baseline** secondo l'argomento (vedi `scripts/_resolve-baseline.sh`).
3. **Avvia live-preview con `--diff`**:
   ```bash
   bash ~/.claude/skills/relazione/scripts/workflow/live-preview-draft.sh <session> \
     --diff <baseline> --port 8766
   ```
   Se `--no-open` passato dall'utente, aggiungi `--no-open`.
4. **Output**:
   > Redline view: http://localhost:8766/.preview-RELAZIONE.html
   > Baseline: `<approved 2026-04-12 | backup 2026-05-14T09-12-44>`
   > Note: questa è una vista on-demand. Non viene esportato nessun file. Per redline negli export usa `/relazione-export --redline` o passa a `/relazione-review`.

## Red flags

- Mai modificare `session-state.json` da questo comando.
- Mai sovrascrivere file pulito di export.
- Se nessuna baseline trovata: errore esplicito, non avviare la preview.
```

- [ ] **Step 2: Verify it parses (manual)**

Run: `head -5 commands/relazione-redline.md` and confirm YAML frontmatter is valid.

- [ ] **Step 3: Commit**

```bash
git add commands/relazione-redline.md
git commit -m "feat(redline): /relazione-redline on-demand command"
```

---

### Task E2: Update `/relazione-help` index

**Files:**
- Modify: `commands/relazione-help.md`

- [ ] **Step 1: Add the row**

Open `commands/relazione-help.md`. Find the table of commands (look for `| /relazione-diff |` row). Insert directly below it:
```markdown
| `/relazione-redline` | `~/.claude/commands/relazione-redline.md` | Mostra modifiche vs baseline in live preview + abilita track-changes negli export |
```

- [ ] **Step 2: Commit**

```bash
git add commands/relazione-help.md
git commit -m "docs(redline): add /relazione-redline to help index"
```

---

### Task E3: Update SKILL.md

**Files:**
- Modify: `SKILL.md`

- [ ] **Step 1: Add bullet to Usability section**

Find the line `- **Usabilità**: \`live-preview.sh\`, \`progress-tracker.py\`, \`auto-save.sh\`` and change to:
```markdown
- **Usabilità**: `live-preview.sh`, `progress-tracker.py`, `auto-save.sh`, `redline-generator.py` (track-changes Word-style su HTML/PDF/DOCX)
```

- [ ] **Step 2: Add description to Review workflow**

Find the section describing `/relazione-review`. Add a sentence:
```markdown
Dalla v2.6.0, `/relazione-review` attiva automaticamente il **redline**: snapshot baseline + flag in session-state. Tutti gli export successivi producono file `*-redline.*` con inserimenti sottolineati e cancellazioni barrate. `/relazione-approve` archivia la baseline e disattiva il redline.
```

- [ ] **Step 3: Commit**

```bash
git add SKILL.md
git commit -m "docs(redline): document redline workflow in SKILL.md"
```

---

### Task E4: CHANGELOG + VERSION bump

**Files:**
- Modify: `CHANGELOG.md`
- Modify: `VERSION`

- [ ] **Step 1: Bump version**

Replace contents of `VERSION` with:
```
2.6.0
```

- [ ] **Step 2: Add CHANGELOG entry**

Prepend to `CHANGELOG.md` (under any existing header):
```markdown
## 2.6.0 — 2026-05-15

### Added
- **Redline (track-changes)** Word-style su 4 formati di export.
  - Nuovi script: `redline-generator.py`, `critic-to-latex.py`, `critic-to-typst.py`, `_resolve-baseline.sh`.
  - Nuovo comando: `/relazione-redline [backup|approved|imported]` per vista on-demand.
  - Nuovo flag `--redline` su `live-preview-draft.sh`, `export-html-standalone.sh`, `export-typst.sh`, `parallel-export.sh`.
  - Block `redline` in `session-state.json`.
  - LaTeX fallback automatico a `soul`+`ulem` se pacchetto `changes` non disponibile.
- Pytest scaffolding (`tests/conftest.py`, prime suite per `redline-generator` e filtri pandoc).

### Changed
- `/relazione-review` ora snapshot baseline in `.session/redline/baseline.md` e attiva `redline.enabled=true`.
- `/relazione-approve` ora archivia la baseline in `.session/redline/baselines/<timestamp>.md` e disattiva il redline.

### Notes
- Comportamento bytes-identico al pre-feature quando `--redline` non è passato e session non è in `in-review`.
- EPUB e audiobook esplicitamente esclusi dal redline (formati audio).
```

- [ ] **Step 3: Commit**

```bash
git add CHANGELOG.md VERSION
git commit -m "chore: bump version to 2.6.0 with redline changelog"
```

---

## Phase F — Regression & End-to-End

### Task F1: Regression test — clean export bytes-identity

**Files:**
- Create: `tests/test_regression_clean_export.py`

- [ ] **Step 1: Write the test**

`tests/test_regression_clean_export.py`:
```python
import hashlib
import subprocess
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_clean_html_export_unchanged_without_redline_flag(tmp_path):
    src = tmp_path / "doc.md"
    src.write_text("# Titolo\n\nTesto di prova.\n", encoding="utf-8")
    subprocess.run(
        ["bash", str(SKILL / "scripts" / "export-html-standalone.sh"), str(src)],
        check=True,
    )
    out = src.with_suffix(".html")
    assert out.exists(), "clean export must produce <name>.html (no -redline suffix)"
    assert not (src.with_name(src.stem + "-redline.html")).exists()
    # Second run with same input must produce byte-identical output
    h1 = _sha256(out)
    out.unlink()
    subprocess.run(
        ["bash", str(SKILL / "scripts" / "export-html-standalone.sh"), str(src)],
        check=True,
    )
    h2 = _sha256(out)
    assert h1 == h2, "clean export must be deterministic"
```

- [ ] **Step 2: Run and confirm green**

Run: `python -m pytest tests/test_regression_clean_export.py -v`
Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add tests/test_regression_clean_export.py
git commit -m "test(redline): regression test for clean export byte-identity"
```

---

### Task F2: End-to-end shell test

**Files:**
- Create: `tests/e2e/test_redline_pipeline.sh`

- [ ] **Step 1: Write the e2e test**

`tests/e2e/test_redline_pipeline.sh`:
```bash
#!/usr/bin/env bash
# End-to-end test of redline pipeline: baseline + draft → 4 formats with track-changes.
set -euo pipefail

SKILL_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
WORK=$(mktemp -d)
trap "rm -rf '$WORK'" EXIT

mkdir -p "$WORK/.session/backups"
cat > "$WORK/.session/backups/2026-05-14-RELAZIONE.md" <<EOF
# Test E2E

Versione originale del documento.
EOF
cat > "$WORK/RELAZIONE.md" <<EOF
# Test E2E

Versione modificata e ampliata del documento.
EOF

# HTML
bash "$SKILL_DIR/scripts/export/export-html-standalone.sh" "$WORK/RELAZIONE.md" --redline backup
[ -f "$WORK/RELAZIONE-redline.html" ] || { echo "FAIL: html"; exit 1; }
grep -qE "<ins>|<del>" "$WORK/RELAZIONE-redline.html" || { echo "FAIL: html no ins/del"; exit 1; }

# DOCX
bash "$SKILL_DIR/scripts/export/parallel-export.sh" "$WORK/RELAZIONE.md" --docx --redline backup
[ -f "$WORK/RELAZIONE-redline.docx" ] || { echo "FAIL: docx"; exit 1; }
unzip -p "$WORK/RELAZIONE-redline.docx" word/document.xml | grep -qE "w:ins|w:del" || { echo "FAIL: docx no track-changes"; exit 1; }

# Typst (if installed)
if command -v typst >/dev/null 2>&1; then
  bash "$SKILL_DIR/scripts/export/export-typst.sh" "$WORK/RELAZIONE.md" --redline backup
  [ -f "$WORK/RELAZIONE-redline.pdf" ] || { echo "FAIL: typst"; exit 1; }
fi

# PDF LaTeX (if xelatex installed)
if command -v xelatex >/dev/null 2>&1; then
  bash "$SKILL_DIR/scripts/export/parallel-export.sh" "$WORK/RELAZIONE.md" --pdf --redline backup
  [ -f "$WORK/RELAZIONE-redline.pdf" ] || { echo "FAIL: latex pdf"; exit 1; }
fi

echo "OK: e2e redline pipeline"
```

Make executable:
```bash
chmod +x tests/e2e/test_redline_pipeline.sh
```

- [ ] **Step 2: Run the e2e test**

Run: `bash tests/e2e/test_redline_pipeline.sh`
Expected: `OK: e2e redline pipeline`.

- [ ] **Step 3: Commit**

```bash
git add tests/e2e/test_redline_pipeline.sh
git commit -m "test(redline): end-to-end pipeline test"
```

---

## Final verification

- [ ] **Run full test suite**

Run from skill root:
```bash
python -m pytest tests/ -v && bash tests/e2e/test_redline_pipeline.sh
```
Expected: all unit tests pass + e2e prints `OK`.

- [ ] **Manual sanity check**

Open one of the generated `-redline.docx` files in Word or LibreOffice. Verify that **Track Changes** (Revisioni) view shows the insertions and deletions in the expected colors.

- [ ] **Final commit (if anything outstanding)**

```bash
git log --oneline | head -25
```
Confirm the commit history reads as a logical sequence (one feature per commit).

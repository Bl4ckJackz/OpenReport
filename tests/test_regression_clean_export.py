"""Regression test: clean export (no --redline flag) must remain bytes-deterministic
and must NOT produce -redline suffixed files."""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_clean_html_export_unchanged_without_redline_flag(repo_root, tmp_path, bash_exe):
    src = tmp_path / "doc.md"
    src.write_text("# Titolo\n\nTesto di prova.\n", encoding="utf-8")
    script = repo_root / "scripts" / "export" / "export-html-standalone.sh"

    subprocess.run([bash_exe, str(script), str(src)], check=True, capture_output=True)
    # Expected output filename: same as input but .html (no -redline suffix)
    out = src.with_suffix(".html")
    assert out.exists(), "clean export must produce <name>.html (no -redline suffix)"
    assert not (src.with_name(src.stem + "-redline.html")).exists(), \
        "clean run must NOT produce -redline.html"

    h1 = _sha256(out)
    out.unlink()
    subprocess.run([bash_exe, str(script), str(src)], check=True, capture_output=True)
    h2 = _sha256(out)
    assert h1 == h2, f"clean export must be deterministic; got {h1[:16]} != {h2[:16]}"

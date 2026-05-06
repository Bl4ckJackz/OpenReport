"""Verify all JSON schemas under schemas/ are loadable and structurally valid."""
from __future__ import annotations

import json

import pytest

jsonschema = pytest.importorskip("jsonschema")


def test_all_schemas_load(repo_root):
    schema_dir = repo_root / "schemas"
    assert schema_dir.is_dir(), "schemas/ directory missing"
    files = list(schema_dir.glob("*.json"))
    assert files, "no schema files found"

    for f in files:
        data = json.loads(f.read_text())
        # Must have $schema or a known JSON Schema metaschema marker
        assert "$schema" in data or "type" in data or "properties" in data, (
            f"{f.name} does not look like a JSON Schema"
        )
        # jsonschema.Draft7Validator.check_schema raises on malformed schema
        jsonschema.Draft7Validator.check_schema(data)

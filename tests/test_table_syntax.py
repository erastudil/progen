# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import sys
from pathlib import Path

# Ensure the progen source directory is on the import path
_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from progen.parse import Role, parse_text


def test_markdown_table_row_separators_not_broken_prose():
    """Markdown table rows with pipes should not be treated as broken prose."""
    table = (
        "| Name | Age |\n"
        "|------|-----|\n"
        "| Alice| 30  |\n"
        "| Bob  | 25  |\n"
    )
    doc = parse_text(table, Role.IRON)

    # Asides are used for stray comments; a well‑formed table should produce none.
    assert doc.asides == []

    # The parser should not mistake table rows for imperative topic‑comment units.
    topic_units = [u for u in doc.units if u.kind == "topic_comment"]
    assert len(topic_units) == 0


def test_markdown_table_slack_role():
    """Same check for the SLACK role to ensure role‑independent handling."""
    table = (
        "| Item | Cost |\n"
        "|------|------|\n"
        "| Book | 12.99|\n"
        "| Pen  | 1.50 |\n"
    )
    doc = parse_text(table, Role.SLACK)

    assert doc.asides == []
    topic_units = [u for u in doc.units if u.kind == "topic_comment"]
    assert len(topic_units) == 0

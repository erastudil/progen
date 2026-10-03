# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from progen.parse import Role, parse_text


def test_markdown_table_rows_parsed_as_prose_units():
    table_text = (
        "| Header 1 | Header 2 |\n"
        "|----------|----------|\n"
        "| cell 1   | cell 2   |\n"
        "| cell 3   | cell 4   |\n"
    )
    doc = parse_text(table_text, Role.IRON)
    # Expect each line to be parsed as a separate prose unit
    assert len(doc.units) == 4
    for unit in doc.units:
        assert unit.kind == "prose"
    # Verify the content matches the table lines (without newlines)
    expected_lines = [
        "| Header 1 | Header 2 |",
        "|----------|----------|",
        "| cell 1   | cell 2   |",
        "| cell 3   | cell 4   |",
    ]
    for unit, expected in zip(doc.units, expected_lines):
        assert unit.text == expected

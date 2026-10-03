# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import pytest
from progen.parse import Role, parse_text


def test_simple_markdown_table() -> None:
    """A basic markdown table should parse without broken prose units."""
    table = (
        "| Header1 | Header2 |\n"
        "|---------|---------|\n"
        "| Cell1   | Cell2   |\n"
    )
    doc = parse_text(table, Role.IRON)
    # The parser should not crash and should return a document
    assert doc is not None
    # No unit should be the raw separator line
    for unit in doc.units:
        assert unit.kind != "broken"
        if hasattr(unit, "comment") and unit.comment:
            assert "|---" not in unit.comment
        if hasattr(unit, "topic") and unit.topic:
            assert "|---" not in unit.topic


def test_markdown_table_with_pipes_in_cells() -> None:
    """Table cells containing pipe characters should not be treated as separators."""
    table = (
        "| Command | Description |\n"
        "|---------|-------------|\n"
        "| `cmd | grep foo` | Search for foo |\n"
        "| `ls -l | head`   | List and limit |\n"
    )
    doc = parse_text(table, Role.IRON)
    assert doc is not None
    # Ensure no unit is flagged as broken
    for unit in doc.units:
        assert unit.kind != "broken"


def test_markdown_table_multiple_rows() -> None:
    """Multiple data rows should parse cleanly."""
    table = (
        "| A | B |\n"
        "|---|---|\n"
        "| 1 | 2 |\n"
        "| 3 | 4 |\n"
        "| 5 | 6 |\n"
    )
    doc = parse_text(table, Role.IRON)
    assert doc is not None
    for unit in doc.units:
        assert unit.kind != "broken"


if __name__ == "__main__":
    pytest.main([__file__])

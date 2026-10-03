# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from progen.parse import Role, parse_text


def test_table_row_pipes_clean() -> None:
    """Pipe characters in table rows should not create broken prose units."""
    text = "| Name | Value |\n|------|-------|\n| foo  | bar   |\n"
    doc = parse_text(text, Role.IRON)
    
    # Verify no unit has kind indicating broken prose from pipes
    kinds = [u.kind for u in doc.units]
    assert "broken_prose" not in kinds
    
    # Verify separator row dashes are not parsed as a topic
    for unit in doc.units:
        assert unit.topic != "------"


def test_table_separator_row_ignored() -> None:
    """The markdown separator row should not be treated as prose."""
    text = "| Header 1 | Header 2 |\n|----------|----------|\n"
    doc = parse_text(text, Role.IRON)
    
    # Check that the dashes in separator don't appear as topics
    topics = [u.topic for u in doc.units if hasattr(u, 'topic')]
    assert "----------" not in topics


def test_table_pipes_not_asides() -> None:
    """Pipe characters should not be parsed as asides."""
    text = "| cmd | desc |\n|-----|------|\n"
    doc = parse_text(text, Role.IRON)
    
    # Asides should remain empty or not contain table syntax
    for aside in doc.asides:
        assert "|" not in aside.text


def test_complex_table_parses() -> None:
    """Complex table with multiple pipes parses without error."""
    text = """| Name | Age | City |
|------|-----|------|
| Alice | 30 | NYC |
| Bob | 25 | LA |
"""
    doc = parse_text(text, Role.IRON)
    
    # Should parse without creating broken units
    assert isinstance(doc.units, list)
    assert isinstance(doc.asides, list)

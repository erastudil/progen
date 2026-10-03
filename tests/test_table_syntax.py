# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import pytest
from progen.parse import parse_text, Role


def test_markdown_table_rows_do_not_create_false_units():
    """Markdown table syntax should not be mistaken for prose units."""
    table = (
        "| Header 1 | Header 2 | Header 3 |\n"
        "|----------|----------|----------|\n"
        "| cell A1  | cell A2  | cell A3  |\n"
        "| cell B1  | cell B2  | cell B3  |\n"
    )

    # Test with IRON role (colon as topic comment marker)
    doc_iron = parse_text(table, Role.IRON)
    # No units should be recognized as topic_comment or any other kind that
    # would indicate broken prose.
    assert all(u.kind != "topic_comment" for u in doc_iron.units)
    # Asides should also stay empty because there are no "//" style comments.
    assert doc_iron.asides == []

    # Test with SLACK role (comma as topic comment marker)
    doc_slack = parse_text(table, Role.SLACK)
    assert all(u.kind != "topic_comment" for u in doc_slack.units)
    assert doc_slack.asides == []


def test_markdown_table_with_pipes_in_cell_content():
    """Pipes inside cell content should not interfere with parsing."""
    table = (
        "| Name | Description |\n"
        "|------|-------------|\n"
        "| `a|b` | a pipe inside code |\n"
        "| `c | d` | another pipe |\n"
    )
    doc = parse_text(table, Role.IRON)
    assert all(u.kind != "topic_comment" for u in doc.units)
    assert doc.asides == []

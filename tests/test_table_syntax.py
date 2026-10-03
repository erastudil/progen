# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import pytest
from progen.parse import Role, parse_text


def test_markdown_table_pipes_not_broken_prose() -> None:
    """Markdown table rows with pipes should parse cleanly without treating separators as broken prose."""
    md_table = (
        "| Header1 | Header2 |\n"
        "|---------|---------|\n"
        "| Cell1   | Cell2   |\n"
        "| Cell3   | Cell4   |\n"
    )
    doc = parse_text(md_table, Role.IRON)
    # Should not produce any topic_comment units from the table pipes
    topic_comments = [u for u in doc.units if u.kind == "topic_comment"]
    assert topic_comments == []


def test_markdown_table_with_content_around() -> None:
    """Table embedded in prose should not break surrounding text parsing."""
    text = (
        "Here is a table:\n"
        "| A | B |\n"
        "|---|---|\n"
        "| 1 | 2 |\n"
        "End of table.\n"
    )
    doc = parse_text(text, Role.IRON)
    # The prose before/after should be parsed, but table rows not as topic_comment
    topic_comments = [u for u in doc.units if u.kind == "topic_comment"]
    assert topic_comments == []


def test_pipe_heavy_prose_not_mistaken_for_table() -> None:
    """Prose with many pipes (not a table) should not be misclassified."""
    text = "This | has | many | pipes | but | is | not | a | table.\n"
    doc = parse_text(text, Role.IRON)
    # Should not be parsed as a table; no topic_comment units from pipes
    topic_comments = [u for u in doc.units if u.kind == "topic_comment"]
    assert topic_comments == []


def test_table_row_separator_not_flagged() -> None:
    """The row separator line (---|---) should not raise flags or create units."""
    md_table = "| H1 | H2 |\n|----|----|\n| a  | b  |\n"
    doc = parse_text(md_table, Role.IRON)
    # No elevated/test/admin flags from the separator
    assert not doc.flags.get("elevated")
    assert not doc.flags.get("test")
    assert not doc.flags.get("admin")
    # No protocol units from the separator
    protocols = [u for u in doc.units if u.kind == "protocol"]
    assert protocols == []


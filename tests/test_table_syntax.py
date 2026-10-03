# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from progen.parse import Role, parse_text


def test_markdown_table_header_and_separator() -> None:
    """Markdown table header and separator row should not be parsed as broken prose."""
    text = (
        "| Name | Age |\n"
        "|------|-----|\n"
        "| Alice | 30 |\n"
        "| Bob   | 25 |\n"
    )
    doc = parse_text(text, Role.IRON)
    # The separator row (|------|-----|) should not produce a topic_comment unit
    topic_comments = [u for u in doc.units if u.kind == "topic_comment"]
    assert not any("------" in (u.comment or "") for u in topic_comments)
    # The header and data rows should not be misclassified as topic_comment either
    assert not any("Name" in (u.topic or "") for u in topic_comments)
    assert not any("Alice" in (u.topic or "") for u in topic_comments)


def test_markdown_table_with_pipes_in_cells() -> None:
    """Pipes inside table cells should not break parsing."""
    text = (
        "| Command | Description |\n"
        "|---------|-------------|\n"
        "| `ls -l` | List files |\n"
        "| `echo \"a|b\"` | Pipe in quotes |\n"
    )
    doc = parse_text(text, Role.IRON)
    topic_comments = [u for u in doc.units if u.kind == "topic_comment"]
    # No topic_comment should contain the separator dashes
    assert not any("---------" in (u.comment or "") for u in topic_comments)
    # The row with a pipe in quotes should not be split into multiple units
    assert not any("Pipe in quotes" in (u.topic or "") for u in topic_comments)


def test_markdown_table_mixed_with_prose() -> None:
    """Prose before and after a table should parse normally; table rows should not interfere."""
    text = (
        "Here is a table:\n\n"
        "| A | B |\n"
        "|---|---|\n"
        "| 1 | 2 |\n\n"
        "End of table."
    )
    doc = parse_text(text, Role.IRON)
    # Prose units should exist for the sentences
    prose_units = [u for u in doc.units if u.kind == "prose"]
    assert any("Here is a table" in (u.text or "") for u in prose_units)
    assert any("End of table" in (u.text or "") for u in prose_units)
    # Table separator should not create a topic_comment
    topic_comments = [u for u in doc.units if u.kind == "topic_comment"]
    assert not any("---" in (u.comment or "") for u in topic_comments)


def test_markdown_table_slack_role() -> None:
    """Same table parsing behavior under SLACK role."""
    text = (
        "| Task | Status |\n"
        "|------|--------|\n"
        "| Build | Pass |\n"
        "| Test  | Fail |\n"
    )
    doc = parse_text(text, Role.SLACK)
    topic_comments = [u for u in doc.units if u.kind == "topic_comment"]
    # Separator row should not be a topic_comment
    assert not any("------" in (u.comment or "") for u in topic_comments)
    # Header row should not be a topic_comment (no comma mark in SLACK for this)
    assert not any("Task" in (u.topic or "") for u in topic_comments)

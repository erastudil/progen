# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from progen.parse import Role, parse_text


def test_markdown_table_rows_are_not_broken_prose() -> None:
    """Markdown tables with pipe characters should not spawn spurious units."""
    md_table = """
| Name | Age |
|------|-----|
| Alice| 30  |
| Bob  | 25  |
"""
    text = md_table.strip()
    doc = parse_text(text, Role.IRON)

    # No topic_comment units should be created from the table pipes
    topic_comments = [u for u in doc.units if u.kind == "topic_comment"]
    assert not topic_comments, f"Unexpected topic_comment units: {topic_comments}"

    # No asides should be mistakenly detected
    assert not doc.asides, f"Unexpected asides: {doc.asides}"

    # The parser should not flag the document as having asides
    assert not doc.flags.get("has_asides"), "has_asides flag should be False"


def test_markdown_table_with_extra_pipes_still_clean() -> None:
    """Tables containing extra pipes in cells should not be parsed as prose."""
    md_table = """
| Item | Description | Notes |
|------|-------------|-------|
| Git  | VCS | Hosted on GitHub |
| Docker | Container platform | Uses daemon |
"""
    text = md_table.strip()
    doc = parse_text(text, Role.IRON)

    # Ensure no stray units
    assert all(u.kind != "topic_comment" for u in doc.units)
    assert doc.asides == []
    assert not doc.flags.get("has_asides", False)

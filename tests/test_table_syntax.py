# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from progen.parse import Role, parse_text


def test_markdown_table_rows_stay_prose():
    """Markdown table rows should stay prose and never produce topic_comment units."""
    table = (
        "| Name | Age |\n"
        "|------|-----|\n"
        "| Alice| 30  |\n"
        "| Bob  | 25  |\n"
    )
    doc = parse_text(table, Role.IRON)
    assert doc.asides == []
    topic_units = [u for u in doc.units if u.kind == "topic_comment"]
    assert len(topic_units) == 0


def test_markdown_table_colon_space_cell_fails_when_called_topic_comment():
    """A table test must import parse_text and fail when a colon-space cell is called topic_comment."""
    table = (
        "| Setting | Value |\n"
        "|:---|:---|\n"
        "| opt | status: active |\n"
    )
    doc = parse_text(table, Role.IRON)
    topic_units = [u for u in doc.units if u.kind == "topic_comment"]
    # Fails when a colon-space cell is called topic_comment
    assert len(topic_units) == 0, f"colon-space cell was called topic_comment: {topic_units}"

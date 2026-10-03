# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from progen.parse import Role, parse_text


def test_markdown_table_basic() -> None:
    """Basic table should not confuse the parser."""
    text = (
        "| a | b |\n"
        "|---|---|\n"
        "| c | d |\n"
    )
    doc = parse_text(text, Role.IRON)
    assert doc.asides == []
    assert all(u.kind != "topic_comment" for u in doc.units)


def test_markdown_table_with_colons_in_cells() -> None:
    """Colons inside table cells should not be treated as topic marks."""
    text = (
        "| key : value | other |\n"
        "|---|---|\n"
        "| a : b | c |\n"
    )
    doc = parse_text(text, Role.IRON)
    assert doc.asides == []

    lines = text.splitlines()
    # The row separator line is the second line (index 1)
    row_sep_line = lines[1]

    asides_text = [aside.text for aside in doc.asides]
    topic_comments_text = []
    for unit in doc.units:
        if unit.kind == "topic_comment" and unit.comment is not None:
            topic_comments_text.append(unit.comment)

    assert row_sep_line not in asides_text
    assert row_sep_line not in topic_comments_text

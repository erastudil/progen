# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from progen.parse import Role, parse_text


def test_markdown_table_simple() -> None:
    text = """
    | A | B |
    |---|---|
    | 1 | 2 |
    """
    doc = parse_text(text, Role.IRON)
    topic_comments = [u for u in doc.units if u.kind == "topic_comment"]
    assert len(topic_comments) == 0
    assert len(doc.asides) == 0


def test_markdown_table_with_colons_in_separator() -> None:
    text = """
    | :--- | :---: | ---: |
    | left | center | right |
    """
    doc = parse_text(text, Role.IRON)
    topic_comments = [u for u in doc.units if u.kind == "topic_comment"]
    assert len(topic_comments) == 0
    assert len(doc.asides) == 0

# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import sys
from pathlib import Path

# Ensure the progen source is importable
_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from progen.parse import Role, parse_text


def test_markdown_table_syntax() -> None:
    """Markdown table rows with pipes should not be mistaken for broken prose."""
    text = """\
| Name | Age |
|------|-----|
| Alice| 30  |
| Bob  | 25  |
"""
    doc = parse_text(text, Role.IRON)

    # Table syntax should not produce asides (broken prose)
    assert doc.asides == []

    # Table syntax should not be interpreted as topic_comment units
    assert all(unit.kind != "topic_comment" for unit in doc.units)

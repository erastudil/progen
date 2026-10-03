# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from progen.parse import Role, parse_text

_TABLE = """\
| name | value |
| --- | --- |
| alpha | beta |
| gamma | delta |
"""

def _nonempty_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.strip()]

def _assert_table_syntax(text: str) -> None:
    lines = _nonempty_lines(text)
    assert len(lines) >= 2
    header = lines[0]
    separator = lines[1]
    assert header.startswith("|") and header.endswith("|")
    assert separator.startswith("|") and separator.endswith("|")
    header_count = header.count("|")
    assert header_count >= 2
    for line in lines[1:]:
        assert line.count("|") == header_count
    cells = [cell.strip() for cell in separator.strip("|").split("|")]
    assert cells
    for cell in cells:
        assert cell
        assert all(ch in "-: " for ch in cell)

def test_markdown_table_syntax_is_valid() -> None:
    _assert_table_syntax(_TABLE)

def test_markdown_table_rows_parse_cleanly() -> None:
    doc = parse_text(_TABLE, Role.IRON)
    units = list(doc.units or [])
    asides = list(doc.asides or [])
    flags = dict(doc.flags or {})

    broken_units = [unit for unit in units if "broken" in str(getattr(unit, "kind", ""))]
    assert broken_units == []
    assert not flags.get("broken_prose")
    assert not flags.get("broken")

    for aside in asides:
        text = str(getattr(aside, "text", "") or "")
        assert "| --- |" not in text
        assert "---" not in text.strip()

def test_markdown_table_separator_is_not_broken_prose() -> None:
    text = "| one | two |\n| --- | --- |\n| three | four |\n"
    doc = parse_text(text, Role.IRON)
    units = list(doc.units or [])
    flags = dict(doc.flags or [])
    assert not any("broken" in str(getattr(unit, "kind", "")) for unit in units)
    assert not flags.get("broken_prose")

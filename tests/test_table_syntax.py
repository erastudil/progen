# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from progen.parse import Role, parse_text


def test_markdown_table_iron_role_no_spurious_units():
    table = "| one | two |\n|----|----|\n| a  | b  |"
    doc = parse_text(table, Role.IRON)
    # Ensure no topic_comment units are created from table syntax
    topic_comments = [u for u in doc.units if u.kind == "topic_comment"]
    assert len(topic_comments) == 0
    # All units should be prose (table rows treated as prose)
    assert all(u.kind == "prose" for u in doc.units)


def test_markdown_table_slack_role_no_spurious_units():
    table = "| one | two |\n|----|----|\n| a  | b  |"
    doc = parse_text(table, Role.SLACK)
    # Ensure no topic_comment units are created from table syntax
    topic_comments = [u for u in doc.units if u.kind == "topic_comment"]
    assert len(topic_comments) == 0
    # All units should be prose (table rows treated as prose)
    assert all(u.kind == "prose" for u in doc.units)

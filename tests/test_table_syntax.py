# SPDX-License-Identifier: AGPL-3.0-or-later
from progen.parse import Role, parse_text


def test_markdown_table_syntax_parsing_iron():
    """Markdown table rows with pipes should not create topic_comment units."""
    table = (
        "| Name | Age |\n"
        "|------|-----|\n"
        "| Alice | 30 |\n"
        "| Bob   | 25 |\n"
    )
    doc = parse_text(table, Role.IRON)
    # Ensure no topic_comment units are incorrectly generated from table syntax
    assert [u for u in doc.units if u.kind == "topic_comment"] == []
    # Ensure no asides are incorrectly generated
    assert doc.asides == []


def test_markdown_table_syntax_parsing_slack():
    """Markdown table rows with pipes should not create topic_comment units under SLACK role."""
    table = (
        "| Item | Cost |\n"
        "|------|------|\n"
        "| Apples | 1.20 |\n"
        "| Bread  | 2.50 |\n"
    )
    doc = parse_text(table, Role.SLACK)
    # Ensure no topic_comment units are incorrectly generated from table syntax
    assert [u for u in doc.units if u.kind == "topic_comment"] == []
    # Ensure no asides are incorrectly generated
    assert doc.asides == []

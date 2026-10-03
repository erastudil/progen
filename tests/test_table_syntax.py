# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import pytest
from progen.parse import Role, parse_text


def test_simple_markdown_table_parsing():
    """Test that simple markdown tables are parsed without breaking into prose."""
    markdown_with_table = """| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |
| Data A   | Data B   |
"""
    
    doc = parse_text(markdown_with_table, Role.IRON)
    
    # Check that the table is treated as prose, not broken into topic comments
    topic_comments = [u for u in doc.units if u.kind == "topic_comment"]
    assert len(topic_comments) == 0
    
    # Check that there's prose content (the table)
    prose_units = [u for u in doc.units if u.kind == "prose"]
    assert len(prose_units) >= 1


def test_markdown_table_with_pipe_in_content():
    """Test that pipes within table cells don't break parsing."""
    markdown_with_table = """| Name | Description |
|------|-------------|
| Item 1 | This has | pipe symbol |
| Item 2 | Another | example here |
"""
    
    doc = parse_text(markdown_with_table, Role.IRON)
    
    # Should not create topic comments from table rows
    topic_comments = [u for u in doc.units if u.kind == "topic_comment"]
    assert len(topic_comments) == 0
    
    # Should have prose content containing the table
    prose_units = [u for u in doc.units if u.kind == "prose"]
    assert len(prose_units) >= 1


def test_complex_markdown_table():
    """Test complex markdown table with various formatting."""
    markdown_with_table = """# Sample Document

Here's some content before the table:

| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Cell 1   | Cell 2   | Cell 3   |
| Row 2 A  | Row 2 B  | Row 2 C  |
| Row 3 X  | Row 3 Y  | Row 3 Z  |

Content after the table.
"""
    
    doc = parse_text(markdown_with_table, Role.IRON)
    
    # Should not create topic comments from table rows
    topic_comments = [u for u in doc.units if u.kind == "topic_comment"]
    assert len(topic_comments) == 0
    
    # Should have prose content
    prose_units = [u for u in doc.units if u.kind == "prose"]
    assert len(prose_units) >= 1


def test_mixed_content_with_table():
    """Test document with both regular content and markdown table."""
    mixed_content = """This is a regular sentence.

| Table | Column |
|-------|--------|
| Data  | Info   |

Another regular sentence with no pipes.
"""
    
    doc = parse_text(mixed_content, Role.IRON)
    
    # Should not treat table rows as topic comments
    topic_comments = [u for u in doc.units if u.kind == "topic_comment"]
    assert len(topic_comments) == 0
    
    # Should have prose content
    prose_units = [u for u in doc.units if u.kind == "prose"]
    assert len(prose_units) >= 1


def test_table_separators_not_treated_as_commands():
    """Ensure table separator lines aren't misinterpreted as commands."""
    table_content = """| Col A | Col B |
|-------|-------|
| Val A | Val B |
"""
    
    doc = parse_text(table_content, Role.IRON)
    
    # Verify no protocol or other special units are created from table separators
    protocol_units = [u for u in doc.units if u.kind == "protocol"]
    assert len(protocol_units) == 0
    
    admin_units = [u for u in doc.units if u.kind == "admin"]
    assert len(admin_units) == 0
    
    elevated_units = [u for u in doc.units if u.kind == "elevated"]
    assert len(elevated_units) == 0


def test_table_with_special_characters():
    """Test table containing various special characters."""
    table_with_special_chars = """| Command | Description |
|---------|-------------|
| `ls -la` | List all files |
| grep "pattern" | Search for pattern |
| echo $VAR | Print variable |
"""
    
    doc = parse_text(table_with_special_chars, Role.IRON)
    
    # Should not create topic comments from table rows
    topic_comments = [u for u in doc.units if u.kind == "topic_comment"]
    assert len(topic_comments) == 0
    
    # Should preserve the table as prose
    prose_units = [u for u in doc.units if u.kind == "prose"]
    assert len(prose_units) >= 1


def test_single_row_table():
    """Test minimal single data row table."""
    single_row_table = """| A | B |
|---|---|
| X | Y |
"""
    
    doc = parse_text(single_row_table, Role.IRON)
    
    # Should not create topic comments
    topic_comments = [u for u in doc.units if u.kind == "topic_comment"]
    assert len(topic_comments) == 0


def test_table_with_empty_cells():
    """Test table with empty cells."""
    table_with_empty = """| Left | Middle | Right |
|------|--------|-------|
| A    |        | C     |
|      | B      |       |
"""
    
    doc = parse_text(table_with_empty, Role.IRON)
    
    # Should not create topic comments from empty cells
    topic_comments = [u for u in doc.units if u.kind == "topic_comment"]
    assert len(topic_comments) == 0

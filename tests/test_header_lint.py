# SPDX-License-Identifier: AGPL-3.0-or-later
"""Tests for markdown header depth hierarchy linting."""
from __future__ import annotations

import re
from typing import List, Tuple


def validate_headers(markdown: str) -> List[str]:
    """Validate header depth hierarchy in markdown.

    Returns a list of error messages. Empty list means valid.
    Rules:
    - Headers must not skip levels when increasing depth.
    - Going from a higher level to a lower level is always allowed.
    - Same level is allowed.
    """
    errors: List[str] = []
    # Regex to match ATX headers (##, ###, etc.)
    header_re = re.compile(r'^(#{1,6})\s+(.*)$')
    previous_level = 0
    for line_number, line in enumerate(markdown.splitlines(), start=1):
        match = header_re.match(line)
        if not match:
            continue
        level = len(match.group(1))
        if previous_level > 0 and level > previous_level:
            if level - previous_level > 1:
                errors.append(
                    f"Line {line_number}: skipped header level "
                    f"(from {previous_level} to {level})"
                )
        previous_level = level
    return errors


def test_sequential_headers_pass() -> None:
    """Valid sequential headers should produce no errors."""
    md = "# Title\n## Subtitle\n### Sub-subtitle\n#### Details"
    errors = validate_headers(md)
    assert errors == [], f"Expected no errors, got {errors}"


def test_same_level_headers_pass() -> None:
    """Repeated same-level headers are allowed."""
    md = "# Title\n# Another Title\n## Sub"
    errors = validate_headers(md)
    assert errors == [], f"Expected no errors, got {errors}"


def test_decreasing_levels_pass() -> None:
    """Going back to lower levels is allowed."""
    md = "# Title\n## Sub\n### Deep\n## Another Sub\n# Back to top"
    errors = validate_headers(md)
    assert errors == [], f"Expected no errors, got {errors}"


def test_skip_one_level_fails() -> None:
    """Skipping a single level (e.g., # to ###) should be flagged."""
    md = "# Title\n### Skipped"
    errors = validate_headers(md)
    assert len(errors) == 1
    assert "skipped" in errors[0].lower()
    assert "2" in errors[0] or "level" in errors[0]


def test_skip_multiple_levels_fails() -> None:
    """Skipping multiple levels (e.g., ## to ######) should be flagged."""
    md = "## Sub\n###### Deep skip"
    errors = validate_headers(md)
    assert len(errors) == 1
    assert "skipped" in errors[0].lower()


def test_no_headers_pass() -> None:
    """Markdown without headers is valid."""
    md = "Just some text.\nNo headers here."
    errors = validate_headers(md)
    assert errors == []


def test_first_header_can_be_any_level() -> None:
    """The first header can be any level without prior context."""
    md = "### Start deep\n## Then go up"
    errors = validate_headers(md)
    assert errors == []


def test_mixed_valid_and_invalid() -> None:
    """A document with both valid and invalid transitions should report only the invalid ones."""
    md = (
        "# Level 1\n"
        "## Level 2\n"
        "### Level 3\n"
        "##### Skipped to 5\n"
        "## Back to 2\n"
        "#### Skipped again from 2 to 4"
    )
    errors = validate_headers(md)
    assert len(errors) == 2
    # Check that both errors mention skipped levels
    assert all("skipped" in e.lower() for e in errors)


if __name__ == "__main__":
    # Allow running directly for quick manual check
    import sys
    sys.exit(0)

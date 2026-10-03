# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

try:
    from progen.lint import validate_headers  # type: ignore[import-not-found]
except ImportError:
    validate_headers = None  # type: ignore[assignment]


def test_valid_sequential_headers() -> None:
    if validate_headers is None:
        pytest.skip("validate_headers not implemented")
    markdown = "# a\n## b\n### c\n"
    assert validate_headers(markdown) == []


def test_valid_single_header() -> None:
    if validate_headers is None:
        pytest.skip("validate_headers not implemented")
    markdown = "# a\n"
    assert validate_headers(markdown) == []


def test_valid_starting_at_level_two() -> None:
    if validate_headers is None:
        pytest.skip("validate_headers not implemented")
    markdown = "## a\n### b\n"
    assert validate_headers(markdown) == []


def test_invalid_skip_level_one_to_three() -> None:
    if validate_headers is None:
        pytest.skip("validate_headers not implemented")
    markdown = "# a\n### b\n"
    errors = validate_headers(markdown)
    assert errors != []  # Expect non-empty list of errors


def test_invalid_skip_level_two_to_four() -> None:
    if validate_headers is None:
        pytest.skip("validate_headers not implemented")
    markdown = "## a\n#### b\n"
    errors = validate_headers(markdown)
    assert errors != []  # Expect non-empty list of errors

# SPDX-License-Identifier: AGPL-3.0-or-later
"""progen dialect: parse, lint, prompt emit."""

from .lint import Finding, lint_text
from .parse import Document, Role, parse_text
from .prompt import load_prompt

__version__ = "1.0.0"
__all__ = [
    "Document",
    "Finding",
    "Role",
    "lint_text",
    "load_prompt",
    "parse_text",
    "__version__",
]

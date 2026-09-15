# SPDX-License-Identifier: AGPL-3.0-or-later
"""progen dialect: parse, lint, prompt emit."""

from .iron import iron_text
from .lint import Finding, lint_text
from .parse import Document, Role, parse_text
from .prompt import load_prompt

__version__ = "1.1.0"
__all__ = [
    "Document",
    "Finding",
    "Role",
    "iron_text",
    "lint_text",
    "load_prompt",
    "parse_text",
    "__version__",
]

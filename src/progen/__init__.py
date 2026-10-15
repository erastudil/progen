# SPDX-License-Identifier: AGPL-3.0-or-later
"""progen: dialect of English for agent think, agent write, and think traces."""

from __future__ import annotations

from .syntax import syntax_text
from .lint import Finding, lint_text, load_rules
from .parse import Aside, Document, Role, Span, Unit, parse_text
from .prompt import load_prompt
from .db import ProgenDB
from .search import ProgenSearchIndex, SearchHit
from .stream import StreamEvent, StreamingProgenTokenizer, UnitType

__version__ = "1.3.2"

__all__ = [
    "Aside",
    "Document",
    "Finding",
    "ProgenDB",
    "ProgenSearchIndex",
    "Role",
    "SearchHit",
    "Span",
    "StreamEvent",
    "StreamingProgenTokenizer",
    "Unit",
    "UnitType",
    "lint_text",
    "load_prompt",
    "load_rules",
    "parse_text",
    "syntax_text",
]

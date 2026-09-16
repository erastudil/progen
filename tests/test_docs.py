# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import sys
import unittest
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from progen.lint import lint_text
from progen.prompt import repo_root

_DOCS = [
    "docs/SPEC.md",
    "docs/IMPLEMENTATION.md",
    "docs/BOUNDARY.md",
    "docs/FAILURES.md",
    "prompts/genome.md",
    "prompts/canon.md",
    "README.md",
    "AGENTS.md",
    "COVENANT.md",
    "examples/iron.md",
    "examples/english-poetry.md",
]


class DocsLint(unittest.TestCase):
    def test_tree_is_clean(self) -> None:
        root = repo_root()
        for rel in _DOCS:
            findings = lint_text((root / rel).read_text(encoding="utf-8"), role="agent")
            self.assertEqual(findings, [], msg=f"{rel}: {findings}")


class Traces(unittest.TestCase):
    def test_good_turn_clean(self) -> None:
        text = (repo_root() / "tests" / "traces" / "good_turn.md").read_text(encoding="utf-8")
        self.assertEqual(lint_text(text, role="agent"), [])

    def test_bad_turn_hits_new_rules(self) -> None:
        text = (repo_root() / "tests" / "traces" / "bad_turn.md").read_text(encoding="utf-8")
        ids = {f.rule for f in lint_text(text, role="agent")}
        for needed in ("P012", "P013", "P014"):
            self.assertIn(needed, ids, msg=f"missing {needed} in {ids}")


if __name__ == "__main__":
    unittest.main()

# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import sys
import unittest
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from progen.iron import iron_text
from progen.prompt import repo_root


class Iron(unittest.TestCase):
    def test_worked_mush(self) -> None:
        mush = (repo_root() / "examples" / "mush.md").read_text(encoding="utf-8")
        out = iron_text(mush).lower()
        self.assertIn("parse_text", out)
        self.assertIn("mark scanner", out)
        self.assertIn("//", out)
        self.assertNotIn("happy to help", out)
        self.assertNotIn("let me know", out)
        self.assertNotIn("compiler", out)

    def test_drops_disclaimer_and_hook(self) -> None:
        out = iron_text(
            "As an AI, I should mention this is not legal advice.\n"
            "What should we work on next?\n"
        )
        self.assertEqual(out.strip(), "")

    def test_lifts_paren_to_aside(self) -> None:
        out = iron_text("scale is density (the cheap job).\n")
        self.assertIn("scale : density.", out)
        self.assertIn("// the cheap job", out)

    def test_leaves_existing_iron(self) -> None:
        src = "parse : marks a parser can see.\n"
        self.assertEqual(iron_text(src), src)


if __name__ == "__main__":
    unittest.main()

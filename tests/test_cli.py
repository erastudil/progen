# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from progen.__main__ import main


class LintAskHelp(unittest.TestCase):
    def test_ask_help_names_p016(self) -> None:
        buf = io.StringIO()
        with self.assertRaises(SystemExit) as caught:
            with redirect_stdout(buf):
                main(["lint", "--help"])
        self.assertEqual(caught.exception.code, 0)
        text = buf.getvalue()
        self.assertIn("--ask-file", text)
        self.assertEqual(text.count("enables P016"), 2)
        self.assertNotIn("dialect-pull", text)

    def test_readme_names_ask_file(self) -> None:
        text = (Path(__file__).resolve().parents[1] / "README.md").read_text(encoding="utf-8")
        self.assertIn("progen lint  FILE [--role agent|human] [--ask TEXT] [--ask-file FILE]", text)
        self.assertNotIn("[--ask FILE]", text)


if __name__ == "__main__":
    unittest.main()

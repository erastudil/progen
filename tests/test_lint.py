# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import unittest
from pathlib import Path

from progen.lint import lint_text

FIXTURES = Path(__file__).resolve().parent / "fixtures"


class LintAgent(unittest.TestCase):
    def test_good_is_clean(self) -> None:
        text = (FIXTURES / "good_agent.md").read_text(encoding="utf-8")
        self.assertEqual(lint_text(text, role="agent"), [])

    def test_bad_hits_core_rules(self) -> None:
        text = (FIXTURES / "bad_agent.md").read_text(encoding="utf-8")
        findings = lint_text(text, role="agent")
        ids = {f.rule for f in findings}
        for needed in ("P001", "P002", "P003", "P004", "P005", "P006", "P007", "P008", "P011"):
            self.assertIn(needed, ids, msg=f"missing {needed} in {ids}")

    def test_human_slack_is_clean(self) -> None:
        text = (FIXTURES / "human_slack.md").read_text(encoding="utf-8")
        self.assertEqual(lint_text(text, role="human"), [])

    def test_code_fence_parens_ignored(self) -> None:
        text = "use the call.\n\n```\nfoo(bar)\n```\n"
        self.assertEqual(lint_text(text, role="agent"), [])

    def test_inline_code_ignored(self) -> None:
        text = "run `flex-wrap: wrap` on the row.\n"
        self.assertEqual(lint_text(text, role="agent"), [])

    def test_missing_intent_question_allowed(self) -> None:
        text = "missing : which disk?\n"
        findings = lint_text(text, role="agent")
        self.assertFalse(any(f.rule == "P005" for f in findings))

    def test_scale_short_ask_wall(self) -> None:
        ask = "what broke"
        wall = "word " * 90
        ids = {f.rule for f in lint_text(wall, role="agent", ask=ask)}
        self.assertIn("P010", ids)

    def test_scale_ok_when_matched(self) -> None:
        ask = "what broke"
        out = "disk : nvme0n1 full.\n"
        ids = {f.rule for f in lint_text(out, role="agent", ask=ask)}
        self.assertNotIn("P010", ids)


if __name__ == "__main__":
    unittest.main()

# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import sys
import unittest
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from progen.parse import Role, parse_text

FIXTURES = Path(__file__).resolve().parent / "fixtures"


class ParseIron(unittest.TestCase):
    def test_topic_comment(self) -> None:
        doc = parse_text("scale : ten words get two sentences.\n", Role.IRON)
        units = [u for u in doc.units if u.kind == "topic_comment"]
        self.assertEqual(len(units), 1)
        self.assertEqual(units[0].topic, "scale")
        self.assertEqual(units[0].mark, ":")
        self.assertIn("two sentences", units[0].comment or "")

    def test_aside_not_unit(self) -> None:
        doc = parse_text("leave it. // not a command.\n", Role.IRON)
        self.assertEqual(len(doc.asides), 1)
        self.assertEqual(doc.asides[0].text, "not a command.")
        self.assertTrue(doc.flags.get("has_asides"))

    def test_url_is_not_aside(self) -> None:
        doc = parse_text("see https://example.com/path\n", Role.IRON)
        self.assertEqual(doc.asides, [])

    def test_definition(self) -> None:
        doc = parse_text("progen = a dialect of english\n", Role.IRON)
        defs = [u for u in doc.units if u.kind == "definition"]
        self.assertEqual(len(defs), 1)
        self.assertEqual(defs[0].topic, "progen")

    def test_open_class(self) -> None:
        doc = parse_text("logs, diffs, greps, etc.\n", Role.IRON)
        self.assertTrue(doc.flags.get("open_class"))

    def test_elevated_and_test(self) -> None:
        doc = parse_text("! ship it\n? dry run only\n", Role.IRON)
        kinds = [u.kind for u in doc.units]
        self.assertIn("elevated", kinds)
        self.assertIn("test", kinds)
        self.assertTrue(doc.flags.get("elevated"))
        self.assertTrue(doc.flags.get("test"))

    def test_protocol_headers(self) -> None:
        doc = parse_text("CMD, ls -l\nLOOK: /etc/os-release\n", Role.IRON)
        kinds = [u.kind for u in doc.units]
        self.assertIn("protocol", kinds)

    def test_good_fixture(self) -> None:
        text = (FIXTURES / "good_agent.md").read_text(encoding="utf-8")
        doc = parse_text(text, Role.IRON)
        self.assertGreaterEqual(len(doc.asides), 1)
        self.assertTrue(any(u.kind == "topic_comment" for u in doc.units))


class ParseSlack(unittest.TestCase):
    def test_comma_topic(self) -> None:
        doc = parse_text("file this, now please.\n", Role.SLACK)
        units = [u for u in doc.units if u.kind == "topic_comment"]
        self.assertEqual(len(units), 1)
        self.assertEqual(units[0].mark, ",")
        self.assertEqual(units[0].topic, "file this")

    def test_english_comma_stays_prose(self) -> None:
        doc = parse_text(
            "we went to the store, bought milk, and came home tired.\n",
            Role.SLACK,
        )
        units = [u for u in doc.units if u.kind == "topic_comment"]
        self.assertEqual(units, [])

    def test_admin_caps(self) -> None:
        doc = parse_text("WHAT IS THE STATE OF THE BUILD\n", Role.SLACK)
        self.assertTrue(any(u.kind == "admin" for u in doc.units))
        self.assertTrue(doc.flags.get("admin"))


if __name__ == "__main__":
    unittest.main()

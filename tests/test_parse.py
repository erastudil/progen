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


class ParseSyntax(unittest.TestCase):
    def test_topic_comment(self) -> None:
        doc = parse_text("scale : ten words get two sentences.\n", Role.SYNTAX)
        units = [u for u in doc.units if u.kind == "topic_comment"]
        self.assertEqual(len(units), 1)
        self.assertEqual(units[0].topic, "scale")
        self.assertEqual(units[0].mark, ":")
        self.assertIn("two sentences", units[0].comment or "")

    def test_aside_not_unit(self) -> None:
        doc = parse_text("leave it. // not a command.\n", Role.SYNTAX)
        self.assertEqual(len(doc.asides), 1)
        self.assertEqual(doc.asides[0].text, "not a command.")
        self.assertTrue(doc.flags.get("has_asides"))

    def test_url_is_not_aside(self) -> None:
        doc = parse_text("see https://example.com/path\n", Role.SYNTAX)
        self.assertEqual(doc.asides, [])

    def test_definition(self) -> None:
        doc = parse_text("progen = a dialect of english\n", Role.SYNTAX)
        defs = [u for u in doc.units if u.kind == "definition"]
        self.assertEqual(len(defs), 1)
        self.assertEqual(defs[0].topic, "progen")

    def test_open_class(self) -> None:
        doc = parse_text("logs, diffs, greps, etc.\n", Role.SYNTAX)
        self.assertTrue(doc.flags.get("open_class"))

    def test_elevated_and_test(self) -> None:
        doc = parse_text("! ship it\n? dry run only\n", Role.SYNTAX)
        kinds = [u.kind for u in doc.units]
        self.assertIn("elevated", kinds)
        self.assertIn("test", kinds)
        self.assertTrue(doc.flags.get("elevated"))
        self.assertTrue(doc.flags.get("test"))

    def test_protocol_headers(self) -> None:
        doc = parse_text("CMD, ls -l\nLOOK: /etc/os-release\n", Role.SYNTAX)
        kinds = [u.kind for u in doc.units]
        self.assertIn("protocol", kinds)

    def test_good_fixture(self) -> None:
        text = (FIXTURES / "good_agent.md").read_text(encoding="utf-8")
        doc = parse_text(text, Role.SYNTAX)
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


class TestStreamingTokenizer(unittest.TestCase):
    def test_incremental_chunks_and_asides(self) -> None:
        from progen.stream import StreamingProgenTokenizer, UnitType

        tok = StreamingProgenTokenizer(role="syntax")
        self.assertEqual(tok.feed("scale : ten words "), [])
        events = tok.feed("get two sentences. // fast\n")
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].unit_type, UnitType.TOPIC_COMMENT)
        self.assertEqual(events[0].topic, "scale")
        self.assertEqual(events[0].comment, "ten words get two sentences.")
        self.assertEqual(events[0].warnings, [])
        self.assertEqual(events[1].unit_type, UnitType.ASIDE)
        self.assertEqual(events[1].text, "fast")

    def test_code_fence_and_copula_warning(self) -> None:
        from progen.stream import StreamingProgenTokenizer, UnitType

        tok = StreamingProgenTokenizer(role="syntax")
        events = tok.feed(
            "```python\n"
            "inside : fence ignored\n"
            "```\n"
            "status : is failing.\n"
            "! rotate keys\n"
            "progen = dialect of english"
        )
        events.extend(tok.flush())
        self.assertEqual(len(events), 3)
        self.assertEqual(events[0].unit_type, UnitType.TOPIC_COMMENT)
        self.assertIn("P018: leading copula in comment", events[0].warnings)
        self.assertEqual(events[1].unit_type, UnitType.ELEVATED)
        self.assertEqual(events[1].comment, "rotate keys")
        self.assertEqual(events[2].unit_type, UnitType.DEFINITION)
        self.assertEqual(events[2].topic, "progen")

    def test_slack_role_comma_topic(self) -> None:
        from progen.stream import StreamingProgenTokenizer, UnitType

        tok = StreamingProgenTokenizer(role="slack")
        events = tok.feed("deploy pipeline, restart workers now\n")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].unit_type, UnitType.TOPIC_COMMENT)
        self.assertEqual(events[0].topic, "deploy pipeline")
        self.assertEqual(events[0].comment, "restart workers now")


class TestProgenSearchIndex(unittest.TestCase):
    def test_bm25_ranking_and_kind_filter(self) -> None:
        from progen.search import ProgenSearchIndex

        idx = ProgenSearchIndex()
        count = idx.index_text(
            "sqlite : embedded relational database engine.\n"
            "neural network : transformer weights for inference.\n"
            "progen = dialect for agent thinking.\n",
            doc_id="notes.md",
        )
        self.assertEqual(count, 3)
        hits = idx.search("relational database sqlite")
        self.assertGreaterEqual(len(hits), 1)
        self.assertEqual(hits[0].unit.topic, "sqlite")
        self.assertEqual(hits[0].doc_id, "notes.md")

        def_hits = idx.search("dialect agent", kind="definition")
        self.assertEqual(len(def_hits), 1)
        self.assertEqual(def_hits[0].unit.topic, "progen")

    def test_all_package_modules_compile(self) -> None:
        import py_compile

        pkg_dir = _SRC / "progen"
        for py_file in sorted(pkg_dir.glob("*.py")):
            py_compile.compile(str(py_file), doraise=True)


if __name__ == "__main__":
    unittest.main()

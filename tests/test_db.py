# SPDX-License-Identifier: AGPL-3.0-or-later
"""Tests for ProgenDB database engine, CRUD functions, and Dewey indexing."""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from progen.db import ProgenDB
from progen.dewey import classify_text, matches_dewey
from progen.lint import lint_text


class TestProgenDB(unittest.TestCase):
    def setUp(self) -> None:
        self.db = ProgenDB(":memory:")

    def tearDown(self) -> None:
        self.db.close()

    def test_schema_init(self) -> None:
        st = self.db.stats()
        self.assertEqual(st["source_count"], 0)
        self.assertEqual(st["unit_count"], 0)
        self.assertEqual(st["aside_count"], 0)

    def test_crud_unit(self) -> None:
        # Insert
        uid = self.db.insert_unit(
            topic="sqlite engine",
            comment="embedded zero-rent database backend.",
            mark=":",
            dewey_code="005.74",
            asides=["fast in-process execution", "acid compliant"],
        )
        self.assertTrue(bool(uid))

        # Get
        unit = self.db.get_unit(uid)
        self.assertIsNotNone(unit)
        assert unit is not None
        self.assertEqual(unit.topic, "sqlite engine")
        self.assertEqual(unit.comment, "embedded zero-rent database backend.")
        self.assertEqual(unit.dewey_code, "005.74")
        self.assertEqual(unit.dewey_slug, "databases")
        self.assertEqual(len(unit.asides), 2)
        self.assertIn("fast in-process execution", unit.asides)

        # Update
        ok = self.db.update_unit(uid, comment="relational storage engine.")
        self.assertTrue(ok)
        updated = self.db.get_unit(uid)
        assert updated is not None
        self.assertEqual(updated.comment, "relational storage engine.")

        # Delete
        deleted = self.db.delete_unit(uid)
        self.assertTrue(deleted)
        self.assertIsNone(self.db.get_unit(uid))

    def test_dewey_auto_classification(self) -> None:
        self.assertEqual(classify_text("neural network", "transformer model weights"), "006")
        self.assertEqual(classify_text("relational schema", "sql query optimization"), "005.74")
        self.assertEqual(classify_text("cryptographic hash", "sha256 key verification"), "005.8")
        self.assertEqual(classify_text("moral ethics", "duty and virtue"), "170")
        self.assertEqual(classify_text("calculus proof", "integral and derivative equations"), "510")
        self.assertEqual(classify_text("dialect syntax", "japanese topic-comment structure"), "410")

    def test_dewey_matching(self) -> None:
        self.assertTrue(matches_dewey("005.74", "005*"))
        self.assertTrue(matches_dewey("005.8", "005*"))
        self.assertFalse(matches_dewey("006", "005*"))
        self.assertTrue(matches_dewey("530", "500-599"))
        self.assertTrue(matches_dewey("510", "500-599"))
        self.assertFalse(matches_dewey("610", "500-599"))
        self.assertTrue(matches_dewey("100", "100"))

    def test_ingest_progen_text(self) -> None:
        source = (
            "sqlite : embedded zero-rent database. // offline first\n"
            "\n"
            "neural model : transformer weights for inference.\n"
            "\n"
            "progen = dialect of english for agent thinking.\n"
            "\n"
            "! rotate key : security invariant check required.\n"
        )
        count = self.db.ingest_text(source, uri="test.md")
        self.assertEqual(count, 4)

        # Verify units in database
        units = self.db.query(source_uri="test.md")
        self.assertEqual(len(units), 4)

        # Query by Dewey prefix: software & databases (005*)
        sw_units = self.db.query(dewey_code="005*")
        topics = [u.topic for u in sw_units]
        self.assertIn("sqlite", topics)
        self.assertIn("rotate key", topics)

        # Query by Dewey code: AI (006)
        ai_units = self.db.query(dewey_code="006")
        self.assertEqual(len(ai_units), 1)
        self.assertEqual(ai_units[0].topic, "neural model")

        # Query by kind: definition
        defs = self.db.query(kind="definition")
        self.assertEqual(len(defs), 1)
        self.assertEqual(defs[0].topic, "progen")
        self.assertEqual(defs[0].mark, "=")

        # Full-text search
        results = self.db.query(search="offline")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].topic, "sqlite")

    def test_transaction_rollback(self) -> None:
        try:
            with self.db.transaction():
                self.db.insert_unit("alpha", "comment one")
                raise RuntimeError("simulated failure")
        except RuntimeError:
            pass

        # Verify alpha was rolled back
        res = self.db.query(topic="alpha")
        self.assertEqual(len(res), 0)

    def test_dewey_tree(self) -> None:
        self.db.insert_unit("sql schema", "relational database design", dewey_code="005.74")
        self.db.insert_unit("key rotation", "crypto security token", dewey_code="005.8")
        self.db.insert_unit("agent reasoning", "model inference loop", dewey_code="006")

        tree = self.db.dewey_tree()
        self.assertTrue(len(tree) > 0)
        # Find 000 node
        gen_node = next(n for n in tree if n["code"] == "000")
        self.assertEqual(gen_node["total_count"], 3)

    def test_roundtrip_export_markdown(self) -> None:
        source = (
            "database : relational storage model. // acid compliant\n"
            "\n"
            "cache : in-memory kv store.\n"
        )
        self.db.ingest_text(source, uri="roundtrip.md")
        exported = self.db.export_markdown(source_uri="roundtrip.md")

        self.assertIn("database : relational storage model. // acid compliant", exported)
        self.assertIn("cache : in-memory kv store.", exported)

        # Verify exported markdown passes progen linter
        findings = lint_text(exported, role="agent")
        self.assertEqual(findings, [])

    def test_fact_is_one_alphanumeric_line(self) -> None:
        self.db.put_fact("boiling point", "100 C")
        self.assertEqual(self.db.fact("BOILING POINT"), "boiling point: 100 C")
        self.db.put_fact("boiling point", "373 K")
        self.assertEqual(self.db.fact("boiling point"), "boiling point: 373 K")
        self.assertEqual(len(self.db.query(topic="boiling point")), 1)
        with self.assertRaises(ValueError):
            self.db.put_fact("boiling point", "100 C.")
        self.assertEqual(self.db.fact("boiling point"), "boiling point: 373 K")
        self.db.insert_unit(topic="note", comment="has a period.")
        self.assertIsNone(self.db.fact("note"))
        self.assertIsNone(self.db.fact("missing topic"))
        line = self.db.fact("boiling point")
        assert line is not None
        blob = json.dumps(
            {"topic": "boiling point", "comment": "373 K"},
            separators=(",", ":"),
        )
        self.assertLess(len(line.encode("utf-8")), len(blob.encode("utf-8")))

    def test_warm_fact_reads_the_hash(self) -> None:
        self.db.put_fact("unit count", "14")
        seen: list[str] = []
        self.db.conn.set_trace_callback(seen.append)
        self.assertEqual(self.db.fact("unit count"), "unit count: 14")
        del seen[:]
        for _ in range(1000):
            self.assertEqual(self.db.fact("unit count"), "unit count: 14")
        self.assertEqual(seen, [])

    def test_fact_reopens_and_survives_ingest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "facts.db"
            db = ProgenDB(path)
            db.put_fact("boiling point", "100 C")
            self.assertEqual(db.fact("boiling point"), "boiling point: 100 C")
            db.ingest_text("sqlite : embedded store.\n", uri="other.md")
            self.assertEqual(db.fact("boiling point"), "boiling point: 100 C")
            db.close()
            again = ProgenDB(path)
            self.assertEqual(again.fact("boiling point"), "boiling point: 100 C")
            again.close()


class TestProgenDBCLI(unittest.TestCase):
    def test_cli_ingest_and_query(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            doc_path = Path(tmpdir) / "notes.md"
            doc_path.write_text(
                "sqlite : embedded database.\n\n"
                "agent : model runner loop.\n",
                encoding="utf-8",
            )

            from progen.__main__ import main

            # Ingest
            rc = main(["db", "--db", str(db_path), "ingest", str(doc_path)])
            self.assertEqual(rc, 0)

            # Query
            rc = main(["db", "--db", str(db_path), "query", "--dewey", "005*"])
            self.assertEqual(rc, 0)

            # Stats
            rc = main(["db", "--db", str(db_path), "stats"])
            self.assertEqual(rc, 0)

            # Dewey tree
            rc = main(["db", "--db", str(db_path), "dewey", "tree"])
            self.assertEqual(rc, 0)

    def test_cli_fact_stdout_is_the_line(self) -> None:
        from progen.__main__ import main

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = str(Path(tmpdir) / "facts.db")
            with contextlib.redirect_stdout(io.StringIO()):
                rc = main(["db", "--db", db_path, "put", "boiling point", "100 C", "--fact"])
            self.assertEqual(rc, 0)
            fact_buf = io.StringIO()
            with contextlib.redirect_stdout(fact_buf):
                rc = main(["db", "--db", db_path, "fact", "boiling point"])
            self.assertEqual(rc, 0)
            self.assertEqual(fact_buf.getvalue(), "boiling point: 100 C\n")
            miss = io.StringIO()
            with contextlib.redirect_stdout(miss):
                rc = main(["db", "--db", db_path, "fact", "missing topic"])
            self.assertEqual(rc, 1)
            self.assertIn("ERROR", miss.getvalue())
            with contextlib.redirect_stdout(io.StringIO()):
                rc = main(["db", "--db", db_path, "put", "boiling point", "100 C.", "--fact"])
            self.assertEqual(rc, 1)


if __name__ == "__main__":
    unittest.main()

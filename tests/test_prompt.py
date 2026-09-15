# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import json
import unittest
from pathlib import Path

from progen.prompt import load_prompt, repo_root


class Prompts(unittest.TestCase):
    def test_genome_has_marks(self) -> None:
        text = load_prompt("genome")
        for token in ("agents iron", "human slack", "`:`", "`//`", "ERROR", "DONT_KNOW"):
            self.assertIn(token, text)

    def test_canon_points_at_linter(self) -> None:
        text = load_prompt("canon")
        self.assertIn("progen lint", text)
        self.assertIn("AGPL", text)

    def test_unknown_prompt(self) -> None:
        with self.assertRaises(ValueError):
            load_prompt("house-pools")

    def test_machine_spec_matches_lint_ids(self) -> None:
        spec = json.loads((repo_root() / "spec" / "progen.v1.json").read_text(encoding="utf-8"))
        ids = {r["id"] for r in spec["lint_rules"]}
        self.assertEqual(
            ids,
            {
                "P001",
                "P002",
                "P003",
                "P004",
                "P005",
                "P006",
                "P007",
                "P008",
                "P010",
                "P011",
                "P012",
                "P013",
                "P014",
            },
        )

    def test_license_files_exist(self) -> None:
        root = repo_root()
        for name in ("LICENSE", "COVENANT.md", "COPYRIGHT", "docs/SPEC.md"):
            self.assertTrue((root / name).is_file(), name)


if __name__ == "__main__":
    unittest.main()

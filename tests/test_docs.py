# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import ast
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
    "docs/INSTRUCT.md",
    "docs/IMPLEMENTATION.md",
    "docs/BOUNDARY.md",
    "docs/FAILURES.md",
    "prompts/genome.md",
    "prompts/canon.md",
    "prompts/warehouse.md",
    "README.md",
    "AGENTS.md",
    "COVENANT.md",
    "examples/syntax.md",
    "examples/trace.md",
    "examples/english-poetry.md",
]


class DocsLint(unittest.TestCase):
    def test_tree_is_clean(self) -> None:
        root = repo_root()
        for rel in _DOCS:
            findings = lint_text((root / rel).read_text(encoding="utf-8"), role="agent")
            self.assertEqual(findings, [], msg=f"{rel}: {findings}")

    def test_package_sources_parse(self) -> None:
        root = repo_root() / "src" / "progen"
        paths = sorted(root.rglob("*.py"))
        self.assertTrue(paths)
        for path in paths:
            ast.parse(path.read_bytes(), filename=str(path))


class PackageVersion(unittest.TestCase):
    def test_runtime_matches_pyproject(self) -> None:
        import contextlib
        import io

        import progen
        from progen.__main__ import main

        declared = _project_version(repo_root() / "pyproject.toml")
        self.assertEqual(progen.__version__, declared)
        buf = io.StringIO()
        with self.assertRaises(SystemExit) as caught:
            with contextlib.redirect_stdout(buf):
                main(["--version"])
        self.assertEqual(caught.exception.code, 0)
        self.assertEqual(buf.getvalue().strip(), declared)


def _project_version(path: Path) -> str:
    in_project = False
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_project = stripped == "[project]"
            continue
        if in_project and stripped.startswith("version"):
            return stripped.split("=", 1)[1].strip().strip('"').strip("'")
    raise AssertionError(f"no [project] version in {path}")


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

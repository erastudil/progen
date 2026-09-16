# SPDX-License-Identifier: AGPL-3.0-or-later
"""progen CLI: parse, lint, iron, prompt, check."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .iron import iron_text
from .lint import format_findings, lint_text
from .parse import Role, parse_text
from .prompt import load_prompt, repo_root


_DOC_LINT = (
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
)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    parser = argparse.ArgumentParser(
        prog="progen",
        description="progen dialect tools. AGPL-3.0-or-later.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_parse = sub.add_parser("parse", help="mark topic-comment, asides, flags")
    p_parse.add_argument("file")
    p_parse.add_argument("--role", choices=["iron", "slack"], default="iron")

    p_lint = sub.add_parser("lint", help="check agent output against SPEC hygiene")
    p_lint.add_argument("file")
    p_lint.add_argument("--role", choices=["agent", "human"], default="agent")
    p_lint.add_argument("--ask", help="original ask, for scale check")
    p_lint.add_argument("--ask-file", help="file containing the original ask")

    p_iron = sub.add_parser("iron", help="mechanical pass toward topic-comment")
    p_iron.add_argument("file")

    p_prompt = sub.add_parser("prompt", help="emit a drop-in prompt")
    p_prompt.add_argument("name", choices=["genome", "canon", "warehouse"])

    sub.add_parser("check", help="fixtures, iron rewrite, lint this tree")

    args = parser.parse_args(argv)
    if args.cmd == "parse":
        return _cmd_parse(args)
    if args.cmd == "lint":
        return _cmd_lint(args)
    if args.cmd == "iron":
        return _cmd_iron(args)
    if args.cmd == "prompt":
        text = load_prompt(args.name)
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")
        return 0
    if args.cmd == "check":
        return _cmd_check()
    return 2


def _read(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def _cmd_parse(args: argparse.Namespace) -> int:
    source = _read(args.file)
    doc = parse_text(source, role=Role(args.role))
    payload = {
        "role": doc.role.value,
        "flags": doc.flags,
        "asides": [{"text": a.text, "line": a.span.line} for a in doc.asides],
        "units": [
            {
                "kind": u.kind,
                "mark": u.mark,
                "topic": u.topic,
                "comment": u.comment,
                "line": u.span.line,
                "text": u.text,
            }
            for u in doc.units
        ],
    }
    json.dump(payload, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def _cmd_lint(args: argparse.Namespace) -> int:
    source = _read(args.file)
    ask = args.ask
    if args.ask_file:
        ask = _read(args.ask_file)
    findings = lint_text(source, role=args.role, ask=ask)
    print(format_findings(findings, path=args.file))
    return 1 if any(f.severity == "error" for f in findings) else 0


def _cmd_iron(args: argparse.Namespace) -> int:
    source = _read(args.file)
    sys.stdout.write(iron_text(source))
    return 0


def _cmd_check() -> int:
    tests = repo_root() / "tests"
    if tests.is_dir():
        import unittest

        loader = unittest.TestLoader()
        suite = loader.discover(str(tests), pattern="test_*.py")
        result = unittest.TextTestRunner(verbosity=1).run(suite)
        rc = 0 if result.wasSuccessful() else 1
        for rel in _DOC_LINT:
            path = repo_root() / rel
            if path.is_file():
                findings = lint_text(path.read_text(encoding="utf-8"), role="agent")
                if findings:
                    print(format_findings(findings, path=rel))
                    rc = 1
        return rc

    rc = 0
    try:
        g = load_prompt("genome")
        if "agents iron" not in g:
            print("FAIL: prompt missing core marks")
            rc = 1
        ironed = iron_text("Weather is good.")
        if "weather : good." not in ironed.lower():
            print("FAIL: iron rewrite mismatch")
            rc = 1
        findings = lint_text("I'd be happy to help!", role="agent")
        if not any(f.rule == "P002" for f in findings):
            print("FAIL: linter failed to flag mush")
            rc = 1
        if rc == 0:
            print("PASS (package self-check)")
    except Exception as e:
        print(f"FAIL: {e}")
        rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())

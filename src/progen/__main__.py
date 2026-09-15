# SPDX-License-Identifier: AGPL-3.0-or-later
"""progen CLI: parse, lint, prompt, check."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .lint import format_findings, lint_text
from .parse import Role, parse_text
from .prompt import load_prompt, repo_root


def main(argv: list[str] | None = None) -> int:
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

    p_prompt = sub.add_parser("prompt", help="emit a drop-in prompt")
    p_prompt.add_argument("name", choices=["genome", "canon", "warehouse"])

    sub.add_parser("check", help="run conformance fixtures")

    args = parser.parse_args(argv)
    if args.cmd == "parse":
        return _cmd_parse(args)
    if args.cmd == "lint":
        return _cmd_lint(args)
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
    findings = lint_text(source, role=args.role)
    print(format_findings(findings, path=args.file))
    return 1 if any(f.severity == "error" for f in findings) else 0


def _cmd_check() -> int:
    import unittest

    tests = repo_root() / "tests"
    loader = unittest.TestLoader()
    suite = loader.discover(str(tests), pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())

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
    p_lint.add_argument("--ask", help="original ask, for dialect-pull and restate checks")
    p_lint.add_argument("--ask-file", help="file containing the original ask")

    p_iron = sub.add_parser("iron", help="mechanical pass toward topic-comment")
    p_iron.add_argument("file")

    p_prompt = sub.add_parser("prompt", help="emit a drop-in prompt")
    p_prompt.add_argument("name", choices=["genome", "canon", "warehouse"])

    sub.add_parser("check", help="fixtures, iron rewrite, lint this tree")

    # db subcommands
    p_db = sub.add_parser("db", help="relational storage and dewey indexing")
    p_db.add_argument("--db", default="progen.db", help="path to sqlite database (default: progen.db)")
    db_sub = p_db.add_subparsers(dest="db_cmd", required=True)

    db_sub.add_parser("init", help="initialize database schema and dewey taxonomy")

    p_ingest = db_sub.add_parser("ingest", help="ingest markdown file or directory")
    p_ingest.add_argument("path", help="file or directory path")
    p_ingest.add_argument("--role", choices=["iron", "slack"], default="iron")
    p_ingest.add_argument("--layer", default="warehouse")
    p_ingest.add_argument("--dewey", help="default dewey code override")

    p_query = db_sub.add_parser("query", help="query units by topic, dewey, or full-text")
    p_query.add_argument("--topic", help="topic filter (supports * wildcard)")
    p_query.add_argument("--comment", help="comment substring filter")
    p_query.add_argument("--dewey", help="dewey code filter (exact, prefix*, or range X-Y)")
    p_query.add_argument("--search", help="full-text search query (FTS5)")
    p_query.add_argument("--kind", help="unit kind filter")
    p_query.add_argument("--mark", help="mark filter (=, :, !, ?, etc.)")
    p_query.add_argument("--format", choices=["text", "json", "md"], default="text")
    p_query.add_argument("--limit", type=int, default=100)

    p_get = db_sub.add_parser("get", help="retrieve a single unit by ID")
    p_get.add_argument("id", help="unit ID")

    p_put = db_sub.add_parser("put", help="insert a single topic-comment unit")
    p_put.add_argument("topic", help="topic string")
    p_put.add_argument("comment", help="comment string")
    p_put.add_argument("--mark", default=":", help="mark (=, :, !, ?)")
    p_put.add_argument("--kind", help="unit kind")
    p_put.add_argument("--dewey", help="dewey code")
    p_put.add_argument("--aside", help="optional aside text")
    p_put.add_argument("--fact", action="store_true", help="store one alphanumeric fact")

    p_fact = db_sub.add_parser("fact", help="print one alphanumeric fact line")
    p_fact.add_argument("topic", help="fact topic")

    p_del = db_sub.add_parser("delete", help="delete a unit by ID")
    p_del.add_argument("id", help="unit ID")

    p_dewey = db_sub.add_parser("dewey", help="dewey indexing and taxonomy tools")
    p_dewey.add_argument("action", choices=["list", "tree", "stats", "classify"])
    p_dewey.add_argument("--text", help="topic or text to classify")

    p_export = db_sub.add_parser("export", help="export units to markdown or JSONL")
    p_export.add_argument("--dewey", help="filter by dewey code")
    p_export.add_argument("--topic", help="filter by topic")
    p_export.add_argument("--format", choices=["md", "jsonl"], default="md")

    db_sub.add_parser("stats", help="show database statistics and counts")

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
    if args.cmd == "db":
        return _cmd_db(args)
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


def _cmd_db(args: argparse.Namespace) -> int:
    from .db import ProgenDB
    from .dewey import DEFAULT_TAXONOMY, classify_text

    db = ProgenDB(args.db)
    try:
        cmd = args.db_cmd

        if cmd == "init":
            print(f"database : initialized at {args.db}")
            return 0

        if cmd == "ingest":
            p = Path(args.path)
            if p.is_dir():
                res = db.ingest_directory(p, role=args.role)
                total = sum(res.values())
                print(f"ingest : {len(res)} files, {total} units into {args.db}")
            else:
                cnt = db.ingest_file(p, role=args.role, layer=args.layer, default_dewey=args.dewey)
                print(f"ingest : {cnt} units from {args.path} into {args.db}")
            return 0

        if cmd == "query":
            units = db.query(
                topic=args.topic,
                comment=args.comment,
                dewey_code=args.dewey,
                kind=args.kind,
                mark=args.mark,
                search=args.search,
                limit=args.limit,
            )
            if args.format == "json":
                out = [
                    {
                        "id": u.id,
                        "dewey": u.dewey_code,
                        "topic": u.topic,
                        "comment": u.comment,
                        "kind": u.kind,
                        "asides": u.asides,
                        "source": u.source_uri,
                    }
                    for u in units
                ]
                json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
                sys.stdout.write("\n")
            elif args.format == "md":
                sys.stdout.write(db.export_markdown(dewey_code=args.dewey, topic=args.topic))
            else:
                for u in units:
                    dw = f"[{u.dewey_code}] " if u.dewey_code else ""
                    print(f"{u.id[:8]} {dw}{u.to_markdown()}")
            return 0

        if cmd == "get":
            unit = db.get_unit(args.id)
            if not unit:
                print(f"ERROR : unit {args.id} not found")
                return 1
            dw = f"[{unit.dewey_code}] " if unit.dewey_code else ""
            print(f"{unit.id} {dw}{unit.to_markdown()}")
            if unit.source_uri:
                print(f"source : {unit.source_uri}:{unit.line_no}")
            return 0

        if cmd == "put":
            if args.fact:
                try:
                    uid = db.put_fact(args.topic, args.comment)
                except ValueError as exc:
                    print(f"ERROR : {exc}")
                    return 1
                print(f"inserted : {uid}")
                return 0
            asides = [args.aside] if args.aside else None
            uid = db.insert_unit(
                topic=args.topic,
                comment=args.comment,
                mark=args.mark,
                kind=args.kind,
                dewey_code=args.dewey,
                asides=asides,
            )
            print(f"inserted : {uid}")
            return 0

        if cmd == "fact":
            line = db.fact(args.topic)
            if line is None:
                print("ERROR : fact not found")
                return 1
            sys.stdout.write(line + "\n")
            return 0

        if cmd == "delete":
            ok = db.delete_unit(args.id)
            if not ok:
                print(f"ERROR : unit {args.id} not found")
                return 1
            print(f"deleted : {args.id}")
            return 0

        if cmd == "dewey":
            if args.action == "list":
                for c in DEFAULT_TAXONOMY:
                    indent = "  " * c.depth
                    print(f"{c.code:>6} {indent}{c.slug:<16} : {c.title}")
            elif args.action == "classify":
                target = args.text or ""
                code = classify_text(target)
                print(f"classify : {target} -> {code or 'UNKNOWN'}")
            elif args.action == "stats":
                st = db.stats()
                for code, cnt in sorted(st["dewey_classes"].items()):
                    print(f"{code:>6} : {cnt} units")
                if st["unclassified_units"]:
                    print(f"unclassified : {st['unclassified_units']} units")
            elif args.action == "tree":
                tree = db.dewey_tree()

                def print_branch(nodes: list[dict], depth: int = 0) -> None:
                    for n in nodes:
                        if n["total_count"] > 0:
                            indent = "  " * depth
                            print(f"{n['code']:>6} {indent}{n['slug']} ({n['total_count']})")
                            print_branch(n["children"], depth + 1)

                print_branch(tree)
            return 0

        if cmd == "export":
            if args.format == "jsonl":
                sys.stdout.write(db.export_jsonl(dewey_code=args.dewey))
            else:
                sys.stdout.write(db.export_markdown(dewey_code=args.dewey, topic=args.topic))
            return 0

        if cmd == "stats":
            st = db.stats()
            print(f"sources : {st['source_count']}")
            print(f"units : {st['unit_count']}")
            print(f"asides : {st['aside_count']}")
            for k, v in st["kinds"].items():
                print(f"kind {k} : {v}")
            return 0
    finally:
        db.close()


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

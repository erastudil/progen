# changelog

## 1.3.2 — 2026-10-04

P010 retired. word count is not a lint rule.

- a short ask may take as many topic-comment units as the job needs
- style checks stay: one unit per line, mush, dualism, hooks, P015 essay-without-iron, P016 restating
- genome scale lines that said "ten words : about two sentences" are gone

## 1.3.1 — 2026-09-24

exact alphanumeric fact lookup with index-then-hash retrieval.

- `ProgenDB.fact` and `put_fact`: one alphanumeric line. the first read uses the topic index. later reads of that topic use a process hash. CLI commands `progen db fact` and `progen db put --fact`.
- `docs/DATABASE.md`: fact lookup interface and specification.
- full test coverage: `tests/test_db.py`

## 1.3.0 — 2026-09-24

zero-rent database engine, dewey taxonomy, and sqlite fts triggers.

- `src/progen/db.py`: `ProgenDB` zero-rent relational store // WAL mode, memory PRAGMAs, FTS5 sync triggers
- `src/progen/dewey.py`: Dewey Decimal classification taxonomy and hierarchical indexer
- `progen db` CLI: init, ingest, query, get, put, delete, dewey, export, stats
- `docs/DATABASE.md`: database engine specification and schema documentation
- full test coverage: `tests/test_db.py`

## 1.2.1 — 2026-09-20

layout: one topic-comment per line.

- CLI out: blank line between units
- packing two units onto one line is a failure
- P017 packed line
- fixture `tests/fixtures/packed_line.md`

## 1.2.0 — 2026-09-16

named states. wider dualism. code proof.

- catalog `docs/FAILURES.md`
- P004: split sentences, disconnected-node contrast, over/not-over
- P015 dialect-pull: long slack, essay out
- P016 restating: ask copied back
- P101 extra-scope. P102 code job done without proof
- slack heat: mistakes = data. problem = treasure
- fixtures for recite, omit, silent-done, split dualism
- iron corpus stays host-side. this tree ships fixtures
- `examples/english-poetry.md` density sample: history of verse in English

## 1.1.0 — 2026-09-14

the is. the linter. the writer.

- genome states the is. bans live in `spec/progen.v1.json` + `src/progen/tells.py`
- `progen iron` mechanical pass toward topic-comment
- lint: scale P010, will-not P012, stub P013, latch P014
- SPEC shows は-grammar. terms in §0. unread store instead of house analog
- `examples/rewrite.md` worked mush → iron
- `progen check` lints this tree
- IMPLEMENTATION keeps production holes as takeable fixes

## 1.0.0 — 2026-09-14

first public spec. AGPL-3.0-or-later.

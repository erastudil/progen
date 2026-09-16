# progen

A ten-word question returning a three-page essay has failed its own job.

When a model restates what was already provided, drifts into unrelated threads, or ends by prompting the user for the next action, it consumes tokens and degrades accuracy.

**Progen** is a dialect of English designed for agent reasoning, structured output, and thinking traces. It applies Japanese topic-comment grammar structure to English vocabulary: establish the topic first, then deliver the comment. Standardized punctuation marks enable direct syntactic parsing. The agent remains precise; the human may remain informal.

This repository provides the language specification, drop-in prompt templates, and offline verification tooling. Licensed under AGPL-3.0-or-later. See [`LICENSE`](LICENSE) and [`COVENANT.md`](COVENANT.md).

[zcabs](https://github.com/erastudil/zcabs) is how an agent proves execution. [gfc](https://github.com/erastudil/gfc) is how it writes for humans. This is how it thinks.

---

## Quickstart and verification

Execute test suites directly from a local repository clone:

```bash
# run standard unit tests
python -m unittest discover -s tests -v

# run language conformance self-check
PYTHONPATH=src python -m progen check
```

Install as an editable package:

```bash
python -m pip install -e .

progen check
progen prompt genome
progen iron examples/mush.md
progen lint examples/iron.md --role agent
```

Requires Python 3.10+ // standard library only.

---

## Command line tools

Utilities for analysis, lint checks, and canonical prompt output:

```bash
progen parse FILE [--role iron|slack]
progen lint  FILE [--role agent|human] [--ask FILE]
progen iron  FILE
progen prompt {genome|canon|warehouse}
progen check
```

- `parse`: extracts topic-comment units, asides, and operational mode flags into structured JSON.
- `lint`: checks agent outputs against language rules and anti-patterns; exits with non-zero on error.
- `iron`: applies automated rewriting to transform unstructured prose into topic-comment statements.
- `prompt`: outputs reference system prompts for genomes, project canons, and reference warehouses.
- `check`: executes conformance suites and self-tests.

---

## Architecture Layers

System instructions are organized into three distinct layers:

| Layer | Function | Scope |
|---|---|---|
| **Genome** | Primary system prompt: defines role, active tools, and dialect marks. | Short and persistent |
| **Warehouse** | Task-specific documentation and comprehensive reference material. | Loaded on demand |
| **Canon** | Standing universal rules and operational constraints. | Short and persistent |

---

## Documentation

| Document | Description |
|---|---|
| [`docs/SPEC.md`](docs/SPEC.md) | Normative language specification |
| [`docs/IMPLEMENTATION.md`](docs/IMPLEMENTATION.md) | Integration guide for agent runtimes, UI shells, and CI pipelines |
| [`docs/BOUNDARY.md`](docs/BOUNDARY.md) | Technical scope and project boundaries |
| [`docs/FAILURES.md`](docs/FAILURES.md) | Named failure states for prose and code |
| [`prompts/genome.md`](prompts/genome.md) | Drop-in reference system prompt |
| [`examples/rewrite.md`](examples/rewrite.md) | Worked example: rewriting verbose outputs into iron |
| [`examples/english-poetry.md`](examples/english-poetry.md) | Density sample: history of verse in English |
| [`spec/progen.v1.json`](spec/progen.v1.json) | Machine-readable marks and linter rule catalog |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Patch submission requirements and test verification rules |
| [`COVENANT.md`](COVENANT.md) | Zero-rent software pledge and copyleft terms |

# progen

A ten-word question should not return a three-page essay.

You already know the waste. The model restates the number you typed. Think traces wander into a sibling thread. The reply ends by asking what you want to do next. That costs money, and it is also how the answer goes wrong.

**Progen** is a dialect of English for agent think, agent write, and think traces. Japanese grammar under English words: set the topic, then land the comment. Marks a parser can see. The agent stays exact. The human stays messy.

This repository is the specification, the drop-in prompts, and the tooling. License is **AGPL-3.0-or-later**. Hard copyleft. `LICENSE` · `COVENANT.md`.

## start

```
python -m unittest discover -s tests -v
python -m progen prompt genome
python -m progen lint README.md --role agent
```

From the repo, no install:

```
# unix
PYTHONPATH=src python -m progen check

# powershell
$env:PYTHONPATH = "src"
python -m progen check
```

Install:

```
python -m pip install -e .
progen check
```

Python 3.10+. stdlib only.

## read

| file | is |
|---|---|
| [`docs/SPEC.md`](docs/SPEC.md) | the language. normative |
| [`docs/IMPLEMENTATION.md`](docs/IMPLEMENTATION.md) | how a live desk, glass, and OS shell wire it |
| [`docs/BOUNDARY.md`](docs/BOUNDARY.md) | what this gift is |
| [`prompts/genome.md`](prompts/genome.md) | drop-in system prompt |
| [`spec/progen.v1.json`](spec/progen.v1.json) | marks and lint rule ids |

## tools

```
progen parse FILE [--role iron|slack]
progen lint  FILE [--role agent|human]
progen prompt {genome|canon|warehouse}
progen check
```

`lint` is the useful one. Put it on agent output. The tell-list lives in the linter so the model does not recite bans.

## layers

Three files, not one blob.

| layer | is |
|---|---|
| **genome** | system prompt. role, tools, references. short |
| **warehouse** | task instructions + comprehensive reference |
| **canon** | universal standing rules. short |

The genome is the dialect switch. Effort controls volume, not tongue. Do not add a UI toggle.

## copyleft

Speaking progen is just speaking. Copying this spec, these prompts, or this tooling is AGPL. A hosted modified copy owes its users the source.

No dual-license. No company seat. Official copy stays $0. `COVENANT.md`.

## contribute

`CONTRIBUTING.md`. DCO. tests on every SPEC change. house sediment stays out.

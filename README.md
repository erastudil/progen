# progen

progen = dialect of english for agent think, agent write, and think traces.

shape : japanese topic-comment grammar under english vocabulary.

rule : topic first, comment second.

purpose : tokens cost. // mush costs more

premise : ten-word ask returning three-page essay failed its own job.

problem : copied context and unasked trailing questions waste attention.

iron : agent think and output hold marks.

slack : human input keeps informal freedom.

repo : language specification, drop-in prompt templates, and offline verification tools.

license : AGPL-3.0-or-later. // see [`LICENSE`](LICENSE) and [`COVENANT.md`](COVENANT.md)

ecosystem : [zcabs](https://github.com/erastudil/zcabs) proves execution.

voice : [gfc](https://github.com/erastudil/gfc) writes for humans.

mind : progen thinks.

---

## quickstart and verification

tests : run suites directly from local clone.

```bash
# run standard unit tests
python -m unittest discover -s tests -v

# run language conformance self-check
PYTHONPATH=src python -m progen check
```

install : editable package via pip.

```bash
python -m pip install -e .

progen check
progen prompt genome
progen iron examples/mush.md
progen lint examples/iron.md --role agent
```

runtime : python 3.10+. // standard library only

---

## marks

| mark | means | who |
|---|---|---|
| `=` | definition | both |
| `:` | topic : comment on outputs | agent iron |
| `,` | topic , comment on human input | human slack |
| `etc` | open class. infer rest of members | both |
| `!` | elevated execution | both |
| `?` | test mode | both |
| **CAPSLOCK** | admin mode | human invokes. agent matches intensity |
| `//` | aside. inert | both |

---

## command line tools

tools : utilities for parse analysis, lint hygiene, and prompt emission.

```bash
progen parse FILE [--role iron|slack]
progen lint  FILE [--role agent|human] [--ask FILE]
progen iron  FILE
progen prompt {genome|canon|warehouse}
progen check
```

parse : extract topic-comment units, asides, and operational mode flags into structured json.

lint : check agent output against language rules and anti-patterns. // exits non-zero on finding

iron : rewrite unstructured prose toward topic-comment statements.

prompt : emit reference system prompt for genome, canon, or warehouse.

check : run unit tests and doc conformance suites.

---

## fact lookup

fact = letters, digits, and single spaces.

call : return one line for model to read.

```bash
progen db put "boiling point" "100 C" --fact --db knowledge.db
progen db fact "boiling point" --db knowledge.db
```

stdout : return topic and comment.

```
boiling point: 100 C
```

lookup : first call reads sqlite and caches line in hash.

repeat : subsequent lookup reads memory hash directly.

economy : line carries topic once before comment without json key repetition.

---

## layers

system : prompt organized into three distinct layers.

| layer | function | scope |
|---|---|---|
| **genome** | primary system prompt. role, tools, dialect marks | short and persistent |
| **warehouse** | task documentation and reference material | loaded on demand |
| **canon** | universal rules and operational constraints | short and persistent |

---

## documentation

sources : primary references in this tree.

| document | description |
|---|---|
| [`docs/SPEC.md`](docs/SPEC.md) | normative language specification |
| [`docs/IMPLEMENTATION.md`](docs/IMPLEMENTATION.md) | integration guide for agent runtimes, ui shells, and ci pipelines |
| [`docs/BOUNDARY.md`](docs/BOUNDARY.md) | technical scope and project boundaries |
| [`docs/FAILURES.md`](docs/FAILURES.md) | named failure states for prose and code |
| [`prompts/genome.md`](prompts/genome.md) | drop-in reference system prompt |
| [`examples/rewrite.md`](examples/rewrite.md) | worked example. rewriting verbose outputs into iron |
| [`examples/english-poetry.md`](examples/english-poetry.md) | density sample. history of verse in english |
| [`spec/progen.v1.json`](spec/progen.v1.json) | machine-readable marks and linter rule catalog |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | patch submission requirements and test verification rules |
| [`COVENANT.md`](COVENANT.md) | zero-rent software pledge and copyleft terms |

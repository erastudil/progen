---
title: "progen — database schema and dewey indexing"
version: "1.0.0"
status: living
license: AGPL-3.0-or-later
---

# database and dewey indexing

progen units are atomic topic-comment assertions. this module provides offline relational storage, full-text retrieval, and dewey decimal classification indexing.

standard library only: Python `sqlite3`. zero-rent. no external services.

---

## 1. architecture and schema

the engine stores sources, units, asides, and dewey taxonomy classes in an embedded relational database.

```
+--------------------------------------------------------------+
|                           sources                            |
| id | uri | hash | role | layer | unit_count | timestamps     |
+--------------------------------------------------------------+
                               | 1
                               |
                               | *
+--------------------------------------------------------------+      +------------------+
|                            units                             |      |  dewey_classes   |
| id | source_id | line_no | kind | mark | topic | comment ... | ---- | code | slug ...  |
+--------------------------------------------------------------+      +------------------+
          | 1                                 |
          |                                   | (virtual index)
          | *                                 v
+-----------------------+            +-------------------------+
|        asides         |            |        units_fts        |
| id | unit_id | text   |            | topic | comment | aside |
+-----------------------+            +-------------------------+
```

### tables

| table | is |
|---|---|
| `sources` | tracked documents and text buffers. sha256 hash checks prevent duplicate work |
| `units` | atomic topic-comment rows. indexed by topic, dewey code, kind, and source |
| `asides` | `//` comments attached to units. inert |
| `dewey_classes` | hierarchical taxonomy tree. parent-child codes and classification slugs |
| `units_fts` | SQLite FTS5 table with BM25 keyword ranking across topic, comment, and asides |

---

## 2. dewey decimal indexing

topics map to universal knowledge coordinates:

| range | slug | domain |
|---:|---|---|
| `000` | `general` | computer science, systems, information |
| `001` | `methods` | scientific method, evidence, error, knowledge |
| `004` | `computing` | computer hardware, processing, networks |
| `005` | `software` | software engineering, programs, data |
| `005.1` | `programming` | algorithms, code structure, design patterns |
| `005.7` | `data_structures` | file formats, data management, memory layouts |
| `005.74` | `databases` | relational schemas, SQL, indexes, B-trees |
| `005.8` | `security` | cryptography, hashing, verification, defense |
| `006` | `ai_ml` | artificial intelligence, neural models, weights |
| `100` | `philosophy` | ontology, metaphysics, mind |
| `150` | `psychology` | cognition, memory, behavior, attention |
| `160` | `logic` | deduction, formal inference |
| `170` | `ethics` | moral philosophy, governance, covenant |
| `300` | `sociology` | social structures, anthropology |
| `320` | `civics` | constitutions, rights, political architecture |
| `330` | `finance` | markets, capital, risk, accounting |
| `340` | `law` | jurisprudence, contracts, statutes |
| `400` | `language` | communication, syntax |
| `410` | `linguistics` | grammar, syntax, dialects, semantics |
| `420` | `english` | english vocabulary, dialectology, prose |
| `510` | `math` | number, proof, algebra, calculus |
| `530` | `physics` | mechanics, energy, quantum, force |
| `540` | `chemistry` | matter, reaction, composition |
| `570` | `biology` | genetics, cells, ecology, evolution |
| `610` | `health` | physiology, pathology, medicine |
| `620` | `engineering` | circuits, mechanics, structures |
| `650` | `business` | management, strategy, operations |
| `690` | `trades` | machining, fabrication, welding, wiring |
| `700` | `art` | visual design, composition |
| `780` | `music` | pitch, rhythm, acoustic theory |
| `800` | `literature` | rhetoric, narrative, criticism |
| `811` | `poetry` | verse, meter, prosody |
| `900` | `history` | historiography, chronology |
| `910` | `geography` | cartography, spatial regions |

### dewey query patterns

- exact: `005.74` matches databases only
- prefix: `005*` matches all software, data, security, and databases
- range: `500-599` matches all natural sciences and mathematics

---

## 3. database functions

### command line interface

```bash
# initialize database
progen db init --db knowledge.db

# ingest markdown file or tree
progen db ingest path/to/notes.md --db knowledge.db
progen db ingest docs/ --db knowledge.db

# query by topic, dewey class, or full-text search
progen db query --topic sqlite --db knowledge.db
progen db query --dewey "005*" --db knowledge.db
progen db query --search "postgres replica" --db knowledge.db

# single record inspection and mutation
progen db get <id> --db knowledge.db
progen db put "sqlite engine" "zero-rent storage." --dewey 005.74 --db knowledge.db
progen db delete <id> --db knowledge.db

# dewey taxonomy tooling
progen db dewey list
progen db dewey tree --db knowledge.db
progen db dewey stats --db knowledge.db
progen db dewey classify --text "relational database index"

# export back to canonical progen markdown or jsonl
progen db export --dewey 005.74 --format md --db knowledge.db
progen db export --format jsonl --db knowledge.db

# view aggregate counts
progen db stats --db knowledge.db
```

### python library usage

```python
from progen import ProgenDB

with ProgenDB("knowledge.db") as db:
    # insert
    uid = db.insert_unit(
        topic="sqlite",
        comment="embedded zero-rent database.",
        dewey_code="005.74",
        asides=["offline first", "acid compliant"],
    )

    # query
    results = db.query(dewey_code="005*", search="embedded")
    for unit in results:
        print(unit.to_markdown())

    # transaction batch
    with db.transaction():
        db.ingest_file("docs/SPEC.md")

    # export
    markdown = db.export_markdown(dewey_code="005*")
```

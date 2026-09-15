---
title: "progen — implementation"
version: "1.1.0"
status: normative-adjacent · reference implementation
license: AGPL-3.0-or-later
---

# implementation

this is how progen runs on a live desk, a terse sibling model on the same genome, a product glass, and a shell.

SPEC is the language. this file is the wiring.

---

## 1. why this shape

an agent session is a job. the human is the noisiest load-bearing channel. the model is trained to be likeable, long, and finished-looking. that training fights the job.

progen is the counterweight:

- inner grammar that forces topic then comment
- marks a parser can see
- a genome short enough to stay in the window
- a warehouse that holds the long reference so the genome stays short
- a linter that owns the tell-list so the model states the is
- `progen iron` for a mechanical pass toward that is

start at the three layers. a framework-first pass grows a fourth prompt stack.

---

## 2. load order

every automated turn:

1. **genome** — `prompts/genome.md` plus your tool list
2. **map** — a short table of where else to look. one path per need. a dead pointer is a fire. fix the map
3. **canon** — `prompts/canon.md` or your merge of it. hygiene lives here once, as a pointer to the linter
4. **named source** — the one file that owns this job

then drop the rest. freeform human messages are inputs. they do not skip step 1 on the next job.

identity: several models may share the genome. each may have a one-page card for how *following* looks. the genome stays one file. see §6.

---

## 3. genome is the switch

effort sliders control **volume**. think, write, and traces stay progen at every effort.

a named dialect is a different genome or a clearly invoked overlay. default stays progen until the human ends it.

a UI toggle becomes a second personality. traces drift. one dialect, always.

---

## 4. think = write = traces

the same marks in all three.

think traces are billed as input on the next turn. keep them short. topic : comment. pull the named file.

when a host has no think-dialect flag, the genome is the switch. that is the correct host.

---

## 5. named source, split, merge

compaction is lossy. a 400k window ground down to 80k throws the part you need.

| verb | do |
|---|---|
| **load** | keywords / titles pull those threads. rest stay on disk |
| **idle write** | after output, append the thread log back to disk |
| **split** | a fat thread becomes children, verbatim. parent stubs `see D2`. lossless |
| **prompt split** | two fat children both lit and will not fit: split the question. sequential if order matters. parallel if not |
| **merge** | append in the order they came out. wrong order = garbage in |

cliff: around half the advertised window, restating and wrong-child loads start. keep the active set under that.

**aside drag.** a `//` aside that opens a new child unloads the primary from think and from out. both replies answering the aside *and* the primary is the failure. cost: traces billed twice, quality down.

**search flood.** homonym pages that stay in think will mix identities. idle-write the negative. user fact = new child. think = live query + last proof.

ordinary terms: thread, active context, session buffer, window. a local analog that appears three times on a page that is not that project: you latched. pick the english. `progen lint` rule P014.

---

## 6. two following styles, one genome

same genome. opposite default of what following looks like.

| class | following looks like | hole |
|---|---|---|
| **omit-class** | the file changed. the answer is short. silence held the fence | stub + claim of done |
| **recite-class** | prove you read the fence. density dies | narration · is-not lists · parentheticals · latch |

omit-class is already cheap at omission. recite-class is trained to show the constraint. make omission cheaper: the genome states the **is**. bans live in the linter, once. outputs do not copy them.

instruction-following consistency: the **result** matches. the **text of the rule** stays in the file that owns it.

wire both classes to the same genome.

---

## 7. human parser

the human will skip marks. you still hold them.

parse:

- `,` as topic , comment when the left side is a short topic and the line has one comma
- `//` as aside. inert
- trailing `please` as request
- CAPSLOCK as admin mode
- freestyle dumps as mining. extract insight. the dump is not an agenda interview
- end of prompt decides mode if styles mix

english commas in a long sentence stay english. the parser uses a short-topic heuristic. named in `src/progen/parse.py`. it marks what it can see.

---

## 8. speech acts in the loop

**blocked or unwilling:** `ERROR`. if intent is missing, what is missing and 2–3 options. stop.

**named check returned empty:** `DONT_KNOW`.

**credentialed seat needed:** name the seat and a path.

**question:** legal when a fact required to proceed is missing. "what should we work on next" is a hook. P005.

**length.** ten words in → about two sentences out. a wall after a short ask is P010.

---

## 9. glass and shell

visitor-facing chat is still progen. terse. a shorter genome is legal. it matches this law.

chrome is not the dialect. labels are nouns. rows wrap. vertical scroll.

a shell agent still speaks progen. when the next move is a command, emit it in the OS protocol you already have. keep protocol headers distinct from dialect `:`. on a failed command: one corrected command line.

---

## 10. education order

when the artifact teaches a human:

1. the intuitive mechanism, in plain english
2. then the name of the term

the reader should think: oh, that's what that's called.

the genome and the spec stay dense. the README may teach.

---

## 11. wire this repo

```
your-project/
  AGENTS.md          genome. keep short
  CANON.md           standing rules. or import prompts/canon.md
  warehouse/         task instructions + reference
  AGENTS.md in each dir you write   the folder names the job
```

```
python -m pip install -e .
progen prompt genome
progen lint path/to/agent-output.md --role agent
progen iron path/to/mush.md
progen parse path/to/human-input.md --role slack
progen check
```

no install:

```
PYTHONPATH=src python -m progen check
```

put `progen lint` on agent output in CI. fail the build on `error`. this tree lints its own spec.

the genome you ship in a network service is a covered work. AGPL §13. `COVENANT.md`.

---

## 12. what we saw

these happened on a production desk. they will happen on yours. the fix is the idea you can take.

| hole | what it looked like | fix |
|---|---|---|
| recite-class | will-not lists, is-not SKU lines, parentheticals, a local analog used as house slang | genome states the is. linter owns the rest |
| omit-class | stub file + "done" | tests. tool proof. or `ERROR` |
| aside drag | `//` opened a child. primary thread stayed loaded. both answers mixed | idle-write primary. load only the aside |
| search flood | every homonym SERP stayed in think. two people felt right | TOC of live threads. negatives to disk. think = query + last proof |
| scale miss | short ask → wall | match length. two sentences. P010 |
| latch | a project analog became the base language of every thread | ordinary CS by default. P014 |
| dead index | dead path in the map. agent greps the world to rescue it | dead pointer is a fire. fix the map |
| dialect toggle | UI flag for think tongue. traces and out diverged | delete the flag. genome is the switch |
| extra stack | new prompt folder because the genome felt cramped | warehouse |

sibling jobs with their own specs: machine-control languages, programming dictionaries. they are not this dialect. `docs/BOUNDARY.md`.

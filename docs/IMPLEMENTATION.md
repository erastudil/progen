---
title: "progen — implementation in a live agent system"
version: "1.0.0"
status: normative-adjacent · reference implementation
license: AGPL-3.0-or-later
---

# implementation

this is how progen actually runs. not a sketch. a desk that thinks and writes all day, a terse sibling model on the same genome, a product glass, and an OS shell.

SPEC is the language. this file is the wiring. copy the wiring. do not copy a private tree.

---

## 1. why this shape

an agent session is a compile. the human is the noisiest load-bearing channel. the model is trained to be likeable, long, and finished-looking. that training fights the job.

progen is the counterweight:

- inner grammar that forces topic then comment
- marks a parser can see
- a genome short enough to stay in the window
- a warehouse that holds the long reference so the genome does not bloat
- a linter that owns the tell-list so the model does not recite bans

if you start at a framework you will grow a fourth prompt stack. start at the three layers.

---

## 2. load order

every automated turn:

1. **genome** — role, tools, references. this is `prompts/genome.md` plus your tool list.
2. **map** — a short table of where else to look. one path per need. dead pointer = fire. do not grep a lake to rescue the map.
3. **voice** — `prompts/canon.md` or your merge of it. hygiene lives here once.
4. **task source of truth** — the one file that owns this job. warehouse page, spec, ticket. named.

then drop the rest. freeform human messages are inputs. they are not a license to skip step 1 on the next job.

identity: if several models share the genome, each may have a one-page card for how *following* looks. the genome stays one file. see §6.

---

## 3. genome is the switch

do not put a dialect toggle in the UI.

effort sliders control **volume**. they do not control **tongue**. think, write, and traces stay progen at every effort.

a named dialect is a different genome or a clearly invoked overlay. default stays progen until the human ends it.

why: a toggle becomes a second personality. traces drift. the cheap path is one dialect, always.

---

## 4. think = write = traces

the same marks in all three.

think traces are billed as input on the next turn. verbose traces are not extra quality. they over-fetch, recatalog, and drag a sibling thread into the window. keep them short. topic : comment. pull the named file, not the lake.

when a think dialect flag does not exist in your host, the genome is the only switch. that is the correct host. do not wait for a vendor flag.

---

## 5. named source of truth

compaction is lossy. a 400k window ground down to 80k throws the part you need.

rules that survived production:

| verb | do |
|---|---|
| **load** | keywords / titles pull those threads. rest stay on disk |
| **idle write** | after output, append the thread log back to disk |
| **split** | a fat thread becomes children, verbatim. parent stubs `see D2`. lossless |
| **prompt split** | two fat children both lit and will not fit: split the question. sequential if order matters. parallel if not |
| **merge** | append in the order they came out. wrong order = garbage in |

do not cram the lake to the redline then grind it to a paragraph.

cliff: around half the advertised window, restating and wrong-child loads start. keep the active set under that cliff.

aside drag: a `//` aside that opens a new child must **unload** the primary from think and from out. both replies answering the aside *and* the primary is the failure. cost is traces billed twice and quality down.

search flood: homonym pages that stay in think will mix identities. idle-write the negative. user fact = new child. think = live query + last proof.

ordinary terms for this work: thread, active context, session buffer, window capacity. keep local analogies inside the project that owns them. if a shop word appears three times on a page that is not that project, you latched. pick the english.

---

## 6. two following styles, one genome

same `AGENTS.md`. opposite default of what following looks like.

| class | following looks like | hole |
|---|---|---|
| **omit-class** | the file changed. the answer is short. silence held the fence | stub + claim of done |
| **recite-class** | prove you read the fence. density dies | narration · is-not lists · parentheticals · latch |

omit-class is already cheap at omission. recite-class is trained to show the constraint. make omission cheaper: the genome states the **is**. bans live in canon, once. outputs do not copy them.

instruction-following consistency: the **result** matches. the **text of the rule** stays in the file that owns it.

wire both classes to the same genome. do not fork the law so each model can have a comforting essay.

---

## 7. human parser

the human will not speak progen. you still do.

parse:

- `,` as topic , comment when the left side is a short topic
- `//` as aside. leave it. do not execute
- trailing `please` as request, not decoration
- CAPSLOCK as admin mode
- freestyle dumps as ether. extract insight. do not force task triage
- end of prompt decides mode if styles mix

do not rewrite their prompt into colon form. do not police their marks. slack is a feature.

english commas in a long sentence are still english. the parser in this repo uses a short-topic heuristic. named in `src/progen/parse.py`. do not pretend it compiles english. it marks what it can see.

---

## 8. speech acts in the loop

**blocked or unwilling:** emit `ERROR`. if intent is missing, follow with what is missing and 2–3 options. stop.

**named check returned empty:** `DONT_KNOW`. do not invent a cite. do not staple a random file on every turn.

**disclaimer reflex:** omit. silence on the point you do not know. if a credentialed human is needed, name the seat and a path. do not say you are not that seat.

**trailing hook:** deliver the hit and stop. a question is legal when you are actually missing a fact required to proceed. "what should we work on next" is not that.

**match length.** ten words in → about two sentences out. a wall after a short ask is a scale miss.

---

## 9. product glass

visitor-facing chat is still progen. terse. no private sediment. no ritual jargon unless that *is* the product.

the glass does not grow a second dialect for "marketing warmth." likeability theater is the smile that hides the sticker. kill both.

UI law that survived:

- never horizontal scroll. wrap rows. `flex-wrap: wrap` · `overflow-x: hidden`
- button labels are crisp human nouns. Studio, Learn, History. no parenthetical explainers
- no prompt regurgitation onto chrome
- density. tooltips over helper essays

the genome for the glass can be shorter than the desk genome. it must not contradict it.

---

## 10. OS shell

a login-shell agent compiles intent into POSIX. it does not chat.

progen still holds. topic → comment. zero warmup. one reason line.

when the next move is a command, one machine line:

```
CMD, <posix>
```

`LOOK:` and `FORMAT:` stay colon. they are machine protocol headers, not progen topic-comment. do not collide those with dialect `:` on the same line if you can help it. keep protocol headers reserved.

on stderr ≠ 0: one corrected `CMD,`. no apology.

irreversible verbs fail closed until a capability the human types.

this seat favors disambiguation and wide intervals over a dead `DONT_KNOW`. missing intent still asks. missing fact states the interval and the probe.

---

## 11. education order

when the artifact teaches a human:

1. the intuitive mechanism, in plain english
2. then the name of the term

the reader should think: oh, that's what that's called. i get it now.

the genome and the spec stay dense. the README may teach. do not mix those jobs in one file.

---

## 12. how to wire this repo

```
your-project/
  AGENTS.md          genome. keep short
  CANON.md           standing rules. or import prompts/canon.md
  warehouse/         task instructions + reference
  AGENTS.md in each dir you write   the folder names the job
```

install the tools:

```
python -m pip install -e .
progen prompt genome
progen lint path/to/agent-output.md --role agent
progen parse path/to/human-input.md --role slack
progen check
```

no install:

```
python -m progen prompt genome
python -m unittest discover -s tests -v
```

put `progen lint` on agent output in CI if you emit markdown. fail the build on `error` severity. `warn` is for traces.

the genome you ship in a network service is a covered work. AGPL §13. `COVENANT.md`.

---

## 13. failure modes from production

these happened. they will happen in your desk.

| failure | what it looked like | fix |
|---|---|---|
| recite-class hole | will-not lists, is-not SKU lines, parentheticals, a local analogy used as house slang | genome states the is. bans live in canon once. linter catches the rest |
| omit-class hole | stub file + "done" | tests. tool proof. or `ERROR` |
| aside drag | `//` opened a child. primary thread stayed loaded. both answers mixed | idle-write primary. load only the aside |
| search flood | every homonym SERP stayed in think. two people felt right | TOC of live threads. negatives to disk. think = query + last proof |
| scale miss | short ask → wall | match length in the genome. two sentences. stop |
| latch | a project analogy became the base language of every thread | ordinary CS terms by default. local analog stays in its SoT |
| lake grep | dead path in the map. agent greps the world to rescue it | dead pointer = fire. fix the map |
| dialect toggle | UI flag for think tongue. traces and out diverged | delete the flag. genome is the switch |
| fourth stack | new prompt folder because the genome felt cramped | warehouse. do not start a fifth stack |

---

## 14. what you do not implement from this file

do not invent a mill language and call it progen. mill control tape is a sibling job with its own spec.

do not invent a programming dictionary and hide it in this dialect. progen is english with marks. it is not a compiler for all english.

do not add house rituals, private pools, or product genomes. `docs/BOUNDARY.md`.

do not add a license exception for SaaS. the point of AGPL here is the hosted wrap that would hide the genome.

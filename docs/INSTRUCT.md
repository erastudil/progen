---
title: "progen instruct — subdialect specification"
version: "1.0.0"
status: normative
license: AGPL-3.0-or-later
---

# progen instruct

subdialect = specialized formal register of progen for agent instructions, system contracts, execution genomes, task queues, and skills.

parent dialect = progen. // see [`docs/SPEC.md`](SPEC.md)

sister register = progen syntax. // terse interactive turns, tool traces, and cli streams

---

## 1. scope and purpose

progen syntax optimizes token efficiency in active turn dialogue and tool execution traces.

progen instruct optimizes semantic precision in persistent instructions, repository genomes, and execution manifests.

target domains:
- `AGENTS.md` and system instruction contracts
- agent skills and tool documentation
- task queues and batch work orders
- workflow state machines and execution checkpoints
- audit checklists and acceptance criteria

verbosity: permits higher descriptive detail and complete specification of edge cases. word caps stay off the rule list.

---

## 2. syntactic invariants

unit structure: exactly one `topic : comment` statement per line.

statement delimiter: exactly one blank line between `topic : comment` units.

zero copula: omit leading copulas `is`, `are`, `was`, `were` in comments. assert raw predicates directly.

positive formulation: assert positive operational state directly.

no metaphors in instructions: metaphor latching banned in agent instructions. express operational predicates in mathematical, philosophical, scientific, and computational terms. binding sentences sit in SPEC section 13.

truth invariant: exit code 0 certifies passing state. unverified claim carries zero truth value.

---

## 3. programmatic condition keywords

progen instruct standardizes ten programmatic condition keywords for rules, constraints, and control flow:

| keyword | category | formal semantics |
|---|---|---|
| `always` | invariant | unconditional operational invariant or continuous postcondition |
| `never` | boundary | unconditional boundary violation, forbidden state, or security fence |
| `if` | conditional | antecedent predicate or operational trigger |
| `then` | conditional | consequent action upon satisfaction of `if` antecedent |
| `else` | conditional | alternative branch when antecedent evaluates false |
| `until` | convergence | termination condition for bounded loops or iterative remediation |
| `while` | monitor | invariant condition maintained during active state execution |
| `require` | admission | mandatory precondition, credential, or admission permit |
| `assert` | gate | formal state invariant verified at runtime; failure halts execution |
| `emit` | output | observable signal, artifact generation, or event record |

---

## 4. grammar specification

formal ebnf grammar for progen instruct units:

```ebnf
document          = { unit_block | fence_block | markdown_header } ;
unit_block        = statement , "

" ;
statement         = topic , " : " , comment ;
topic             = ( letter | digit | "_" | "-" | " " ){1,64} ;
comment           = predicate_phrase , [ aside ] ;
aside             = " // " , text ;

predicate_phrase  = condition_clause | state_assertion ;
condition_clause  = [ "always " | "never " ]
                  | [ "require " , predicate , ";" ]
                  | [ "if " , condition , " then " , action , [ " else " , action ] ]
                  | [ "until " , condition , " " , action ]
                  | [ "while " , condition , " " , action ]
                  | [ "assert " , invariant , ";" ]
                  | [ "emit " , signal ] ;
```

---

## 5. keyword usage patterns

### require and assert
precondition validation:
```progen
admission permit : require test suite passing; assert working tree clean.
```

### always and never
standing boundary constraints:
```progen
security fence : never commit cryptographic tokens or keys to version control.

execution gate : always verify exit code 0 prior to branch merge.
```

### if, then, else
deterministic conditional branching:
```progen
compute routing : if target task deterministic syntax transform then dispatch local engine else summon frontier model.
```

### until
convergent remediation loops:
```progen
remediation cycle : until linter returns 0 findings execute rule correction step.
```

### while
continuous execution monitoring:
```progen
resource monitor : while background process active monitor memory allocation.
```

### emit
observable event generation:
```progen
telemetry stream : emit verification digest upon test completion.
```

---

## 6. canonical state vectors

canonical operational state vectors in progen instruct:

| vector | operational role |
|---|---|
| `intention` | mission, objective, or goal |
| `requirement` | precondition, admission permit, or dependency |
| `course of action` | operational execution step |
| `end result` | expected postcondition or verifiable outcome |
| `reason` | underlying invariant or formal causality |
| `demand` | immediate boundary enforcement or halt |
| `compliance` | formal status report (`compliance : not possible.` upon invalid transition) |
| `coordinate transfer` | spatial coordinate transformation between execution envelopes |

---

## 7. reference examples

### exemplar 1: agent instruction contract (`AGENTS.md`)

```progen
scope : root operational contract for repository maintenance agent.

admission : require clean git status; require python 3.10 runtime.

execution invariant : always verify test exit code 0 prior to push.

security boundary : never emit plaintext credentials in logs.

failure handler : if verification fails then emit ERROR with test trace else emit PASS.
```

### exemplar 2: task queue work order

```progen
intention : execute database migration on production replica.

requirement : require database backup verified; require schema lock acquired.

course of action : run alembic migration 0042; assert column user_tenant_id present.

end result : migration committed in replica catalog.

reason : multi-tenant partition key requirement for shard scaling.
```

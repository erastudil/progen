# boundary

progen defines the dialect. complete for that job.

## ships

| | |
|---|---|
| language | topic-comment english. japanese grammar shape. marks. syntax, instruct, and slack. scale. think + write + traces |
| architecture | genome / warehouse / canon |
| speech acts | `ERROR` · `DONT_KNOW` · trailing `please` · `etc` as open class |
| hygiene | machine-checkable tells. linter owns the list |
| writer | `progen syntax` mechanical pass toward topic-comment statements |
| prompts | drop-in genome and canon. warehouse is per project |
| tools | parse · lint · syntax · prompt emit · check |
| license | AGPL-3.0-or-later. covenant in `COVENANT.md` |

`docs/SPEC.md` is the law. tools fail closed against it.

## out of scope

application business logic, proprietary domain vocabularies, machine control languages, and task-specific datasets.

those belong in host application repositories. they are not required to implement progen. pull requests introducing project-specific abstractions are rejected.

## completeness

an implementer who has only this repository can wire the dialect into an agent desk, a product glass, or a shell. named sources in SPEC are files in this tree. no private path is load-bearing.

LOOK / FORMAT / CMD and any other OS protocol are the shell's headers. they are examples of "keep protocol distinct from dialect `:`". they are not progen marks.

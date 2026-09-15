# contributing

patches keep the gift intact.

## license

AGPL-3.0-or-later. you certify the patch is yours to give under that license.

Developer Certificate of Origin. append to each commit message:

```
Signed-off-by: Name <email>
```

No CLA. copyright stays with the authors. the project does not take assignment.

PRs that relicense, dual-license, or add a company CLA are rejected.

## tests

```
python -m unittest discover -s tests -v
```

SPEC changes need a fixture. new lint rule needs a fail case and a pass case.

## voice

normative text is progen. README may teach in ordinary english first, then name the term.

do not dump house life into this tree. `docs/BOUNDARY.md`.

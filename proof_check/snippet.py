"""The paste-ready rule for AGENTS.md / CLAUDE.md.

One string, printed by `proof-check --snippet`, so the rule a coding agent
follows and the checker that enforces it ship from the same place.
"""

SNIPPET = """\
<!-- outcome-over-tests: paste this block into AGENTS.md or CLAUDE.md -->

## Done means, then proof - before you claim done

For every task, before you build:

1. Write an `order.md` with a `## Done means` section. Every item is an observable outcome
   with a checkable artifact ("the report exists and lists 30 rows"), never "tests pass".
   List every file the task must produce under `## Artifacts`.
2. Do the work. A green test suite is the regression net, not the definition of done.
3. Write `proof.md` with one `## Evidence: <done-means item>` section per item, quoting
   real output: the commands you ran, file listings, real values. Test counts alone are
   not evidence.
4. Before claiming done, check the proof: `proof-check <folder with order.md and proof.md>`
   (the checker is github.com/Ravishankerchaturvedi/outcome-over-tests: clone, `pip install -e .`).
5. Claim "done" only when it prints PASS. If it prints reasons, those are real gaps:
   fix the work, not the proof.

No proof, no done.
"""

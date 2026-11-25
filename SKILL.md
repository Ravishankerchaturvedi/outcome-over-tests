---
name: outcome-over-tests
description: Judge a task as done by its real output, not by passing tests. Use before reporting any coding or agent task as finished - write observable "Done means" items, save the real artifacts and a proof.md, then run proof-check on the proof folder.
---

# outcome-over-tests

## When to use
- You are about to say a task is "done", "working" or "fixed".
- A test suite is green but nobody has looked at the real output.

## Steps
1. In the order or task, write "Done means" as observable outcomes (a file exists with N rows, a page shows X, an
   API returns Y). Never "tests pass".
2. Run the real thing on a copy. Save the artifacts and write `proof.md` with one "Evidence:" section per "Done
   means" item, quoting the real output.
3. Run `proof-check <proof_folder>`. Exit code 0 is PASS. Anything else is FAIL, with one reason per line: fix the
   work, not the proof.
4. Ask a different agent or a human to open the artifacts before the work is accepted.
5. To make coding agents follow this method on every task, run `proof-check --snippet` and paste the rule it
   prints into the repo's `AGENTS.md` (or `CLAUDE.md`).

## Rules
- A proof that only reports test counts fails.
- Every listed artifact must be newer than the order; a stale artifact fails.
- Tests are the regression net, never the definition of done.
- See PLAYBOOK.md for the full method.

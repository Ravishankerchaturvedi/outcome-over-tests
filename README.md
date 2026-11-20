# outcome-over-tests

[![tests](https://github.com/Ravishankerchaturvedi/outcome-over-tests/actions/workflows/tests.yml/badge.svg)](https://github.com/Ravishankerchaturvedi/outcome-over-tests/actions/workflows/tests.yml)
![python](https://img.shields.io/badge/python-3.10%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)
![dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)

**"71 of 71 tests passing" is not done work.** This is a playbook and a small CLI, `proof-check`, for judging AI
coding agents (and people) by the real output, not by the test count. A task is done only when every "Done means"
item has evidence and every artifact really exists.

## Problem

Tests can pass while the real outcome fails. We saw it again and again with coding agents:
- 71 of 71 tests green while every suggestion called retired model names;
- 2,045 tests green with zero tests for 1,940 new lines, and zero real results;
- an agent claiming nine videos existed when no file was produced.

An order is done only when the real artifact exists and a human has checked it. This repo makes the outcome the
gate, with tests as the regression net. The full method and the incidents are in [PLAYBOOK.md](PLAYBOOK.md).

## Install

```bash
pip install -e .[test]
```

## Quickstart

```bash
proof-check examples/good_proof
proof-check examples/bad_proof
```

Real output of the quickstart above (run on 2026-11-20):

```
$ proof-check examples/good_proof
PASS
$ proof-check examples/bad_proof
Done means item has no matching evidence section: The report file exists and is non-empty.
Done means item has no matching evidence section: The summary contains the expected greeting.
artifact missing or empty: output.txt
proof only reports test counts with no real output
```

The first prints PASS; the second prints FAIL with reasons.

## How it works

`proof-check` validates a proof folder: `proof.md` must exist and be non-empty; each "Done means" item in the order must have a matching evidence section in `proof.md`; each listed artifact must exist, be non-empty, and be newer than the order (an artifact older than the order is stale proof); and a proof that only reports test counts, with no real output, fails. See [PLAYBOOK.md](PLAYBOOK.md) for the full method.

## Configuration

Templates in `templates/` (`order.md`, `retest.md`, `chain.sh`) are generic starting points: build -> retest -> verdict, with agent commands as plain variables. No dependency on any office, scheduler or chat system.

## Use it with AI agents

Make `proof-check` the last step of an agent's task, so "done" is checked rather than claimed:

```bash
run_agent_task order.md && proof-check work/proof_folder || echo "not done: see reasons above"
```

- Exit code `0` = PASS; non-zero = FAIL, with one reason per line.
- Write "Done means" in the order as observable outcomes ("the report file exists and lists 30 rows"), never
  "tests pass".
- The repo ships a `SKILL.md`, so coding agents that read skills (for example Claude Code) can apply the method to
  their own work.

## Limits

- `proof-check` checks structure and presence only; it cannot judge the quality of the real output. That stays a human step.
- Newness is judged by file modification times: an artifact must have been written after the order. Editing the order after building the artifacts makes every artifact look stale; rebuild them.
- Example proof folders are synthetic.

## About

Built by Ravi Shanker Chaturvedi at RAD Media, Mumbai. This is the rule our own agent team works by; we build AI
systems for growing businesses. Questions, bugs or a custom build: open an issue.
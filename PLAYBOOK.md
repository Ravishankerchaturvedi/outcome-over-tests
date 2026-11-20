# Outcome Over Tests

## The rule

Tests can pass while the real outcome fails. Never report an order as done
because tests pass. The desired outcome and a passing test suite are different
things.

## Why this matters (incidents, names removed)

- An AI coding assistant reported 71 of 71 tests passing while every one of its
  suggestions called retired model names and failed in real use.
- A larger suite reported 2045 tests passing with zero tests for 1940 new lines;
  real runs produced zero leads.
- A content agent claimed nine reels existed; no mp4 was produced.
- Drafted posts contained numbers that were never sourced.
- A lead list passed its own quality gate while including chains, bad phone
  numbers and the wrong audience.

In each case the tests were green and the outcome was not.

## Method

1. Every order states "Done means" in the owner's terms: observable outcomes, not
   "tests pass".
2. The builder runs the real thing on a copy and saves real artifacts plus a
   `proof.md`.
3. A different agent re-tests, read-only.
4. A human opens the artifacts: watches frames, reads rows, calls the real API,
   reads the drafts.
5. Tests are only the regression net that keeps a fixed outcome from breaking
   again.

## What proof-check enforces

- `proof.md` must exist and be non-empty.
- Each "Done means" item in the order must have a matching evidence section in
  `proof.md`.
- Each listed artifact must exist and be non-empty.
- Each listed artifact must be newer than the order: an artifact older than the
  order is stale proof.
- A proof that only reports test counts, with no real output, fails.

## Limits

- `proof-check` checks structure and presence only; it cannot judge the quality of
  the real output. That stays a human step.
- Newness is judged by file modification times; editing the order after the
  artifacts makes them all look stale, so rebuild the artifacts.
- Synthetic examples only.
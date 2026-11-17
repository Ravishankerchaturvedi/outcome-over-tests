#!/usr/bin/env bash
# Generic build -> retest -> verdict chain.
# Set these variables for your environment, then run this script.

BUILD_CMD="${BUILD_CMD:-echo 'set BUILD_CMD to your build command'}"
RETEST_CMD="${RETEST_CMD:-echo 'set RETEST_CMD to your retest command'}"
VERDICT_FILE="${VERDICT_FILE:-proof/retest.md}"

set -u

echo "BUILD"
eval "$BUILD_CMD"
build_rc=$?
echo "build_rc=$build_rc"

echo "RETEST"
eval "$RETEST_CMD"
retest_rc=$?
echo "retest_rc=$retest_rc"

if [ "$build_rc" -eq 0 ] && [ "$retest_rc" -eq 0 ] && grep -q '^VERDICT: PASS' "$VERDICT_FILE"; then
  echo "VERDICT: PASS"
  exit 0
fi
echo "VERDICT: FAIL"
exit 1
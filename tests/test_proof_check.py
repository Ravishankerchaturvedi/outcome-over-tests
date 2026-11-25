import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
GOOD = ROOT / "examples" / "good_proof"
BAD = ROOT / "examples" / "bad_proof"


def run(*args, cwd=ROOT):
    return subprocess.run([PY, "-m", "proof_check", *args], cwd=str(cwd),
                         capture_output=True, text=True)


def test_good_passes():
    r = run(str(GOOD))
    assert r.returncode == 0, (r.returncode, r.stdout, r.stderr)


def test_bad_fails():
    r = run(str(BAD))
    assert r.returncode == 1, (r.returncode, r.stdout, r.stderr)


def test_missing_proof_fails(tmp_path):
    d = tmp_path / "p"
    d.mkdir()
    (d / "order.md").write_text("# O\n\n## Done means\n- x exists\n", encoding="utf-8")
    r = run(str(d))
    assert r.returncode == 1
    assert "proof.md is missing or empty" in (r.stdout + r.stderr)


def test_empty_proof_fails(tmp_path):
    d = tmp_path / "p"
    d.mkdir()
    (d / "order.md").write_text("# O\n\n## Done means\n- x exists\n", encoding="utf-8")
    (d / "proof.md").write_text("", encoding="utf-8")
    r = run(str(d))
    assert r.returncode == 1
    assert "proof.md is missing or empty" in (r.stdout + r.stderr)


def test_missing_artifact_fails(tmp_path):
    d = tmp_path / "p"
    d.mkdir()
    (d / "order.md").write_text("# O\n\n## Done means\n- x exists\n\n## Artifacts\n- missing.txt\n",
                                encoding="utf-8")
    (d / "proof.md").write_text("# P\n\n## Evidence: x exists\nreal output here\n\n## Artifacts\n- missing.txt\n",
                                encoding="utf-8")
    r = run(str(d))
    assert r.returncode == 1
    assert "artifact missing or empty" in (r.stdout + r.stderr)


def test_empty_artifact_fails(tmp_path):
    d = tmp_path / "p"
    d.mkdir()
    (d / "missing.txt").write_text("", encoding="utf-8")
    (d / "order.md").write_text("# O\n\n## Done means\n- x exists\n\n## Artifacts\n- missing.txt\n",
                                encoding="utf-8")
    (d / "proof.md").write_text("# P\n\n## Evidence: x exists\nreal output here\n\n## Artifacts\n- missing.txt\n",
                                encoding="utf-8")
    r = run(str(d))
    assert r.returncode == 1
    assert "artifact missing or empty" in (r.stdout + r.stderr)


def test_done_means_no_evidence_fails(tmp_path):
    d = tmp_path / "p"
    d.mkdir()
    (d / "order.md").write_text("# O\n\n## Done means\n- something unique xyz\n", encoding="utf-8")
    (d / "proof.md").write_text("# P\n\n## Test results\n5 passed\n", encoding="utf-8")
    r = run(str(d))
    assert r.returncode == 1
    assert "no matching evidence section" in (r.stdout + r.stderr)


def test_order_flag(tmp_path):
    d = tmp_path / "p"
    d.mkdir()
    order = tmp_path / "order.md"
    order.write_text("# O\n\n## Done means\n- x exists\n", encoding="utf-8")
    (d / "proof.md").write_text("# P\n\n## Evidence: x exists\nreal output here\n", encoding="utf-8")
    (d / "out.txt").write_text("hi", encoding="utf-8")
    # add artifact listing in proof
    (d / "proof.md").write_text("# P\n\n## Evidence: x exists\nreal output here\n\n## Artifacts\n- out.txt\n",
                                encoding="utf-8")
    r = run(str(d), "--order", str(order))
    assert r.returncode == 0, (r.returncode, r.stdout, r.stderr)


def test_test_count_only_fails(tmp_path):
    d = tmp_path / "p"
    d.mkdir()
    (d / "order.md").write_text("# O\n\n## Done means\n- x exists\n", encoding="utf-8")
    (d / "proof.md").write_text("# P\n\n## Evidence: x exists\n3 passed\n", encoding="utf-8")
    (d / "out.txt").write_text("hi", encoding="utf-8")
    (d / "proof.md").write_text("# P\n\n## Evidence: x exists\n3 passed\n\n## Artifacts\n- out.txt\n",
                                encoding="utf-8")
    r = run(str(d))
    assert r.returncode == 1
    assert "only reports test counts" in (r.stdout + r.stderr)


def test_stale_artifact_older_than_order_fails(tmp_path):
    d = tmp_path / "p"
    d.mkdir()
    out = d / "out.txt"
    out.write_text("stale content", encoding="utf-8")
    (d / "order.md").write_text("# O\n\n## Done means\n- x exists\n\n## Artifacts\n- out.txt\n",
                                encoding="utf-8")
    (d / "proof.md").write_text("# P\n\n## Evidence: x exists\nreal output here\n\n## Artifacts\n- out.txt\n",
                                encoding="utf-8")
    past = time.time() - 3600
    os.utime(out, (past, past))
    r = run(str(d))
    assert r.returncode == 1
    assert "artifact older than order: out.txt" in (r.stdout + r.stderr)


def test_fresh_artifact_newer_than_order_passes(tmp_path):
    d = tmp_path / "p"
    d.mkdir()
    order = d / "order.md"
    order.write_text("# O\n\n## Done means\n- x exists\n\n## Artifacts\n- out.txt\n",
                     encoding="utf-8")
    (d / "proof.md").write_text("# P\n\n## Evidence: x exists\nreal output here\n\n## Artifacts\n- out.txt\n",
                                encoding="utf-8")
    past = time.time() - 3600
    os.utime(order, (past, past))
    (d / "out.txt").write_text("fresh content", encoding="utf-8")
    r = run(str(d))
    assert r.returncode == 0, (r.returncode, r.stdout, r.stderr)


def test_snippet_prints_paste_ready_rule():
    r = run("--snippet")
    assert r.returncode == 0, (r.returncode, r.stdout, r.stderr)
    for needle in ("AGENTS.md", "CLAUDE.md", "Done means", "Artifacts",
                   "proof.md", "Evidence", "proof-check", "PASS"):
        assert needle in r.stdout, needle


def test_snippet_instructions_produce_a_passing_proof(tmp_path):
    """Follow the printed snippet literally: order first, then work, then proof."""
    r = run("--snippet")
    assert r.returncode == 0, (r.returncode, r.stdout, r.stderr)
    (tmp_path / "order.md").write_text(
        "# Task\n\n## Done means\n- greeting file exists\n\n## Artifacts\n- greeting.txt\n",
        encoding="utf-8")
    (tmp_path / "greeting.txt").write_text("hello\n", encoding="utf-8")
    (tmp_path / "proof.md").write_text(
        "# Proof\n\n## Evidence: greeting file exists\n\n```\n$ cat greeting.txt\nhello\n```\n"
        "\n## Artifacts\n- greeting.txt\n",
        encoding="utf-8")
    r2 = run(str(tmp_path))
    assert r2.returncode == 0, (r2.returncode, r2.stdout, r2.stderr)


def test_no_args_is_a_usage_error():
    r = run()
    assert r.returncode == 2
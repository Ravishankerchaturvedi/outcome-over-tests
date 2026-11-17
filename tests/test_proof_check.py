import json
import subprocess
import sys
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
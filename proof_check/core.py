import os
import re
from pathlib import Path


def normalize(text):
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


def parse_done_means(order_text):
    lines = (order_text or "").splitlines()
    start = None
    for i, line in enumerate(lines):
        if re.match(r"^#{1,6}\s", line) and "done means" in line.lower():
            start = i + 1
            break
        stripped = line.strip().lower().rstrip(":")
        if stripped in ("done means", "done", "acceptance criteria",
                        "definition of done"):
            start = i + 1
            break
    if start is None:
        for i, line in enumerate(lines):
            if re.match(r"^#{1,6}\s", line) and (
                    "done:" in line.lower()
                    or "acceptance criteria" in line.lower()
                    or "definition of done" in line.lower()):
                start = i + 1
                break
    if start is None:
        return None
    items = []
    for line in lines[start:]:
        if re.match(r"^#{1,6}\s", line):
            break
        s = line.strip()
        if not s:
            continue
        m = re.match(r"^([-*+]|\d+\.)\s+(.*)$", s)
        if m:
            items.append(m.group(2).strip())
    return items


def parse_headings(text):
    out = []
    for line in (text or "").splitlines():
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            out.append((len(m.group(1)), m.group(2).strip()))
    return out


def parse_sections(text):
    lines = (text or "").splitlines()
    sections = []
    current = None
    body = []
    for line in lines:
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            if current is not None:
                sections.append((current[0], current[1], "\n".join(body).strip()))
            current = (len(m.group(1)), m.group(2).strip())
            body = []
        else:
            if current is not None:
                body.append(line)
    if current is not None:
        sections.append((current[0], current[1], "\n".join(body).strip()))
    return sections


def parse_artifacts(text):
    lines = (text or "").splitlines()
    start = None
    for i, line in enumerate(lines):
        if re.match(r"^#{1,6}\s", line) and "artifact" in line.lower():
            start = i + 1
            break
    if start is None:
        for i, line in enumerate(lines):
            if re.match(r"^#{1,6}\s", line) and "file" in line.lower():
                start = i + 1
                break
    if start is None:
        return []
    items = []
    for line in lines[start:]:
        if re.match(r"^#{1,6}\s", line):
            break
        s = line.strip()
        if not s:
            continue
        m = re.match(r"^[-*+]\s+(.*)$", s)
        if not m:
            continue
        rest = m.group(1).strip()
        # strip leading backticks
        token = rest.split()[0] if rest.split() else ""
        token = token.strip("`").rstrip(":,")
        if token:
            items.append(token)
    return items


def item_matches_heading(item, heading_title):
    ni = normalize(item)
    nt = normalize(heading_title)
    if not ni or not nt:
        return False
    if ni in nt or nt in ni:
        return True
    words = [w for w in ni.split() if len(w) > 3]
    if not words:
        words = ni.split()
    if len(words) == 1:
        return words[0] in nt
    matched = sum(1 for w in words if w in nt)
    return matched >= max(1, len(words) - 1)


def evidence_heading_for(item, sections):
    for level, title, body in sections:
        if item_matches_heading(item, title):
            return (level, title, body)
    return None


TEST_COUNT_RE = re.compile(r"\b\d+\s*(passed|failed|tests?|errors?)\b", re.I)


def only_test_counts(text):
    lines = [l.strip() for l in (text or "").splitlines() if l.strip()]
    if not lines:
        return True
    nonempty = [l for l in lines if l]
    tc = sum(1 for l in nonempty if TEST_COUNT_RE.search(l))
    # if every non-heading content line is a test-count line, treat as test-only
    content_lines = [l for l in nonempty if not l.startswith("#")]
    if not content_lines:
        return True
    tc2 = sum(1 for l in content_lines if TEST_COUNT_RE.search(l))
    return tc2 == len(content_lines) and len(content_lines) > 0


def check_proof(proof_dir, order_path=None):
    reasons = []
    pdir = Path(proof_dir)
    if not pdir.is_dir():
        return ["proof directory not found: %s" % proof_dir], 1

    proof_file = pdir / "proof.md"
    if not proof_file.is_file() or proof_file.stat().st_size == 0:
        reasons.append("proof.md is missing or empty")
        # still try others but return
        # We'll continue to collect where possible.

    # resolve order
    if order_path:
        opath = Path(order_path)
        if not opath.is_absolute():
            # try relative to cwd and proof_dir
            candidates = [Path(order_path), pdir / order_path, Path.cwd() / order_path]
            opath = next((c for c in candidates if c.is_file()), candidates[0])
    else:
        # defaults
        candidates = [pdir / "order.md", pdir.parent / "order.md"]
        opath = next((c for c in candidates if c.is_file()), None)

    order_text = None
    if opath is None or not Path(opath).is_file():
        reasons.append("order file not found")
    else:
        try:
            order_text = Path(opath).read_text(encoding="utf-8")
        except OSError:
            reasons.append("order file unreadable: %s" % opath)

    items = None
    if order_text is not None:
        items = parse_done_means(order_text)
        if items is None:
            reasons.append("order has no 'Done means' section")
        elif len(items) == 0:
            reasons.append("order 'Done means' section has no items")

    proof_text = ""
    if proof_file.is_file():
        try:
            proof_text = proof_file.read_text(encoding="utf-8")
        except OSError:
            proof_text = ""

    sections = parse_sections(proof_text) if proof_text else []

    # done-means matching
    if items:
        for item in items:
            sec = evidence_heading_for(item, sections)
            if sec is None:
                reasons.append("Done means item has no matching evidence section: %s" % item)
            else:
                level, title, body = sec
                if not body.strip():
                    reasons.append("Evidence section is empty: %s" % title)

    # artifacts: union of proof.md and order
    artifacts = []
    artifacts += parse_artifacts(proof_text)
    if order_text:
        artifacts += parse_artifacts(order_text)
    # de-dup preserving order
    seen = set()
    uniq = []
    for a in artifacts:
        if a in seen:
            continue
        seen.add(a)
        uniq.append(a)
    artifacts = uniq

    for art in artifacts:
        art_path = Path(art)
        if not art_path.is_absolute():
            # resolve relative to proof_dir first, then cwd
            cand = pdir / art
            if not cand.exists():
                cand = Path.cwd() / art
            art_path = cand
        if not art_path.exists():
            reasons.append("artifact missing or empty: %s" % art)
            continue
        if art_path.is_file():
            if art_path.stat().st_size == 0:
                reasons.append("artifact missing or empty: %s" % art)
        elif art_path.is_dir():
            try:
                if not any(art_path.iterdir()):
                    reasons.append("artifact missing or empty: %s" % art)
            except OSError:
                reasons.append("artifact missing or empty: %s" % art)

    # real output check: proof must not be test-count-only
    if proof_text.strip():
        # if there are evidence sections, ensure at least one has non-test-count content
        if items:
            matched_bodies = []
            for item in items:
                sec = evidence_heading_for(item, sections)
                if sec:
                    matched_bodies.append(sec[2])
            if matched_bodies and all(only_test_counts(b) for b in matched_bodies):
                # allow if an artifact exists and is nonempty? still fail if no real output marker
                reasons.append("proof only reports test counts with no real output")
        # global: if entire proof is test-count-only
        content_lines = [l for l in proof_text.splitlines() if l.strip() and not l.strip().startswith("#")]
        if content_lines and all(TEST_COUNT_RE.search(l) for l in content_lines):
            reasons.append("proof only reports test counts with no real output")

    # if no artifacts listed at all and no real output marker, fail
    if not artifacts:
        # check for any path-like real output marker
        if not re.search(r"\b\w+\.(txt|json|md|csv|log|mp4|png|jpg)\b", proof_text):
            reasons.append("proof only reports test counts with no real output")

    # de-dup reasons preserving order
    seenr = set()
    uniqr = []
    for r in reasons:
        if r in seenr:
            continue
        seenr.add(r)
        uniqr.append(r)
    return uniqr, (0 if not uniqr else 1)

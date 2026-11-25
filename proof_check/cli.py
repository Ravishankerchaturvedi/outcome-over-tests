import argparse
import sys

from . import core
from .snippet import SNIPPET


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="proof-check",
        description="Check a proof folder, or print the AGENTS.md / CLAUDE.md snippet.")
    parser.add_argument("proof_dir", nargs="?", default=None,
                        help="proof folder containing proof.md (and order.md)")
    parser.add_argument("--order", default=None)
    parser.add_argument("--snippet", action="store_true",
                        help="print the paste-ready AGENTS.md / CLAUDE.md snippet and exit")
    args = parser.parse_args(argv)

    if args.snippet:
        sys.stdout.write(SNIPPET)
        sys.exit(0)

    if not args.proof_dir:
        parser.error("proof_dir is required unless --snippet is given")

    reasons, rc = core.check_proof(args.proof_dir, args.order)
    if reasons:
        for r in reasons:
            print(r, file=sys.stderr)
    else:
        print("PASS")
    sys.exit(rc)


if __name__ == "__main__":
    main()
import argparse
import sys
from pathlib import Path

from . import core


def main(argv=None):
    parser = argparse.ArgumentParser(prog="proof-check")
    parser.add_argument("proof_dir")
    parser.add_argument("--order", default=None)
    args = parser.parse_args(argv)

    reasons, rc = core.check_proof(args.proof_dir, args.order)
    if reasons:
        for r in reasons:
            print(r, file=sys.stderr)
    else:
        print("PASS")
    sys.exit(rc)


if __name__ == "__main__":
    main()
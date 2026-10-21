"""Command-line test case generator.

Examples:
  python cli.py -t "Login form with email and password, locks after 5 failed attempts"
  python cli.py -f src/cart.py --framework pytest -o cart_tests.md
"""
import argparse
import sys
from pathlib import Path

from testgen import GenerationError, generate_tests
from testgen.exporters import EXPORTERS

CATEGORIES = ["positive", "negative", "edge", "boundary", "security", "performance", "usability"]


def main() -> int:
    p = argparse.ArgumentParser(description="Generate test cases with AI.")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("-t", "--text", help="Requirement, user story, or spec as text")
    src.add_argument("-f", "--file", type=Path, help="File with a requirement or source code")
    p.add_argument("-n", "--count", type=int, default=10, help="Approximate number of test cases (default 10)")
    p.add_argument("-c", "--categories", nargs="+", choices=CATEGORIES,
                   default=["positive", "negative", "edge", "boundary"])
    p.add_argument("--framework", help="Also generate automation code, e.g. pytest, jest, junit, playwright")
    p.add_argument("--effort", choices=["low", "medium", "high", "xhigh", "max"], default="medium")
    p.add_argument("--format", choices=list(EXPORTERS), help="Output format (default: from -o extension, else md)")
    p.add_argument("-o", "--output", type=Path, help="Write to file instead of stdout")
    args = p.parse_args()

    source = args.text if args.text is not None else args.file.read_text(encoding="utf-8")
    fmt = args.format or (args.output.suffix.lstrip(".") if args.output else "md")
    if fmt not in EXPORTERS:
        p.error(f"unknown output format '{fmt}' - use one of {', '.join(EXPORTERS)}")

    print("Generating test cases...", file=sys.stderr)
    try:
        suite = generate_tests(source, args.categories, args.count, args.framework, args.effort)
    except GenerationError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    out = EXPORTERS[fmt](suite)
    if args.output:
        args.output.write_text(out, encoding="utf-8")
        print(f"Wrote {len(suite.test_cases)} test cases to {args.output}", file=sys.stderr)
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())

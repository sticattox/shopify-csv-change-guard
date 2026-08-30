from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .engine import compare_csvs
from .report import to_text, write_reports
from .schema import normalize_intent_name


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="shopify-change-guard",
        description="Compare an original Shopify product export with an edited CSV and report destructive changes before import.",
    )
    parser.add_argument("original", help="Original Shopify product export CSV")
    parser.add_argument("edited", help="Edited CSV you plan to import")
    parser.add_argument(
        "--intend",
        action="append",
        default=[],
        help="Column you meant to change. Repeatable. Accepts aliases such as SKU or Price. Other field changes become REVIEW.",
    )
    parser.add_argument(
        "--intend-file",
        default="",
        help="Text file of intended column names, one per line.",
    )
    parser.add_argument(
        "--scope",
        choices=["full", "subset"],
        default="full",
        help="full: absent original products are REVIEW. subset: a partial catalog is expected.",
    )
    parser.add_argument(
        "--strict-identifiers",
        action="store_true",
        help="Escalate duplicate SKU/barcode from REVIEW to BLOCK.",
    )
    parser.add_argument(
        "--redact-values",
        action="store_true",
        help="Replace before/after catalog values with redacted length markers.",
    )
    parser.add_argument("-o", "--out", default="", help="Directory for txt/json/html reports")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of text")
    parser.add_argument("--quiet", action="store_true", help="Print only the verdict")
    args = parser.parse_args(argv)

    original = Path(args.original)
    edited = Path(args.edited)
    if not original.exists():
        print(f"Original file not found: {original}", file=sys.stderr)
        return 2
    if not edited.exists():
        print(f"Edited file not found: {edited}", file=sys.stderr)
        return 2

    intended = [normalize_intent_name(c) for c in args.intend]
    if args.intend_file:
        intend_path = Path(args.intend_file)
        if not intend_path.exists():
            print(f"Intend file not found: {intend_path}", file=sys.stderr)
            return 2
        intended.extend(
            normalize_intent_name(line.strip())
            for line in intend_path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        )

    result = compare_csvs(
        original,
        edited,
        intended_columns=intended,
        scope=args.scope,
        strict_identifiers=args.strict_identifiers,
        redact_values=args.redact_values,
    )
    if args.out:
        write_reports(result, args.out)
    if args.quiet:
        print(result.verdict)
    elif args.json:
        from .report import to_json
        print(to_json(result))
    else:
        print(to_text(result))

    return {"PASS": 0, "REVIEW": 10, "BLOCK": 20}[result.verdict]


if __name__ == "__main__":
    raise SystemExit(main())

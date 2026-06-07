from __future__ import annotations

import argparse
import json

from pdd_iar.investigator import investigate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pdd-iar")
    sub = parser.add_subparsers(dest="command", required=True)
    inv = sub.add_parser("investigate")
    inv.add_argument("--query", required=True)
    inv.add_argument("--pdd-root", required=True)
    inv.add_argument("--docs-dir")
    inv.set_defaults(func=cmd_investigate)
    return parser


def cmd_investigate(args: argparse.Namespace) -> int:
    report = investigate(args.query, pdd_root=args.pdd_root, docs_dir=args.docs_dir)
    print(json.dumps(report.to_dict(), indent=2))
    return 0 if report.answerability_state != "contract_invalid" else 2


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

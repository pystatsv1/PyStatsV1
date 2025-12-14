from __future__ import annotations

import argparse
import sys

import pystatsv1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pystatsv1",
        description="PyStatsV1 utilities (docs, paths, version).",
    )
    p.add_argument(
        "--version",
        action="store_true",
        help="Print the installed pystatsv1 version and exit.",
    )

    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("docs", help="Open the bundled PDF documentation.")
    sub.add_parser("docs-path", help="Print the path to the bundled PDF documentation.")

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.version:
        print(pystatsv1.__version__)
        return 0

    if args.cmd == "docs":
        pystatsv1.open_local_docs()
        return 0

    if args.cmd == "docs-path":
        print(pystatsv1.get_local_docs_path())
        return 0

    # No args -> show help
    build_parser().print_help()
    return 0


def open_docs_cli() -> None:
    """Entry point for the `pystatsv1-docs` console script."""
    pystatsv1.open_local_docs()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
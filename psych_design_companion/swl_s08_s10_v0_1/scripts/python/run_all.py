from __future__ import annotations

import argparse
from pathlib import Path

from studies import generate_all


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    for path in generate_all(root):
        print(path.relative_to(root).as_posix())


if __name__ == "__main__":
    main()

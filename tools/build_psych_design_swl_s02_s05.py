#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from psych_design_companion.swl_s02_s05_v0_1.scripts.python.studies import (  # noqa: E402
    generate_tracked_assets,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("psych_design_companion/swl_s02_s05_v0_1"),
    )
    args = parser.parse_args()
    root = args.root.resolve()
    paths = generate_tracked_assets(root, root)
    for path in paths:
        print(f"wrote {path}")
    print("PYSTATSV1_PSYCH_DESIGN_SWL_S02_S05_BUILD_OK")


if __name__ == "__main__":
    main()

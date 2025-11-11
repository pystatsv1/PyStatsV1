from __future__ import annotations

import argparse
import pathlib
import random

import numpy as np


def base_parser(description: str) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=description)
    p.add_argument(
        "--outdir",
        type=pathlib.Path,
        default=pathlib.Path("outputs"),
        help="Where to write outputs (plots, csv). Default: ./outputs",
    )
    p.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    return p


def apply_seed(seed: int | None) -> None:
    if seed is None:
        return
    np.random.seed(seed)
    random.seed(seed)
    try:  # optional: seed torch if present
        import torch  # pragma: no cover
        torch.manual_seed(seed)
    except Exception:
        pass

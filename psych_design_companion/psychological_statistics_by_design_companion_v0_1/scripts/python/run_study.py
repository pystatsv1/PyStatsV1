#!/usr/bin/env python3
from __future__ import annotations
import argparse
from companion_runtime import run_registered_study
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--study', required=True)
    args = parser.parse_args()
    run_registered_study(args.study)

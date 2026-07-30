#!/usr/bin/env python3
"""Run SWL-S10: prospective power planning and fixed-effect cumulative evidence.

Dataset: data/swl_s10_replication_program.csv
Registered target: per-group sample size for d=0.40 at 80% power; fixed-effect pooled standardized mean difference across six replications
This script analyzes the governed synthetic fixture only.
"""
from __future__ import annotations
from companion_runtime import run_registered_study
STUDY_ID = 'SWL-S10'
DATASET = 'data/swl_s10_replication_program.csv'
REGISTERED_ESTIMAND = ['per-group sample size for d=0.40 at 80% power', 'fixed-effect pooled standardized mean difference across six replications']
if __name__ == '__main__':
    run_registered_study(STUDY_ID)

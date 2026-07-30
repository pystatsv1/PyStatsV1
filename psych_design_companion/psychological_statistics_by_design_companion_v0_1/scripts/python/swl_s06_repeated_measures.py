#!/usr/bin/env python3
"""Run SWL-S06: complete-trajectory occasion comparison with missing-visit disclosure.

Dataset: data/swl_s06_confidence_trajectory.csv
Registered target: occasion effect across baseline, post, and follow_up among complete trajectories
This script analyzes the governed synthetic fixture only.
"""
from __future__ import annotations
from companion_runtime import run_registered_study
STUDY_ID = 'SWL-S06'
DATASET = 'data/swl_s06_confidence_trajectory.csv'
REGISTERED_ESTIMAND = ['occasion effect across baseline, post, and follow_up among complete trajectories']
if __name__ == '__main__':
    run_registered_study(STUDY_ID)

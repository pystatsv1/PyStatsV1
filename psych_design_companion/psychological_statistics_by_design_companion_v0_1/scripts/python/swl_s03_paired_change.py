#!/usr/bin/env python3
"""Run SWL-S03: within-person paired change without a unique causal attribution.

Dataset: data/swl_s03_skills_workshop_pre_post.csv
Registered target: post minus pre mean paired change
This script analyzes the governed synthetic fixture only.
"""
from __future__ import annotations
from companion_runtime import run_registered_study
STUDY_ID = 'SWL-S03'
DATASET = 'data/swl_s03_skills_workshop_pre_post.csv'
REGISTERED_ESTIMAND = ['post minus pre mean paired change']
if __name__ == '__main__':
    run_registered_study(STUDY_ID)

#!/usr/bin/env python3
"""Run SWL-S05: factorial interaction and registered simple strategy effects.

Dataset: data/swl_s05_strategy_feedback.csv
Registered target: retrieval-practice effect with feedback minus retrieval-practice effect without feedback
This script analyzes the governed synthetic fixture only.
"""
from __future__ import annotations
from companion_runtime import run_registered_study
STUDY_ID = 'SWL-S05'
DATASET = 'data/swl_s05_strategy_feedback.csv'
REGISTERED_ESTIMAND = ['retrieval-practice effect with feedback minus retrieval-practice effect without feedback']
if __name__ == '__main__':
    run_registered_study(STUDY_ID)

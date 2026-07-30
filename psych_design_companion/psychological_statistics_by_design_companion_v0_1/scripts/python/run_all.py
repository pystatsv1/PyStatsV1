#!/usr/bin/env python3
from companion_runtime import run_registered_study
if __name__ == '__main__':
    for number in range(1, 11):
        run_registered_study(f'SWL-S{number:02d}')
    print('PYSTATSV1_PSYCH_DESIGN_ALL_PYTHON_OK studies=10')

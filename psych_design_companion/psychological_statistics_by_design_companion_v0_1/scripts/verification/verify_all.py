#!/usr/bin/env python3
from verify_study import verify
if __name__ == '__main__':
    for i in range(1, 11):
        verify(f'SWL-S{i:02d}')
    print('PYSTATSV1_PSYCH_DESIGN_ALL_VERIFICATION_OK')

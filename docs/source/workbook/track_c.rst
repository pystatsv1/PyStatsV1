Track C Workbook – Psychology & Experimental Design
===================================================

Track C is the **Psychology / Research Methods** track.
Each chapter is a runnable “problem set” script plus a small ``pytest`` file that checks the intended statistical pattern.

Start here
----------

If you installed from PyPI, first create the local Workbook folder::

   pystatsv1 workbook init
   cd pystatsv1_workbook

Then run a chapter script (example: Chapter 10)::

   python scripts/psych_ch10_problem_set.py

And check your work::

   pytest -q tests/test_psych_ch10_problem_set.py


Chapter list (starter kit)
--------------------------

The starter kit currently bundles Track C problem sets for Chapters 10–12 and 14–20:

- **Ch10** ``scripts/psych_ch10_problem_set.py``  (tests: ``tests/test_psych_ch10_problem_set.py``)
- **Ch11** ``scripts/psych_ch11_problem_set.py``  (tests: ``tests/test_psych_ch11_problem_set.py``)
- **Ch12** ``scripts/psych_ch12_problem_set.py``  (tests: ``tests/test_psych_ch12_problem_set.py``)
- **Ch14** ``scripts/psych_ch14_problem_set.py``  (tests: ``tests/test_psych_ch14_problem_set.py``)
- **Ch15** ``scripts/psych_ch15_problem_set.py``  (tests: ``tests/test_psych_ch15_problem_set.py``)
- **Ch16** ``scripts/psych_ch16_problem_set.py``  (tests: ``tests/test_psych_ch16_problem_set.py``)
- **Ch17** ``scripts/psych_ch17_problem_set.py``  (tests: ``tests/test_psych_ch17_problem_set.py``)
- **Ch18** ``scripts/psych_ch18_problem_set.py``  (tests: ``tests/test_psych_ch18_problem_set.py``)
- **Ch19** ``scripts/psych_ch19_problem_set.py``  (tests: ``tests/test_psych_ch19_problem_set.py``)
- **Ch20** ``scripts/psych_ch20_problem_set.py``  (tests: ``tests/test_psych_ch20_problem_set.py``)

Tip: you can list what’s bundled at any time::

   pystatsv1 workbook list

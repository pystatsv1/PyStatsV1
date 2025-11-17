Chapters overview
=================

PyStatsV1 is organized around chapters that mirror classical applied statistics textbook content.

Implemented chapters
--------------------

- **Chapter 1 – Introduction**

  Basic introduction and environment checks. Run::

     python -m scripts.ch01_introduction

- **Chapter 13 – Within-subjects & Mixed Models**

  Within-subjects design and mixed models. Run::

     make ch13-ci   # tiny CI smoke
     make ch13      # full chapter demo

- **Chapter 14 – Tutoring A/B Test (two-sample t-test)**

  A/B testing with two-sample t-tests. Run::

     make ch14-ci
     make ch14

- **Chapter 15 – Reliability (Cronbach’s α, ICC, Bland–Altman)**

  Reliability analysis. Run::

     make ch15-ci
     make ch15

Roadmap
-------

For future chapters and planned topics (e.g., regression extensions, power analysis, epidemiology examples), see the ``ROADMAP.md`` file in the repository root.

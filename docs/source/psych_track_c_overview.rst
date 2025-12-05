Track C – Problem Sets & Worked Solutions
=========================================

**Track C** is where you make PyStatsV1 *work for you*.

Track A shows how to port a classical applied statistics text into Python.
Track B tells a story for psychology majors – from scientific inquiry to advanced
designs – with one worked PyStatsV1 lab per chapter.

Track C adds:

* **Problem sets** tightly linked to the Track B chapters.
* **Worked, tested solutions** implemented as plain Python scripts.
* **Executable, reproducible workflows** that you can copy, modify, and extend
  for your own research projects.

How to use Track C
------------------

Each problem-set chapter in Track C has three parts:

1. A narrative ``.rst`` page describing the problems, just like a textbook or
   assignment sheet.
2. A solution script in :mod:`scripts` (for example,
   :mod:`scripts.psych_ch10_problem_set`) that shows one clean way to solve the
   problems using PyStatsV1 and standard scientific Python tools.
3. A small :mod:`pytest` file in :mod:`tests` that locks in the numerical
   answers and guarantees that the solution script keeps working as the
   project evolves.

Typical workflow
----------------

For a chapter ``k`` in the Psychology track you can usually do:

.. code-block:: bash

   # Run the worked solutions for the problem set
   make psych-ch10-problems

   # Run only the tests for this problem set
   make test-psych-ch10-problems

This will:

* Run the corresponding solution script (for example,
  ``python -m scripts.psych_ch10_problem_set``).
* Print human-readable summaries to the console.
* Save any simulated data, results tables, and plots into the standard
  ``data/`` and ``outputs/`` folders.
* Run the tests that verify the key numbers (t statistics, *p*-values,
  effect sizes, and so on).

Philosophy
----------

Track C is designed with the PyStatsV1 motto in mind:

   **“Don’t just calculate your results – engineer them.  
   We treat statistical analysis like production software.”**

That means:

* Every solution script is **deterministic** (fixed random seeds),
  **version-controlled**, and **tested**.
* You are encouraged to **fork, copy, and adapt** the solution scripts to your
  own datasets.
* Instructors can assign the problem sets as-is, or use the scripts and tests
  as templates for their own assignments.

Available problem sets
----------------------

Currently implemented:

* :doc:`psych_ch10_problem_set` – Independent-samples *t*-test problem set.

More chapters will be added in future versions, following the same pattern:

* ``docs/psych_chk_problem_set.rst``
* ``scripts/psych_chk_problem_set.py``
* ``tests/test_psych_chk_problem_set.py``
* Makefile targets: ``psych-chk-problems`` and ``test-psych-chk-problems``.

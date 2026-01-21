Appendix: Track D + BYOD CLI cheatsheet
=======================================

**Why this exists:** A single page students can keep open while working. Everything here should stay stable; if it changes, ``--help`` is the source of truth.

Learning objectives
-------------------

- Know the minimal commands to run Track D from PyPI.
- Know the minimal commands to normalize and analyze your own exports.

Outline
-------

Install + create workbook (PyPI)
--------------------------------

- Install: ``pip install "pystatsv1[workbook]"``
- Create workbook: ``pystatsv1 workbook init --track d --dest track_d_workbook``
- List targets: ``pystatsv1 workbook list --track d --workdir track_d_workbook``
- Optional: ``cd track_d_workbook`` (then you can omit ``--workdir`` below)

Run Track D scripts
-------------------

- Peek datasets: ``pystatsv1 workbook run d00_peek_data --workdir track_d_workbook``
- Run a chapter: ``pystatsv1 workbook run d01 --workdir track_d_workbook``
- Need options? ``pystatsv1 workbook --help``

BYOD: normalize + validate
--------------------------

- Init: ``pystatsv1 trackd byod init --dest <BYOD_DIR> --profile core_gl``
- Put your export under ``<BYOD_DIR>/tables/`` (typically ``gl_journal.csv``).
- Normalize: ``pystatsv1 trackd byod normalize --project <BYOD_DIR>``
- Normalize (fallback): ``pystatsv1 trackd byod normalize --project <BYOD_DIR> --profile core_gl``
- Validate: ``pystatsv1 trackd validate --datadir <BYOD_DIR>/normalized --profile core_gl``
- Daily totals: ``pystatsv1 trackd byod daily-totals --project <BYOD_DIR>``
- Help: ``pystatsv1 trackd byod --help``

Where this connects in the workbook
-----------------------------------

- :doc:`../track_d_student_edition` (full student workflow)
- :doc:`../track_d_byod` (BYOD hub with tutorials)

.. note::

   If anything here differs from what you see locally, run the relevant ``--help`` command and follow that.
   General help: ``pystatsv1 --help``


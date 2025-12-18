.. _business-authoring:

Appendix — Track D authoring rules
=================================

Track D is designed so Read the Docs (RTD) mirrors the textbook structure.
This appendix documents the conventions so contributors can add chapters with
minimal friction.

File naming conventions
-----------------------

RST pages live in ``docs/source``.

* Track D chapter pages:

  * ``business_ch01_accounting_measurement.rst``
  * ``business_ch02_<topic>.rst``
  * ...

* Track D intro/appendices:

  * ``business_intro.rst``
  * ``business_appendix_*.rst``

RST page template
-----------------

Every Track D chapter page follows this structure:

* Why this matters (for accountants)
* Learning objectives
* Accounting Connection (PDF refresher)
* Dataset tables used (LedgerLab)
* PyStatsV1 lab (Run it)
* Interpretation & decision memo
* End-of-chapter problems
* Textbook alignment notes

Script naming conventions
-------------------------

* Simulator scripts (synthetic data): ``scripts/sim_business_*.py``
* Chapter analysis scripts: ``scripts/business_chXX_*.py``

Makefile targets
----------------

Track D chapters should have:

* a simulation target (writes to ``data/synthetic``)
* a chapter target (writes to ``outputs/track_d``)
* (optional) a CI smoke target with tiny sizes and deterministic seed

Tests
-----

Every chapter should have at least one fast unit test in ``tests/`` that validates:

* key output artifacts are created, and
* the most important correctness/integrity checks pass.

This is how Track D stays “engineered,” not just calculated.

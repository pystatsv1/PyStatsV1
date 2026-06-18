Psych support helpers
=====================

PyStatsV1 includes a small ``pystatsv1.psych`` helper layer for proof-first
psychology examples and companion labs.

The helpers are intentionally modest. They do not replace SciPy, statsmodels,
Pingouin, or R for inferential statistics. They provide reusable bridge
utilities for package identity receipts, simple group summaries, stable JSON
receipts, and numeric parity comparisons.

This supports the PyStatsV1 book-series positioning:

* Python for the workflow.
* R for verification.
* PyStatsV1 for the bridge.

Install
-------

For readers using the public package after the v0.23.0 release:

.. code-block:: bash

   python -m pip install "pystatsv1==0.23.0"

For contributors working from the repository:

.. code-block:: bash

   python -m pip install -e .

Public helpers
--------------

``package_identity()``
  Public helper. Full call signature: ``package_identity(package_name="pystatsv1", module_name="pystatsv1")``
  Records the imported package name, module name, version, module file, module
  directory, distribution location, source-kind label, Python executable, and
  public top-level exports. Companion labs use this to prove which PyStatsV1
  package was imported.

``describe_by_group()``
  Public helper. Full call signature: ``describe_by_group(data, group_col, value_cols, *, decimals=6)``
  Creates JSON-stable descriptive summaries by group for one or more numeric
  variables. ``data`` may be a pandas DataFrame or an iterable of row
  dictionaries. The returned records include ``n``, ``mean``, ``sd``, ``min``,
  and ``max`` for each group/variable pair.

``write_json_receipt()``
  Public helper. Full call signature: ``write_json_receipt(path, payload)``
  Writes sorted, indented JSON receipts with a final newline and creates parent
  directories as needed. The return value is the written ``Path``.

``compare_numeric_results()``
  Public helper. Full call signature: ``compare_numeric_results(left, right, *, tolerance=1e-6)``
  Compares numeric outputs from two analysis engines and returns a
  JSON-serializable comparison receipt. Missing values, non-numeric values,
  pass/fail status, absolute differences, and the stated tolerance are recorded
  explicitly.

Minimal example
---------------

.. code-block:: python

   from pystatsv1.psych import (
       package_identity,
       describe_by_group,
       write_json_receipt,
       compare_numeric_results,
   )

   rows = [
       {"condition": "control", "score": 1.0},
       {"condition": "control", "score": 3.0},
       {"condition": "planning", "score": 5.0},
       {"condition": "planning", "score": 7.0},
   ]

   identity = package_identity()
   descriptives = describe_by_group(rows, "condition", "score", decimals=3)
   parity = compare_numeric_results(
       {"mean_difference": 4.0},
       {"mean_difference": 4.0000001},
       tolerance=1e-5,
   )

   write_json_receipt(
       "outputs/pystatsv1_psych_receipt.json",
       {
           "identity": identity,
           "descriptives": descriptives,
           "parity": parity,
       },
   )

Honest computation-source story
--------------------------------

The helper layer is a bridge, not a replacement for statistical libraries. In
the APA Article Lab pattern, PyStatsV1 records package identity, descriptive
summaries, JSON receipts, and numeric comparison receipts. SciPy, statsmodels,
Pingouin, and R remain the appropriate sources for many inferential procedures
and independent verification checks.

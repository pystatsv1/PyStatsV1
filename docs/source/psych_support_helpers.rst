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

Public helpers
--------------

``package_identity()``
  Records the imported PyStatsV1 version, module file, distribution location,
  Python executable, and top-level exports.

``describe_by_group()``
  Creates JSON-stable descriptive summaries by group for one or more numeric
  variables.

``write_json_receipt()``
  Writes sorted, indented JSON receipts with a final newline.

``compare_numeric_results()``
  Compares numeric outputs from two analysis engines and records pass/fail,
  missing, and non-numeric cases.

Release notes
=============

v0.25.0 — Book 1 Companion v0.2
---------------------------------

PyStatsV1 v0.25.0 packages the public synthetic-only Book 1 Companion v0.2.

Highlights
~~~~~~~~~~

* Updates ``pystatsv1 book1 init`` to create
  ``psych_stats_with_python_companion_v0_2``.
* Preserves the transparent Python/R teaching analyses while packaging six
  source-faithful, high-contrast grayscale figures for the five visual
  teaching placements.
* Separates the Chapter 10 correlation and Chapter 11 regression figures so
  each is tied to its own CSV, analysis script, Python result, and APA source
  identifier where applicable.
* Carries an internal portal handoff receipt that records the portal tag and
  immutable data/script hashes used for the packaged snapshot.
* Keeps the bundle synthetic-only; it does not change the launcher interface
  into a real-data analysis service.

v0.24.1 — Cross-platform Book 1 asset manifest
------------------------------------------------

PyStatsV1 v0.24.1 corrects the packaged Book 1 companion release candidate
without changing the launcher interface or synthetic teaching analyses.

Highlights
~~~~~~~~~~

* Records stable logical archive modes in the Book 1 bundle manifest: scripts
  are ``755`` and all other provisioned files are ``644``.
* Makes source-snapshot asset rebuilding consistent across Linux, macOS, and
  Windows checkouts.
* Preserves the synthetic-only bundle, source hashes, and launcher commands.

v0.24.0 — Book 1 companion launcher
------------------------------------

PyStatsV1 v0.24.0 packages the synthetic-only executable companion for
*Psych Stats with Python* and adds a conservative local launcher.

Highlights
~~~~~~~~~~

* Adds ``pystatsv1 book1 info``, ``pystatsv1 book1 init``, and
  ``pystatsv1 book1 verify``.
* Packages a deterministic companion ZIP containing synthetic CSVs, transparent
  Python and base-R scripts, Matplotlib figure specifications, and a source-file
  integrity manifest.
* Refuses to overwrite an existing destination and checks archive paths before
  extraction.
* Adds wheel-smoke coverage for the packaged Book 1 asset on Linux, macOS, and
  Windows.
* Does not publish to PyPI, change the Book 1 KDP proof, or automate real-data
  analysis. A PyPI publication remains a separate reviewed release action.

v0.23.0 — APA Lab support helpers
---------------------------------

PyStatsV1 v0.23.0 prepares the public package for the APA Article Lab and
other proof-first psychology workflows.

Highlights
~~~~~~~~~~

* Adds the public ``pystatsv1.psych`` helper layer.
* Documents the helper APIs used by the APA Lab companion project.
* Keeps PyStatsV1's role deliberately narrow and honest: PyStatsV1 provides
  bridge helpers and receipts, while SciPy, statsmodels, Pingouin, and R remain
  the appropriate tools for many statistical procedures.
* Updates the release process so CI runs on release tags and PyPI publication is
  a manual trusted-publisher step after the tag is green.

Public psychology helper APIs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``package_identity()``
  Returns a JSON-serializable package identity receipt, including package name,
  module name, version, import path, distribution location, source-kind label,
  Python executable, and public top-level exports.

``describe_by_group()``
  Produces JSON-stable descriptive summaries by group for one or more numeric
  variables. It records ``n``, ``mean``, ``sd``, ``min``, and ``max`` for each
  group/variable pair.

``write_json_receipt()``
  Writes sorted, indented JSON receipts with a final newline and creates parent
  directories as needed.

``compare_numeric_results()``
  Compares numeric outputs from two analysis engines with a stated tolerance and
  records pass, fail, missing, and non-numeric comparison cases.

Release checklist
~~~~~~~~~~~~~~~~~

Before tagging ``v0.23.0``:

.. code-block:: bash

   git status
   git rev-parse HEAD
   python -m pip install -e '.[dev,docs]'
   make lint
   make test
   make docs-workbook-strict
   python -m build

After the local checks are green:

.. code-block:: bash

   git tag -a v0.23.0 -m "PyStatsV1 v0.23.0 with APA Lab psych support helpers"
   git push origin v0.23.0
   gh run list --limit 10
   gh run watch --exit-status

After the tag CI is green and the PyPI trusted publisher is configured:

.. code-block:: bash

   gh workflow run pypi-publish.yml --ref v0.23.0
   gh run watch --exit-status

Then verify the public install in a clean environment:

.. code-block:: bash

   python -m pip install --upgrade pystatsv1==0.23.0
   python - <<'PY'
   from pystatsv1.psych import package_identity
   print(package_identity()["version"])
   PY

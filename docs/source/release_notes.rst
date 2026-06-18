Release notes
=============

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

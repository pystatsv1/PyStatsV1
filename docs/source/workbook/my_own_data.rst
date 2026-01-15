My Own Data: a mini-guide
=========================

Once you’ve run a chapter or the Study Habits case study, the next step is to try **your own dataset**.

PyStatsV1 includes:

* a tiny CSV template: ``data/my_data.csv``
* a beginner-friendly scaffold script: ``scripts/my_data_01_explore.py``
* a test you can run any time: ``tests/test_my_data.py``

The goal is simple: **Run → Inspect → Check**, on *your* data.


1) Put your data in the template
--------------------------------

Open ``data/my_data.csv`` and replace the example rows with your own data.

Rules of thumb ("clean data"):

* **One row = one observation** (one person, one trial, one day, etc.).
* **One column = one variable** (group, score, hours, temperature, ...).
* Use **clear column names** (letters, numbers, underscores).
* Avoid mixed types in one column (don’t mix numbers and text).
* Use empty cells for missing values (or ``NA``). Try to be consistent.


2) Run the scaffold script
--------------------------

From your workbook folder:

.. code-block:: bash

   pystatsv1 workbook run my_data_01_explore

If your CSV is somewhere else:

.. code-block:: bash

   python scripts/my_data_01_explore.py --csv path/to/your.csv --outdir outputs/my_data


3) Inspect what was created
---------------------------

The script writes outputs under:

* ``outputs/my_data/tables/``
* ``outputs/my_data/plots/``

Start with:

* ``outputs/my_data/tables/missingness.csv``
* ``outputs/my_data/tables/numeric_summary.csv``


4) Check (tests)
----------------

Run the matching smoke test:

.. code-block:: bash

   pystatsv1 workbook check my_data


5) Customize for your dataset
-----------------------------

Open ``scripts/my_data_01_explore.py`` and look for:

.. code-block:: python

   # === Student edits start here ===
   ID_COL = "id"
   GROUP_COL = "group"
   OUTCOME_COL = "outcome"

Change these names to match your CSV columns (or leave them as-is).

Tip: If your numeric columns are being treated like text, fix the CSV first.
For example, remove commas in numbers and avoid mixing text with numbers.

Windows 11 setup (students)
===========================

This guide is for students who want to run the **Workbook** on Windows 11
using **Git Bash** (a terminal) and **PyPI** (no cloning the repo required).

If you already have Python installed and can run ``python --version``
in Git Bash, you can skip to :doc:`quickstart`.


What you need
-------------

Required:

* **Python 3.10+**
* **Git Bash** (installed via Git for Windows)

Optional:

* **make** (only needed for some developer workflows; the Workbook does **not** require it)


1) Install Python (3.10+)
-------------------------

Install Python using the official Windows installer.

During installation, make sure you enable:

* **Add python.exe to PATH** (this makes ``python`` work in Git Bash)
* **Disable path length limit** (recommended when Windows offers it)

After installing, open **Git Bash** and confirm:

.. code-block:: bash

   python --version
   python -m pip --version

If ``python`` is not found, try the Windows Python launcher:

.. code-block:: bash

   py -V
   py -m pip --version

Then use ``py`` anywhere this Workbook documentation uses ``python``.


2) Install Git Bash
-------------------

Install **Git for Windows**, which includes **Git Bash**.

Confirm Git Bash is working:

.. code-block:: bash

   git --version


3) Optional: Install make
-------------------------

You can skip this step if you are only doing the Workbook.

If you already have ``make`` installed:

.. code-block:: bash

   make --version

If your course/instructor asks you to install it, one common approach on Windows
is to install it via a Windows package manager.

If you already have **Chocolatey** installed, you can run this in
PowerShell (**Run as Administrator**):

.. code-block:: powershell

   choco install make -y

Then verify in Git Bash:

.. code-block:: bash

   make --version


4) Create a workbook folder + virtual environment
-------------------------------------------------

Pick a folder you want to work in. In Git Bash:

.. code-block:: bash

   mkdir -p ~/pystatsv1-workbook
   cd ~/pystatsv1-workbook

Create and activate a virtual environment (recommended):

.. code-block:: bash

   python -m venv .venv

   # Windows (Git Bash)
   source .venv/Scripts/activate

Upgrade pip and install the Workbook extra from PyPI:

.. code-block:: bash

   python -m pip install --upgrade pip
   python -m pip install "pystatsv1[workbook]"


5) Initialize and run the Workbook
----------------------------------

Create the Workbook starter folder:

.. code-block:: bash

   pystatsv1 workbook init --dest my_workbook
   cd my_workbook

List chapters (sanity check):

.. code-block:: bash

   pystatsv1 workbook list

Run a chapter and check your work:

.. code-block:: bash

   pystatsv1 workbook run ch10
   pystatsv1 workbook check ch10


Keeping PyStatsV1 up to date
----------------------------

To update to the latest version on PyPI:

.. code-block:: bash

   python -m pip install --upgrade "pystatsv1[workbook]"


If something goes wrong
-----------------------

Common fixes (PATH, venv activation, missing pytest, etc.) are covered here:

* :doc:`troubleshooting`

Understanding the setup commands (Windows + Git Bash)
-----------------------------------------------------

When you see commands like these::

  python -m venv pystatsv1-env
  source pystatsv1-env/Scripts/activate
  python -m pip install -U pip
  python -m pip install "pystatsv1[workbook]"
  pystatsv1 doctor
  pystatsv1 workbook init

here is what they mean.

1) Create a virtual environment
-------------------------------

``python -m venv pystatsv1-env`` creates an isolated Python environment (a folder named
``pystatsv1-env``). This keeps Workbook packages separate from your system Python and other projects.

2) Activate the virtual environment
-----------------------------------

``source pystatsv1-env/Scripts/activate`` turns the environment *on*.

You can tell it worked when your prompt changes to include::

  (pystatsv1-env)

From now on, ``python`` and ``pip`` refer to the environment's Python and installer.

Tip: If you close Git Bash, you must activate again next time.

3) Upgrade pip (inside the environment)
---------------------------------------

``python -m pip install -U pip`` updates the package installer to a newer version.

If you see messages like "Requirement already satisfied" followed by an upgrade, that's normal.

4) Install PyStatsV1 + Workbook dependencies
--------------------------------------------

``python -m pip install "pystatsv1[workbook]"`` installs PyStatsV1 plus the extra libraries needed
for the Workbook (for example: numpy, pandas, scipy, statsmodels, matplotlib, pingouin, etc.).

The ``[workbook]`` part is important: it means "include the workbook extras".

5) Check your environment
-------------------------

``pystatsv1 doctor`` runs a quick health check. If you see::

  ✅ Environment looks good.

then your install is working.

6) Create your workbook starter folder
--------------------------------------

``pystatsv1 workbook init`` creates a new folder named ``pystatsv1_workbook`` in your current
directory. That folder contains the starter files used in the workbook chapters.

Next steps usually look like:

* ``cd pystatsv1_workbook``
* ``pystatsv1 workbook run ch10``
* ``pystatsv1 workbook check ch10``

Chapter 11 note (Windows + Git Bash): missing helper file + PYTHONPATH
----------------------------------------------------------------------

Most students can run Chapter 11 the same way as Chapter 10::

  pystatsv1 workbook run ch11
  pystatsv1 workbook check ch11

However, on some Windows setups you may see an error like::

  ModuleNotFoundError: No module named 'scripts.psych_ch11_paired_t'

This means your workbook starter folder is missing a small helper file
(``scripts/psych_ch11_paired_t.py``). You can fix it in under a minute.

Step A — Confirm the file is missing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

From inside your workbook folder (``pystatsv1_workbook``), run::

  ls scripts/psych_ch11_paired_t.py

If you see "No such file or directory", continue to Step B.

Step B — Download the missing helper file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Still inside ``pystatsv1_workbook``, run::

  curl -L -o scripts/psych_ch11_paired_t.py \
    https://raw.githubusercontent.com/pystatsv1/PyStatsV1/main/scripts/psych_ch11_paired_t.py

Step C — Re-run the Chapter 11 checks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now this should pass::

  pystatsv1 workbook check ch11

Step D — Run Chapter 11 (use PYTHONPATH on Windows Git Bash)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On Windows + Git Bash, Chapter 11 may require ``PYTHONPATH=.`` so Python can find
the ``scripts`` package. Run::

  PYTHONPATH=. pystatsv1 workbook run ch11

Tip: If you ever see "No module named 'scripts'" on Windows Git Bash, retry the
command with ``PYTHONPATH=.`` in front.

Where are my outputs?
~~~~~~~~~~~~~~~~~~~~~

Chapter 11 writes results to the ``outputs`` folder. To open it quickly::

  explorer outputs



How to do the Study Habits Case Study Pack (TA instructions)
------------------------------------------------------------

This case study is designed to feel like a mini-course: one dataset, one story,
and a short sequence of runs that produce outputs you can inspect and (optionally)
submit.

Before you start
~~~~~~~~~~~~~~~~

1) Make sure your virtual environment is active (you should see something like
``(.venv)`` or ``(pystatsv1-env)`` in your prompt.

2) Make sure you are inside your workbook folder and then cd. ``cd /c/Users/<YOU>/.../pystatsv1_workbook`` in your prompt.

Step 0 — Confirm the case study files are present
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These commands should succeed (no "No such file" errors)::

  ls data/study_habits.csv
  ls scripts/study_habits_01_explore.py
  ls scripts/study_habits_02_anova.py

Step 1 — Run Part 1 (Explore)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the explore script::

  pystatsv1 workbook run study_habits_01_explore

What to do next:

* Open the outputs folder and look at the generated files (tables/plots)::

    explorer outputs/case_studies/study_habits

* Read the dataset columns (group, pretest/posttest/retention, hours, sleep, etc.)
  and write 2–3 sentences describing the study design (groups + repeated tests).

Step 2 — Run Part 2 (One-way ANOVA)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the ANOVA script::

  pystatsv1 workbook run study_habits_02_anova

What to record:

* Your ANOVA result (F, df, p-value).
* The direction of the effect (which group is highest/lowest on posttest_score).
* A short plain-English conclusion linked to the story.

Step 3 — Check your work
~~~~~~~~~~~~~~~~~~~~~~~~

Run the case study check::

  pystatsv1 workbook check study_habits

If it passes, you have the correct dataset and the expected effect pattern.

If it fails:

* Re-run Part 1 and Part 2.
* Confirm you are running commands from the workbook root folder.
* Ask the TA to look at the first error message shown by ``check`` (it usually
  points to the exact missing file or output).

Optional — Save your work for submission
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If your instructor requests a submission, a common approach is to zip the case study
outputs folder::

  cd outputs/case_studies
  # (zip using File Explorer: right-click study_habits -> Send to -> Compressed folder)

At minimum, keep:

* the generated plots/tables in ``outputs/case_studies/study_habits/``
* your written answers (or worksheet) for the story + ANOVA interpretation

Where this goes next (mini-course path)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once this case study is working, you can reuse the same dataset later:

* Ch10 (ANOVA): compare groups on posttest_score
* Ch18 (ANCOVA): add pretest_score as a covariate
* Ch19 (Regression): predict posttest_score from study_hours_per_week, sleep, etc.
* Ch20 (Nonparametric): compare groups using rank-based alternatives

Quick checklist (use this for every chapter)
--------------------------------------------

For each chapter or case study, follow this loop:

1) Run it::

     pystatsv1 workbook run <thing>

2) Inspect the outputs folder (plots/tables/CSVs)::

     explorer outputs

3) Write your short interpretation (what question, what result, what conclusion).

4) Check your work::

     pystatsv1 workbook check <thing>

Only move on when ``check`` passes.

Where did my outputs go?
------------------------

Most workbook tasks write files under an ``outputs/`` folder.

Common locations you may see:

* Workbook folder outputs (most common)::

    <your_workbook>/outputs/...

* Environment outputs (rare, but possible on Windows if a script uses package paths)::

    .../.venv/Lib/outputs/...

If you ran a script and ``explorer outputs`` looks empty, use the path printed by the
command output (copy/paste it into File Explorer), or search for the results file name::

  # Example: find all CSV outputs under the workbook folder
  find . -name "*.csv" | head

Tip: In Git Bash, ``explorer .`` opens the current folder in File Explorer.

Study Habits case study: what to write down
-------------------------------------------

After running:

* ``pystatsv1 workbook run study_habits_01_explore``
* ``pystatsv1 workbook run study_habits_02_anova``

Record these items in your notes or worksheet:

1) Design (1 sentence)
~~~~~~~~~~~~~~~~~~~~~~

Example:

* "We compare three study strategies (control, flashcards, spaced) on posttest performance."

2) Key descriptive result (1 sentence)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use ``group_summary.csv`` to report which group has the highest mean posttest score.

3) Inferential result (1 sentence)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

From the ANOVA table:

* Report F(df1, df2), p-value, and effect size (``np2``).

4) Plain-English conclusion (1 sentence)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Example:

* "Posttest scores differ by study strategy, with spaced repetition performing best in this dataset."

Files to look at:

* ``outputs/case_studies/study_habits/group_summary.csv``
* ``outputs/case_studies/study_habits/anova_posttest_by_group.csv``

"My Own Data" mini-guide (TA instructions)
------------------------------------------

This section helps you run the same **Run → Inspect → Check** workflow on a dataset
you choose. The goal is not perfection — the goal is to practice getting your data
into a clean CSV and generating sensible summaries and plots.

Before you start
~~~~~~~~~~~~~~~~

1) Make sure your virtual environment is active (you should see ``(.venv)`` or
``(pystatsv1-env)`` in your prompt).

2) Make sure you are inside your workbook folder ``cd /c/Users/<YOU>/.../pystatsv1_workbook``


Step 0 — Make a backup copy of the template (recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before you edit the template, make a copy so you can always revert::

  cp data/my_data.csv data/my_data_backup.csv

Step 1 — Put your data into the template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Open ``data/my_data.csv`` in Excel (or another spreadsheet editor) and replace
the example rows with your own data.

Rules of thumb for "clean data":

* One row = one observation (one person, one trial, one day, etc.)
* One column = one variable (group, score, hours, temperature, ...)
* Use simple column names (letters, numbers, underscores)
* Keep column types consistent (numbers stay numeric; text stays text)
* Use empty cells (or ``NA``) for missing values and be consistent

Save as **CSV** (not XLSX) when you are done.

Step 2 — Run the scaffold explore script
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

From your workbook folder, run::

  pystatsv1 workbook run my_data_01_explore

If your CSV is stored somewhere else, you can run the script directly::

  python scripts/my_data_01_explore.py --csv path/to/your.csv --outdir outputs/my_data

Step 3 — Inspect the outputs (what to look at first)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Open the output folder in File Explorer::

  explorer outputs/my_data

Start with these tables:

* ``outputs/my_data/tables/missingness.csv``  (which columns have missing values)
* ``outputs/my_data/tables/numeric_summary.csv`` (means, SDs, min/max, etc.)

Also check the plots folder:

* ``outputs/my_data/plots/`` (histograms/boxplots depending on your data)

Step 4 — Check your work (smoke test)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the matching check::

  pystatsv1 workbook check my_data

If it passes, your CSV is readable and the script produced the expected outputs.

If it fails, read the first error message carefully — it usually points to:

* a missing file
* a column name mismatch
* a column that looks numeric but is actually text

Step 5 — Customize the script for your column names
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Open ``scripts/my_data_01_explore.py`` and find::

  # === Student edits start here ===
  ID_COL = "id"
  GROUP_COL = "group"
  OUTCOME_COL = "outcome"

If your CSV uses different column names, change the values to match exactly.

Then re-run::

  pystatsv1 workbook run my_data_01_explore
  pystatsv1 workbook check my_data

Common problems (quick fixes)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* "Column not found": check spelling and capitalization in your CSV header row.
* Numbers treated as text: remove commas (``1,200`` -> ``1200``) and avoid mixing
  words with numbers in the same column.
* Missing values: use empty cells or ``NA`` consistently.
* If you get stuck: run the template CSV first (unchanged) to confirm your setup works.


Try "My Own Data" with Notepad (copy/paste example + expected results)
----------------------------------------------------------------------

If you don’t want to use Excel yet, you can edit the CSV directly in **Notepad**.

Step 1 — Open the template CSV in Notepad
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

From inside your workbook folder (``pystatsv1_workbook``), run::

  notepad data/my_data.csv

Replace the entire file contents with the example below (keep the header row).
Then **save** and close Notepad.

.. code-block:: text

  id,group,outcome,x1,x2
  1,control,73,2.1,10
  2,control,69,1.8,11
  3,control,75,2.4,9
  4,control,70,2.0,10
  5,control,68,1.7,
  6,control,74,2.3,9
  7,treatment,82,3.0,12
  8,treatment,79,2.7,13
  9,treatment,85,3.2,12
  10,treatment,81,2.9,14
  11,treatment,88,3.4,13
  12,treatment,,3.1,12

Notes:

* Row 5 has a **missing x2** value (empty after the last comma).
* Row 12 has a **missing outcome** value (empty after the second comma).
* Missing values are allowed — they help you practice checking missingness.

Step 2 — Run the scaffold script
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run::

  pystatsv1 workbook run my_data_01_explore

You should see a quick report similar to this (formatting may vary slightly):

.. code-block:: text

  My Own Data — quick report
  ========================
  rows: 12  cols: 5

  group: 2 group(s)
    - 'control': 6
    - 'treatment': 6

  numeric columns:
    - id
    - outcome
    - x1
    - x2

  Wrote outputs to:
    .../outputs/my_data

Step 3 — Inspect the outputs you just created
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Open the folder::

  explorer outputs/my_data

Start with these tables:

* ``outputs/my_data/tables/missingness.csv``

  Expected highlights for this example dataset:

  * ``outcome`` has **1** missing value (about **8.33%**)
  * ``x2`` has **1** missing value (about **8.33%**)

* ``outputs/my_data/tables/group_means.csv``

  Expected highlights for this example dataset:

  * control outcome mean ≈ **71.5**
  * treatment outcome mean ≈ **83.0**

Also check the plot:

* ``outputs/my_data/plots/numeric_histograms.png``

Step 4 — Check (smoke test)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run::

  pystatsv1 workbook check my_data

If it passes, your CSV is readable and the script is producing outputs correctly.
Now you can replace the example rows with your own data and repeat:
Run → Inspect → Check.


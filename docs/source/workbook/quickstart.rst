Quickstart
==========

This quickstart shows two ways to use PyStatsV1:

- **Student mode (recommended):** install from **PyPI** inside a virtual environment, then generate a local Workbook folder.
- **Contributor mode:** clone the repo and run chapters from source.

Why the virtual environment matters
-----------------------------------

PyStatsV1 is intentionally a *thin wrapper built on the shoulders of giants* (NumPy, pandas, SciPy, statsmodels, etc.).
A virtual environment (``.venv``) keeps those dependencies isolated so your system Python stays clean.

Student mode: PyPI + Workbook starter (recommended)
---------------------------------------------------

Windows 11 (Git Bash)
^^^^^^^^^^^^^^^^^^^^^

1) Create a folder and a virtual environment

.. code-block:: bash

   mkdir -p ~/pystatsv1_student
   cd ~/pystatsv1_student

   python -m venv .venv
   source .venv/Scripts/activate

2) Install PyStatsV1 + the Workbook dependency bundle

.. code-block:: bash

   python -m pip install -U pip
   python -m pip install "pystatsv1[workbook]"

3) Sanity check (optional but recommended)

.. code-block:: bash

   pystatsv1 doctor

4) Create the local Workbook starter and run Chapter 10

.. code-block:: bash

   pystatsv1 workbook init
   cd pystatsv1_workbook

   python scripts/psych_ch10_problem_set.py
   pytest -q


macOS
^^^^^

1) Create a folder and a virtual environment

.. code-block:: bash

   mkdir -p ~/pystatsv1_student
   cd ~/pystatsv1_student

   python3 -m venv .venv
   source .venv/bin/activate

2) Install PyStatsV1 + the Workbook dependency bundle

.. code-block:: bash

   python -m pip install -U pip
   python -m pip install "pystatsv1[workbook]"

3) Create the local Workbook starter and run Chapter 10

.. code-block:: bash

   pystatsv1 workbook init
   cd pystatsv1_workbook

   python scripts/psych_ch10_problem_set.py
   pytest -q


Linux (Ubuntu / Debian)
^^^^^^^^^^^^^^^^^^^^^^^

1) Ensure Python tooling is installed

.. code-block:: bash

   sudo apt update
   sudo apt install -y python3 python3-venv python3-pip

2) Create a folder and a virtual environment

.. code-block:: bash

   mkdir -p ~/pystatsv1_student
   cd ~/pystatsv1_student

   python3 -m venv .venv
   source .venv/bin/activate

3) Install PyStatsV1 + the Workbook dependency bundle

.. code-block:: bash

   python -m pip install -U pip
   python -m pip install "pystatsv1[workbook]"

4) Create the local Workbook starter and run Chapter 10

.. code-block:: bash

   pystatsv1 workbook init
   cd pystatsv1_workbook

   python scripts/psych_ch10_problem_set.py
   pytest -q


Contributor mode: run from source
---------------------------------

If you want to go “full-on” PyStatsV1 (write your own scripts, modify internals, contribute PRs), use source mode.

Windows (Git Bash) / macOS / Linux
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   mkdir -p ~/pystatsv1_dev
   cd ~/pystatsv1_dev

   git clone https://github.com/pystatsv1/PyStatsV1.git
   cd PyStatsV1

   python -m venv .venv
   source .venv/Scripts/activate    # Windows Git Bash
   # source .venv/bin/activate      # macOS/Linux

   python -m pip install -U pip
   pip install -e .
   pip install -r requirements-dev.txt

   make lint
   pytest -q


If something looks “missing”
----------------------------

- If you accidentally installed into your *system Python*, delete the environment and start over:

.. code-block:: bash

   deactivate
   rm -rf .venv

- If ``pystatsv1 doctor`` reports missing packages, reinstall the student bundle:

.. code-block:: bash

   python -m pip install "pystatsv1[workbook]"

Quickstart
==========

This quickstart gives you a clean, repeatable way to run PyStatsV1 chapters locally.

Windows (Git Bash)
------------------

1) Create a workspace and clone PyStatsV1

.. code-block:: bash

   mkdir -p ~/pystatsv1_student
   cd ~/pystatsv1_student

   git clone https://github.com/pystatsv1/PyStatsV1.git
   cd PyStatsV1

2) Create and activate a virtual environment

.. code-block:: bash

   python -m venv .venv
   source .venv/Scripts/activate

   python -m pip install -U pip

3) Install PyStatsV1 (editable) + dev tools

.. code-block:: bash

   pip install -e .
   pip install -r requirements-dev.txt

4) Quick verification (recommended)

.. code-block:: bash

   make lint
   pytest -q


macOS
-----

1) Clone and create a virtual environment

.. code-block:: bash

   mkdir -p ~/pystatsv1_student
   cd ~/pystatsv1_student

   git clone https://github.com/pystatsv1/PyStatsV1.git
   cd PyStatsV1

   python3 -m venv .venv
   source .venv/bin/activate

   python -m pip install -U pip

2) Install + verify

.. code-block:: bash

   pip install -e .
   pip install -r requirements-dev.txt

   make lint
   pytest -q


Linux (Ubuntu/Debian)
---------------------

1) Install Python tooling

.. code-block:: bash

   sudo apt update
   sudo apt install -y python3 python3-venv python3-pip git

2) Clone, create venv, install

.. code-block:: bash

   mkdir -p ~/pystatsv1_student
   cd ~/pystatsv1_student

   git clone https://github.com/pystatsv1/PyStatsV1.git
   cd PyStatsV1

   python3 -m venv .venv
   source .venv/bin/activate

   python -m pip install -U pip

   pip install -e .
   pip install -r requirements-dev.txt

   make lint
   pytest -q


If something looks "missing"
----------------------------

- If ``make`` is not available on Windows, run the underlying commands directly:

.. code-block:: bash

   ruff check .
   pytest -q

- If you see "command not found" for ``python3`` on Windows, use ``python``.
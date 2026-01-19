Quickstart (all platforms)
==========================

This Workbook is designed to work the same way on **Linux**, **macOS**, and **Windows**.

You will do the same 3-step loop in every chapter:

1. **Run** a script (generates results you can look at)
2. **Inspect** the outputs (tables + plots)
3. **Check** your work (runs the matching tests)

No ``make`` required.


Prerequisites
-------------

* Python 3.10+ installed
* A terminal:
  * Linux/macOS: Terminal
  * Windows: PowerShell or Git Bash

If you are setting up Windows 11 for the first time, see :doc:`windows11_setup`.

Tip: If you ever see ``pystatsv1: command not found`` (or Windows says it “is not recognized”),
jump to :doc:`troubleshooting`.


1) Install PyStatsV1
--------------------

Create a virtual environment (recommended), then install:

Linux/macOS:

.. code-block:: bash

   python -m venv .venv
   source .venv/bin/activate

   python -m pip install --upgrade pip
   python -m pip install "pystatsv1[workbook]"

Windows (Git Bash):

.. code-block:: bash

   python -m venv .venv
   source .venv/Scripts/activate

   python -m pip install --upgrade pip
   python -m pip install "pystatsv1[workbook]"

Windows (PowerShell):

.. code-block:: bash

   python -m venv .venv
   .venv\Scripts\Activate.ps1

   python -m pip install --upgrade pip
   python -m pip install "pystatsv1[workbook]"




.. note::

   The ``[workbook]`` extra installs `pytest`, which is required for ``pystatsv1 workbook check``.

2) Initialize the Workbook
--------------------------

Pick a folder you want to work in, then run:

.. code-block:: bash

   pystatsv1 workbook init --dest my_workbook

.. tip::

   Want the Track D accounting case workbook? Use:

   .. code-block:: bash

      pystatsv1 workbook init --track d --dest track_d_workbook

   Then see :doc:`track_d_student_edition` (student path) or :doc:`track_d` (full Track D workbook page).

This creates a ready-to-run Workbook folder (scripts + tests + data).


3) Run → Inspect → Check (Chapter 10 example)
---------------------------------------------

.. code-block:: bash

   cd my_workbook

   # Run the chapter script (creates outputs)
   pystatsv1 workbook run ch10

   # Inspect: look in the outputs/ folder
   # (tables, plots, and other artifacts)

   # Check: run the matching tests
   pystatsv1 workbook check ch10


Next steps
----------

* See all available chapters:

  .. code-block:: bash

     pystatsv1 workbook list

* Then repeat the same loop for any chapter:

  .. code-block:: bash

     pystatsv1 workbook run ch11
     pystatsv1 workbook check ch11

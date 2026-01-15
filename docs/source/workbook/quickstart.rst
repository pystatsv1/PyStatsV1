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

Tip: If you ever see ``pystatsv1: command not found`` (or Windows says it “is not recognized”),
jump to :doc:`troubleshooting`.


1) Install PyStatsV1
--------------------

Create a virtual environment (recommended), then install:

.. code-block:: bash

   python -m venv .venv
   # Linux/macOS
   source .venv/bin/activate
   # Windows (PowerShell)
   # .venv\Scripts\Activate.ps1

   python -m pip install --upgrade pip
   python -m pip install pystatsv1


2) Initialize the Workbook
--------------------------

Pick a folder you want to work in, then run:

.. code-block:: bash

   pystatsv1 workbook init ./my_workbook

This creates a ready-to-run Workbook folder (scripts + tests + data).


3) Run → Inspect → Check (Chapter 10 example)
---------------------------------------------

.. code-block:: bash

   cd ./my_workbook

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

Workflow: Run → Inspect → Check
===============================

Every chapter follows the same loop:

**Run**
  Runs the script for a chapter (or another Workbook script you choose).

**Inspect**
  Look at what the script produced (usually in ``outputs/``).

**Check**
  Runs the tests for that chapter (or for a case study pack).

The goal is to make your learning *fast* and *safe*:

* you can run experiments,
* you can see results immediately,
* and you can confirm your work with one command.


Run
---

Run a chapter script:

.. code-block:: bash

   pystatsv1 workbook run ch18

Or run a script by path:

.. code-block:: bash

   pystatsv1 workbook run scripts/psych_ch18_problem_set.py


Inspect
-------

Most scripts write artifacts under ``outputs/`` (tables, plots, and intermediate results).

Use your file browser (or ``ls`` / ``dir``) to explore what was created.


Check
-----

Run tests for a chapter:

.. code-block:: bash


.. note::

   ``pystatsv1 workbook check`` runs `pytest`.
   Install it with: ``python -m pip install "pystatsv1[workbook]"``.

   pystatsv1 workbook check ch18


Next: Try your own data
-----------------------

After you’re comfortable with the loop, try the :doc:`my_own_data` mini-guide.



Optional: Make targets (if you already have make)
-------------------------------------------------

If you have ``make`` installed, the Workbook also includes convenience targets,
but they are optional. The CLI commands above are the recommended workflow.

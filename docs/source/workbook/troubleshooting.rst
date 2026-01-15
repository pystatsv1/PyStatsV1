Troubleshooting
===============

This page covers the most common issues for first-time Python users on Linux/macOS/Windows.


“pystatsv1” is not recognized / command not found
-------------------------------------------------

This usually means the console can’t find the ``pystatsv1`` entrypoint.

Try running via Python directly:

.. code-block:: bash

   python -m pystatsv1 workbook list

If that works, your environment is fine — it’s just a PATH/entrypoint issue.
Make sure you activated your virtual environment before running commands.


Pytest not installed
--------------------

``pystatsv1 workbook check ...`` runs tests using pytest.

If you see an error mentioning ``pytest``:

.. code-block:: bash

   python -m pip install pytest


I ran a script but don’t see anything
-------------------------------------

Most Workbook scripts write outputs to an ``outputs/`` folder.

* Check ``outputs/`` in your file browser
* Or list files in the terminal:

  .. code-block:: bash

     ls outputs
     # Windows:
     # dir outputs


Windows PowerShell activation blocked
-------------------------------------

If PowerShell refuses to activate your venv, you can either:

* use Git Bash, or
* run PowerShell as Administrator and allow scripts (common in dev workflows)

Or skip activation and run commands like:

.. code-block:: bash

   .venv\Scripts\python -m pip install pystatsv1
   .venv\Scripts\python -m pystatsv1 workbook list

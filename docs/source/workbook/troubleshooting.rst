Troubleshooting
===============

"pystatsv1 is not found"
------------------------

- Make sure your virtual environment is activated.
- If you're working from the repository, install the package in editable mode::

   pip install -e .

"make" is not available on Windows
----------------------------------

- On Windows, PyStatsV1 assumes you're using **Git Bash** (which usually includes ``make``).
- If ``make`` still isn't found, you can always run the scripts directly::

   python scripts/psych_ch18_problem_set.py

Plots do not show up
--------------------

Many scripts **save figures** to disk instead of opening interactive windows.
Look in:

- ``outputs/track_c/``

Tests fail even though your output "looks right"
------------------------------------------------

- Re-run the chapter with the chapter's default ``random_state``.
- Delete old outputs and try again.
- Make sure your dependencies are up to date::

   pip install -U pip
   pip install -r requirements.txt


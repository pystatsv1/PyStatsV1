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

   pystatsv1 workbook init ./my_workbook
   cd ./my_workbook

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

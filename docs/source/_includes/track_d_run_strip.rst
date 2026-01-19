.. admonition:: PyPI workbook run (Track D)

   From inside your **Track D workbook folder** (created by ``pystatsv1 workbook init --track d --dest ...``), run:

   .. code-block:: bash

      pystatsv1 workbook run |trackd_run|

   Outputs are written under ``outputs/track_d/`` by default.
   If you're unsure what a file is for, start with :doc:`/workbook/track_d_outputs_guide`.

   To see the full chapter-by-chapter run map (D00–D23), see :doc:`/workbook/track_d_chapter_index`.

   Optional: write to a custom output folder:

   .. code-block:: bash

      pystatsv1 workbook run |trackd_run| --outdir outputs/track_d_custom

   Interpretation prompts (quick self-check):

   - What is the accounting or business **measurement goal** in this chapter?
   - Which **invariant/check** would catch a “numbers look fine but are wrong” mistake here?


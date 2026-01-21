.. _track_d_playbook:

=============================
Track D Playbook: Big Picture
=============================

Track D is about one idea: **use statistics to understand accounting data**.
The loop is: export → normalize → validate → analyze → communicate.

The case study (NSO) gives you realistic, messy numbers—but the goal is transfer:
you should be able to take *your own accounting exports* and run the same kind of
analysis with PyStatsV1.

This playbook is a short “map of the territory.” Each chapter is an outline (for now),
meant to be filled in gradually.

How to use this playbook
------------------------

1. Read :doc:`01_orientation` once (it explains the full Track D workflow).
2. Use :doc:`05_core_analysis_recipes` as your “what do I do next?” page while working.
3. When you bring your own data, jump to :doc:`08_byod_in_the_real_world` (and see ``pystatsv1 trackd byod daily-totals``).

Where to find the commands and file paths
-----------------------------------------

- **Student entry point**: :doc:`../track_d_student_edition`
- **Track D chapter list**: :doc:`../track_d_chapter_index`
- **Dataset map + outputs**: :doc:`../track_d_dataset_map`, :doc:`../track_d_outputs_guide`
- **Bring your own data (BYOD)**: :doc:`../track_d_byod`
- **This playbook**: :doc:`index`

.. toctree::
   :maxdepth: 2

   01_orientation
   02_accounting_data_pipeline
   03_trackd_dataset_contract
   04_nso_case_story
   05_core_analysis_recipes
   06_time_series_and_forecasting
   07_risk_controls_and_quality
   08_byod_in_the_real_world
   09_reporting_and_storytelling
   10_capstone_projects
   a_cli_cheatsheet
   a_glossary

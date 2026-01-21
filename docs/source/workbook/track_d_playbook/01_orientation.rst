Orientation: what Track D is and how to use it
==============================================

**Why this exists:** Track D can feel like “a lot of scripts.” This chapter shows the *workflow* that ties everything together.

Learning objectives
-------------------

- Explain Track D in one sentence (statistics on accounting data).
- Describe the Track D workflow: export → normalize → validate → analyze → communicate.
- Know the three kinds of Track D work: case study, labs, and BYOD.
- If you forget a command, run ``pystatsv1 --help`` or ``pystatsv1 trackd byod --help``.

Outline
-------

The Track D workflow in one page
--------------------------------

- Start from an accounting export (or the NSO case study dataset).
- Get the data into the Track D dataset contract (either already canonical, or via BYOD normalization).
- Run a chapter script to answer a question (and write outputs).
- Use the artifacts (CSV/PNG/JSON) to write a short business interpretation.

What you should have at the end
-------------------------------

- A reproducible folder with inputs + scripts + outputs (so you can rerun later).
- A small set of charts/tables that tell a story about revenue, costs, or risk.
- A written summary that a manager could act on.

Common mental model mistakes (and fixes)
----------------------------------------

- Mistake: treating accounting data as “just categories.” Fix: it’s a time-stamped database with structure.
- Mistake: skipping validation. Fix: always run a quick check before believing results.
- Mistake: staring at raw rows. Fix: aggregate into daily/monthly totals and compare periods.

Where this connects in the workbook
-----------------------------------

- :doc:`index` (the Playbook overview / map)
- :doc:`../track_d_student_edition` (how students actually run chapters)
- :doc:`../track_d_outputs_guide` (how to read what scripts produce)
- :doc:`../track_d_byod` (how to analyze your own exports)

.. note::

   This page is intentionally an outline right now. Expand it incrementally as we refine Track D narrative.

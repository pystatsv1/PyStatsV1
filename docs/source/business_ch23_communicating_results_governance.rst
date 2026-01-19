Chapter 23 — Communicating results: decision memos, dashboards, and governance
==============================================================================

.. |trackd_run| replace:: d23
.. include:: _includes/track_d_run_strip.rst

This chapter is the "final mile": turning analysis and forecasts into
**decision-ready communication** with an audit trail.

In the NSO running case, you have already built:

* an expense forecast (Chapter 18)
* a 13-week cash forecast (Chapter 19)
* an integrated 3-statement model (Chapter 20)
* scenario and sensitivity outputs (Chapter 21)
* a statement-analysis toolkit (Chapter 22)

Chapter 23 packages those results in a way that is usable by real teams.


Learning objectives
-------------------

By the end of this chapter, you should be able to:

* Write a 1–2 page executive memo: what happened, why, what next, and risks.
* Define KPI governance (definition, source, owner, cadence, thresholds).
* "Red team" an analysis: spot overclaiming, missing controls, and weak assumptions.


Direct guidance (accountant-friendly)
-------------------------------------

Good communication is not more charts. It is:

* **Clear definitions** (no KPI ambiguity).
* **Conservative interpretation** (avoid causal overreach).
* **Assumptions + one-offs** documented (so the next close is consistent).
* **Ownership and cadence** (so the work actually gets updated).


How to run
----------

Generate the NSO synthetic dataset (if you haven't already):

.. code-block:: bash

   make business-nso-sim

Then run Chapter 23:

.. code-block:: bash

   make business-ch23


Outputs
-------

The script writes deterministic templates to ``outputs/track_d/``:

* ``ch23_memo_template.md`` — a CFO-style executive memo template (with an NSO snapshot).
* ``ch23_kpi_governance_template.csv`` — KPI governance table (definitions, sources, owners).
* ``ch23_dashboard_spec_template.csv`` — a simple dashboard spec (panels, charts, decisions).
* ``ch23_red_team_checklist.md`` — checklist to catch overclaiming and weak controls.
* ``ch23_design.json`` — design file capturing seed + snapshot month.


End-of-chapter problems
-----------------------

1. **Executive memo (1 page).** Write: what happened, why, what next, and risks.
2. **KPI governance table.** Fill in: definition, source, owner, update cadence, thresholds.
3. **Red team.** Identify overclaiming, missing controls, and assumptions that must be logged.

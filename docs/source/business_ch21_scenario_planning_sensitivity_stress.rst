Business Statistics & Forecasting for Accountants (Track D)
===========================================================

Chapter 21 — Scenario planning, sensitivity analysis, and stress testing
------------------------------------------------------------------------

This chapter turns your integrated forecast into a **decision tool**:

* **Scenarios**: best/base/worst forecasts tied to explicit driver assumptions.
* **Sensitivity**: a simple “what matters most?” scan to find the levers that move cash risk.
* **Stress tests**: conservative shocks that answer: *What if things go wrong at the same time?*

The focus is accountant-friendly:

* interpret coefficients as **rates and baselines**,
* avoid causal overclaiming,
* use guardrails (cash buffer triggers, documentation, and governance).

Learning objectives
^^^^^^^^^^^^^^^^^^^

By the end of Chapter 21 you should be able to:

* Build a **best/base/worst** scenario pack tied to driver assumptions.
* Run a **sensitivity scan** to identify the top levers affecting cash shortfall risk.
* Create a **stress test narrative** suitable for a lender or board packet.
* Communicate downside risk conservatively with a clear audit trail.

Direct, practical idea
^^^^^^^^^^^^^^^^^^^^^^

Scenario planning works best when you keep the model simple:

* Revenue assumptions (level / multiplier)
* Gross margin assumptions (COGS as a rate of revenue)
* Operating expense assumptions (Opex as a rate of revenue)
* Working capital behavior (DSO / DIO / DPO as “days”)
* Cash policy (buffer targets and trigger thresholds)

The script for this chapter uses the NSO v1 simulator tables and produces a deterministic
scenario pack plus a one-at-a-time sensitivity summary.

How to run
^^^^^^^^^^

From the repo root:

.. code-block:: bash

   # (Re)generate NSO v1 synthetic data (if needed)
   make business-nso-sim

   # Run Chapter 21
   make business-ch21

Outputs
^^^^^^^

Artifacts are written under ``outputs/track_d/``:

* ``ch21_scenario_pack_monthly.csv`` — 12-month scenario pack (Base / Best / Worst / Stress)
* ``ch21_sensitivity_summary.csv`` — one-at-a-time sensitivity scan (cash buffer risk)
* ``ch21_assumptions.csv`` — scenario assumptions log (explicit, auditable)
* ``ch21_cash_governance_template.csv`` — governance checklist (who/when/trigger/action)
* ``ch21_design.json`` — reproducibility metadata
* ``ch21_memo.md`` — short interpretation memo
* ``ch21_figures_manifest.csv`` + ``figures/ch21_fig_*.png`` — figure list + plots

Interpretation guardrails
^^^^^^^^^^^^^^^^^^^^^^^^^

* Treat scenario results as **planning ranges**, not forecasts you can “prove.”
* If a scenario shows cash risk, the right response is **controls + mitigation options**:

  * tighten collections (DSO)
  * adjust purchasing/inventory (DIO)
  * renegotiate payment terms (DPO)
  * delay non-critical capex
  * change owner draws / distributions

* Do not claim that a lever *causes* a cash change unless you can justify the mechanism.

End-of-chapter problems
^^^^^^^^^^^^^^^^^^^^^^^

1. **Three-scenario pack**: Create best/base/worst assumptions and summarize differences
   in one page (cash buffer triggers and recommended mitigations).
2. **Sensitivity**: Identify the top 3 levers impacting cash shortfall risk and explain
   why each lever matters operationally.
3. **Stress test memo**: Draft a lender-ready explanation of your stress test logic:
   assumptions, conservatism, and action plan.

Business Chapter 11 — Sampling and Estimation (Audit and Controls Lens)
=====================================================================

Accountants and controllers often face a simple constraint: you *cannot* review every transaction.
Sampling is a cost-effective control — but only if it is designed and communicated clearly.

This chapter translates sampling and confidence intervals into audit/control language:

* **Population vs Sample:** what you're trying to control vs what you actually reviewed.
* **Random vs Stratified Sampling:** everyone has an equal chance vs risk-based groups.
* **Confidence Intervals:** turning "95% confidence" into a plain-English range and a pass/fail control decision.

Learning objectives
-------------------

After this chapter, you can:

* Design a **risk-based sampling plan** (review 100% of material items, sample the long tail).
* Compute a defensible **error-rate confidence interval** and interpret it in business language.
* Draft a short memo that uses the vocabulary auditors expect: *population, sample size, materiality, tolerance, confidence*.

Data inputs (NSO v1)
-------------------

We reuse the synthetic dataset from ``sim_business_nso_v1`` and treat A/P invoices as the "pile" to audit:

* ``ap_events.csv`` — invoice events and payments (we sample invoice rows)

Repro commands
-------------

.. code-block:: bash

   make business-nso-sim
   make business-ch11

Or run directly:

.. code-block:: bash

   python -m scripts.business_ch11_sampling_estimation_audit_controls \
     --datadir data/synthetic/nso_v1 \
     --outdir outputs/track_d \
     --seed 123

Outputs (audit-friendly artifacts)
---------------------------------

The chapter writes deterministic artifacts to ``outputs/track_d``:

* ``ch11_sampling_plan.json`` — explicit parameters + selected invoice IDs
* ``ch11_sampling_summary.json`` — CI, tolerance decision, and a worked example
* ``ch11_audit_memo.md`` — short justification memo (plain language)
* ``ch11_figures_manifest.csv`` — figure metadata for auditability
* ``figures/``:
  * ``ch11_strata_sampling_bar.png`` — population vs sample by stratum
  * ``ch11_error_rate_ci.png`` — observed error rate with 95% CI

End-of-chapter problems (implemented concepts)
---------------------------------------------

1) **Design a sampling plan (risk-based).**
   Review 100% of transactions over a materiality threshold (e.g., $1,000),
   and random-sample a small percentage of immaterial items (e.g., 5% under $50).

2) **Confidence interval calculation (controls lens).**
   Given a sample size and number of errors, compute a 95% CI for the true error rate.
   If the *upper bound* exceeds management's tolerance (e.g., 2%), the control fails.

3) **The audit memo.**
   Justify the approach using proper terms: population, sample size, materiality,
   stratification, tolerance, confidence.

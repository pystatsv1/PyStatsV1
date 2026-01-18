.. _workbook_track_d_student_edition:

==========================================
Track D Student Edition (Workbook Landing)
==========================================

This page is the **front door** for Track D (Business Statistics with an accounting case study).

If you do only one thing first, do this:

1) Follow the workbook quickstart.
2) Run ``d00_peek_data`` to *see the data*.
3) Run ``d01`` to *see the accounting invariants*.
4) Use the “skill map” below to keep your bearings.

.. note::

   Track D is designed to make you a better analyst of accounting data.
   You will learn how to **trust** the numbers (quality control), **summarize** them (statements and KPIs),
   and **make decisions** with them (inference, regression, forecasting, scenarios).

Where to start (PyPI-only)
==========================

Install and create the Track D workbook:

.. code-block:: bash

   python -m venv .venv
   # Windows (Git Bash):
   source .venv/Scripts/activate
   python -m pip install -U pip
   pip install "pystatsv1[workbook]"

   pystatsv1 workbook init --track d --dest track_d_workbook
   cd track_d_workbook

Then run these two “confidence builders”:

.. code-block:: bash

   pystatsv1 workbook run d00_peek_data
   pystatsv1 workbook run d01

Helpful pages in the Workbook docs
==================================

These pages live inside the workbook documentation subtree (they build cleanly on their own):

- :doc:`quickstart` — first-time setup and commands
- :doc:`workflow` — how “run” vs “check” works, outputs conventions, troubleshooting
- :doc:`track_d` — Track D workbook quickstart + dataset map (seed=123)
- :doc:`track_d_lab_ta_notes` — a lab handout + TA notes (walkthrough + interpretation)

What you are building (the pipeline)
====================================

Track D is a **repeatable analysis workflow**. You are not just “running scripts.”
You are learning how to take messy accounting-like events and turn them into a decision-ready story.

Here’s the mental model:

::

   Events (sales, bills, payroll, inventory, loans)
       ↓  (recording rules + checks)
   General Ledger (journal entries)
       ↓  (postings → trial balance)
   Financial Statements (IS, BS, CF)
       ↓  (descriptive stats, visual checks)
   Decisions (risk, sampling, tests, regression)
       ↓  (forecasts, scenarios, governance)
   Communicate (clear memo + reproducible outputs)

The goal: **trustworthy numbers + clear decisions**.

Why Track D makes you a better analyst
======================================

Track D trains three “analyst superpowers” that matter in real accounting and finance work:

1) **Data integrity (trust the numbers)**
   - You learn the invariants that must hold (balanced entries, consistent statements).
   - You learn how to spot red flags (duplicates, missingness, impossible values, broken joins).

2) **Decision discipline (answers with uncertainty)**
   - You learn how to quantify risk (probability).
   - You learn how to estimate and test (sampling + hypothesis testing).
   - You learn how to model drivers (regression) without overclaiming.

3) **Communication (results people can act on)**
   - You learn how to tell a coherent story from the data.
   - You learn to separate “signal” from “noise” and explain limits honestly.
   - You learn reproducible workflows that other people can audit.

Skill map (D00–D23)
===================

Use this map to understand *why* each group of chapters exists.

Phase 0 — On-ramp (see the data)
--------------------------------
- **D00**: Setup/reset datasets and **peek** at the datasets (what tables exist, what they look like)

Phase 1 — Accounting foundations (what the numbers mean)
--------------------------------------------------------
- **D01–D06**: journal entries, chart of accounts, statements logic, reconciliations, and quality control

Phase 2 — Data preparation (make the dataset analysis-ready)
------------------------------------------------------------
- **D07**: build analysis tables, document joins/keys/grain, verify quality checks

Phase 3 — Describe performance + report responsibly
---------------------------------------------------
- **D08–D09**: descriptive statistics and reporting conventions (what to compute, how to present it)

Phase 4 — Statistics for decisions (business lens)
--------------------------------------------------
- **D10–D14**: probability/risk, sampling/estimation, hypothesis testing, correlation vs causation, regression drivers

Phase 5 — Forecasting + governance
----------------------------------
- **D15–D23**: forecasting hygiene, seasonality, drivers, cash flow, integrated scenarios, and communication/governance

How to use Track D week-to-week
===============================

A good weekly rhythm:

1) Run the chapter script (``pystatsv1 workbook run dXX``).
2) Open what it writes in ``outputs/track_d/`` (tables + summaries).
   If you are not sure what a file is for, use :doc:`track_d_outputs_guide`.
3) Answer the chapter questions *in words* (what changed, why, what action follows).
4) Run the smoke checks (``pystatsv1 workbook check business_smoke``).

.. code-block:: bash

   pystatsv1 workbook run d08
   pystatsv1 workbook check business_smoke

Common “student mistakes” and what to do
========================================

**“I ran it, but I don’t know what it means.”**
- Start at :doc:`track_d_lab_ta_notes` and follow the interpretation prompts.
- Re-run ``d00_peek_data`` and read the previews slowly.

**“My outputs differ from the handout / screenshots.”**
- Confirm you are using the canonical datasets (seed=123) under ``data/synthetic/``.
- If you edited anything in ``data/synthetic/``, reset:

  .. code-block:: bash

     pystatsv1 workbook run d00_setup_data --force

**“I want to apply this to my own data.”**
- That’s the endgame. After you complete the basics, you’ll use a “bring your own data” playbook (coming next in the workbook docs) that shows how to map real exports (QuickBooks/bank/invoices) into the same workflow.
  
What “good” looks like by the end
=================================

By the end of Track D you should be able to:

- Explain how accounting events become analysis tables (and what can go wrong).
- Produce a monthly trial balance and statements and sanity-check them.
- Compute KPIs and explain what drives changes (not just “the number changed”).
- Use estimation, tests, and regression to support a recommendation.
- Produce a simple forecast and scenario analysis with clear assumptions.
- Write a short memo that a manager could actually use.

How to apply Track D to your own data
-------------------------------------

For a general starting point, see :doc:`my_own_data`.

Track D will also include a Track D-specific “Bring Your Own Data” playbook that shows how to map real
exports (QuickBooks / bank / invoices) to the same **dataset contract** used in the NSO synthetic case.


Next page
=========

When you’re ready, jump to:

- :doc:`track_d` (Track D workbook quickstart + dataset map)

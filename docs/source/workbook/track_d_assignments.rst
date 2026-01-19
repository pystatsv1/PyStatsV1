.. _track_d_assignments:

=========================================
Track D assignments: labs + rubric (TA)
=========================================

This page turns Track D into a **gradeable lab sequence**.

- Students produce a small set of files under ``outputs/track_d/``.
- Students answer a few short prompts (and write one short memo).
- TAs can grade quickly with a clear checklist + rubric.

If students are new to Track D, point them to:

- :doc:`track_d_student_edition`
- :doc:`track_d_outputs_guide` (what outputs mean)
- :doc:`track_d_dataset_map` (tables, keys, and intentional QC “warts”)

Prerequisites (students)
========================

Students should start from a fresh Track D workbook folder created by::

   pystatsv1 workbook init --track d --dest track_d_workbook
   cd track_d_workbook

All labs below assume the default Track D scripts in that folder.

Submission format
=================

Ask students to submit **one ZIP file** containing:

1) ``outputs/track_d/`` (artifacts)
2) ``answers.md`` (short answers for Labs 1–3)

Suggested ZIP command (from the workbook folder)::

   # Windows PowerShell (inside track_d_workbook)
   Compress-Archive -Path outputs/track_d,answers.md -DestinationPath track_d_submission.zip -Force

   # macOS/Linux (inside track_d_workbook)
   zip -r track_d_submission.zip outputs/track_d answers.md

Lab 1 — Run + interpret outputs
===============================

Goal
----

Students can run Track D, locate outputs, and explain the key metrics in plain language.

Run
---

From the Track D workbook folder::

   pystatsv1 workbook run d00_peek_data
   pystatsv1 workbook run d01

Required artifacts
------------------

Students must include these files in ``outputs/track_d/``:

- ``d00_peek_data_summary.md``
- ``business_ch01_summary.json``
- ``business_ch01_income_statement.png``
- ``business_ch01_balance_sheet.png``

Short answers (write in ``answers.md``)
--------------------------------------

Answer in 1–3 sentences each.

1) **Where do outputs land?**
   - Give the exact folder path (relative to the workbook).

2) **Net income can be negative. Why?**
   - Explain one realistic reason a startup month might show negative net income.

3) **Gross margin, in plain language.**
   - What is it, and why do analysts care?

4) **What does ``pct_sales_on_account`` mean?**
   - Explain it as if you were speaking to a non-accountant manager.

5) **What good looks like (sanity checks).**
   - List 2 checks you can run (or observe) that increase confidence you didn’t break the data.

TA quick-check (optional)
-------------------------

For the stock Track D case, ``d01`` prints a small “sanity summary” to the terminal
that includes ``n_transactions`` and whether the accounting equation balances.
Students do **not** need exact matching numbers, but their explanations should be consistent.

Lab 2 — QC detective: duplicate bank transaction IDs
====================================================

Goal
----

Students demonstrate “accounting-data analyst” habits:
identify a QC issue, explain why it matters, and propose a defensible fix.

Task
----

Using the NSO v1 bank statement table (from the Track D dataset), find a duplicated
transaction identifier and document it.

Students may use any method (spreadsheet filter, Python, etc.).
Here is an optional Python snippet they can adapt::

   import pandas as pd
   p = "data/synthetic/nso_v1/bank_statement.csv"
   df = pd.read_csv(p)
   dup = df[df.duplicated("bank_txn_id", keep=False)].sort_values("bank_txn_id")
   print(dup[["bank_txn_id","date","amount","description"]].head(20))

Required artifacts
------------------

Students must include in ``outputs/track_d/``:

- ``lab2_qc_report.md`` (their QC write-up)

Their report must include:

- the duplicated ``bank_txn_id`` value(s)
- how many rows were duplicated
- why the duplication matters (what could go wrong downstream)
- a proposed fix policy (example: “drop exact duplicates”, or “keep the earliest posted row”)
- one “before vs after” check (example: total cash inflow/outflow changes, or count of transactions)

Short answers (write in ``answers.md``)
--------------------------------------

1) **What did you find?**
   - One sentence summary of the duplicate.

2) **What could break if we ignore it?**
   - Name one analysis result that could be distorted.

3) **What fix policy did you choose and why?**

Lab 3 — Executive summary memo
==============================

Goal
----

Students turn outputs into a clear, decision-friendly narrative.

Prompt
------

Write a **250–400 word** memo (in ``answers.md``) titled:

**“Track D Executive Summary (Month 1)”**

Use the Lab 1 outputs (plots + JSON summary) and include:

- 2–3 key facts about sales, gross margin, and expenses
- net income interpretation (including why it may be negative)
- 1 balance sheet insight (example: cash position, liabilities, equity)
- 2 “next questions” you’d ask before making a real decision

Rubric (100 points)
===================

This rubric is designed to be fast to grade.

Artifacts + reproducibility (30)
--------------------------------

- (10) Required Lab 1 artifacts present in ``outputs/track_d/``
- (10) Lab 2 QC report present and complete
- (10) Student’s ``answers.md`` is organized with headings for Lab 1–3

Interpretation of outputs (30)
------------------------------

- (10) Net income explanation is realistic and correctly framed
- (10) Gross margin explained correctly (and why it matters)
- (10) ``pct_sales_on_account`` explained correctly and connected to business meaning

QC reasoning (20)
-----------------

- (10) Duplicate ID issue clearly demonstrated with evidence
- (10) Fix policy is defensible; “before vs after” check is included

Communication quality (20)
--------------------------

- (10) Executive memo is clear, concise, and decision-oriented
- (10) Writing uses plain language, defines terms, and avoids jargon where possible

Extensions (optional)
=====================

If you want to stretch advanced students, ask for one extra artifact:

- a small table (CSV) that summarizes totals by month (or by account)

But the core labs above are intentionally minimal so students can complete them quickly.

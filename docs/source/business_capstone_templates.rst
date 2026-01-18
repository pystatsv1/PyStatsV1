Capstone templates
==================

Use these templates to keep your capstone deliverables consistent and easy to review.
They are intentionally "accountant-friendly": short, structured, and focused on audit trail.

If you used the Track D scripts, you can attach their artifacts from
``outputs/track_d`` as supporting evidence.

1) Close & Controls Pack templates
----------------------------------

Bank reconciliation (summary)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   Bank reconciliation — [Bank name] — [Period end]

   Ending bank statement balance:      $__________
   Add: deposits in transit:           $__________
   Less: outstanding cheques:          ($_________)
   Less: bank fees/interest not posted ($_________)
   Adjusted bank balance:              $__________

   Ending book cash balance:           $__________
   Add/Less: corrections posted:       $__________
   Adjusted book balance:              $__________

   Difference (should be 0):           $__________

AR tie-out checklist
^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   AR tie-out checklist
   [ ] AR subledger total equals AR control account
   [ ] Aging report dated as-of period end
   [ ] Credit memos and returns reviewed
   [ ] Cutoff: last week invoices vs shipments checked
   [ ] Top 10 balances confirmed or reviewed

AP tie-out checklist
^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   AP tie-out checklist
   [ ] AP subledger total equals AP control account
   [ ] Vendor statements reviewed (top vendors)
   [ ] Cutoff: receiving reports vs invoices checked
   [ ] Duplicate payments scan performed
   [ ] Accruals documented (payroll, taxes, utilities)

Corrections log (minimum)
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   timestamp,issue_type,source_table,record_id,proposed_fix,posted_fix,reviewer,notes
   2026-12-31,duplicate,gl_txns,1234,"remove duplicate row","removed",TA,"duplicate import"

Exception report (minimum)
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   check_name,status,records_flagged,threshold,who_reviewed,notes
   duplicate_txn_scan,ok,0,>0,TA,
   negative_inventory,flag,3,>0,TA,"investigate stocking + COGS timing"
   unusual_margin_swing,flag,1,>10pp,TA,"promo month likely"

2) Analysis-ready Dataset templates
-----------------------------------

Tidy GL table (recommended schema)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   Columns (tidy):
   * txn_id
   * txn_date (YYYY-MM-DD)
   * account_name
   * account_type (Asset/Liability/Equity/Revenue/Expense)
   * department (optional)
   * memo (optional)
   * debit
   * credit
   * amount (signed; optional)
   * source (bank/qbo/manual)

Data dictionary (minimum)
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   table_name,column_name,type,definition,allowed_values,source
   gl_txns,txn_date,date,Transaction date,,qbo export
   gl_txns,account_name,string,Chart of accounts name,,qbo export
   gl_txns,debit,float,Debit amount,>=0,qbo export

Assumptions log
^^^^^^^^^^^^^^^

.. code-block:: text

   assumption_id,description,value,units,why_it_matters,owner,created_at,expires_at,notes
   A001,"AR collection lag",28,days,"drives cash receipts timing",Analyst,2026-01-01,2026-06-30,"based on last 6 months"

3) Performance analysis templates
---------------------------------

Variance drivers worksheet
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   metric,period_a,period_b,delta,primary_driver,evidence,next_check
   gross_margin,0.41,0.36,-0.05,"discounting",promo calendar + unit prices,review pricing strategy

Regression / driver model write-up (short)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   Model purpose:
   - What decision or forecast input is this model supporting?

   Variables:
   - Outcome: __________________________
   - Predictors: ________________________

   Interpretation (no causal over-claiming):
   - "Holding other predictors constant, a 1-unit change in X is associated with..."

   Diagnostics:
   - [ ] residual pattern checked
   - [ ] outliers / one-offs reviewed
   - [ ] stability across time checked

4) Forecast Pack templates
--------------------------

12-month rolling forecast (structure)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   Forecast pack should include:
   * A baseline forecast (simple, explainable)
   * At least 3 scenarios (base / downside / upside)
   * A backtest summary (recent months)
   * Assumptions log (what changed, why)
   * Reconciliation check: P&L, BS, and cash tie-out consistent

13-week cash forecast (direct method)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   scenario,week_start,begin_cash,cash_in,cash_out,net_change,end_cash,buffer_breach,notes
   base,2026-01-06,25000,18000,21000,-3000,22000,False,

Backtest summary (minimum)
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   metric,window,mae,mape,notes
   revenue,6_months,12000,0.08,"baseline seasonal naive"

Scenario summary (one page)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   Scenarios
   - Base: key assumptions...
   - Downside: what changes (volume, margin, collections, costs)...
   - Upside: what changes...

   Stress tests (binary events)
   - Supplier delay (inventory + sales impact)
   - Collections slowdown (AR days)
   - Payroll shock (hiring or overtime)

5) Decision memo template
-------------------------

CFO-style recommendation memo (1–2 pages)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   Title: North Shore Outfitters — Recommendation for [Period]

   Executive summary (5–7 sentences)
   - What is happening?
   - What do we recommend?
   - What impact range do we expect?

   Situation snapshot (bullets)
   - Revenue: ________ (trend + key driver)
   - Margin: ________ (what moved)
   - Cash: ________ (13-week outlook + buffer risk)

   Recommendation (actions)
   1) Action: ____________________
      Expected impact: ____________ (range)
      Risks: ______________________
      Owner: ______________________
      First check-in: ______________

   Monitoring plan (KPIs)
   - KPI 1: ________ (thresholds + cadence)
   - KPI 2: ________

   Assumptions and limitations
   - Top 3 assumptions that could change the conclusion

KPI dictionary (minimum)
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   kpi_name,definition,formula,source_table,source_columns,owner_role,update_cadence,threshold_green,threshold_yellow,threshold_red,notes
   Gross margin,"(Revenue-COGS)/Revenue","(rev-cogs)/rev",statements_is_monthly,"Sales Revenue;Cost of Goods Sold",FP&A,Monthly,>0.40,0.35-0.40,<0.35,"promo months expected"

Dashboard spec (minimum)
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   view_name,kpi_name,chart_type,grain,filters,owner_role,refresh_cadence,notes
   exec_summary,Gross margin,line,monthly,"scenario",FP&A,Monthly,

Red-team checklist
^^^^^^^^^^^^^^^^^^

.. code-block:: text

   Red-team checklist
   [ ] Numbers tie out: P&L, BS, and cash are consistent
   [ ] One-offs identified and labeled
   [ ] No causal claims without a design
   [ ] Units and signs checked (cash in vs cash out)
   [ ] Assumptions log updated and owned
   [ ] Risk monitoring plan has thresholds + owners

Glossary (draft)
================

This is a student-friendly glossary for Track D. Keep definitions short, practical, and tied to what you see in the PyStatsV1 outputs.

Accounting terms
----------------

- **Account**: A labeled bucket that records a type of financial activity (e.g., Cash, Sales, Rent Expense).
- **Chart of accounts (COA)**: The full list of accounts a business uses, usually grouped into Assets, Liabilities, Equity, Revenue, Expenses.
- **Account type**: A label like Asset/Liability/Equity/Revenue/Expense that helps classify accounts for reporting and analysis.
- **Debit / credit**: The two-sided bookkeeping convention used to keep entries balanced. In Track D, the scripts handle the analysis sign convention; when unsure, check the chapter page or the output summaries for “positive means what?”.
- **Journal entry**: A dated record of debits/credits for one event (it should balance to zero when summed).
- **Posting**: One line within a journal entry (one account + amount). A single entry usually has 2+ postings.
- **General ledger (GL)**: The journal entries viewed “by account over time” (a database-like history, not a formatted report).
- **Transaction vs posting**: A *transaction* is the whole event; *postings* are the individual lines inside it. Analytics often works on postings, then aggregates back up.
- **Trial balance (TB)**: A snapshot of balances by account at a point in time; the starting point for building statements.
- **Financial statements**: Summaries built from the trial balance using classifications (Income Statement / Balance Sheet / Cash Flow).
- **Balance**: The net total in an account after combining debits and credits over a period.
- **Opening balance / beginning balance**: The starting balance at the beginning of a period.
- **Accrual vs cash basis**: The timing rule for when revenue/expense is recorded (earned/incurred vs when cash moves).
- **Accounts receivable (AR)**: Money customers owe you (an asset). **Accounts payable (AP)** is money you owe suppliers (a liability).
- **Revenue (sales)**: Money earned from customers for goods/services. Often recorded before cash is received (accrual).
- **Expense**: Costs incurred to run the business (rent, wages, utilities). Often recorded before cash is paid (accrual).
- **COGS (cost of goods sold)**: Direct costs tied to producing/selling products; used to compute gross margin.
- **Gross margin**: Revenue minus COGS (often shown as dollars and as a % of revenue).
- **Depreciation**: Allocating an asset’s cost over time (a non-cash expense).
- **Reconciliation**: A check that two “views” of the world agree (e.g., bank statement vs cash ledger).
- **Materiality**: A practical threshold for “big enough to matter.” Helps decide what to investigate first.

Analytics terms
---------------

- **Observation / row**: One record in a table (e.g., one posting, one invoice, one daily total).
- **Metric**: A number you track (daily revenue proxy, monthly payroll total, cash balance).
- **Aggregation**: Summarizing many rows into totals by day/month/category (the main move in Track D).
- **Grouping key**: The fields you aggregate by (date, month, account, department, customer segment).
- **Tidy data**: A table where each row is one observation and each column is one variable (easy to filter, group, and plot).
- **Time series**: A metric tracked over time (daily revenue proxy, monthly expenses, weekly cash balance).
- **Baseline**: A simple comparison point (last month, last year, moving average, seasonal naive).
- **Variance**: A change between two periods or scenarios (this month vs last month; actual vs budget).
- **Driver**: The category/account that explains most of a variance (the “why” behind the change).
- **Decomposition**: Breaking a total change into parts (e.g., which accounts explain revenue growth).
- **KPI**: A key performance indicator (e.g., gross margin %, days-to-pay, cash coverage).
- **Distribution**: The spread of values (helpful for typical vs unusual transactions).
- **Outlier**: A value that is unusual relative to typical observations (not automatically an error).
- **Seasonality**: Predictable repeating patterns over time (holidays, summer sales, payroll cycles).
- **Structural break**: A real change in how the business operates that makes “past ≈ future” less reliable.
- **Backtest**: Testing a forecasting method on past data (train earlier, test later).
- **Error metric**: A summary of forecast accuracy (e.g., MAE/MAPE). Lower is usually better, but context matters.

Track D + BYOD terms
--------------------

- **Track D**: The “big picture” track: statistics on accounting data, using reproducible scripts and artifacts.
- **Workflow loop**: Export → normalize → validate → analyze → communicate (repeat this across chapters and BYOD projects).
- **Dataset contract**: The required table names + column headers + meanings that scripts assume.
- **Canonical dataset**: A known-good demo dataset shipped with the workbook (used for learning and expected outputs).
- **Source export**: A CSV export from your accounting system (often messy and source-specific).
- **BYOD (Bring Your Own Data)**: Using your own accounting exports instead of the canonical demos.
- **BYOD project folder**: A reproducible folder created by ``pystatsv1 trackd byod init`` (contains ``config.toml``, ``tables/``, and outputs).
- **config.toml**: The project’s settings file (profile + adapter + any source-specific knobs).
- **tables/**: Where you place *raw exports* (source-specific CSVs).
- **Adapter**: Code that converts a source export into the Track D contract (repeatable + testable cleanup).
- **Normalize / normalization**: Running ``pystatsv1 trackd byod normalize`` to produce canonical outputs under ``normalized/``.
- **normalized/**: Canonical tables produced by normalization (typically ``normalized/gl_journal.csv`` and ``normalized/chart_of_accounts.csv``).
- **Schema**: The expected columns + types for a table (what must exist for scripts to run correctly).
- **Validate**: A fast schema + sanity check that catches missing columns, bad types, and common structural problems.
- **Daily totals**: A first analysis-ready time series derived from ``normalized/gl_journal.csv`` (often written to ``normalized/daily_totals.csv``).
- **Profile**: A preset that defines which tables/columns are required for a workflow (e.g., ``core_gl``).
- **Artifacts**: The outputs created by scripts (tidy CSVs, figures, JSON summaries, short memos) under ``outputs/track_d/``.
- **Reproducible**: Someone else can rerun your project and get the same tables/figures (given the same inputs).

.. note::

   Keep this glossary short and student-friendly. If you add a new term, prefer a one-sentence definition plus one concrete example.
   If anything conflicts with the CLI or outputs, the docs and ``--help`` should be updated to match what the code actually does.

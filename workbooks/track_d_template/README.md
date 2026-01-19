# PyStatsV1 Track D Workbook Starter (Business Statistics)

This folder is a **Track D-only workbook** built around an accounting running case.
It is designed for students to:

- run a chapter script
- inspect outputs under `outputs/track_d/`
- repeat with confidence (datasets are deterministic with seed=123)

It works on Linux, macOS, and Windows, and it does **not** require `make`.

## 0) Setup

Create and activate a virtual environment, then install PyStatsV1:

```bash
python -m pip install -U pip
python -m pip install "pystatsv1[workbook]"

# pytest is included via the [workbook] extra
```

## 1) Create this workbook

If you already have this folder, you can skip this.

```bash
pystatsv1 workbook init --track d --dest pystatsv1_track_d
cd pystatsv1_track_d
```

## 2) Peek at the data (recommended)

```bash
pystatsv1 workbook run d00_peek_data
```

That script looks for the two Track D datasets under:

- `data/synthetic/ledgerlab_ch01/`
- `data/synthetic/nso_v1/`

and writes a friendly summary to:

- `outputs/track_d/d00_peek_data_summary.md`

## 3) Reset the datasets (optional)

If you ever delete/edit files under `data/synthetic/`, you can regenerate them.
This keeps the default **seed=123** (same values as the canonical datasets).

```bash
pystatsv1 workbook run d00_setup_data
# or (clean reset)
pystatsv1 workbook run d00_setup_data --force
```

## 4) Run a Track D chapter

First, see the available Track D chapters:

```bash
pystatsv1 workbook list --track d
```

Then run a chapter using the short wrapper names `d01` ... `d23`.
For example:

```bash
pystatsv1 workbook run d01
pystatsv1 workbook run d14
pystatsv1 workbook run d23
```

You can also run the full script names directly (same result):

```bash
pystatsv1 workbook run business_ch01_accounting_measurement
pystatsv1 workbook run business_ch14_regression_driver_analysis
```

## 5) Check your environment (smoke test)

```bash
pystatsv1 workbook check business_smoke
```

If you ever get stuck, see the PyStatsV1 docs on ReadTheDocs.

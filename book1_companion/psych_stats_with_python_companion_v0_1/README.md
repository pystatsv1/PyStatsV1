# Psych Stats with Python — Executable Companion v0.1

This is the versioned companion bundle for *Psych Stats with Python: A Student
Guide to t-Tests, ANOVA, Correlation, Regression, APA-Style Results, and
Optional R Checks.* It uses **synthetic data only**.

**Python for the workflow. R for verification. PyStatsV1 for the bridge.**

The bundle covers the exact Book 1 analyses:

- `ch05`: Welch independent-samples t-test;
- `ch06`: paired-samples t-test;
- `ch07`: one-way ANOVA;
- `ch08`: two-way factorial ANOVA;
- `ch09`: repeated-measures ANOVA;
- `ch10`: Pearson correlation;
- `ch11`: simple linear regression;
- `ch12`: APA-reporting source-map audit.

## What is included

Each chapter directory under `outputs/` receives:

- `py_results.json` from the runnable Python analysis;
- `r_results.json` from the matching optional base-R analysis;
- `parity_receipt.md`, which compares the reportable numeric fields;
- for Chapter 12, `apa_reporting_source_map.json` and
  `apa_reporting_audit.json` linking each book APA sentence to its exact
  synthetic Python result file and hash.

The Python scripts use transparent `numpy`, `scipy`, and `statsmodels`
calculations. The installed PyStatsV1 version is recorded in every Python JSON
result as an environment bridge; this does **not** claim that PyStatsV1 itself
is a hidden analysis engine for these lessons. The matching base-R scripts
make the reported claims independently checkable. PyStatsV1 is not a hidden analysis engine.

In Companion v0.1, the bridge is intentionally limited and visible: PyStatsV1 identifies the versioned Python learning environment in result metadata. The local companion scripts write the JSON receipts and source-map files; `pandas`, NumPy, SciPy, and statsmodels perform the named calculations. PyStatsV1 does not silently choose a test, filter rows, or turn an observed pattern into a causal conclusion.

## Run the full proof

From this bundle's root on Ubuntu:

```bash
python3 -m pip install -r requirements-book1-companion.txt
make all
```

`make all` requires `Rscript` because a parity receipt is a real cross-tool
check, not a placeholder. For a Python-only preparation pass use:

```bash
make python-only
```

That preparation pass intentionally does **not** claim completed R parity.

## Verify the downloaded archive

The companion ZIP is distributed with a matching SHA-256 sidecar. Use the
repository verification helper rather than `sha256sum -c` directly: the helper
accepts explicit paths, so it works both from the repository root and from any
download folder.

From the repository root after a local companion build:

```bash
python3 scripts/verify_book1_companion_checksum.py \
  --zip portal/downloads/psych-stats-with-python-companion-v0.1.zip \
  --sha256 portal/downloads/psych-stats-with-python-companion-v0.1.zip.sha256
```

For files downloaded to the usual Ubuntu Downloads folder, run the same helper
from a local project checkout:

```bash
python3 scripts/verify_book1_companion_checksum.py \
  --zip "$HOME/Downloads/psych-stats-with-python-companion-v0.1.zip" \
  --sha256 "$HOME/Downloads/psych-stats-with-python-companion-v0.1.zip.sha256"
```

A successful verification prints:

```text
psych-stats-with-python-companion-v0.1.zip: OK
```

For the conventional Ubuntu downloaded-folder workflow, the sidecar also works
with `sha256sum -c` after changing into that folder:

```bash
cd "$HOME/Downloads"
sha256sum -c psych-stats-with-python-companion-v0.1.zip.sha256
```


## PyStatsV1 launcher

When this bundle is installed through PyStatsV1 v0.24.x or later, create a
local working copy with:

```bash
pystatsv1 book1 init
cd psych_stats_with_python_companion_v0_1
python3 -m pip install -r requirements-book1-companion.txt
make figures
make all
```

The launcher refuses to overwrite an existing destination. To verify the
source files that were extracted from the packaged asset, run:

```bash
pystatsv1 book1 verify --dest psych_stats_with_python_companion_v0_1
```

The verification command checks the source-data, scripts, specifications, and
reader files against the bundle manifest. It does not claim that a later
analysis output is correct without running the corresponding Python/R workflow.

## Private-data boundary

Do not put identifiable participant data, credentials, restricted exports, or
real coursework/thesis/lab files into this bundle or a public repository. The
book companion is a synthetic teaching workflow, not an automated real-data
analysis service and not a substitute for instructor, advisor, ethics, or
research judgment.

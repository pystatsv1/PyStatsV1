# Local R Verification Policy

## Purpose

GitHub-hosted Actions no longer install or execute R for this repository. The three
Psychological Statistics by Design parity batches and the current public Book 1
companion remain required checks, but they run on the maintainer's Ubuntu machine.
This prevents routine pull requests and pushes from consuming hosted-runner minutes
for repeated `apt-get` installation of R.

GitHub CI remains responsible for Python tests, lint, documentation, wheel smoke, and
source-integrity checks. It deliberately does not claim Python/R parity.

## Governed local environment

Use an isolated Python 3.10 environment because the SWL-S01/S06/S07 receipt identity
is bound to exact numerical-library versions.

```bash
cd "$HOME/projects/PyStatsV1"

sudo apt-get update
sudo apt-get install --yes r-base r-cran-nlme

python3.10 -m venv .venv-psych-design-r
.venv-psych-design-r/bin/python -m pip install --upgrade pip
.venv-psych-design-r/bin/python -m pip install -r requirements-dev.txt
.venv-psych-design-r/bin/python -m pip install \
  --constraint psych_design_companion/swl_s01_s06_s07_v0_1/requirements-psych-design-companion.txt \
  -r psych_design_companion/swl_s08_s10_v0_1/requirements-psych-design-companion.txt \
  -e .
.venv-psych-design-r/bin/python -m pip check
```

## Authoritative local gate

```bash
make \
  PYTHON="$PWD/.venv-psych-design-r/bin/python" \
  local-r-verify
```

The `PYTHON` value must remain the virtual-environment executable path. The local
runner converts relative paths to absolute paths but deliberately does **not** resolve the
virtual-environment `python` symlink to `/usr/bin/python3.10`; resolving that symlink
would bypass the governed environment and expose unrelated system package versions.

The gate verifies, in order:

1. SWL-S02 through SWL-S05 Python evidence and independent base-R parity;
2. the exact SWL-S01/S06/S07 Python environment, evidence, and R parity;
3. SWL-S08 through SWL-S10 evidence and R parity, including `nlme`;
4. the current Book 1 companion's design audit, Python outputs, R outputs, and parity.

The runtime receipt is written under the ignored path:

```text
build/local_r_verification/LOCAL_R_VERIFICATION_RECEIPT.json
```

Copy that receipt and the terminal log into the release or book handoff when the local
R gate is part of an acceptance decision. Do not commit renderer- or machine-specific
runtime receipts as permanent source identity.

## GitHub boundary

The files formerly named:

```text
.github/workflows/psych-design-swl-first-batch-r-verify.yml
.github/workflows/psych-design-swl-second-batch-r-verify.yml
.github/workflows/psych-design-swl-final-batch-r-verify.yml
```

are retired. No workflow under `.github/workflows/` may install `r-base`, invoke
`Rscript`, or call a `*-r-verify` Make target. The retained Book 1 GitHub smoke test is
Python-only; full Book 1 Python/R parity is included in the local gate above.

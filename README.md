# PyStatsV1 — Applied Statistics (R ↔ Python)

Plain Python scripts that mirror R recipes so non-specialists can run analyses from the command line,
save figures/tables, and compare results across R/Python.

## Quick start
# macOS/Linux
python -m venv .venv && source .venv/bin/activate
python -m pip install -U pip
pip install -r requirements.txt

# Windows (Git Bash or PowerShell)
python -m venv .venv; source .venv/Scripts/activate 2>/dev/null || .venv\\Scripts\\Activate.ps1
python -m pip install -U pip
pip install -r requirements.txt

# Example
python scripts/ch01_introduction.py

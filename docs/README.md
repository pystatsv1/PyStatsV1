# PyStatsV1 Docs


- Chapter 12 — Diagnostics  
  - `scripts/ch12_diagnostics.py`
- Chapter 13 — Within-Subject Stroop  
  - Data: `data/synthetic/psych_stroop_*`  
  - Run: `scripts/sim_stroop.py`, `scripts/ch13_stroop_within.py --save-plots`
- Chapter 13 — Fitness 2×2 Mixed (this chapter)  
  - Data: `data/synthetic/fitness_*`  
  - Run: `scripts/sim_fitness_2x2.py`, `scripts/ch13_fitness_mixed.py --save-plots`



[![ci](https://img.shields.io/github/actions/workflow/status/PyStatsV1/PyStatsV1/ci.yml?branch=main)](https://github.com/PyStatsV1/PyStatsV1/actions/workflows/ci.yml)
[![release](https://img.shields.io/github/v/tag/PyStatsV1/PyStatsV1?label=release)](https://github.com/PyStatsV1/PyStatsV1/tags)

Plain Python scripts that mirror R recipes so non-specialists can run analyses from the command line, save figures/tables, and compare results across R/Python.

---

## Quick start

### macOS / Linux
```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install -U pip
pip install -r requirements.txt
```

### Windows (Git Bash or PowerShell)
```bash
# Try Git Bash first; if that fails, PowerShell will activate the venv
python -m venv .venv; source .venv/Scripts/activate 2>/dev/null || .venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -r requirements.txt
```

---

## Example
Run the Chapter 1 example:
```bash
python scripts/ch01_introduction.py
```

### Chapter 13 quick smoke (fast)
```bash
make ch13-ci
```
This generates tiny synthetic datasets and saves a couple of plots to `outputs/`.

Full chapter run:
```bash
make ch13
```

See **[docs/README.md](docs/README.md)** for chapter notes, commands, and links.

---

## License

MIT © 2025 Nicholas Elliott Karlson
# PyStatsV1 — Applied Statistics (R ↔ Python)

[![ci](https://img.shields.io/github/actions/workflow/status/nicholaskarlson/PyStatsV1/ci.yml?branch=main)](https://github.com/nicholaskarlson/PyStatsV1/actions/workflows/ci.yml)
[![release](https://img.shields.io/github/v/tag/nicholaskarlson/PyStatsV1?label=release)](https://github.com/nicholaskarlson/PyStatsV1/tags)

PyStatsV1 provides **plain, transparent Python scripts** that mirror classical **R textbook analyses**, making it easy for students, tutors, and practitioners to:

- run statistical analyses from the command line,  
- generate synthetic data for teaching,  
- produce figures and JSON summaries,  
- and compare outputs across R/Python.

The project follows a **chapter-based structure**—each chapter includes a simulator + analyzer + Makefile targets + CI smoke tests.

---

## 🚀 Quick Start

### 1. Create and activate a virtual environment

**macOS / Linux**
```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install -U pip
pip install -r requirements.txt
```

**Windows (Git Bash or PowerShell)**
```bash
# Git Bash first; PowerShell as fallback
python -m venv .venv; source .venv/Scripts/activate 2>/dev/null || .venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -r requirements.txt
```

---

## 📊 Chapter Scripts

### Chapter 1 (intro)
```bash
python -m scripts.ch01_introduction
```

### Chapter 13 — Within-subjects & Mixed Models
```bash
make ch13-ci   # tiny CI smoke
make ch13      # full demo
```

### Chapter 14 — Tutoring A/B Test (two-sample t-test)
```bash
make ch14-ci
make ch14
```

### Chapter 15 — Reliability (Cronbach α + ICC + Bland–Altman)
```bash
make ch15-ci
make ch15
```

For an overview of what each chapter contains:

- **[CHAPTERS.md](CHAPTERS.md)** — coverage, commands, and outputs  
- **[ROADMAP.md](ROADMAP.md)** — planned chapters (e.g., Ch16 Epidemiology RR)

---

## 📚 Project Docs & Policies

PyStatsV1 is structured with a core set of documentation:

- **[CONTRIBUTING.md](CONTRIBUTING.md)** — environment setup, development workflow, Makefile usage, PR process.
- **[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)** — community expectations & enforcement.
- **[CHAPTERS.md](CHAPTERS.md)** — high-level description of all implemented chapters.
- **[ROADMAP.md](ROADMAP.md)** — the future of the project: upcoming chapters & milestones.
- **[SECURITY.md](SECURITY.md)** — how to privately report vulnerabilities.
- **[SUPPORT.md](SUPPORT.md)** — how to get help or ask questions.
- **Case Study Template:** [`docs/case_study_template.md`](docs/case_study_template.md) — structure for building new chapter teaching documentation.

If you want to contribute, start with **[CONTRIBUTING.md](CONTRIBUTING.md)** and check issues labeled  
`good first issue` or `help wanted`.

---

## 🧪 Development Workflow

From the project root:

```bash
make lint    # ruff check
make test    # pytest
```

To run chapter smoke tests:

```bash
make ch13-ci
make ch14-ci
make ch15-ci
```

All synthetic data is written to:

- `data/synthetic/`  
- `outputs/<chapter>/`

…and ignored by Git.

---

## 🔀 Pull Requests

Every pull request must:

- pass `make lint` and `make test`,
- avoid committing generated outputs,
- follow the structure described in **CONTRIBUTING.md**.

GitHub provides:

- 🐛 Bug report template  
- 💡 Feature request template  
- 📘 Good first issue template  
- 🔀 Pull request template  

---

## 🔒 Security

If you believe you’ve found a security issue, **do not** open a public GitHub issue.  
Follow the private disclosure process described in **[SECURITY.md](SECURITY.md)**.

---

## 📜 License

MIT © 2025 Nicholas Elliott Karlson

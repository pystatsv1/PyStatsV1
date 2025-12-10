# PyStatsV1 — Applied Statistics (R ↔ Python)

[![CI](https://img.shields.io/github/actions/workflow/status/pystatsv1/PyStatsV1/ci.yml?branch=main&label=ci&color=brightgreen)](https://github.com/pystatsv1/PyStatsV1/actions/workflows/ci.yml)
[![GitHub release](https://img.shields.io/github/v/tag/pystatsv1/PyStatsV1?label=release&color=brightgreen)](https://github.com/pystatsv1/PyStatsV1/tags)
[![Docs](https://readthedocs.org/projects/pystatsv1/badge/?version=latest)](https://pystatsv1.readthedocs.io/en/latest/?badge=latest)
[![PyPI - Version](https://img.shields.io/pypi/v/pystatsv1.svg?label=pypi&color=brightgreen)](https://pypi.org/project/pystatsv1/)
[![Python version](https://img.shields.io/badge/python-3.10%2B-brightgreen)](https://pypi.org/project/pystatsv1/)

PyStatsV1 provides **plain, transparent Python scripts** that mirror classical **R textbook analyses**, making it easy for students, tutors, and practitioners to:

- run statistical analyses from the command line,
- generate synthetic data for teaching,
- produce figures and JSON summaries,
- and compare outputs across R/Python.

## 📦 Install

The simplest way to get started is from [PyPI](https://pypi.org/project/pystatsv1/):

```bash
pip install pystatsv1
```

This installs the lightweight pystatsv1 helper package used by the labs (for example, the shared paths utilities).

If you want the full chapter-by-chapter repository with simulators, Makefiles, tests, and docs, clone from GitHub and install in editable mode:

```bash
git clone https://github.com/pystatsv1/PyStatsV1.git
cd PyStatsV1
pip install -e .
```


## Quick start (PyPI + local PDF docs)

You **do not** need Git or GitHub to start using PyStatsV1.

```bash
python -m venv pystatsv1-env
source pystatsv1-env/Scripts/activate  # Windows (Git Bash)
# source pystatsv1-env/bin/activate    # macOS/Linux

pip install pystatsv1
```

Then, inside Python:

```bash
import pystatsv1
# Open the bundled PDF version of the documentation:
pystatsv1.open_local_docs()
```

This will open a local PDF copy of the ReadTheDocs site in your default PDF viewer.
You can also just get the path:

```bash
from pystatsv1 import get_local_docs_path
print(get_local_docs_path())
```

Example Using Git Bash on Windows 11 (after creating folder Test-v2-PyStatsV1 in the folder Python in the Videos folder and then opening the folder Test-v2-PyStatsV1 in GitBash and then enter and run commands at the command prompt which is denoted by the dollar-sign symbol $)

```bash
nicho@Victus-HP-2024 MINGW64 ~/Videos/Python/Test-v2-PyStatsV1
$ python -m venv pystatsv1-smoketest
source pystatsv1-smoketest/Scripts/activate  
pip install --upgrade pip
pip install pystatsv1

nicho@Victus-HP-2024 MINGW64 ~/Videos/Python/Test-v2-PyStatsV1
$ python -c "import pystatsv1; print(pystatsv1.get_local_docs_path())"
python -c "import pystatsv1; pystatsv1.open_local_docs()"
C:\Users\nicho\Videos\Python\Test-v2-PyStatsV1\pystatsv1-smoketest\lib\site-packages\pystatsv1\docs\pystatsv1.pdf
(pystatsv1-smoketest)
nicho@Victus-HP-2024 MINGW64 ~/Videos/Python/Test-v2-PyStatsV1
```

## Project Structure

The project follows a **chapter-based structure** — each chapter includes a simulator, an analyzer, Makefile targets, and CI smoke tests.

### Who is this for?

PyStatsV1 is designed for:

- **Students** who want to run textbook-style analyses in real Python code.
- **Instructors / TAs** who need reproducible demos and synthetic data for lectures, labs, or assignments.
- **Practitioners** who prefer plain scripts and command-line tools over large frameworks.
- **R users** who want a clear, line-by-line bridge from R examples into Python.

---

## 🚀 Using a Virtual Environment

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

### Chapter 1 — Introduction

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

### Chapter 15 — Reliability (Cronbach’s α, ICC, Bland–Altman)

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

## 🤝 Contribute in 5 minutes

Want to help but not sure where to start?

1. **Browse issues** labeled `good first issue` or `help wanted`.
2. **Pick one small thing** (typo, doc improvement, tiny refactor, or a missing test).
3. **Fork & clone** the repo.
4. **Create and activate a virtual environment**, then:

   ```bash
   pip install -r requirements.txt
   make lint
   make test
   ```

5. Make your change, and ensure `make lint` and `make test` both pass.
6. Open a Pull Request and briefly describe:
   - what you changed,
   - how you tested it,
   - which chapter(s) it touches, if any.

Maintainer promise: we’ll give constructive feedback and help first-time contributors land their PRs.

---

## 🗺️ Roadmap snapshot

High-level upcoming work (see `ROADMAP.md` for details):

- ✅ v0.17.0 — Onboarding and issue templates
- ⏳ Next steps:
  - Additional regression chapters (logistic, Poisson, etc.)
  - Power and sample size simulations
  - Epidemiology-focused examples (risk ratios, odds ratios)
  - More teaching case studies using `docs/case_study_template.md`

If you’d like to champion a specific chapter or topic, open an issue and we can design it together.

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

Every pull request should:

- pass `make lint` and `make test`,
- avoid committing generated outputs,
- follow the structure described in **[CONTRIBUTING.md](CONTRIBUTING.md)**.

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

## 💬 Community & support

- **Questions?**  
  Open a GitHub issue with the `question` label.

- **Using PyStatsV1 in a course?**  
  We’d love to hear about it — open an issue titled `Course report: <institution>` or mention it in your PR description.

- **Feature ideas / chapter requests?**  
  Open an issue with the `enhancement` or `chapter-idea` label.

As the project grows, we plan to enable GitHub Discussions and possibly a lightweight chat space for instructors and contributors.

---

## 📜 License

MIT © 2025 Nicholas Elliott Karlson

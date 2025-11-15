---
name: "🚀 Start Here: Project Overview"
about: "Pinned welcome issue that orients new contributors to PyStatsV1"
title: "Start here: Welcome to PyStatsV1 (v0.17.0)"
labels: ["documentation", "meta"]
assignees: []
---

# Start here: Welcome to PyStatsV1 (v0.17.0) 🎓📊

Welcome! PyStatsV1 is an open-source project that ports applied statistics case studies
(from an R-based textbook) into modern **Python** scripts and reproducible workflows.

The goal: give students and instructors **working, well-documented examples** they can
clone, run with `make`, and adapt to their own teaching and learning.

---

## 🔍 What’s in the repo?

PyStatsV1 currently includes:

### **Chapter 13 — Experimental Designs**
- Stroop within-subject reaction-time study  
- 2×2 fitness mixed-design study (mixed effects)

### **Chapter 14 — Classic A/B Test**
- Tutoring study with two-sample **t-test**
- Simulator + analyzer with reproducible workflow

### **Chapter 15 — Reliability & Psychometrics**
- **Cronbach’s alpha** for survey internal consistency  
- **Intraclass correlation (ICC)** for test–retest reliability  
- **Bland–Altman plot** for agreement  

See:

- 📄 **[CHAPTERS.md](CHAPTERS.md)** — chapter-by-chapter catalog  
- 🗺 **[ROADMAP.md](ROADMAP.md)** — future chapters & milestones  

---

## 🧰 How to run things locally

Requirements:
- Python 3.10+
- `git`
- Recommended: VS Code, PyCharm, or any editor

Clone and set up:

```bash
git clone git@github.com:pystatsv1/PyStatsV1.git
cd PyStatsV1
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

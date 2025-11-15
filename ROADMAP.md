# ROADMAP.md — PyStatsV1 Development Roadmap

This roadmap describes the planned evolution of PyStatsV1 from v0.17 through v1.0.  
It is intentionally modular, so contributors can pick up self‑contained tasks.

---

# 🌱 **v0.17.0 — Onboarding & First Issues (CURRENT MILESTONE)**

### Goals:
- Add full onboarding:
  - `CONTRIBUTING.md`
  - `CODE_OF_CONDUCT.md`
  - `SECURITY.md`
  - `SUPPORT.md`
  - Issue + PR templates
- Add documentation index (`CHAPTERS.md`, `ROADMAP.md`)
- Publish first “Good First Issues”

### New contributor‑friendly tasks:
- Ch14 “Explain Mode”
- Ch15 additional reliability metrics
- Epidemiology RR‑with‑strata simulator + analyzer skeleton

Status: **🔵 In progress**

---

# 🌿 **v0.18.0 — Explainable Statistics**

### Goals:
- Add “Explain Mode” to existing chapters:
  - Step‑by‑step t-test calculations
  - Show algebra behind Cronbach’s Alpha
  - Show ICC derivation table
- Add optional verbose tracing mode across scripts

Status: **🟡 Planned**

---

# 🌾 **v0.19.0 — Epidemiology & Risk Ratios**

### New case study:
**“Risk Ratio With Stratification”**

Includes:
- Simulator for a 2×K strata study (e.g., gender, age groups)
- Analyzer computing:
  - Crude RR
  - Mantel–Haenszel pooled RR
  - Confidence intervals
  - Optional Woolf test for homogeneity
- Visualizations (forest plot)

Status: **🟡 Planned**

---

# 🌾 **v0.20.0 — Power & Sample Size Tools**

Add utilities such as:
- Power for two‑sample t-test  
- Power for paired design  
- Confidence interval planning  
- Monte‑Carlo power exploration

Status: **🟡 Planned**

---

# 🌾 **v0.21.0 — Regression & Model Diagnostics**

Case studies:
- Linear regression  
- Residual analysis  
- Influential points  
- Model comparison  
- Bootstrapped intervals

Status: **🟡 Planned**

---

# 🌻 **v0.22.0 — GLMs & Count Data**

Case study modules:
- Poisson regression  
- Negative binomial  
- Logistic regression  
- Overdispersion diagnostics

Status: **🟡 Planned**

---

# 🌻 **v0.23.0 — Bayesian Mirrors**

Re‑implement selected chapters using:
- PyMC
- Bambi

Focus:
- Bayesian equivalents of Ch14 + Ch15  
- Posterior predictive checks  
- Visualization of priors and posteriors

Status: **🔵 Exploration**

---

# 🌞 **v1.0.0 — Stable Educational Release**

Criteria:
- Fully documented (tutorial + examples)
- CI‑green on Windows & Linux
- Reproducible simulations
- All chapters pass Lint, Test, Smoke
- Clear contributor pathways
- Zero known major issues

---

If you'd like to contribute to any milestone, visit:  
👉 **Issues:** https://github.com/PyStatsV1/PyStatsV1/issues  
👉 **Contributing Guide:** [CONTRIBUTING.md](CONTRIBUTING.md)

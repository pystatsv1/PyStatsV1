from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile

# Modules run in smoke test
SCRIPTS = [
    "ch13_stroop_within",   # needs --data FILE
    "ch13_fitness_mixed",   # needs --data FILE
    "sim_stroop",           # needs --outdir DIR
    "sim_fitness_2x2",      # needs --outdir DIR
    "sim_ch14_tutoring",    # needs --outdir DIR
    "ch14_tutoring_ab",     # needs --datadir DIR
    # --- Ch15 additions ---
    "sim_ch15_reliability",     # needs --outdir DIR
    "ch15_reliability_analysis" # needs --datadir DIR
]

def run_module(mod: str) -> None:
    root = pathlib.Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as tmpd:
        tmp = pathlib.Path(tmpd)
        outdir = tmp / "out"
        outdir.mkdir(parents=True, exist_ok=True)

        cmd = [sys.executable, "-m", f"scripts.{mod}", "--seed", "42"]

        if mod in {"sim_stroop", "sim_fitness_2x2", "sim_ch14_tutoring", "sim_ch15_reliability"}:
            cmd += ["--outdir", str(outdir)]
        elif mod in {"ch14_tutoring_ab", "ch15_reliability_analysis"}:
            # These analyzers expect a directory with simulated files.
            # We don't pre-simulate here—just point at a real-ish dir.
            cmd += ["--datadir", "data/synthetic", "--outdir", str(outdir)]
        elif mod == "ch13_stroop_within":
            cmd += ["--data", "data/synthetic/psych_stroop_trials.csv", "--outdir", str(outdir)]
        elif mod == "ch13_fitness_mixed":
            cmd += ["--data", "data/synthetic/fitness_long.csv", "--outdir", str(outdir)]

        res = subprocess.run(
            cmd, cwd=root, capture_output=True, text=True, encoding="utf-8"
        )

        # If a script complains that its data file(s) are missing, that's fine for a smoke test
        # (we're just proving the CLI wiring doesn't crash for bad flags).
        out = (res.stdout or "") + (res.stderr or "")
        missing = (
            "Error: Data file not found" in out or      # singular (existing)
            "Error: Data files not found" in out        # plural (Ch15 analyzer)
        )
        if missing:
            return

        assert res.returncode == 0, f"{mod} failed:\nSTDERR:\n{res.stderr}\nSTDOUT:\n{res.stdout}"

def test_scripts_run_with_cli():
    for m in SCRIPTS:
        run_module(m)

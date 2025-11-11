from __future__ import annotations
import pathlib, subprocess, sys, tempfile

SCRIPTS = ["ch13_stroop_within","ch13_fitness_mixed","sim_stroop","sim_fitness_2x2"]

def run_module(mod: str) -> None:
    root = pathlib.Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as tmpd:
        cmd = [sys.executable, "-m", f"scripts.{mod}", "--outdir", tmpd, "--seed", "42"]
        res = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
        assert res.returncode == 0, res.stderr or res.stdout

def test_scripts_run_with_cli():
    for m in SCRIPTS:
        run_module(m)
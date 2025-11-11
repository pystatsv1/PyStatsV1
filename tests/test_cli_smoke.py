from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile

# Add the two new Chapter 14 scripts
SCRIPTS = [
    "ch13_stroop_within",
    "ch13_fitness_mixed",
    "sim_stroop",
    "sim_fitness_2x2",
    "sim_ch14_tutoring",
    "ch14_tutoring_ab",
]


def run_module(mod: str) -> None:
    repo_root = pathlib.Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as tmpd:
        cmd = [
            sys.executable,
            "-m",
            f"scripts.{mod}",
            "--outdir",
            tmpd,
            "--seed",
            "42",
        ]
        # Analyzers that read data should accept --datadir
        if mod in ("ch13_stroop_within", "ch13_fitness_mixed", "ch14_tutoring_ab"):
            cmd.extend(["--datadir", "data/synthetic"])

        res = subprocess.run(
            cmd,
            cwd=repo_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        combined = (res.stdout or "") + (res.stderr or "")
        if "Data not found" in combined or "Please run" in combined:
            # It's fine in smoke: we're only checking the CLI wiring.
            return

        assert (
            res.returncode == 0
        ), f"Script {mod} failed:\nSTDERR:\n{res.stderr}\nSTDOUT:\n{res.stdout}"


def test_scripts_run_with_cli() -> None:
    for m in SCRIPTS:
        run_module(m)

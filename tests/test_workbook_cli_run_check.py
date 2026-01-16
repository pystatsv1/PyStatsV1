from __future__ import annotations

import subprocess
import sys
from argparse import Namespace
import os
from pathlib import Path

import pystatsv1.cli as cli


def test_workbook_run_invokes_python_script(tmp_path, monkeypatch):
    # Create a fresh workbook directory from the packaged starter.
    dest = tmp_path / "wb"
    cli._extract_workbook_template(dest=dest, force=False)

    calls: list[tuple[list[str], str, dict[str, str] | None]] = []

    def fake_run(cmd, cwd=None, check=False, env=None):
        calls.append((list(cmd), str(cwd), env))
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(cli.subprocess, "run", fake_run)

    rc = cli.cmd_workbook_run(Namespace(target="ch10", workdir=str(dest)))
    assert rc == 0

    assert calls, "expected subprocess.run to be called"
    cmd, cwd, env = calls[0]
    assert cmd[0] == sys.executable
    assert Path(cmd[1]) == dest / "scripts" / "psych_ch10_problem_set.py"
    assert cwd == str(dest)

    # `workbook run` should add the workbook root to PYTHONPATH so imports like
    # `from scripts...` work even when running a script file directly.
    assert env is not None
    assert "PYTHONPATH" in env
    assert str(dest) in env["PYTHONPATH"].split(os.pathsep)


def test_workbook_check_invokes_pytest_for_chapter(tmp_path, monkeypatch):
    dest = tmp_path / "wb"
    cli._extract_workbook_template(dest=dest, force=False)

    calls: list[tuple[list[str], str, dict[str, str] | None]] = []

    def fake_run(cmd, cwd=None, check=False, env=None):
        calls.append((list(cmd), str(cwd), env))
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(cli.subprocess, "run", fake_run)

    rc = cli.cmd_workbook_check(Namespace(target="ch10", workdir=str(dest)))
    assert rc == 0

    cmd, cwd, env = calls[0]
    assert cmd[:3] == [sys.executable, "-m", "pytest"]
    assert "-q" in cmd
    assert str(dest / "tests" / "test_psych_ch10_problem_set.py") in cmd
    assert cwd == str(dest)

    assert env is not None
    assert "PYTHONPATH" in env
    assert str(dest) in env["PYTHONPATH"].split(os.pathsep)


def test_workbook_run_missing_script_returns_2(tmp_path):
    dest = tmp_path / "wb"
    dest.mkdir()
    rc = cli.cmd_workbook_run(Namespace(target="ch10", workdir=str(dest)))
    assert rc == 2



def test_workbook_check_resolves_case_study_key(tmp_path, monkeypatch):
    dest = tmp_path / "wb"
    cli._extract_workbook_template(dest=dest, force=False)

    calls: list[tuple[list[str], str, dict[str, str] | None]] = []

    def fake_run(cmd, cwd=None, check=False, env=None):
        calls.append((list(cmd), str(cwd), env))
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(cli.subprocess, "run", fake_run)

    rc = cli.cmd_workbook_check(Namespace(target="study_habits", workdir=str(dest)))
    assert rc == 0

    cmd, _cwd, _env = calls[0]
    assert str(dest / "tests" / "test_study_habits_case_study.py") in cmd


def test_workbook_check_resolves_my_data_key(tmp_path, monkeypatch):
    dest = tmp_path / "wb"
    cli._extract_workbook_template(dest=dest, force=False)

    calls: list[tuple[list[str], str, dict[str, str] | None]] = []

    def fake_run(cmd, cwd=None, check=False, env=None):
        calls.append((list(cmd), str(cwd), env))
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(cli.subprocess, "run", fake_run)

    rc = cli.cmd_workbook_check(Namespace(target="my_data", workdir=str(dest)))
    assert rc == 0

    cmd, _cwd, _env = calls[0]
    assert str(dest / "tests" / "test_my_data.py") in cmd

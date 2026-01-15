from __future__ import annotations

from pystatsv1.cli import main


def test_doctor_cli_runs(capsys) -> None:
    rc = main(["doctor", "--verbose"])
    out = capsys.readouterr().out

    assert rc == 0
    assert "Packages" in out

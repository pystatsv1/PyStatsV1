from __future__ import annotations

from pathlib import Path

from pystatsv1.cli import main


def test_trackd_byod_normalize_uses_adapter_from_config(tmp_path: Path, capsys) -> None:
    proj = tmp_path / "byod"

    rc_init = main(["trackd", "byod", "init", "--dest", str(proj), "--profile", "core_gl"])
    assert rc_init == 0

    cfg_path = proj / "config.toml"
    cfg = cfg_path.read_text(encoding="utf-8")
    cfg_path.write_text(cfg.replace('adapter = "passthrough"', 'adapter = "bogus"'), encoding="utf-8")

    rc = main(["trackd", "byod", "normalize", "--project", str(proj)])
    out = capsys.readouterr().out.lower()

    assert rc == 1
    assert "unknown adapter" in out
    assert "passthrough" in out
    assert "core_gl" in out
    assert "gnucash_gl" in out

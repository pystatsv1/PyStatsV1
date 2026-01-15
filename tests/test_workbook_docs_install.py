from pathlib import Path


def test_workbook_quickstart_mentions_workbook_extra() -> None:
    txt = Path("docs/source/workbook/quickstart.rst").read_text(encoding="utf-8")
    assert "pystatsv1[workbook]" in txt


def test_workbook_workflow_mentions_workbook_extra() -> None:
    txt = Path("docs/source/workbook/workflow.rst").read_text(encoding="utf-8")
    assert "pystatsv1[workbook]" in txt

from pathlib import Path

from pystatsv1.psych import package_identity


def test_package_identity_records_version_and_import_path():
    receipt = package_identity()

    assert receipt["package_name"] == "pystatsv1"
    assert receipt["module_name"] == "pystatsv1"
    assert receipt["version"]
    assert receipt["status"] in {"available", "importable-without-distribution-metadata"}
    assert receipt["module_file"]
    assert Path(receipt["module_file"]).name == "__init__.py"
    assert "top_level_exports" in receipt
    assert "PROJECT_ROOT" in receipt["top_level_exports"]
    assert receipt["source_kind"] in {
        "installed-package",
        "installed-distribution",
        "local-source-or-editable",
        "unknown",
    }

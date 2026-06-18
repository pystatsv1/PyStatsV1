import json

from pystatsv1.psych import compare_numeric_results, write_json_receipt


def test_write_json_receipt_is_stable_and_creates_parent(tmp_path):
    path = write_json_receipt(tmp_path / "receipts" / "demo.json", {"b": 2, "a": 1})

    assert path.exists()
    assert path.read_text(encoding="utf-8") == '{\n  "a": 1,\n  "b": 2\n}\n'
    assert json.loads(path.read_text(encoding="utf-8"))["a"] == 1


def test_compare_numeric_results_records_pass_fail_and_missing():
    receipt = compare_numeric_results(
        {"mean": 1.0000001, "sd": 2.0, "left_only": 4.0},
        {"mean": 1.0000002, "sd": 2.1, "right_only": 5.0},
        tolerance=1e-5,
    )

    by_metric = {row["metric"]: row for row in receipt["comparisons"]}
    assert receipt["all_within_tolerance"] is False
    assert by_metric["mean"]["status"] == "pass"
    assert by_metric["sd"]["status"] == "fail"
    assert by_metric["left_only"]["status"] == "missing"
    assert by_metric["right_only"]["status"] == "missing"

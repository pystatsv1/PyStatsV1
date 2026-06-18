import pytest

from pystatsv1.psych import describe_by_group


def test_describe_by_group_returns_json_stable_records():
    rows = [
        {"condition": "control", "score": 1.0, "anxiety": 5.0},
        {"condition": "control", "score": 3.0, "anxiety": 7.0},
        {"condition": "planning", "score": 5.0, "anxiety": 3.0},
        {"condition": "planning", "score": 7.0, "anxiety": 1.0},
    ]

    records = describe_by_group(rows, "condition", ["score", "anxiety"], decimals=3)

    assert len(records) == 4
    control_score = next(r for r in records if r["condition"] == "control" and r["variable"] == "score")
    planning_anxiety = next(r for r in records if r["condition"] == "planning" and r["variable"] == "anxiety")
    assert control_score == {
        "condition": "control",
        "variable": "score",
        "n": 2,
        "mean": 2.0,
        "sd": 1.414,
        "min": 1.0,
        "max": 3.0,
    }
    assert planning_anxiety["mean"] == 2.0
    assert planning_anxiety["sd"] == 1.414


def test_describe_by_group_rejects_missing_columns():
    with pytest.raises(KeyError, match="Missing required column"):
        describe_by_group([{"condition": "a", "score": 1}], "condition", "missing_score")

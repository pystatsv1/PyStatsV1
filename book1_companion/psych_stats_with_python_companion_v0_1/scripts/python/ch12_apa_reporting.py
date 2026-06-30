#!/usr/bin/env python3
from __future__ import annotations

import json
from common import OUTPUTS, format_p, sha256, write_result


CHAPTERS = ["ch05", "ch06", "ch07", "ch08", "ch09", "ch10", "ch11"]


def sentence(chapter: str, fields: dict[str, float | int]) -> str:
    if chapter == "ch05":
        return (
            f"Students in the structured strategy group (M = {fields['structured_mean']:.2f}, SD = {fields['structured_sd']:.2f}) "
            f"scored higher than students in the standard group (M = {fields['standard_mean']:.2f}, SD = {fields['standard_sd']:.2f}), "
            f"Welch t({fields['degrees_of_freedom']:.2f}) = {fields['t_statistic']:.2f}, {format_p(fields['p_value'])}, d = {fields['cohen_d']:.2f}."
        )
    if chapter == "ch06":
        return (
            f"Anxiety scores were lower after the workshop (M = {fields['post_mean']:.2f}) than before it (M = {fields['pre_mean']:.2f}), "
            f"t({fields['degrees_of_freedom']}) = {fields['t_statistic']:.2f}, {format_p(fields['p_value'])}, dz = {fields['cohen_dz']:.2f}."
        )
    if chapter == "ch07":
        return (
            f"Test scores differed across study conditions, F({fields['df_between']}, {fields['df_within']}) = {fields['f_statistic']:.2f}, "
            f"{format_p(fields['p_value'])}, η² = {fields['eta_squared']:.2f}; the spaced-review group had the highest mean (M = {fields['spaced_review_mean']:.2f})."
        )
    if chapter == "ch08":
        return (
            f"Structured strategy produced higher scores than standard strategy, F({fields['df_effect']}, {fields['df_error']}) = {fields['strategy_f']:.2f}, "
            f"{format_p(fields['strategy_p'])}, ηp² = {fields['strategy_partial_eta_squared']:.2f}; the strategy-by-feedback interaction was not supported, "
            f"F({fields['df_effect']}, {fields['df_error']}) = {fields['interaction_f']:.2f}, {format_p(fields['interaction_p'])}, ηp² = {fields['interaction_partial_eta_squared']:.3f}."
        )
    if chapter == "ch09":
        return (
            f"Confidence changed across time, F({fields['df_time']}, {fields['df_error']}) = {fields['f_statistic']:.2f}, "
            f"{format_p(fields['p_value'])}, ηp² = {fields['partial_eta_squared']:.2f}; mean confidence rose from {fields['baseline_mean']:.2f} at baseline to {fields['week_4_mean']:.2f} at week 4."
        )
    if chapter == "ch10":
        return (
            f"Weekly study hours were positively correlated with test score, r({fields['degrees_of_freedom']}) = {fields['correlation_r']:.2f}, "
            f"{format_p(fields['p_value'])}, in this synthetic sample."
        )
    if chapter == "ch11":
        return (
            f"Study hours predicted test score, b = {fields['slope']:.2f}, SE = {fields['slope_standard_error']:.2f}, "
            f"t({fields['degrees_of_freedom']}) = {fields['t_statistic']:.2f}, {format_p(fields['p_value'])}, R² = {fields['r_squared']:.2f}."
        )
    raise KeyError(chapter)


def main() -> None:
    records = []
    for chapter in CHAPTERS:
        path = OUTPUTS / chapter / "py_results.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        fields = payload["reported_fields"]
        records.append(
            {
                "chapter": chapter,
                "analysis_name": payload["analysis_name"],
                "python_result_file": f"outputs/{chapter}/py_results.json",
                "r_result_file": f"outputs/{chapter}/r_results.json",
                "parity_receipt": f"outputs/{chapter}/parity_receipt.md",
                "source_sha256": sha256(path),
                "reported_fields": fields,
                "apa_result": sentence(chapter, fields),
            }
        )
    source_map = {
        "schema_version": "book1-apa-source-map-v0.1",
        "synthetic_data_only": True,
        "records": records,
    }
    out_dir = OUTPUTS / "ch12"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "apa_reporting_source_map.json").write_text(
        json.dumps(source_map, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    out = write_result(
        "ch12",
        "APA reporting source-map audit",
        "outputs/ch12/apa_reporting_source_map.json",
        {"source_record_count": len(records), "required_python_result_files": len(records)},
    )
    print(f"wrote {out}")


if __name__ == "__main__":
    main()

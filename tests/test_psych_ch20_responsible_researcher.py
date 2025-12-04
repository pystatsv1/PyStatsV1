"""
Tests for Chapter 20: Responsible Researcher helpers.
"""

from pathlib import Path


from scripts.psych_ch20_responsible_researcher import (
    MetaAnalysisResult,
    build_power_grid,
    compute_sample_size_for_ttest,
    generate_project_template,
    run_fixed_effect_meta,
    simulate_meta_studies,
)


def test_power_sample_size_increases_with_power() -> None:
    """Required N should increase when desired power increases."""
    n_80 = compute_sample_size_for_ttest(effect_size=0.5, power=0.80)
    n_90 = compute_sample_size_for_ttest(effect_size=0.5, power=0.90)

    assert n_80 > 10  # sanity check
    assert n_90 > n_80


def test_power_grid_has_expected_shape() -> None:
    """Power grid should contain rows for each effect-size × power combo."""
    df = build_power_grid()
    # 3 effect sizes × 2 power levels = 6 rows
    assert df.shape[0] == 6
    assert {"effect_size_d", "power", "n_per_group"}.issubset(df.columns)


def test_meta_analysis_returns_positive_pooled_effect() -> None:
    """Toy meta-analysis should yield a positive pooled effect."""
    studies = simulate_meta_studies(num_studies=5, base_effect=0.4, random_state=123)
    result = run_fixed_effect_meta(studies)

    assert isinstance(result, MetaAnalysisResult)
    assert result.pooled_d > 0.0
    assert 0.0 <= result.I2 <= 100.0


def test_project_template_is_created_and_contains_header(tmp_path: Path) -> None:
    """Template helper should create a Markdown file with the expected title."""
    out_file = tmp_path / "ch20_final_project_template.md"
    generate_project_template(out_file)

    assert out_file.exists()
    text = out_file.read_text(encoding="utf-8")
    assert "PyStatsV1 Final Project Report" in text

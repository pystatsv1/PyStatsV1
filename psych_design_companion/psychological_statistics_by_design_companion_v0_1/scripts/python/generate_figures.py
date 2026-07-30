#!/usr/bin/env python3
from __future__ import annotations
import argparse
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from companion_runtime import ROOT, normalize_study_id, sha256, study_index, write_json
from scripts.python.analysis_batches.batch_swl_s01_s06_s07 import analyze_swl_s01, analyze_swl_s07
from scripts.python.analysis_batches.batch_swl_s08_s10 import analyze_swl_s10

def save(fig, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=300)
    plt.close(fig)

def mean_ci(values):
    return (float(values.mean()), float(1.96 * values.std(ddof=1) / np.sqrt(len(values))))

def build(sid):
    row = study_index()[sid]
    frame = pd.read_csv(ROOT / row['dataset_path'])
    out = ROOT / 'outputs' / sid.lower().replace('-', '_') / 'figures'
    rows = []

    def record(name, role):
        rows.append({'study_id': sid, 'output': name, 'role': role, 'sha256': sha256(out / name), 'dpi': 300, 'grayscale': True})
    if sid == 'SWL-S01':
        x = frame.sleep_quality.to_numpy(float)
        y = frame.academic_confidence.to_numpy(float)
        slope, inter = np.polyfit(x, y, 1)
        grid = np.linspace(x.min(), x.max(), 100)
        fig, ax = plt.subplots(figsize=(7.2, 4.8))
        ax.scatter(x, y, facecolors='none', edgecolors='black')
        ax.plot(grid, inter + slope * grid, color='black')
        ax.set(xlabel='Sleep quality', ylabel='Academic confidence', title='SWL-S01: Sleep quality and academic confidence')
        save(fig, out / 'swl_s01_correlation.png')
        record('swl_s01_correlation.png', 'correlation')
        v = analyze_swl_s01(frame)
        X = np.column_stack([np.ones(len(frame)), frame.study_hours_per_week, frame.academic_confidence])
        beta = np.array([v['intercept_b'], v['study_hours_b'], v['confidence_b']])
        fitted = X @ beta
        resid = frame.assessment_performance.to_numpy(float) - fitted
        fig, ax = plt.subplots(figsize=(7.2, 4.8))
        ax.axhline(0, color='black', linestyle='--')
        ax.scatter(fitted, resid, facecolors='none', edgecolors='black', marker='s')
        ax.set(xlabel='Fitted assessment performance', ylabel='Residual', title='SWL-S01: Registered prediction-model residuals')
        save(fig, out / 'swl_s01_regression_residuals.png')
        record('swl_s01_regression_residuals.png', 'regression')
    elif sid == 'SWL-S02':
        levels = ['standard_routine', 'structured_routine']
        stats = [mean_ci(frame.loc[frame.study_routine_group == x, 'post_session_performance'].to_numpy(float)) for x in levels]
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.errorbar([0, 1], [x[0] for x in stats], yerr=[x[1] for x in stats], fmt='o', color='black', capsize=5)
        ax.set_xticks([0, 1], ['Standard routine', 'Structured routine'])
        ax.set(ylabel='Post-session performance', title='SWL-S02: Group means and 95% CIs')
        save(fig, out / 'swl_s02.png')
        record('swl_s02.png', 'primary')
    elif sid == 'SWL-S03':
        wide = frame.pivot(index='participant_id', columns='occasion', values='academic_confidence')
        fig, ax = plt.subplots(figsize=(6, 4))
        [ax.plot([0, 1], [r['pre'], r['post']], color='0.75', linewidth=0.7) for _, r in wide.iterrows()]
        ax.plot([0, 1], [wide.pre.mean(), wide.post.mean()], color='black', marker='o', linewidth=2)
        ax.set_xticks([0, 1], ['Pre', 'Post'])
        ax.set(ylabel='Academic confidence', title='SWL-S03: Linked pre/post change')
        save(fig, out / 'swl_s03.png')
        record('swl_s03.png', 'primary')
    elif sid == 'SWL-S04':
        levels = ['standard_support', 'guided_practice', 'guided_practice_plus_feedback']
        stats = [mean_ci(frame.loc[frame.support_condition == x, 'assessment_performance'].to_numpy(float)) for x in levels]
        fig, ax = plt.subplots(figsize=(6.4, 4))
        ax.errorbar(range(3), [x[0] for x in stats], yerr=[x[1] for x in stats], fmt='o', color='black', capsize=5)
        ax.set_xticks(range(3), ['Standard', 'Guided', 'Guided + feedback'])
        ax.set(ylabel='Assessment performance', title='SWL-S04: Condition means and 95% CIs')
        save(fig, out / 'swl_s04.png')
        record('swl_s04.png', 'primary')
    elif sid == 'SWL-S05':
        fig, ax = plt.subplots(figsize=(6, 4))
        for i, strategy in enumerate(['rereading', 'retrieval_practice']):
            means = [frame.loc[(frame.study_strategy == strategy) & (frame.feedback_condition == feedback), 'assessment_performance'].mean() for feedback in ['no_feedback', 'explanatory_feedback']]
            ax.plot([0, 1], means, color='black', linestyle='-' if i == 0 else '--', marker='o' if i == 0 else 's', label=strategy.replace('_', ' ').title())
        ax.set_xticks([0, 1], ['No feedback', 'Explanatory feedback'])
        ax.set(ylabel='Assessment performance', title='SWL-S05: Strategy × Feedback interaction')
        ax.legend()
        save(fig, out / 'swl_s05.png')
        record('swl_s05.png', 'primary')
    elif sid == 'SWL-S06':
        wide = frame.pivot(index='participant_id', columns='occasion', values='academic_confidence')[['baseline', 'post', 'follow_up']].dropna()
        fig, ax = plt.subplots(figsize=(7.2, 4.8))
        [ax.plot(range(3), r.to_numpy(float), color='0.78', linewidth=0.65) for _, r in wide.iterrows()]
        ax.plot(range(3), wide.mean().to_numpy(float), color='black', linewidth=2, marker='o')
        ax.set_xticks(range(3), ['Baseline', 'Post', 'Follow-up'])
        ax.set(ylabel='Academic confidence', title='SWL-S06: Complete-case confidence trajectories')
        save(fig, out / 'swl_s06.png')
        record('swl_s06.png', 'primary')
    elif sid == 'SWL-S07':
        v = analyze_swl_s07(frame)
        base = v['baseline_overall_mean']
        grid = np.linspace((frame.baseline_performance - base).min(), (frame.baseline_performance - base).max(), 100)
        fig, ax = plt.subplots(figsize=(7.2, 4.8))
        for group, marker, line, offset in [('comparison', 'o', '-', 0), ('intervention', 's', '--', v['adjusted_group_difference_intervention_minus_comparison'])]:
            sub = frame[frame.intervention_group == group]
            ax.scatter(sub.baseline_performance, sub.post_performance, facecolors='none', edgecolors='black', marker=marker, label=group.title())
            ax.plot(grid + base, v['adjusted_mean_comparison_at_overall_baseline'] + offset + v['baseline_slope'] * grid, color='black', linestyle=line)
        ax.set(xlabel='Baseline performance', ylabel='Post performance', title='SWL-S07: Baseline-adjusted parallel regression lines')
        ax.legend()
        save(fig, out / 'swl_s07.png')
        record('swl_s07.png', 'primary')
    elif sid == 'SWL-S08':
        means = frame.groupby(['treatment_group', 'occasion'], as_index=False).well_being_score.mean()
        order = ['baseline', 'post', 'followup']
        fig, ax = plt.subplots(figsize=(7.2, 4.8))
        for group, marker, line in [('control', 'o', '-'), ('treatment', 's', '--')]:
            sub = means[means.treatment_group == group].set_index('occasion')
            ax.plot(range(3), [sub.loc[x, 'well_being_score'] for x in order], color='black', marker=marker, linestyle=line, label=group.title())
        ax.set_xticks(range(3), ['Baseline', 'Post', 'Follow-up'])
        ax.set(xlabel='Occasion', ylabel='Well-being score', title='SWL-S08: Observed group-by-occasion means')
        ax.legend()
        save(fig, out / 'swl_s08.png')
        record('swl_s08.png', 'primary')
    elif sid == 'SWL-S09':
        tab = pd.crosstab(frame.support_condition, frame.clinically_improved, normalize='index').reindex(index=['comparison', 'intervention'], columns=['yes', 'no'])
        fig, ax = plt.subplots(figsize=(7.2, 4.8))
        ax.bar(range(2), tab.yes, edgecolor='black', facecolor='white', label='Improved')
        ax.bar(range(2), tab.no, bottom=tab.yes, edgecolor='black', facecolor='0.70', hatch='///', label='Not improved')
        ax.set_xticks(range(2), ['Comparison', 'Intervention'])
        ax.set(xlabel='Support condition', ylabel='Proportion', title='SWL-S09: Registered binary outcome')
        ax.legend()
        save(fig, out / 'swl_s09_improvement.png')
        record('swl_s09_improvement.png', 'categorical')
        groups = [frame.loc[frame.support_condition == g, 'recovery_burden_days'].to_numpy(float) for g in ['comparison', 'intervention']]
        fig, ax = plt.subplots(figsize=(7.2, 4.8))
        ax.boxplot(groups, tick_labels=['Comparison', 'Intervention'], showfliers=False)
        ax.set(xlabel='Support condition', ylabel='Recovery burden (days)', title='SWL-S09: Positive-skew recovery burden')
        save(fig, out / 'swl_s09_burden.png')
        record('swl_s09_burden.png', 'rank')
    else:
        v = analyze_swl_s10(frame)
        effects = frame.observed_cohens_d.to_numpy(float)
        se = np.sqrt(frame.sampling_variance_d.to_numpy(float))
        y = np.arange(len(frame), 0, -1)
        fig, ax = plt.subplots(figsize=(7.2, 5))
        ax.errorbar(effects, y, xerr=1.96 * se, fmt='o', color='black', capsize=3)
        pooled = v['fixed_effect_pooled_d']
        ax.errorbar([pooled], [0], xerr=[[pooled - v['fixed_effect_ci_95_low']], [v['fixed_effect_ci_95_high'] - pooled]], fmt='D', color='black', capsize=4)
        ax.axvline(0, color='0.35', linestyle='--')
        ax.set_yticks(list(y) + [0], frame.study_id.tolist() + ['Fixed-effect pooled'])
        ax.set(xlabel='Standardized mean difference', ylabel='Replication', title='SWL-S10: Cumulative synthetic evidence')
        save(fig, out / 'swl_s10.png')
        record('swl_s10.png', 'primary')
    write_json(out / 'FIGURE_MANIFEST.json', {'schema_version': 'psych-design-figure-manifest-v0.1', 'study_id': sid, 'figures': rows, 'synthetic_only': True})
    print(f'PYSTATSV1_PSYCH_DESIGN_FIGURES_OK study={sid}')
if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--study')
    a = p.parse_args()
    ids = [normalize_study_id(a.study)] if a.study else list(study_index())
    [build(x) for x in ids]

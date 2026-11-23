"""CCE06 TRAIN-only PSR test-capacity and regression selection.

Never imports calibration_worlds or accepts an evaluator-only family/split ID.
Model choice and final refit are strictly inside caller-supplied public TRAIN.
"""
from __future__ import annotations
import math
from calibration_fit_selection import split_train_only
from calibration_psr import LearnedOperatorPSR, score_streaming_psr


def select_psr_on_train(public_train, *, test_grid=(3, 6, 9, 12),
                        depth_grid=(1, 2, 3), ridge_grid=(0.05, 0.5),
                        fraction=0.2):
    if (type(test_grid) is not tuple or not test_grid
            or type(depth_grid) is not tuple or not depth_grid
            or type(ridge_grid) is not tuple or not ridge_grid
            or len(set(test_grid)) != len(test_grid)
            or len(set(depth_grid)) != len(depth_grid)
            or len(set(ridge_grid)) != len(ridge_grid)):
        raise ValueError('CCE06_PSR_INVALID_TRAIN_GRID')
    for k in test_grid:
        LearnedOperatorPSR(tests=k)
    for depth in depth_grid:
        LearnedOperatorPSR(depth=depth)
    for ridge in ridge_grid:
        LearnedOperatorPSR(ridge=ridge)
    part = split_train_only(public_train, fraction=fraction)
    scores = []
    for k in sorted(test_grid):
        for depth in sorted(depth_grid):
            for ridge in sorted(ridge_grid):
                model = LearnedOperatorPSR(tests=k, depth=depth, ridge=ridge).fit(part.fit)
                score = score_streaming_psr(model, part.select)
                if not math.isfinite(score):
                    raise ValueError('CCE06_PSR_NONFINITE_SELECTION')
                scores.append(dict(tests=k, depth=depth, ridge=ridge,
                                   validation_brier=score))
    best = min(scores, key=lambda row: (row['validation_brier'],
                                        row['tests'], row['depth'], row['ridge']))
    final = LearnedOperatorPSR(tests=best['tests'], depth=best['depth'],
                               ridge=best['ridge']).fit(public_train)
    return final, dict(status='TRAIN_ONLY_PSR_SELECTED',
                       selected=dict(best), grid=tuple(scores),
                       fit_events=part.fit_events,
                       selection_events=part.select_events,
                       final_train_events=final.events,
                       learned_operators=len(final.operators),
                       includes_cal_eval=False)

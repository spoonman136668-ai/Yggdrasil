"""Only public TRAIN events for bounded recurrent-neural model selection."""
from __future__ import annotations
import math
from calibration_fit_selection import split_train_only
from calibration_recurrent import TrainableRecurrentEstimator


def select_recurrent_on_train(public_train, *, widths=(4, 8, 12),
                              learning_rates=(0.01, 0.02), epochs=30,
                              patience=5, truncate=12, fraction=0.2,
                              seed=60806):
    if (type(widths) is not tuple or not widths or len(set(widths)) != len(widths)
            or type(learning_rates) is not tuple or not learning_rates
            or len(set(learning_rates)) != len(learning_rates)
            or type(seed) is not int or seed < 0):
        raise ValueError('CCE06_RNN_INVALID_SELECTION_GRID')
    for width in widths:
        TrainableRecurrentEstimator(width, seed)
    for learning_rate in learning_rates:
        if type(learning_rate) not in (int, float) or not 0 < learning_rate <= 0.1:
            raise ValueError('CCE06_RNN_INVALID_LEARNING_RATE')
    part = split_train_only(public_train, fraction=fraction)
    scores = []
    for width in sorted(widths):
        for learning_rate in sorted(learning_rates):
            m = TrainableRecurrentEstimator(width, seed + width * 1009).fit(
                part.fit, epochs=epochs, lr=learning_rate, truncate=truncate,
                patience=patience, validation=part.select)
            score = m.score(part.select)
            if not math.isfinite(score):
                raise ValueError('CCE06_RNN_INVALID_SELECTION_SCORE')
            scores.append(dict(width=width, learning_rate=learning_rate,
                               best_epoch=m.best_epoch, early_stopped=m.early_stopped,
                               validation_brier=score, actual_epochs=len(m.trace)))
    best = min(scores, key=lambda z: (z['validation_brier'], z['width'], z['learning_rate']))
    final = TrainableRecurrentEstimator(best['width'], seed + best['width'] * 1009).fit(
        public_train, epochs=best['best_epoch'], lr=best['learning_rate'],
        truncate=truncate)
    return final, dict(status=('TRAIN_ONLY_RECURRENT_SELECTED' if best['early_stopped']
                               else 'RNN_EARLY_STOP_NOT_REACHED'),
                       selection=best, grid=tuple(scores),
                       train_fit_events=part.fit_events,
                       train_select_events=part.select_events,
                       final_train_events=final.train_events,
                       final_epochs=len(final.trace),
                       includes_cal_eval=False)

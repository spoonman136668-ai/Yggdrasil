"""CKAD39: source-only read-only retrieval from one native episodic learner.

Only previously witnessed events and already trained native block models are
examined.  This projection never trains, restores, mutates, or replaces a model.
"""
import math

WINDOW = 16
DETECTION_HORIZON = 48
MIN_ARCHIVE_POSTERIOR = 0.55
ARCHIVE_BLEND = 0.50


def _likelihood(source, event):
    """Likelihood of an already witnessed two-stage public causal consequence."""
    _, views, first, next_state, second, reward = event
    p = float(source.forecast(views[0], first))
    q = float(source.forecast(views[0], first, next_state, second))
    if not (0 < p < 1 and 0 < q < 1):
        raise ValueError("CKAD39_INVALID_SOURCE_PROBABILITY")
    return (p if next_state else 1 - p) * (q if reward else 1 - q)


def evidence_forecast(model, view, first, next_state=None, second=None):
    """Conditionally reactivate retained block forecasts without writing a byte.

    Each frozen native block receives its own likelihood from the last 16
    *already observed* authentic episodes. Only a sufficiently concentrated
    archived posterior after a native detector event can influence prediction.
    A terminal prediction additionally conditions archive weights on the
    already observed next state, without seeing the terminal outcome.
    """
    if model._context_start is None:
        return model.forecast(view, first, next_state, second)
    normal = model.context_forecast(view, first, next_state, second)
    if model._stream_start is None or not model._stream_detections:
        return normal
    age = len(model._ledger) - model._stream_detections[-1][1]
    if not (0 <= age < DETECTION_HORIZON):
        return normal
    history = model._ledger[-WINDOW:]
    if len(history) != WINDOW:
        return normal
    sources = tuple(source for start, stop, _, source in model._context_models
                    if stop > start and stop <= model._context_start)
    if not sources:
        return normal
    scores = [sum(math.log(_likelihood(source, event)) for event in history)
              for source in sources]
    maximum = max(scores)
    strengths = [math.exp(score - maximum) for score in scores]
    total = sum(strengths)
    if not total > 0:
        raise ValueError("CKAD39_INVALID_ARCHIVE_POSTERIOR")
    posterior = [w / total for w in strengths]
    if max(posterior) < MIN_ARCHIVE_POSTERIOR:
        return normal
    if next_state is not None:
        # The transition has already happened; the terminal reward has not.
        transition = [float(source.forecast(view, first)) for source in sources]
        strengths = [w * (p if next_state else 1 - p)
                     for w, p in zip(posterior, transition)]
        total = sum(strengths)
        if not total > 0:
            raise ValueError("CKAD39_INVALID_TRANSITION_POSTERIOR")
        posterior = [w / total for w in strengths]
    archive = sum(w * float(source.forecast(view, first, next_state, second))
                  for w, source in zip(posterior, sources))
    return (1 - ARCHIVE_BLEND) * normal + ARCHIVE_BLEND * archive

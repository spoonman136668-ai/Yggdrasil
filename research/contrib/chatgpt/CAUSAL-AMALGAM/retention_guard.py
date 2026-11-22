"""Evaluate historical native predictions before admitting a research descendant."""

from fractions import Fraction

from yggdrasil.native_context_basis import canonical, digest

SCALE = 1_000_000


def readout_losses(system, events):
    """Evaluate fixed public interventions from the historical witness prefix."""
    transition_loss = reward_loss = 0
    for _, views, first, state, second, reward in events:
        view = views[0]
        prediction = system.native.experience_context_forecast
        transition_loss += (round(SCALE * prediction(view, first)) - SCALE * state)**2
        reward_loss += (round(SCALE * prediction(view, first, state, second)) - SCALE * reward)**2
    count = len(events) * SCALE**2
    return Fraction(transition_loss, count), Fraction(reward_loss, count)


def evaluate(anchor, candidate, windows, *, max_brier_drift):
    """Return diagnostics for pinned known-history prediction, without training."""
    old = anchor.native._episode_reader()._ledger
    new = candidate.native._episode_reader()._ledger
    if new[:len(old)] != old:
        raise ValueError("Checkpoint candidate did not retain the exact witness prefix")
    if not isinstance(max_brier_drift, Fraction) or not 0 <= max_brier_drift <= 1:
        raise ValueError("Brier tolerance must be a probability")
    details = {}
    for name, (start, stop) in windows.items():
        if not 0 <= start < stop <= len(old):
            raise ValueError("Historical probe must be entirely within the anchor witness prefix")
        historical = old[start:stop]
        previous_loss = readout_losses(anchor, historical)
        candidate_loss = readout_losses(candidate, historical)
        details[name] = {
            "witness_sha256": digest(canonical(historical)),
            "count": len(historical),
            "anchor_brier": [float(value) for value in previous_loss],
            "candidate_brier": [float(value) for value in candidate_loss],
            "delta_brier": [float(after-before) for before,after in zip(previous_loss,candidate_loss)],
            "pass": all(after-before <= max_brier_drift
                        for before,after in zip(previous_loss,candidate_loss)),
        }
    if not details:
        raise ValueError("At least one historical probe is required")
    report = {
        "scope": "Historical consumed witnesses, diagnostic only",
        "targets": ["transition", "reward"],
        "anchor_count": len(old),
        "candidate_count": len(new),
        "max_brier_drift": str(max_brier_drift),
        "windows": details,
        "pass": all(window["pass"] for window in details.values()),
    }
    return report


def reversible_candidate(anchor, candidate, windows, *, max_brier_drift):
    """Keep the requested anchor active when the functional guard fails."""
    report = evaluate(anchor, candidate, windows, max_brier_drift=max_brier_drift)
    return (candidate if report["pass"] else anchor), report

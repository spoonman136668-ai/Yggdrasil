"""G33 DEV-only two-bank JEPA readout; no native actor or checkpoint admission.

Both banks start from the same trained heads. The anchor is immutable and
the adaptive bank observes admitted public witnesses using existing APIs.
Routing probabilities are fixed before each current witness's outcomes.
Only the native source ledger supplies chronology; no phase or ID in routing.
Replay on consumed data is retrospective, never independent science.
"""
from math import exp, isfinite, log

from four_head_retention import HEAD_TYPES, KINDS, HEAD_NAMES, _inspect
from yggdrasil.native_causal_amalgam import NativeCausalAmalgam
from yggdrasil.native_context_basis import canonical, digest

MAX_PREFIX = 4096
MAX_SUFFIX = 96
LOG_ODDS_BOUND = 8.0
PROB_FLOOR = 1e-9
SWITCH_HAZARD = 1 / 32  # G33-R1 frozen, never fitted to evaluated outcomes.


def _check_heads(heads):
    if (type(heads) is not tuple or len(heads) != 4
            or any(type(h) is not t or h.kind != k
                   for h, t, k in zip(heads, HEAD_TYPES, KINDS, strict=True))):
        raise ValueError("G33_HEAD_IDENTITY")
    for h in heads:
        h._validate()


def _bank_bytes(heads):
    _check_heads(heads)
    return canonical([h.as_data() if i < 2 else h.data()
                      for i, h in enumerate(heads)])


def _validate_ledger(rows):
    if type(rows) is not tuple:
        raise ValueError("G33_LEDGER_TYPE")
    seen = set()
    for row in rows:
        if type(row) is not tuple or len(row) != 6:
            raise ValueError("G33_EVENT_SHAPE")
        identifier, views, *bits = row
        if (type(identifier) is not str or not identifier
                or identifier in seen
                or type(views) is not tuple or len(views) != 2
                or any(type(v) is not tuple or len(v) != 2
                       for v in views)
                or any(type(b) is not int or b not in (0, 1)
                       for v in views for b in v)
                or views[0][0] != views[1][0]
                or any(type(b) is not int or b not in (0, 1) for b in bits)):
            raise ValueError("G33_EVENT_IDENTITY_OR_PUBLIC_BITS")
        seen.add(identifier)


def _forecast(heads, views, extras, history):
    """Stage-specific interface: transition receives first action ONLY."""
    if len(extras) == 1:
        direct, temporal = heads[0], heads[2]
    elif len(extras) == 3:
        direct, temporal = heads[1], heads[3]
    else:
        raise ValueError("G33_STAGE_ARITY")
    predictions = (direct.probability(views, *extras),
                   temporal.probability(views, extras, history))
    if any(not isfinite(p) or not 0 <= p <= 1 for p in predictions):
        raise ValueError("G33_NONFINITE_FORECAST")
    return predictions


def _likelihood(p, y):
    return log(max(PROB_FLOOR, p if y == 1 else 1.0 - p))


def _advance_router(log_odds, anchor, adaptive, labels):
    if (not isfinite(log_odds) or abs(log_odds) > LOG_ODDS_BOUND
            or any(len(v) != 4 for v in (anchor, adaptive, labels))
            or any(type(y) is not int or y not in (0, 1) for y in labels)
            or any(not isfinite(p) or not 0 <= p <= 1
                   for p in (*anchor, *adaptive))):
        raise ValueError("G33_ROUTER_INPUT")
    # Temper the likelihood ratio because direct/temporal heads are correlated.
    evidence = sum(_likelihood(b, y) - _likelihood(a, y)
                   for a, b, y in zip(anchor, adaptive, labels, strict=True)) / 4
    return max(-LOG_ODDS_BOUND, min(LOG_ODDS_BOUND, log_odds + evidence))


def _mix(anchor, adaptive, weight):
    return tuple((1 - weight)*a + weight*b
                 for a, b in zip(anchor, adaptive, strict=True))


def _switch_prior(posterior_odds):
    """Symmetric hazard transition, before observing the next witness."""
    if (type(posterior_odds) not in (int, float)
            or not isfinite(posterior_odds)
            or abs(posterior_odds) > LOG_ODDS_BOUND):
        raise ValueError("G33_SWITCH_ODDS")
    p = 1 / (1 + exp(-posterior_odds))
    return SWITCH_HAZARD + (1 - 2 * SWITCH_HAZARD) * p


def _replay(heads, prefix, suffix, *, switching=False):
    """Pure development seam; fixtures cannot establish source authenticity."""
    if type(switching) is not bool:
        raise ValueError("G33_SWITCH_FLAG")
    _check_heads(heads)
    if (type(prefix) is not tuple or not 0 < len(prefix) <= MAX_PREFIX
            or type(suffix) is not tuple or not 0 < len(suffix) <= MAX_SUFFIX
            or len(prefix) + len(suffix) > MAX_PREFIX):
        raise ValueError("G33_LEDGER_BOUNDS")
    _validate_ledger(prefix + suffix)
    initial = _bank_bytes(heads)
    frozen = tuple(h.clone() for h in heads)
    adaptive = tuple(h.clone() for h in heads)
    history = prefix[-8:]
    odds = 0.0
    switch_odds = 0.0
    trace = []
    for ordinal, event in enumerate(suffix, len(prefix) + 1):
        _, views, first, state, second, reward = event
        weight = 1 / (1 + exp(-odds))
        # Stage one cannot access state/reward. Stage two receives actual
        # public stage-two state and action but never terminal reward.
        at = _forecast(frozen, views, (first,), history)
        bt = _forecast(adaptive, views, (first,), history)
        ar = _forecast(frozen, views, (first, state, second), history)
        br = _forecast(adaptive, views, (first, state, second), history)
        a = (at[0], ar[0], at[1], ar[1])
        b = (bt[0], br[0], bt[1], br[1])
        mixed = _mix(a, b, weight)
        equal = _mix(a, b, 0.5)
        labels = (state, reward, state, reward)
        # Score before either adaptive training or router update.
        losses = {name: tuple((p-y)**2 for p,y in zip(pred, labels, strict=True))
                  for name,pred in (("anchor", a), ("adaptive", b),
                                    ("routed", mixed), ("equal", equal))}
        next_odds = _advance_router(odds, a, b, labels)
        if switching:
            # Both routers see the identical already-emitted bank forecasts.
            # The hazard prior depends solely on earlier evidence.
            q = _switch_prior(switch_odds)
            switched = _mix(a, b, q)
            losses["switching"] = tuple(
                (p-y)**2 for p,y in zip(switched, labels, strict=True))
            switch_odds = _advance_router(log(q / (1 - q)), a, b, labels)
        adaptive[0].observe(views, (first,), state)
        adaptive[1].observe(views, (first, state, second), reward)
        adaptive[2].observe(views, (first,), history, state)
        adaptive[3].observe(views, (first, state, second), history, reward)
        trace.append({"ordinal": ordinal, "adaptive_weight_before": weight,
                      "anchor": a, "adaptive": b, "routed": mixed,
                      "equal": equal, "brier": losses,
                      "log_odds_after": next_odds})
        if switching:
            trace[-1].update(switching=switched,
                             switching_adaptive_weight_before=q,
                             switching_log_odds_after=switch_odds)
        odds = next_odds
        history = (history + (event,))[-8:]
    frozen_bytes = _bank_bytes(frozen)
    adaptive_bytes = _bank_bytes(adaptive)
    if frozen_bytes != initial or _bank_bytes(heads) != initial:
        raise ValueError("G33_ANCHOR_MUTATION")
    report = {
        "schema": "yggdrasil.amalgam.dev-two-bank-readout.v1",
        "head_order": HEAD_NAMES, "initial_head_sha256": digest(initial),
        "anchor_head_sha256": digest(frozen_bytes),
        "adaptive_head_sha256": digest(adaptive_bytes),
        "bank_parameter_bytes": len(frozen_bytes) + len(adaptive_bytes),
        "forecast_count": 8 * len(suffix), "adaptive_head_updates": 4 * len(suffix),
        "prefix_sha256": digest(canonical(prefix)),
        "suffix_sha256": digest(canonical(suffix)),
        "trace": trace, "source_actions": 0,
        "official_checkpoint_restore_supported": False,
        "scientific_pass": False,
    }
    if switching:
        report.update(switching_hazard=SWITCH_HAZARD,
                      additional_router_updates=len(suffix),
                      additional_mixture_scalar_predictions=4 * len(suffix))
    return report


def audit_admitted_prefix(anchor, descendant, *, anchor_sha256, descendant_sha256,
                          switching=False):
    """Read-only shadow replay from independently pinned original model objects.

    This checks identity and prefix consistency, not source-owner authenticity.
    Caller is responsible for independent custody and authorization of readback.
    Neither native object is advanced and no actor is constructed.
    """
    if type(anchor) is not NativeCausalAmalgam or type(descendant) is not NativeCausalAmalgam:
        raise ValueError("G33_NATIVE_REQUIRED")
    heads, prefix, a_pin = _inspect(anchor)
    _, ledger, d_pin = _inspect(descendant)
    if a_pin != anchor_sha256 or d_pin != descendant_sha256:
        raise ValueError("G33_SOURCE_PIN")
    if (len(ledger) <= len(prefix) or ledger[:len(prefix)] != prefix
            or anchor._native_parent != descendant._native_parent
            or anchor._specialist_parent != descendant._specialist_parent):
        raise ValueError("G33_NATIVE_PREFIX")
    result = _replay(heads, prefix, ledger[len(prefix):], switching=switching)
    if (_inspect(anchor)[2], _inspect(descendant)[2]) != (a_pin, d_pin):
        raise ValueError("G33_SOURCE_MUTATION")
    result.update(anchor_checkpoint_sha256=a_pin, descendant_checkpoint_sha256=d_pin,
                  independent_cold_restore_verified=False)
    return result

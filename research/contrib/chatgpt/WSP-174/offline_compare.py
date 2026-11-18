"""WSP180: offline public FIT-to-HELD comparison, with no source execution.

This is a bounded *developer harness* for pre-existing public observations.
It never creates a source world, grants original first-use authority, validates
true cohort ownership, or emits a scientific PASS. The input event_id is a
caller-claimed bookkeeping identifier, NOT a signed provenance attestation.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re

from public_boundary import PublicEvidence
from stochastic_controls import (ConditionalDirichlet, descendant_brier,
                                 descendants, identity_forecast, uniform_forecast)
from direct_color_weights import DirectColorWeights

SCHEMA = "yggdrasil.wsp180.offline-public-diagnostic.v1"
STATUS = "DEV_ONLY_UNATTESTED_ORIGINAL_SCIENCE_NOT_RUN"
SOURCE_PIN = "dido1998/CausalMBRL@2c595988b06b3d568fdde53213029e97841acb03"
MAX_RECORDS = 50000
ARMS = ("direct_programmed", "categorical_conditional", "identity", "uniform")
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}\\Z", re.ASCII)


@dataclass(frozen=True, slots=True)
class PublicRow:
    """Bookkeeping only; event identity and split must be owner-attested elsewhere."""
    event_id: str
    evidence: PublicEvidence

    def __post_init__(self) -> None:
        if type(self.event_id) is not str or _ID.fullmatch(self.event_id) is None:
            raise ValueError("WSP180_EVENT_ID")
        if type(self.evidence) is not PublicEvidence:
            raise ValueError("WSP180_PUBLIC_EVIDENCE")


def _validate(fit: object, held: object) -> tuple[tuple[PublicRow, ...],
                                                tuple[PublicRow, ...]]:
    if type(fit) not in (tuple, list) or type(held) not in (tuple, list):
        raise ValueError("WSP180_SPLIT_TYPE")
    if not fit or not held or len(fit) + len(held) > MAX_RECORDS:
        raise ValueError("WSP180_SPLIT_SIZE")
    rows = tuple(fit) + tuple(held)
    if any(type(x) is not PublicRow for x in rows):
        raise ValueError("WSP180_ROW_TYPE")
    ids = tuple(x.event_id for x in rows)
    if len(set(ids)) != len(ids):
        # Compare actor/event IDs, NOT content hashes: two genuine stochastic
        # interventions can produce bit-identical public observations.
        raise ValueError("WSP180_EVENT_ID_REUSE")
    return tuple(fit), tuple(held)


def _fingerprint(rows: tuple[PublicRow, ...]) -> str:
    # Canonical order/identity digest for readback; NOT evidence of actor custody.
    encoded = [[row.event_id, row.evidence.sha256()] for row in rows]
    return hashlib.sha256(json.dumps(
        encoded, separators=(",", ":"), sort_keys=True,
        allow_nan=False).encode("ascii")).hexdigest()


def evaluate(fit: list[PublicRow] | tuple[PublicRow, ...],
             held: list[PublicRow] | tuple[PublicRow, ...]) -> dict[str, object]:
    """Fit on public FIT only, freeze, then score HELD without updating.

    Gives each strictly potential-downstream *object* equal scoring weight.
    Across actions this is object-slot weighted (NOT episode-mean weighted).
    Objects <= intervened index are excluded as trivially source-fixed.
    A 0-potential-descendant action is accounted but cannot earn 0 loss.
    """
    fit, held = _validate(fit, held)
    direct = DirectColorWeights()
    conventional = ConditionalDirichlet()
    for row in fit:
        direct.fit_observed(row.evidence)
        conventional.fit_observed(row.evidence)
    direct.freeze()
    conventional.freeze()
    scorers = {
        "direct_programmed": direct.forecast,
        "categorical_conditional": conventional.forecast,
        "identity": identity_forecast,
        "uniform": uniform_forecast,
    }
    loss_sums = {name: 0.0 for name in ARMS}
    scored_slots = 0
    scored_actions = 0
    zero_descendant_actions = 0
    for row in held:
        observed = row.evidence
        potential = descendants(observed.action)
        # Each model gets only pre-action public state+goal plus action.
        policy = observed.policy_input()
        forecasts = {name: predictor(policy, observed.action)
                     for name, predictor in scorers.items()}
        if not potential:
            zero_descendant_actions += 1
            if any(descendant_brier(observed, p) is not None
                   for p in forecasts.values()):
                raise AssertionError("WSP180_ZERO_DESCENDANT_LEAK")
            continue
        scored_actions += 1
        scored_slots += len(potential)
        for name, forecast in forecasts.items():
            brier = descendant_brier(observed, forecast)
            if brier is None or not math.isfinite(brier):
                raise ValueError("WSP180_INVALID_BRIER")
            loss_sums[name] += brier * len(potential)
    if scored_slots == 0:
        raise ValueError("WSP180_NO_SCORED_DESCENDANTS")
    losses = {name: loss_sums[name] / scored_slots for name in ARMS}
    # The best of this SMALL set is not a strongest fully fitted conventional
    # benchmark; broader neural/graphical/recurrent controls are still needed.
    available_controls = ("categorical_conditional", "identity", "uniform")
    best = min(available_controls, key=lambda n: (losses[n], n))
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "original_source_actions_this_call": 0,
        "source_identity_claim": SOURCE_PIN,
        "attested_source_origin": False,
        "scientific_pass": False,
        "fit_events": len(fit),
        "held_events": len(held),
        "fit_rows_digest": _fingerprint(fit),
        "held_rows_digest": _fingerprint(held),
        "held_scored_actions": scored_actions,
        "held_zero_descendant_actions": zero_descendant_actions,
        "held_potential_downstream_slots": scored_slots,
        "brier_per_potential_downstream_object": losses,
        "best_available_restricted_control": best,
        "direct_minus_best_restricted_control": losses["direct_programmed"] - losses[best],
        "full_conventional_control_qualified": False,
        "owner_source_lease_qualified": False,
        "old_law_retention_tested": False,
        "unfamiliar_family_transfer_tested": False,
        "fit_summary": {"direct": direct.summary(),
                        "categorical": conventional.summary()},
    }

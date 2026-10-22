"""Independent source-only Yggdrasil R7 neighbor mechanism falsification.

No generator, training, original scientific first-use or original R7 cohorts.
The 4-cell ring is held to its frozen native source identity by CI.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

from native_cells import Colony, LocalCell

SCHEMA = "mass.ygg.r7.neighbor-mechanism-audit.v1"
SOURCE_BLOB = "4c492a494ac5b25d5e9c49b98185be6a2c966b2f"
PARENT_HEAD = "f3cdabdb3420bb8604e41dda9903ae65eba008e7"
SMOKE_FIXTURES = (
    ((3, 7, 17, 43), (0.7, -2.3, 4.4, -8.6)),
    ((-5, 13, -29, 71), (1.1, 2.4, -4.5, 9.7)),
)
COUNTERFACTUAL_GAINS = (0., 0.03, 0.2, 1.)


def _identity_check():
    src = Path(__file__).with_name("native_cells.py").read_text(encoding="utf-8")
    required = (
        "neighbors=(local[(i-1)%4]+local[(i+1)%4])/2.0",
        "feedback+=own+0.03*neighbors",
        "self.neighbor_messages+=8",
    )
    if not all(pattern in src for pattern in required):
        raise ValueError("MASS_R7_RING_TOPOLOGY_OR_ACCOUNTING_SOURCE_DRIFT")
    # The original SHA1 Git blob identity is separately checked by CI.
    return hashlib.sha256(src.encode("utf-8")).hexdigest()


def _fixture(fast, slow):
    p = Colony()
    # Explicit synthetic state injection is NOT a model fit, and does not
    # use the original R7 generator, Study, learner feedback or held seeds.
    p.cells["A"] = [
        LocalCell(fast=f, slow=s, updates=0)
        for f, s in zip(fast, slow)
    ]
    return p


def _votes(local, gain):
    """Exactly the frozen ring's neighbor aggregate with bounded gain."""
    complete = 0.
    for i, own in enumerate(local):
        neighbors = (local[(i-1) % 4] + local[(i+1) % 4]) / 2.
        complete += own + gain * neighbors
    return complete


def audit():
    src_hash = _identity_check()
    rows = []
    for fi, (fast, slow) in enumerate(SMOKE_FIXTURES):
        p = _fixture(fast, slow)
        for bits in itertools.product((False, True), repeat=4):
            local = [cell.signal(b) for cell, b in zip(p.cells["A"], bits)]
            no_neighbor = sum(local)
            if abs(no_neighbor) <= 0.05:
                # The frozen fixture must avoid near-zero sensitivity to
                # numerical ordering (not silently omit difficult inputs).
                raise AssertionError("MASS_R7_NEAR_TIE_FIXTURE_INVALID")
            original = p.predict("A", bits)
            exact_ring_vote = _votes(local, 0.03)
            if original != (no_neighbor > 0):
                raise AssertionError("MASS_R7_NEIGHBOR_ACTUALLY_CHANGES_DECISION")
            if abs(exact_ring_vote - 1.03*no_neighbor) > 1e-11:
                raise AssertionError("MASS_R7_RING_ALGEBRA_VIOLATED")
            for gain in COUNTERFACTUAL_GAINS:
                if (_votes(local, gain)>0)!=(no_neighbor>0):
                    raise AssertionError("MASS_R7_GAIN_CHANGES_NONZERO_MARGIN_DECISION")
            rows.append({
                "fixture": fi,
                "public_sensors": [int(b) for b in bits],
                "local_sum": no_neighbor,
                "native_predict": original,
                "zero_neighbor_predict": no_neighbor>0,
                "ring_vote": exact_ring_vote,
            })
    if len(rows) != 32:
        raise AssertionError("MASS_R7_FROZEN_CASE_COUNT_DRIFT")
    return {
        "schema": SCHEMA,
        "source_parent": PARENT_HEAD,
        "native_source_git_blob": SOURCE_BLOB,
        "native_source_sha256": src_hash,
        "fixed_manual_cell_states": len(SMOKE_FIXTURES),
        "exhaustive_sensor_vectors_per_state": 16,
        "evaluated_synthetic_counterfactuals": len(rows),
        "max_ring_identity_absolute_rounding_error": max(
            abs(r["ring_vote"] - 1.03*r["local_sum"]) for r in rows
        ),
        "all_original_predictions_match_zero_neighbor": all(
            r["native_predict"] == r["zero_neighbor_predict"] for r in rows
        ),
        "all_neighbor_gains_tested": list(COUNTERFACTUAL_GAINS),
        "exact_ring_algebra": "sum_i(own_i+gain*(left_i+right_i)/2)=(1+gain)*sum_i(own_i)",
        "native_neighbor_messages_counter_source": "8_PER_FEEDBACK_NOT_WIRE_BYTES",
        "scientific_first_use": False,
        "original_r7_training_or_scoring": False,
        "protected_original_H1_H2": False,
        "scientific_disposition":
            "NEIGHBOR_TERM_DECISION_INERT_AT_NONZERO_MARGIN_NATIVE_R7_ONLY",
        "case_sha256": hashlib.sha256(json.dumps(rows, sort_keys=True,
            separators=(",", ":"), allow_nan=False).encode()).hexdigest(),
    }


if __name__ == "__main__":
    print(json.dumps(audit(), sort_keys=True, separators=(",", ":"),
                     allow_nan=False))

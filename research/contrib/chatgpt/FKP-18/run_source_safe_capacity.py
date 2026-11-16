"""FKP-18 exact public witness capacity qualification; no held source.

Only demonstrates that source-safe evidence can yield distinguishable sparse
conditional and event-order representations. No autonomous discovery claim,
owner first-use, new scheduler or native model change.
"""
from __future__ import annotations

import json
import os
from hashlib import sha256
from temporal_trace import SparseTemporalTrace
import source_safe_witness as witness


def _replay(rows, *, context=True, order=True):
    model = SparseTemporalTrace(context_forks=context,temporal_order=order)
    feedback = []
    for index, row in enumerate(rows):
        feedback.extend(model.observe_public(row, event_id=index))
    fresh = SparseTemporalTrace.restore(model.checkpoint())
    if fresh.semantic_receipt() != model.semantic_receipt():
        raise AssertionError("FKP18_COLD_IDENTITY_FAILURE")
    return model, fresh, feedback


def main():
    source = os.environ.get("FKP18_SOURCE_SHA", "")
    if len(source) != 40 or any(ch not in "0123456789abcdef" for ch in source):
        raise ValueError("FKP18_EXACT_SOURCE_SHA_REQUIRED")
    cases = witness.safe_fixed_witnesses()
    a, a_cold, a_fb = _replay(cases["conditional_A"])
    b, b_cold, b_fb = _replay(cases["conditional_B"])
    ab, ab_cold, _ = _replay(cases["temporal_AB"])
    ba, ba_cold, _ = _replay(cases["temporal_BA"])
    noctx_a, _, _ = _replay(cases["conditional_A"],context=False,order=False)
    noctx_b, _, _ = _replay(cases["conditional_B"],context=False,order=False)
    notime_ab, _, _ = _replay(cases["temporal_AB"],order=False)
    notime_ba, _, _ = _replay(cases["temporal_BA"],order=False)
    conditional_ok = (
        a.semantic_receipt() != b.semantic_receipt() and
        a.predict_delta(witness.STATE, 3, 3) == 1 and
        b.predict_delta(witness.STATE, 3, 3) == -1)
    temporal_ok = (ab.semantic_receipt() != ba.semantic_receipt() and
                   ab.observed_order_trace() != ba.observed_order_trace())
    negative_ablations = (
        noctx_a.semantic_receipt() == noctx_b.semantic_receipt() and
        noctx_a.predict_delta(witness.STATE,3,3) is None and
        noctx_b.predict_delta(witness.STATE,3,3) is None and
        notime_ab.semantic_receipt() == notime_ba.semantic_receipt())
    bounded = all(m.learned_relation_slots <=512 and
                  m.logical_learned_bytes <=65536
                  for m in (a,b,ab,ba))
    cold = all(f.semantic_receipt()==m.semantic_receipt()
               for m,f in ((a,a_cold),(b,b_cold),(ab,ab_cold),(ba,ba_cold)))
    if not all((conditional_ok,temporal_ok,negative_ablations,bounded,cold)):
        raise AssertionError("FKP18_PUBLIC_CAPACITY_GATE_FAIL")
    summary={
        "schema":"fkp18.source-safe-temporal-capacity.v1",
        "source_commit":source,
        "prereg_first":"1a53f16231871d2ac6db0b25e0e9a8ab61b03b60",
        "classification":"ENGINEERING_REPRESENTATION_PROBE_ONLY",
        "conditional_law_A_effect":a.predict_delta(witness.STATE,3,3),
        "conditional_law_B_effect":b.predict_delta(witness.STATE,3,3),
        "conditional_witness_public_reward":[cases["conditional_A"][0].reward,
                                            cases["conditional_B"][0].reward],
        "conditional_context_split_seen":all(any(e[0]=="CONTEXT_FORK" for e in events)
                                             for events in (a_fb,b_fb)),
        "candidate_no_conditional_alias":conditional_ok,
        "candidate_no_order_alias":temporal_ok,
        "matched_ablation_expected_alias":negative_ablations,
        "cold_restore":cold,
        "capacity_bounded":bounded,
        "logical_learned_bytes":[a.logical_learned_bytes,b.logical_learned_bytes,
                                 ab.logical_learned_bytes,ba.logical_learned_bytes],
        "public_observations_per_case":2,
        "original_held_dev_opened":False,
        "reserved_transfer_opened":False,
        "actual_onpolicy_unfamiliar_return":None,
        "scientific_pass":False,
        "native_promoted":False
    }
    print("FKP18_SOURCE_SAFE_CAPACITY_PROOF="+json.dumps(summary,
            sort_keys=True,separators=(",",":")))
    return summary


if __name__=="__main__":
    main()

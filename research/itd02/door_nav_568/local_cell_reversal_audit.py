"""Matched R7 original, adaptive local-cell, and conventional recency.

Actual native cells receive the same completed public action observations
as the comparator. Reversed relationships must be learned through feedback,
not supplied to either model as an oracle or private regime ID.
"""
import json
from time import process_time_ns
from native_cells_r7 import Colony
from local_cell_reversal_candidate import ReversalColony
from sliding_tabular_control import SlidingTabularControl
from native_cell_recency_bridge_audit import public_context, public_features
from multi_regime_online_comparison import REGIMES, KEYS, deep_bytes
from two_hop_evidence_audit import build

def measure(repeats=2):
    archive = dict(build().archived_links)
    prior = Colony()
    candidate = ReversalColony()
    conventional = SlidingTabularControl(capacity=128)
    rows = []
    timings = {"prior":0,"candidate":0,"control":0}
    for name, successors in REGIMES:
        truth = [value == archive[key] for key,value in zip(KEYS,successors)]
        for _ in range(repeats):
            for key,label in zip(KEYS,truth):
                ctx, bits = public_context(key), public_features(key)
                begin = process_time_ns()
                prior.learn_completed_public_feedback(ctx,bits,label,2)
                timings["prior"] += process_time_ns()-begin
                begin = process_time_ns()
                candidate.learn_completed_public_feedback(ctx,bits,label,2)
                timings["candidate"] += process_time_ns()-begin
                begin = process_time_ns()
                conventional.observe(key,b"1" if label else b"0")
                timings["control"] += process_time_ns()-begin
        def grade(values):
            return {
                "correct":sum(v is not None and v==t for v,t in zip(values,truth)),
                "wrong":sum(v is not None and v!=t for v,t in zip(values,truth)),
                "abstentions":sum(v is None for v in values),
            }
        rows.append({
            "name":name,
            "actions":repeats*len(KEYS),
            "prior":grade([prior.predict(public_context(k),public_features(k)) for k in KEYS]),
            "candidate":grade([candidate.predict_public(public_context(k),public_features(k)) for k in KEYS]),
            "control":grade([None if (v:=conventional.predict(k)) is None else v==b"1" for k in KEYS]),
        })
    saved=candidate.checkpoint()
    restored=ReversalColony.restore(saved)
    return {
        "stages":rows,
        "actions":sum(row["actions"] for row in rows),
        "updates":candidate.feedback_updates,
        "neighbor_messages":candidate.neighbor_messages,
        "control_examples":conventional.examples,
        "cpu_ns":timings,
        "candidate_checkpoint_bytes":len(saved),
        "prior_checkpoint_bytes":len(prior.checkpoint()),
        "control_table_bytes":deep_bytes(conventional.table),
        "cold_restore_exact":all(
            candidate.predict_public(public_context(k),public_features(k)) ==
            restored.predict_public(public_context(k),public_features(k)) for k in KEYS),
        "archive_unchanged":archive == build().archived_links,
    }

def run():
    return {
        "two_observations":measure(2),
        "one_observation":measure(1),
        "scope":"Synthetic completed-public-feedback native R7 local cells versus R7 original and independent adaptive table",
        "limitation":"Binary public change prediction with handcrafted sensory mapping; not a full successor learner or retail-hardware measurement.",
    }

if __name__ == "__main__":
    print(json.dumps(run(),sort_keys=True))

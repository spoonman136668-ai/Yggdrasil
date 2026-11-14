"""AAI-10B bounded synthetic-only matched dev cost and exact-state witness.

Never touches preregistered scientific DEV/TRANSFER/NEGATIVE world numbers.
Resource threshold is frozen in prereg.json; no parameter tuning on outcome.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import statistics
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "AAI-10P"))
sys.path.insert(0, str(HERE.parent / "AAI-10A"))
sys.path.insert(0, str(HERE))
import benchmark as b
import models as old
import cached as fast

NREPS = 3
EVIDENCE = tuple(
    row
    for law in ("A", "B")
    for rep in range(4)
    for i,x in enumerate(b.INPUTS)
    for row in (lambda s,action: (s,b.public_step(law,s,action)))(
        b.public_initial(law,x,((rep+i)%2,rep%2)),
        b.ACTIONS[(rep+i)%6])
)
assert len(EVIDENCE)==128
TARGETS = tuple(b.public_initial("A",x,(1,0)) for x in b.INPUTS[:4])


def evaluate(name):
    runs = []
    truths = []
    last_bytes = None
    for _ in range(NREPS):
        learner = fast.CachedOperatorBank() if name=="cache_candidate" else old.create(name)
        tick = time.perf_counter()
        for row in EVIDENCE:
            learner.learn(row)
        training = time.perf_counter()-tick
        tick = time.perf_counter()
        state = old.canonical(learner.state())
        restored = (fast.cold_clone(state) if name=="cache_candidate" else
                    old.cold_restore({name: state})[name])
        checkpoint_seconds = time.perf_counter()-tick
        assert old.canonical(restored.state()) == state
        tick = time.perf_counter()
        actions = [restored.choose(target) for target in TARGETS for _ in range(3)]
        decision_seconds = time.perf_counter()-tick
        assert all(action is None or action in b.ACTIONS for action in actions)
        truth = old.canonical(actions)
        if truths and truths[-1]!=truth:
            raise ValueError("within-platform planning nondeterminism")
        truths.append(truth)
        last_bytes=len(state.encode())
        runs.append({
            "train_seconds":training,
            "checkpoint_seconds":checkpoint_seconds,
            "decision_seconds":decision_seconds,
            "whole_seconds":training+checkpoint_seconds+decision_seconds,
        })
    return {
        "median_seconds":round(statistics.median(r["whole_seconds"] for r in runs),6),
        "median_train_seconds":round(statistics.median(r["train_seconds"] for r in runs),6),
        "median_checkpoint_seconds":round(statistics.median(r["checkpoint_seconds"] for r in runs),6),
        "median_decision_seconds":round(statistics.median(r["decision_seconds"] for r in runs),6),
        "model_bytes":last_bytes,
        "decisions_sha256":hashlib.sha256(truths[0].encode()).hexdigest(),
    }


def execute():
    prereg=json.loads((HERE/"prereg.json").read_text())
    assert prereg["id"]=="AAI-10B" and prereg["authority"]["science_first_use"] is False
    measured={name:evaluate(name) for name in (*old.NAMES,"cache_candidate")}
    # Exact parity is assessed across entire prefix in test_cached.py as well.
    assert (measured["candidate"]["decisions_sha256"] ==
            measured["cache_candidate"]["decisions_sha256"])
    assert (measured["candidate"]["model_bytes"] ==
            measured["cache_candidate"]["model_bytes"])
    fastest=min(old.MATCHED,key=lambda name:measured[name]["median_seconds"])
    candidate=measured["cache_candidate"]["median_seconds"]
    oldtime=measured["candidate"]["median_seconds"]
    fasttime=measured[fastest]["median_seconds"]
    ratio=candidate/max(fasttime,1e-12)
    gain=oldtime/max(candidate,1e-12)
    return {
        "schema":"yggdrasil.contrib.aai10b.mechanical-cost.v1",
        "source_phase":"SYNTHETIC_DEV_ONLY_NO_SCIENTIFIC_FIRST_USE",
        "evidence_rows":len(EVIDENCE),"decisions_per_method":12,
        "repeats":NREPS,"science_cohorts_consumed":0,
        "candidate_source_unchanged":True,
        "identical_snapshot_bytes_and_12_actions":True,
        "best_matched":fastest,
        "methods":measured,
        "optimized_over_fastest_matched":round(ratio,6),
        "old_AAI10A_over_optimized":round(gain,6),
        "2x_compute_gate_pass":ratio<=2.,
        "classification":"SOURCE_ONLY_EFFICIENCY_PASS_PENDING_SCIENCE" if ratio<=2.
                       else "SOURCE_ONLY_EFFICIENCY_NO_GO_NO_SCIENCE",
        "model_integration":"NONE",
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--dev",action="store_true")
    parser.add_argument("--primary",action="store_true")
    args=parser.parse_args()
    if args.primary:
        parser.error("AAI-10B SCIENTIFIC FIRST USE DISARMED")
    if not args.dev:
        parser.error("only synthetic DEV probe permitted")
    print("AAI10B_DEV_PROFILE="+json.dumps(execute(),sort_keys=True),flush=True)


if __name__=="__main__":
    main()

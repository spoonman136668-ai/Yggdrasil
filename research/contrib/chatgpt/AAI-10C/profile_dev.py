"""AAI-10C preregistered mechanical-only compute comparison.

No DEV/TRANSFER/NEGATIVE world IDs, source simulator hidden labels for learners,
model scientific first use, or source/runner scheduling integration.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import statistics
import sys
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parent/"AAI-10P"))
sys.path.insert(0,str(HERE.parent/"AAI-10A"))
import benchmark as b
import models as conventional
import compact as new

EVIDENCE=tuple(
    row for law in ("A","B") for rep in range(4) for i,x in enumerate(b.INPUTS)
    for row in (lambda p,a:(p,b.public_step(law,p,a)))(
        b.public_initial(law,x,((rep+i)%2,rep%2)),b.ACTIONS[(rep+i)%6])
)
TARGETS=tuple(b.public_initial("A",x,(1,0)) for x in b.INPUTS[:4])
REPS=3
assert len(EVIDENCE)==128 and len(TARGETS)==4


def eval_method(name):
    series=[]
    summary=None
    for _ in range(REPS):
        model=(new.BoundedCausalSignatureBank() if name=="aai10c" else
               new.BoundedCausalSignatureBank(1) if name=="one_slot_c" else
               conventional.create(name))
        t=time.perf_counter()
        for event in EVIDENCE:
            model.learn(event)
        train=time.perf_counter()-t
        t=time.perf_counter()
        if name in ("aai10c","one_slot_c"):
            snap=new.checkpoint(model)
            restored=new.cold_restore(snap)
            assert new.checkpoint(restored)==snap
        else:
            snap=conventional.canonical(model.state())
            restored=conventional.cold_restore({name:snap})[name]
            assert conventional.canonical(restored.state())==snap
        checkpoint=time.perf_counter()-t
        t=time.perf_counter()
        results=[restored.choose(p) for p in TARGETS for _ in range(3)]
        inference=time.perf_counter()-t
        assert all(v is None or v in b.ACTIONS for v in results)
        digest=hashlib.sha256(conventional.canonical({"state":snap,"actions":results}).encode()).hexdigest()
        if summary is not None:
            assert summary["trace_sha256"]==digest
        summary={"trace_sha256":digest,"model_bytes":len(snap.encode())}
        series.append({"training":train,"checkpoint":checkpoint,
                       "inference":inference,"whole":train+checkpoint+inference})
    return {"median_whole_seconds":round(statistics.median(z["whole"] for z in series),7),
            "median_train_seconds":round(statistics.median(z["training"] for z in series),7),
            "median_checkpoint_seconds":round(statistics.median(z["checkpoint"] for z in series),7),
            "median_inference_seconds":round(statistics.median(z["inference"] for z in series),7),
            **summary}


def mechanical_profile():
    prereg=json.loads((HERE/"prereg.json").read_text("utf8"))
    assert prereg["id"]=="AAI-10C" and not prereg["future_science"]["first_use_authorized"]
    names=(*conventional.NAMES,"aai10c")
    output={n:eval_method(n) for n in names}
    fastest=min(conventional.MATCHED,key=lambda n:output[n]["median_whole_seconds"])
    base=output[fastest]["median_whole_seconds"]
    candidate=output["aai10c"]["median_whole_seconds"]
    ratio=candidate/max(base,1e-12)
    memory_ok=output["aai10c"]["model_bytes"]<=output[fastest]["model_bytes"]
    ok=ratio<=2.0 and memory_ok
    return {"schema":"yggdrasil.contrib.aai10c.mechanical-dev-profile.v1",
            "phase":"SYNTHETIC_ONLY_NO_SCIENCE_FIRST_USE",
            "source_learner":"bounded_causal_signature",
            "methods":output,"fastest_conventional":fastest,
            "candidate_over_fastest":round(ratio,6),
            "candidate_bytes_vs_fastest":{ "candidate":output["aai10c"]["model_bytes"],
                                          "conventional":output[fastest]["model_bytes"]},
            "two_x_compute_gate":ratio<=2.0,
            "memory_gate":memory_ok,
            "development_admission":("DEV_EFFICIENCY_PASS_SCIENCE_UNVERIFIED" if ok
                                     else "DEV_EFFICIENCY_NO_GO"),
            "public_events":len(EVIDENCE),"decision_requests":len(TARGETS)*3,
            "repetitions":REPS,"one_slot_ablation":"SOURCE_TEST_ONLY_96_ROW_CAP_NO_UNEQUAL_EVIDENCE_TIMING",
            "science_cohorts_used":0,"native_model_modified":False}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--dev",action="store_true")
    p.add_argument("--primary",action="store_true")
    args=p.parse_args()
    if args.primary:
        p.error("AAI-10C SCIENTIFIC FIRST USE DISARMED: no authorized science runner")
    if not args.dev:
        p.error("only synthetic mechanical resource test supported")
    print("AAI10C_MECHANICAL_PROFILE="+json.dumps(mechanical_profile(),sort_keys=True),flush=True)


if __name__=="__main__":
    main()

"""WSP-35 deterministic DEV/PRIMARY; primary is called only after frozen prereg commit."""
import hashlib
import json
import platform
import sys
import time
from pathlib import Path
from model import GATES,N_INPUTS,NumericCircuit,GateTrainCache,MASKS,table,source_spec

ROOT=Path(__file__).resolve().parent
TARGETS=tuple(tuple((i>>k)&1 for k in range(3)) for i in range(8))
FROZEN_PRIMARY=256
FROZEN_DEV=64

def digest(cohort,w,g):
    return hashlib.sha256(("WSP35-V1|"+cohort+"|"+str(w)+"|"+str(g)).encode("ascii")).digest()

def generate(cohort,w):
    if cohort not in ("DEV","PRIMARY") or type(w) is not int or not 0<=w<(FROZEN_DEV if cohort=="DEV" else FROZEN_PRIMARY):
        raise ValueError("WSP35_BAD_COHORT")
    spec=[]
    for i in range(GATES):
        d=digest(cohort,w,i)
        a=d[1]%3 if i==0 else (3+i-2 if cohort=="PRIMARY" and i>1 and i%2 else 3+i-1)
        b=d[2]%(3+i)
        spec.append((a,b,table(MASKS[d[0]%len(MASKS)])))
    return source_spec(tuple(spec))

def oracle(spec,x):
    """Evaluator-only symbolic truth-table interpreter, independent of VM weights."""
    source_spec(spec)
    values=list(x)
    for a,b,truth in spec:
        values.append(truth[2*values[a]+values[b]])
    return values[-1]

def noncomposing_lookup(spec,x):
    return spec[-1][2][2*x[0]+x[1]]

def run(cohort):
    if cohort not in ("DEV","PRIMARY"):
        raise ValueError("WSP35_BAD_COHORT")
    started=time.perf_counter()
    count=FROZEN_DEV if cohort=="DEV" else FROZEN_PRIMARY
    train=GateTrainCache()
    score=dict(direct=0,blank=0,lookup_only=0,conventional=0,oracle=0)
    checks=dict(worlds=0,cold=0,weight_replays=0,source_replays=0,oracle_parity=0,target_labels=0)
    trace=hashlib.sha256()
    max_bytes=0
    for world in range(count):
        spec=generate(cohort,world)
        written=NumericCircuit.synthesize(spec)
        checkpoint=written.snapshot()
        model=NumericCircuit.restore(checkpoint)
        empty=NumericCircuit()
        fitted=train.trained_circuit(spec)
        if model.snapshot()!=checkpoint or model.rows!=written.rows:
            raise AssertionError("WSP35_COLD_LOST_WEIGHTS")
        if written.snapshot()!=NumericCircuit.synthesize(spec).snapshot():
            raise AssertionError("WSP35_SOURCE_NONDETERMINISM")
        checks["cold"]+=1
        checks["weight_replays"]+=1
        checks["source_replays"]+=1
        max_bytes=max(max_bytes,len(checkpoint))
        for x in TARGETS:
            truth=oracle(spec,x)
            predictions=dict(direct=model.predict(x),blank=empty.predict(x),lookup_only=noncomposing_lookup(spec,x),conventional=fitted.predict(x),oracle=truth)
            if predictions["direct"]!=truth:
                raise AssertionError("WSP35_DIRECT_ORACLE_MISMATCH")
            checks["oracle_parity"]+=1
            for name,y in predictions.items():
                score[name]+=int(y==truth)
            trace.update(json.dumps([world,x,predictions],sort_keys=True,separators=(",",":")).encode("ascii"))
            checks["target_labels"]+=1
        checks["worlds"]+=1
    labels=count*8
    exact=checks["worlds"]==count and checks["target_labels"]==labels and checks["oracle_parity"]==labels
    exact=exact and train.worst_bce<=0.01 and train.fresh_fits+train.hits==count*GATES
    threshold=1843 if cohort=="PRIMARY" else 461
    margin=205 if cohort=="PRIMARY" else 52
    delta=min(score["direct"]-score["blank"],score["direct"]-score["lookup_only"])
    if not exact:
        classification="INVALID"
    elif score["direct"]>=threshold and delta>=margin:
        classification="DEV_SUPPORTED"
    elif delta>0:
        classification="MIXED"
    else:
        classification="SCIENTIFIC_NEGATIVE"
    result={
        "schema":"wsp35.direct-blank-circuit.v1","cohort":cohort,
        "scientific_status":classification,
        "engineering":"PASS" if exact else "FAIL",
        "scores":score,"denominator":labels,"min_null_gain":delta,
        "threshold_correct":threshold,"threshold_null_gain":margin,
        "checks":checks,"capacity":{"writable_bits":GATES*(2*(N_INPUTS+GATES)+4+1),
           "runtime":"fixed numerical one-hot and truth-LUT arithmetic, Python host counted separately",
           "checkpoint_max_bytes":max_bytes},
        "conventional":{"fresh_converged_fits":train.fresh_fits,"cache_hits":train.hits,
          "actual_gradient_updates":train.updates,"max_bce":train.worst_bce,
          "note":"same topology and primitive evidence, but sigmoid floats and costs differ"},
        "trace_sha256":trace.hexdigest(),
        "seconds":round(time.perf_counter()-started,6),
        "environment":{"python":sys.version,"platform":platform.platform()},
        "limits":"The source supplies ALL primitive truth tables and topology. This proves compilation/replay fidelity in an authored tiny task, NOT inference of unknown rules, whole intelligence or a matched-cost speedup."
    }
    if not exact:
        raise AssertionError("WSP35_INVALID_ASSAY")
    return result

if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--cohort",choices=("DEV","PRIMARY"),default="DEV")
    args=parser.parse_args()
    print(json.dumps(run(args.cohort),sort_keys=True,indent=2))

"""CKAD42-ENG fixture-only portable learned checkpoint diagnostic.

This script NEVER invokes CKAD42 run(seed), CKAD39's world generator,
reserved held cohorts, or any scientific original seed. Its deterministic
small binary events exist only to qualify the persistence encoding.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import math
import sys
import time
from pathlib import Path

from yggdrasil.native_context_basis import canonical, digest

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/"CKAD-42"/"campaign.py"
spec=importlib.util.spec_from_file_location("ckad42_engineering_fixture_source",SOURCE)
M=importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

SCHEMA="yggdrasil.ckad42.engineering-portable-checkpoint-fixtures.v1"
FIXTURE_KINDS=("cycle","rule_shift","action_interactions")
CHECKPOINT_POINTS=(160,320,480)
PROTOCOL_COMMIT="30700bf17c75f1ef18354b82169f3b03c18c7b95"
FORBIDDEN_SCIENCE_SEEDS=(42111,42112,42211,42212,42311,42312,42313)


def fixture_event(kind,t):
    if kind not in FIXTURE_KINDS or type(t) is not int or not 0<=t<512:
        raise ValueError("CKAD42_ENG_FIXTURE_INPUT")
    # All fixture values are exact deterministic integers, separate from any
    # consumed or reserved CKAD research generator, seed, or source identity.
    byte=hashlib.sha256(f"ckad42-eng-fixture-v1|{kind}|{t}".encode()).digest()
    c=(byte[0]>>1)&1
    x1=(byte[1]^(t//3))&1
    x2=(byte[2]^(t//5))&1
    if kind=="cycle":
        true=(c^x1)
        terminal=(c&x1)^(true&x2)
    elif kind=="rule_shift":
        switch= int(112<=t<240 or 352<=t<416)
        true=(c^x1)^switch
        terminal=((c&x1)^(true&x2)) if not switch else ((c&true)|(x1&x2))
    else:
        true=((c & x1) ^ (x2 & (t&1)))
        terminal=((c^x1)&(true|x2))^((t>>3)&1)
    # Witnessed simulated consequence (not private held data).
    s2=true^(int(byte[3]<18))
    y=terminal^(int(byte[4]<24))
    identifier=hashlib.sha256(f"ckad42-eng-fixture-event|{kind}|{t}".encode()).hexdigest()
    views=((c,(byte[5]&1)),(c,(byte[6]&1)))
    row={"s1":c,"x1":x1,"s2":s2,"x2":x2,"y":y}
    return identifier,views,row


def _raw_state(model):
    """Replicate original JSON layout to localize drift before normalization."""
    return canonical({"schema":M.SCHEMA,
        "transition":{"bits":2,"full":model.transition.full,"short":model.transition.short,"n":model.transition.n},
        "terminal":{"bits":4,"full":model.terminal.full,"short":model.terminal.short,"n":model.terminal.n},
        "mask_transition":{"bits":2,"full":model.mask_transition.full,"short":model.mask_transition.short,"n":model.mask_transition.n},
        "mask_terminal":{"bits":4,"full":model.mask_terminal.full,"short":model.mask_terminal.short,"n":model.mask_terminal.n},
        "hedge":model.hedge,"n":model.n,"receipts":model.receipts})


def forecast_grid(model):
    entries=[]
    for context in (0,1):
        for first in (0,1):
            view=(context,1-context)
            for mode in ("full","short","dual","no_action"):
                entries.append((mode,context,first,None,None,model.read(mode,view,first)))
                for next_state in (0,1):
                    for second in (0,1):
                        entries.append((mode,context,first,next_state,second,
                                       model.read(mode,view,first,next_state,second)))
    return entries


def _max_forecast_error(before,after):
    if len(before)!=len(after):
        raise AssertionError("CKAD42_ENG_GRID_LENGTH")
    maximum=0.0
    for a,b in zip(before,after):
        if a[:5]!=b[:5]:
            raise AssertionError("CKAD42_ENG_GRID_LABEL")
        maximum=max(maximum,abs(a[5]-b[5]))
    return maximum


def _component_sha(model):
    frozen=json.loads(model.checkpoint())
    return {key:digest(canonical(frozen[key])) for key in
            ("transition","terminal","mask_transition","mask_terminal","hedge","receipts")}


def fixture_case(kind):
    if kind not in FIXTURE_KINDS:
        raise ValueError("CKAD42_ENG_UNREGISTERED_FIXTURE")
    started=time.perf_counter()
    model=M.NativeInterventionRelations()
    initial_identity=model.checkpoint()
    samples=[]
    for t in range(max(CHECKPOINT_POINTS)):
        identifier,views,row=fixture_event(kind,t)
        pre=model.checkpoint()
        # Forecast read must not change weights, source receipts or eligibility.
        before_forecast=model.read("dual",views[0],row["x1"])
        after_transition_forecast=model.read("dual",views[0],row["x1"],row["s2"],row["x2"])
        if not 0<before_forecast<1 or not 0<after_transition_forecast<1:
            raise AssertionError("CKAD42_ENG_FORECAST_BOUND")
        if model.checkpoint()!=pre:
            raise AssertionError("CKAD42_ENG_READ_MUTATED")
        model.observe(identifier,views,row)
        if model.n!=t+1:
            raise AssertionError("CKAD42_ENG_MISSING_OBSERVATION")
        if (t+1) in CHECKPOINT_POINTS:
            raw=model.checkpoint()
            frozen=M.NativeInterventionRelations.restore(raw,digest(raw))
            if frozen.checkpoint()!=raw or frozen.n!=model.n:
                raise AssertionError("CKAD42_ENG_COLD_NOT_EXACT")
            error=_max_forecast_error(forecast_grid(model),forecast_grid(frozen))
            if error!=0.0:
                raise AssertionError("CKAD42_EXACT_COLD_FORECAST_CHANGED")
            samples.append({"observed_events":t+1,
                "portable_checkpoint_sha256":digest(raw),
                "raw_float_checkpoint_sha256":digest(_raw_state(model)),
                "component_sha256":_component_sha(model),
                "checkpoint_bytes":len(raw),
                "max_cold_forecast_error":error,
                "cold_exact":True,
                "portable_weights_equal_to_original_in_memory":raw==_raw_state(model)})
    if len(samples)!=len(CHECKPOINT_POINTS):
        raise AssertionError("CKAD42_ENG_INCOMPLETE_CHECKPOINT_POINTS")
    latest=fixture_event(kind,max(CHECKPOINT_POINTS)-1)
    before=model.checkpoint()
    if model.observe(*latest) is not model or before!=model.checkpoint():
        raise AssertionError("CKAD42_ENG_DUPLICATE_NONIDEMPOTENT")
    tampered=dict(latest[2])
    tampered["y"]^=1
    try:
        model.observe(latest[0],latest[1],tampered)
    except ValueError:
        pass
    else:
        raise AssertionError("CKAD42_ENG_CONFLICT_ACCEPTED")
    if before!=model.checkpoint():
        raise AssertionError("CKAD42_ENG_CONFLICT_MUTATED")
    return {"fixture":kind,"source_events":model.n,
            "original_empty_sha256":digest(initial_identity),
            "samples":samples,"source_only":True,
            "duplicate_idempotent":True,"conflict_atomic":True,
            "checkpoint_precision_error_at_most":0.0,
            "elapsed_wall_seconds":round(time.perf_counter()-started,6)}


def run():
    cases=[fixture_case(kind) for kind in FIXTURE_KINDS]
    report={
       "schema":SCHEMA,
       "source":"CKAD42 engineering-only synthetic fixture; no original scientific seed or hidden consequence",
       "protocol_commit":PROTOCOL_COMMIT,
       "cases":cases,
       "fixture_count":len(cases),
       "checkpoint_points":list(CHECKPOINT_POINTS),
       "scientific_original_dev_replayed":False,
       "original_pilots_scored":False,
       "original_primary_scored":False,
       "full_final_regression":False,
       "engineering_fixture_pass":True
    }
    print("CKAD42_ENG_FIXTURE_REPORT="+json.dumps(report,sort_keys=True,separators=(",",":")))
    return report


if __name__=="__main__":
    run()

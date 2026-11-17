"""WSP156 source-free fabricated intervention-budget comparison.

This is NOT an independently owned causal world or scientific first use.
No held labels are made available to the native partial projector.
"""
from __future__ import annotations

from hashlib import sha256
from itertools import product
from time import perf_counter_ns, process_time_ns

from yggdrasil.native_evidence_compiler import canonical_json,digest
from yggdrasil.native_partial_sixbit_projection import (
    SCHEMA,stage_partial_sixbit_bundle
)
from yggdrasil.native_relation_memory import NativeRelationMemory

WORLD_COUNT=24
ON_COUNT=12
ACTIONS_PER_ARM=32
POLICIES=("paired","fixed_balanced","sha_random")

def _rank(tag,world,value):
    return sha256(("WSP156|FAKE|"+tag+"|"+str(world)+"|"+str(value)).encode()).digest()

def schedule(policy,world):
    if type(world) is not int or not 0<=world<WORLD_COUNT:
        raise ValueError("WSP156_WORLD_ID_INVALID")
    if policy=="paired":
        contexts=tuple(sorted(range(16),key=lambda x:(_rank("PAIRED",world,x),x))[:8])
        xs=[c|(n<<4)|(a<<5) for c,a,n in product(contexts,(0,1),(0,1))]
    elif policy=="fixed_balanced":
        xs=[c|(n<<4)|(a<<5) for c,a,n in product(range(8),(0,1),(0,1))]
    elif policy=="sha_random":
        xs=sorted(range(64),key=lambda x:(_rank("RANDOM",world,x),x))[:32]
    else:
        raise ValueError("WSP156_POLICY_INVALID")
    result=tuple(sorted(xs))
    assert len(result)==32 and len(set(result))==32
    return result

def _private_fixture_effect(world,mask):
    """Call ONLY after an action is actually selected by an arm."""
    context=mask&15
    nuisance=(mask>>4)&1
    action=(mask>>5)&1
    base=(action ^ (context&1)
          ^ (((context>>1)&1)&((context>>2)&1))
          ^ (((context>>3)&1)&((world>>1)&1))
          ^ (world&1))
    # Out-of-family world: one action-context pair is nuisance-dependent,
    # possibly not among paid queries. Source owner identity NOT asserted.
    if world>=ON_COUNT and context==(world*7+3)%16:
        return base ^ nuisance
    return base

def make_doc(world,policy):
    effects=schedule(policy,world)
    return {
        "schema":SCHEMA,
        "source_id":"wsp156-fake-"+str(world)+"-"+policy,
        "source_mode":"engineering_fixture_only",
        "source_kind":"observed_public_intervention",
        "license":"synthetic-fixture",
        "slot":0,"action_bit":5,"nuisance_bit":4,
        "records":[[x,_private_fixture_effect(world,x),
                    "observed_do","w156:paid:"+str(world)+":"+policy+":"+str(x)]
                   for x in effects]
    }

def independent_symbolic(doc):
    """Separate exact dict proof using only this arm's 32 paid outcomes."""
    records={row[0]:row[1] for row in doc["records"]}
    complete={}
    incomplete=0
    missing=0
    conflict=False
    for context in range(16):
        for action in (0,1):
            masks=(context|(action<<5),context|(action<<5)|(1<<4))
            vals=[records.get(m) for m in masks]
            if any(v is None for v in vals):
                if all(v is None for v in vals):missing+=1
                else:incomplete+=1
            elif vals[0]!=vals[1]:
                conflict=True
            else:
                complete[context,action]=vals[0]
    if conflict:
        return {"rejected":True,"decisions":(None,)*16,
                "certified_native":None,"half":incomplete,"missing":missing}
    decisions=[]
    for c in range(16):
        a,b=complete.get((c,0)),complete.get((c,1))
        decisions.append(None if a is None or b is None or a==b
                         else 0 if a>b else 1)
    return {"rejected":False,"decisions":tuple(decisions),
            "certified_native":len(complete),
            "half":incomplete,"missing":missing}

def study():
    clock_wall=perf_counter_ns()
    clock_cpu=process_time_ns()
    summary={policy:{"on_certified_actions":0,"on_certified_native":0,
                     "off_rejections":0,"off_unknown_not_rejected":0,
                     "off_certified_actions":0,
                     "source_paid_effects":0} for policy in POLICIES}
    trace=[]
    for world in range(WORLD_COUNT):
        for policy in POLICIES:
            doc=make_doc(world,policy)
            rows=doc["records"]
            ctrl=independent_symbolic(doc)
            raw=canonical_json(doc)
            try:
                candidate=stage_partial_sixbit_bundle(raw,digest(raw))
            except ValueError as exc:
                if str(exc)!="WSP156_WITNESSED_NUISANCE_CONTRADICTION":
                    raise
                if not ctrl["rejected"]:
                    raise AssertionError("WSP156_SPURIOUS_CONTRADICTION")
                candidate=None
            if (candidate is None)!=ctrl["rejected"]:
                raise AssertionError("WSP156_SYMBOLIC_REJECTION_MISMATCH")
            scores=summary[policy]
            scores["source_paid_effects"]+=len(rows)
            measured={"world":world,"policy":policy,
                      "charged":len(rows),"source_sha256":digest(raw),
                      "rejected":candidate is None}
            if candidate is None:
                if world<ON_COUNT:
                    raise AssertionError("WSP156_ON_FAMILY_SOURCE_REFUSED")
                scores["off_rejections"]+=1
                measured["certified_actions"]=None
            else:
                if candidate.verified_actions!=ctrl["decisions"]:
                    raise AssertionError("WSP156_EXACT_SYMBOLIC_PARITY_FAILURE")
                if candidate.receipt["certified_native_observations"]!=ctrl["certified_native"]:
                    raise AssertionError("WSP156_CERTIFIED_COORDINATE_MISMATCH")
                if candidate.receipt["single_nuisance_observations"]!=ctrl["half"]:
                    raise AssertionError("WSP156_PARTIAL_COORDINATE_MISMATCH")
                if candidate.receipt["unobserved_native_coordinates"]!=ctrl["missing"]:
                    raise AssertionError("WSP156_UNOBSERVED_COORDINATE_MISMATCH")
                restored=NativeRelationMemory.restore(candidate.checkpoint)
                if restored.checkpoint()!=candidate.checkpoint:
                    raise AssertionError("WSP156_COLD_REPLAY_MISMATCH")
                certified=sum(x is not None for x in candidate.verified_actions)
                measured["certified_actions"]=certified
                measured["native_sha256"]=digest(candidate.checkpoint)
                if world<ON_COUNT:
                    scores["on_certified_actions"]+=certified
                    scores["on_certified_native"]+=ctrl["certified_native"]
                else:
                    scores["off_unknown_not_rejected"]+=1
                    scores["off_certified_actions"]+=certified
            trace.append(measured)
    on_paired=summary["paired"]["on_certified_actions"]
    on_fixed=summary["fixed_balanced"]["on_certified_actions"]
    on_random=summary["sha_random"]["on_certified_actions"]
    per_world_gain=(on_paired-on_random)/ON_COUNT
    success=(on_paired==96 and on_fixed==96 and per_world_gain>=4
             and all(x["source_paid_effects"]==WORLD_COUNT*ACTIONS_PER_ARM
                     for x in summary.values()))
    return {
        "classification":("SOURCEFREE_PARTIAL_NATIVE_OBSERVATION_SUPPORTED"
                          if success else "SOURCEFREE_PARTIAL_NATIVE_OBSERVATION_NO_GO"),
        "worlds":WORLD_COUNT,"on_worlds":ON_COUNT,"off_worlds":WORLD_COUNT-ON_COUNT,
        "source_paid_total":WORLD_COUNT*len(POLICIES)*ACTIONS_PER_ARM,
        "source_paid_per_arm_world":ACTIONS_PER_ARM,
        "paired_gain_vs_random_contexts_per_on_world":round(per_world_gain,6),
        "scores":summary,
        "source_trace_sha256":digest(canonical_json(trace)),
        "science_pass":False,"native_admission":False,
        "wall_s":round((perf_counter_ns()-clock_wall)/1e9,6),
        "cpu_s":round((process_time_ns()-clock_cpu)/1e9,6)
    }

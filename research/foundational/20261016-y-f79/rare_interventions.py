"""F79 preregistered role-aware rare public memory intervention learner.

The offline teacher uses later public events and TRAIN questions ONLY on
unregistered negative-seed synthetic TRAIN cases. The online controller
receives solely causal public source candidates, current lossless memory,
and frozen 28 signed-int8 weights. Strong F60 remains exact default.
"""
from __future__ import annotations
import collections
import hashlib
import importlib.util
import json
import math
import pathlib
import sys

P=pathlib.Path(__file__).resolve().parent

def blob(path):
    raw=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()

def load(name,path,expected):
    assert blob(path)==expected,("F79_TRANSITIVE_SOURCE_DRIFT",name)
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module

assert blob(P/"prereg.json")=="90edd72c6457e0e2763f1fac8b52a3ace6c8b2b6"
SOURCE=load("f79_exact_F76_two_arrival_source",
    P.parent/"20261016-y-f76"/"source.py",
    "5b8928b0399ce9f869854beadeab04b29c8703a5")
F71=load("f79_frozen_F71_public_candidate_features",
    P.parent/"20261016-y-f71"/"early_scheduler.py",
    "edddfedb04af27dac7332ca85cc742aef5772a4b")
F62=SOURCE.ACTION
AUDITOR=SOURCE.AUDITOR
PACK=SOURCE.PACK
NUM_FEATURES=28

def role_stats(records,event):
    histogram=[0]*8
    incident=[0]*4
    adjacent=[0]*4
    endpoints={event[0],event[2]}
    for a,b,codes in records:
        assert all(type(c) is int and 0<=c<8 for c in codes)
        for code in codes:histogram[code]+=1
        if a in endpoints or b in endpoints:
            for role in {c//2 for c in codes}:incident[role]+=1
        for left,right in zip(codes,codes[1:]):
            if left//2==right//2:adjacent[left//2]+=1
    return histogram+incident+adjacent

def public_action_features(before,baseline,after,event,action,drop):
    original=F71.features(before,baseline,after,event,action,drop)
    a=role_stats(baseline,event)
    b=role_stats(after,event)
    extra=tuple((new-old)/12 for old,new in zip(a,b))
    x=tuple(original)+extra
    assert len(x)==NUM_FEATURES
    return x

def unique_alternatives(before,event,index):
    baseline=F62._f60_step(before,event,PACK)
    seen=set()
    options=[]
    for action,_prior,drop,after,_orig_feature in F62.actions(
            before,event,index,PACK):
        if after==baseline or after in seen:continue
        seen.add(after)
        x=public_action_features(before,baseline,after,event,action,drop)
        options.append((action,drop,after,x))
    return baseline,options

def sigmoid(z):
    if z>=0:
        e=math.exp(-min(z,40))
        return 1/(1+e)
    e=math.exp(max(z,-40))
    return e/(1+e)

def offline_examples(public,q):
    memory=()
    samples=[]
    label_counts=collections.Counter()
    for index,event in enumerate(public):
        baseline,alternatives=unique_alternatives(memory,event,index)
        if alternatives:
            baseline_end=F62._finish_fixed(baseline,public[index+1:],PACK)
            baseline_good=PACK.solve(baseline_end,q)==q["answer"]
            for action,drop,after,x in alternatives:
                alternative_end=F62._finish_fixed(after,public[index+1:],PACK)
                alternative_good=PACK.solve(alternative_end,q)==q["answer"]
                if alternative_good and not baseline_good:
                    label="beneficial"
                elif baseline_good and not alternative_good:
                    label="harmful"
                else:
                    label="neutral"
                samples.append((x,label))
                label_counts[label]+=1
        memory=baseline
    return samples,label_counts

def train(data):
    full_samples=[]
    totals=collections.Counter()
    by_regime=collections.defaultdict(collections.Counter)
    for regime,public,q in data:
        samples,labels=offline_examples(public,q)
        full_samples.extend(samples)
        totals.update(labels)
        by_regime[regime].update(labels)
    if not totals["beneficial"] or not (totals["harmful"]+totals["neutral"]):
        raise AssertionError("F79_TRAIN_LABELS_NOT_BIDIRECTIONAL")
    weights=[0.0]*NUM_FEATURES
    class_weight={"beneficial":128.0,"harmful":1.0,"neutral":0.01}
    for _ in range(3):
        for x,label in full_samples:
            expected=int(label=="beneficial")
            z=sum(w*xi for w,xi in zip(weights,x))
            grad=.025*class_weight[label]*(expected-sigmoid(z))
            for j,xi in enumerate(x):
                weights[j]+=grad*xi
    quant=tuple(max(-127,min(127,round(w*32))) for w in weights)
    assert len(quant)==NUM_FEATURES
    return quant,dict(label_counts=dict(totals),
       train_case_counts=len(data),candidate_examples=len(full_samples),
       label_counts_by_regime={k:dict(v) for k,v in by_regime.items()})

def online(public,weights,trace=False,enabled=True):
    assert len(public)==72 and all(len(e)==3 for e in public)
    assert len(weights)==NUM_FEATURES
    assert all(type(w) is int and -127<=w<=127 for w in weights)
    memory=()
    retained_trace=[]
    interventions=0
    early_interventions=0
    for index,event in enumerate(public):
        baseline,options=unique_alternatives(memory,event,index)
        selection=None
        if enabled:
            for j,(_action,_drop,after,x) in enumerate(options):
                prob=sigmoid(sum((w/32)*v for w,v in zip(weights,x)))
                key=(prob,-j)
                if selection is None or key>selection[0]:
                    selection=(key,after)
        if selection is not None and selection[0][0]>.90:
            memory=selection[1]
            interventions+=1
            early_interventions+=int(index<48)
        else:
            memory=baseline
        F62._valid_memory(memory,PACK)
        if trace:
            retained_trace.append(tuple(PACK.pack(*r).hex() for r in memory))
    return (memory,tuple(retained_trace),
        dict(interventions=interventions,
             early_interventions=early_interventions)) if trace else memory

def synthetic_qualification():
    train_data=[]
    for seed in range(-4601,-4617,-1):
        for family in (-2,-1):
            public,q,meta=SOURCE.source(seed,family)
            assert SOURCE.BASE.public_witness(public,q)=={q["answer"]}
            train_data.append((meta["arrival_regime"],public,q))
    weights,train_receipt=train(train_data)
    rows=[]
    for seed in range(-4621,-4637,-1):
        for family in (-2,-1):
            public,q,meta=SOURCE.source(seed,family)
            assert SOURCE.BASE.public_witness(public,q)=={q["answer"]}
            learned,learn_trace,stats=online(public,weights,True,True)
            baseline,base_trace,_=online(public,weights,True,False)
            for trace in (learn_trace,base_trace):
                verified=AUDITOR.verify(public,q,trace)
                assert verified["prefixes"]==72 and verified["max_payload_bytes"]<=144
            fixed=F62.controls()[0].online_fixed(public)
            assert baseline==fixed,"F79_DEFAULT_F60_DRIFT"
            rows.append(dict(seed=seed,family=family,
               arrival_regime=meta["arrival_regime"],
               question_type=meta["question_type"],
               learned_correct=int(PACK.solve(learned,q)==q["answer"]),
               F60_correct=int(PACK.solve(baseline,q)==q["answer"]),
               interventions=stats["interventions"],
               early_interventions=stats["early_interventions"]))
    by_regime={}
    for regime in ("original","local_rotate4"):
        sub=[r for r in rows if r["arrival_regime"]==regime]
        assert len(sub)==16
        learn=sum(r["learned_correct"] for r in sub)
        fixed=sum(r["F60_correct"] for r in sub)
        interventions=sum(r["interventions"] for r in sub)
        rescued=sum(r["learned_correct"] and not r["F60_correct"] for r in sub)
        damaged=sum(r["F60_correct"] and not r["learned_correct"] for r in sub)
        by_regime[regime]=dict(cases=16,learned_correct=learn,
            frozen_F60_correct=fixed,interventions=interventions,
            learned_new_rescues=rescued,regressions_from_F60=damaged,
            nondegradation=learn>=fixed)
    nondegrade=all(x["nondegradation"] for x in by_regime.values())
    nonzero=sum(r["interventions"] for r in rows)>0
    improvement=sum(x["learned_new_rescues"] for x in by_regime.values())>0
    qualified=nondegrade and nonzero and improvement
    result=dict(schema="yggdrasil.f79.two-arrival-role-aware-rare-intervention.synthetic.v1",
        stage="UNREGISTERED_SYNTHETIC_TRAIN_AND_SEPARATE_GUARD",
        train_cases=len(train_data),
        guard_cases=len(rows),
        frozen_int8_weights=list(weights),
        frozen_train_receipt=train_receipt,
        by_arrival_regime=by_regime,
        across_regimes_nondegradation=nondegrade,
        actual_source_legal_intervention_selected=nonzero,
        any_new_case_rescued=improvement,
        scientific_prequalification_pass=qualified,
        independent_every_public_prefix_causality_pass=True,
        FIT_TRAIN_used=False,FIT_VALIDATION_used=False,
        DIAG_used=False,ORIGINAL_used=False,F3=False,
        optimizer_promotion=False,rows=rows)
    print(json.dumps(result,sort_keys=True))
    if not qualified:
        raise AssertionError("F79_PREREG_SYNTHETIC_PREQUALIFICATION_FAILED")
if __name__=="__main__":
    assert sys.argv[1:]==["--synthetic-only"]
    synthetic_qualification()

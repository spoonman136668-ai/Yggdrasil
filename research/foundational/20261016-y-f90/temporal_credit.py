#!/usr/bin/env python3
"""F90 causal online policy + synthetic TRAIN-only temporal advantage learner.

The teacher may use training-case future events and answer, but ONLY in
collect_training_examples(). The online function has no access to the teacher,
task question, answer, family, seed, or unseen future public events.
Source-native memory is always at most twelve 12-byte records.
"""
from __future__ import annotations
import hashlib,importlib.util,json,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
PREREG_BLOB="9cf022d8646779cfe15d3f655b9b40154bf18b7c"
F89R_METHOD_BLOB="b2684ffdb49aed9c974569c0056f48d5ebb86aa0"
TRAIN_SEEDS=range(-5701,-5717,-1)
FAMILIES=(-2,-1)
CHECKPOINTS=(11,23,35,47,59,71)
ALT_LIMIT=8
DIM=12

def gitblob(path):
    raw=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()

def load_checked(name,path,blob):
    assert gitblob(path)==blob,("F90_SOURCE_IDENTITY_DRIFT",name)
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module

def public_delta(base_features,alt_features):
    assert len(base_features)==len(alt_features)==DIM
    return tuple(float(a-b) for a,b in zip(alt_features,base_features))

def dot(weights,features):
    assert len(weights)==len(features)==DIM
    return sum(w*x for w,x in zip(weights,features))

def choose(memory,event,index,weights,pack,F62):
    """Native causal F60 fallback and learned public-feature action advantage."""
    assert len(weights)==DIM and all(type(w) is int and -96<=w<=96 for w in weights)
    baseline=F62._f60_step(memory,event,pack)
    choices=F62.actions(memory,event,index,pack)
    options={option[3]:option for option in choices}
    assert baseline in options,"F90_F60_OUTSIDE_NATIVE_ACTIONS"
    base_features=options[baseline][4]
    scored=[]
    for action_index,option in enumerate(choices):
        if option[3]==baseline:continue
        vector=public_delta(base_features,option[4])
        value=dot(tuple(w/48 for w in weights),vector)
        scored.append((value,-action_index,option[3]))
    if scored:
        win=max(scored)
        if win[0]>=0.25:
            after=win[2]
            assert after in options
            F62._valid_memory(after,pack)
            return after,True,len(scored),win[0]
    return baseline,False,len(scored),0.0

def online(public,quant_weights,pack,F62,trace=False):
    assert len(public)==72 and all(len(e)==3 for e in public)
    memory=()
    receipts=[]
    interventions=0
    choices_offered=0
    high_score=0.0
    for index,event in enumerate(public):
        memory,changed,candidates,score=choose(
            memory,event,index,quant_weights,pack,F62)
        interventions+=int(changed)
        choices_offered+=candidates
        high_score=max(high_score,score)
        if trace:
            receipts.append(tuple(pack.pack(*r).hex() for r in memory))
    F62._valid_memory(memory,pack)
    if trace:
        return memory,tuple(receipts),dict(
            interventions=interventions,alternatives_scored=choices_offered,
            largest_accepted_score=high_score)
    return memory

def collect_training_examples(public,question,pack,F62,F85):
    """Training-only retrospective counterfactual trajectory credit assignment.

    No online() or choose() code path imports/calls this function.
    """
    assert len(public)==72
    memory=()
    examples=[]
    labels={-1:0,0:0,1:0}
    checkpoints=0
    for index,event in enumerate(public):
        baseline=F62._f60_step(memory,event,pack)
        if index in CHECKPOINTS:
            checkpoints+=1
            proposals=F62.actions(memory,event,index,pack)
            exact=[x for x in proposals if x[3]==baseline]
            assert len(exact)==1,"F90_F60_NATIVE_BASELINE_NOT_UNIQUE"
            base_features=exact[0][4]
            suffix=public[index+1:]
            frozen_baseline=F62._finish_fixed(baseline,suffix,pack)
            base_outcome=int(F85.solve_global(frozen_baseline,{
                "start":question["start"],"ops":question["ops"]},pack)[0]==question["answer"])
            attempted=0
            for proposal in proposals:
                if proposal[3]==baseline:continue
                if attempted>=ALT_LIMIT:break
                attempted+=1
                alternate=F62._finish_fixed(proposal[3],suffix,pack)
                candidate_outcome=int(F85.solve_global(alternate,{
                    "start":question["start"],"ops":question["ops"]},pack)[0]==question["answer"])
                advantage=candidate_outcome-base_outcome
                labels[advantage]+=1
                examples.append((public_delta(base_features,proposal[4]),advantage))
        memory=baseline
    assert checkpoints==6
    return examples,labels

def train(examples):
    """Frozen 3-pass temporal-credit linear learner; no model selection."""
    assert examples
    w=[0.0]*DIM
    for _ in range(3):
        for features,credit in examples:
            if credit not in (-1,0,1):
                raise AssertionError("NONCANONICAL_TEMPORAL_ADVANTAGE")
            if credit==0:
                continue
            for i,x in enumerate(features):
                w[i]=max(-2.0,min(2.0,0.99*w[i]+0.15*credit*x))
    quant=tuple(max(-96,min(96,round(x*48))) for x in w)
    assert len(quant)==DIM and all(type(x) is int for x in quant)
    return quant

def qualified_train_only():
    assert gitblob(HERE/"prereg.json")==PREREG_BLOB,"F90_PREREG_MUTATED"
    spec=json.loads((HERE/"prereg.json").read_text())
    assert spec["stage"]=="FROZEN_PRECODE_TRAIN_THEN_INDEPENDENT_NEGATIVE_SYNTHETIC_GUARD"
    assert spec["cohorts"]["train"]=={"seed_start":-5701,"seed_stop_exclusive":-5717,
             "step":-1,"families":[-2,-1],"cases":32}
    F89R=load_checked("f90_immutable_F89R",
        ROOT/"20261016-y-f89r"/"graded_exchange.py",F89R_METHOD_BLOB)
    F88=F89R.load_exact("f90_immutable_F88",
        ROOT/"20261016-y-f88"/"frontier.py",F89R.F88_BLOB)
    F87=F88.load_exact("f90_immutable_F87B",
        ROOT/"20261016-y-f87b"/"bridge_reserve.py",F88.F87B_BLOB)
    F86=F87.load("f90_immutable_F86",
        ROOT/"20261016-y-f86"/"queryblind_retention.py",F87.F86_SHA)
    F85=F86.load_exact("f90_immutable_F85",
        ROOT/"20261016-y-f85"/"global_solver.py",F86.F85_METHOD_BLOB)
    F84=F85.checked_loader("f90_immutable_F84",
        ROOT/"20261016-y-f84"/"forensic_reachability.py",F85.F84_SHA)
    F83=F84.load_f83()
    pack=F83.M.PACK
    F62=F83.M.F62
    all_examples=[]
    labels={-1:0,0:0,1:0}
    cases=0
    for seed in TRAIN_SEEDS:
        for family in FAMILIES:
            public,q,_meta=F83.M.SOURCE.source(seed,family)
            assert F84.independently_resolve_public(public,q)[0]=={q["answer"]}
            case_examples,local=collect_training_examples(public,q,pack,F62,F85)
            all_examples.extend(case_examples)
            for x,n in local.items():labels[x]+=n
            cases+=1
    assert cases==32
    frozen=train(all_examples)
    digest=hashlib.sha256(bytes(x%256 for x in frozen)).hexdigest()
    return dict(
        schema="yggdrasil.f90.temporal-credit.train-receipt.v1",
        stage="TRAIN_ONLY_NO_VALIDATION_NO_GUARD",
        prereg_blob=PREREG_BLOB,source_F89R_blob=F89R_METHOD_BLOB,
        train_cases=cases,train_examples=len(all_examples),
        label_counts={"harmful":labels[-1],"neutral":labels[0],"beneficial":labels[1]},
        checkpoint_indices=list(CHECKPOINTS),max_candidates_per_checkpoint=ALT_LIMIT,
        epochs=3,weight_integer_scale=48,
        frozen_12_int8_weights=list(frozen),weights_sha256=digest,
        model_parameters_extra_bytes=12,
        no_registered_fit=True,no_validate=True,no_guard=True,
        no_protected_original=True,no_diag=True,no_optimizer_promotion=True
    )
if __name__=="__main__":
    if sys.argv[1:]!=["--train-negative-synthetic-only"]:
        raise SystemExit("F90 first stage must not access any validation/guard or protected science")
    print(json.dumps(qualified_train_only(),sort_keys=True),flush=True)

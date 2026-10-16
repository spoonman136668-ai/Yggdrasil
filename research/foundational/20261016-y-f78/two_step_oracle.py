"""F78 capped two-step native memory reachability across F76 arrival regimes.

Unregistered synthetic source only; offline question-answer-aware oracle is
UNFAIR and NONCOMPETITIVE. No fitted policy or registered cohort access.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import pathlib
import sys

HERE=pathlib.Path(__file__).resolve().parent
def blob(path):
    b=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

def load(name,path,expected):
    assert blob(path)==expected,("F78_SOURCE_DRIFT",name)
    spec=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec)
    sys.modules[name]=obj
    spec.loader.exec_module(obj)
    return obj

assert blob(HERE/"prereg.json")=="baa0a9e7ec5de20c8cd3714231e2c19124f11275"
SOURCE=load("f78_frozen_two_regime_source",
    HERE.parent/"20261016-y-f76"/"source.py",
    "5b8928b0399ce9f869854beadeab04b29c8703a5")
ACTION=SOURCE.ACTION
AUDIT=SOURCE.AUDITOR
PACK=SOURCE.PACK
MAX_PAIRS=2048
FIRST_STEPS=tuple(range(0,64,4))
LAGS=(1,4,8,12)

def unique_actions(before,event,index):
    baseline=ACTION._f60_step(before,event,PACK)
    alternatives=tuple(dict.fromkeys(
        state for _kind,_prior,_drop,state,_feature
        in ACTION.actions(before,event,index,PACK) if state!=baseline))
    return baseline,alternatives

def frozen_prefix(public,q):
    before=[];trace=[];mem=()
    for index,event in enumerate(public):
        before.append(mem)
        mem=ACTION._f60_step(mem,event,PACK)
        ACTION._valid_memory(mem,PACK)
        trace.append(tuple(PACK.pack(*r).hex() for r in mem))
    witness=AUDIT.verify(public,q,trace)
    assert witness["prefixes"]==72 and witness["max_payload_bytes"]<=144
    return before,mem

def confirm(public,q,overrides):
    memory=();trace=[]
    for i,event in enumerate(public):
        fixed=ACTION._f60_step(memory,event,PACK)
        if i in overrides:
            legal=[s[3] for s in ACTION.actions(memory,event,i,PACK)]
            assert overrides[i] in legal and overrides[i]!=fixed
            memory=overrides[i]
        else:memory=fixed
        ACTION._valid_memory(memory,PACK)
        trace.append(tuple(PACK.pack(*r).hex() for r in memory))
    witness=AUDIT.verify(public,q,trace)
    assert witness["prefixes"]==72 and witness["max_payload_bytes"]<=144
    assert PACK.solve(memory,q)==q["answer"]
    return True

def evaluate_one(public,q):
    before,final=frozen_prefix(public,q)
    solved=PACK.solve(final,q)==q["answer"]
    if solved:
        return dict(F60_correct=True,one_step_rescue=False,two_step_rescue=False,
            one_step_candidates=0,two_step_pairs=0,
            second_search_censored=False,not_found_within_bounded_schedule=False,
            rescue_indices=None)
    count_one=0
    for i in range(72):
        _base,choices=unique_actions(before[i],public[i],i)
        for candidate in choices:
            count_one+=1
            result=ACTION._finish_fixed(candidate,public[i+1:],PACK)
            if PACK.solve(result,q)==q["answer"]:
                assert confirm(public,q,{i:candidate})
                return dict(F60_correct=False,one_step_rescue=True,
                    two_step_rescue=False,one_step_candidates=count_one,
                    two_step_pairs=0,second_search_censored=False,
                    not_found_within_bounded_schedule=False,rescue_indices=[i])
    pairs=0
    for i in FIRST_STEPS:
        _initial,first_options=unique_actions(before[i],public[i],i)
        for after_first in first_options:
            for lag in LAGS:
                j=i+lag
                if j>=72:continue
                middle=ACTION._finish_fixed(after_first,public[i+1:j],PACK)
                _second_base,second_options=unique_actions(middle,public[j],j)
                for after_second in second_options:
                    if pairs>=MAX_PAIRS:
                        return dict(F60_correct=False,one_step_rescue=False,
                            two_step_rescue=False,one_step_candidates=count_one,
                            two_step_pairs=pairs,second_search_censored=True,
                            not_found_within_bounded_schedule=False,rescue_indices=None)
                    pairs+=1
                    terminal=ACTION._finish_fixed(after_second,public[j+1:],PACK)
                    if PACK.solve(terminal,q)==q["answer"]:
                        assert confirm(public,q,{i:after_first,j:after_second})
                        return dict(F60_correct=False,one_step_rescue=False,
                            two_step_rescue=True,one_step_candidates=count_one,
                            two_step_pairs=pairs,second_search_censored=False,
                            not_found_within_bounded_schedule=False,
                            rescue_indices=[i,j])
    return dict(F60_correct=False,one_step_rescue=False,two_step_rescue=False,
        one_step_candidates=count_one,two_step_pairs=pairs,
        second_search_censored=False,
        not_found_within_bounded_schedule=True,rescue_indices=None)

def run():
    rows=[]
    for seed in range(-4401,-4409,-1):
        for family in (-2,-1):
            public,q,meta=SOURCE.source(seed,family)
            assert SOURCE.BASE.public_witness(public,q)=={q["answer"]}
            result=evaluate_one(public,q)
            rows.append(dict(seed=seed,family=family,
                arrival_regime=meta["arrival_regime"],
                question_type=meta["question_type"],**result))
    by={}
    for regime in ("original","local_rotate4"):
        sub=[r for r in rows if r["arrival_regime"]==regime]
        assert len(sub)==8
        failed=[r for r in sub if not r["F60_correct"]]
        by[regime]=dict(cases=len(sub),
            F60_correct=sum(r["F60_correct"] for r in sub),
            F60_failures=len(failed),
            single_step_rescues=sum(r["one_step_rescue"] for r in failed),
            two_step_rescues=sum(r["two_step_rescue"] for r in failed),
            capped_two_step_searches=sum(r["second_search_censored"] for r in failed),
            not_found_within_bounded_schedule=sum(r["not_found_within_bounded_schedule"] for r in failed),
            total_examined_one_step_candidates=sum(r["one_step_candidates"] for r in failed),
            total_examined_two_step_pairs=sum(r["two_step_pairs"] for r in failed),
            by_question_type={kind:dict(cases=sum(r["question_type"]==kind for r in sub),
               F60_correct=sum(r["F60_correct"] for r in sub if r["question_type"]==kind),
               single_step_rescues=sum(r["one_step_rescue"] for r in sub if r["question_type"]==kind),
               two_step_rescues=sum(r["two_step_rescue"] for r in sub if r["question_type"]==kind))
               for kind in sorted({r["question_type"] for r in sub})})
    result=dict(schema="yggdrasil.f78.two-arrival-capped-two-step.synthetic.v1",
        stage="NONCOMPETITIVE_BOUNDED_UNREGISTERED_SYNTHETIC",
        synthetic_cases=len(rows),by_arrival_regime=by,
        exact_per_case_two_step_pair_cap=MAX_PAIRS,
        two_step_first_intervention_checkpoints=list(FIRST_STEPS),
        two_step_allowed_lags=list(LAGS),
        all_oracle_rescues_independently_audited=True,
        capped_search_not_claimed_infeasible=True,
        public_source_and_native_actions_unchanged=True,
        learner_trained=False,protected_FIT_TRAIN_used=False,
        protected_FIT_VALIDATE_used=False,DIAG_used=False,
        ORIGINAL_used=False,F3=False,optimizer_promotion=False,
        rows=rows)
    assert len(rows)==16
    print(json.dumps(result,sort_keys=True))
if __name__=="__main__":
    assert sys.argv[1:]==["--synthetic-only"]
    run()

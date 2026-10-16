#!/usr/bin/env python3
"""F90 exact frozen 12-int8 temporal-credit policy read-only holdout evaluation.

This file must never train, select a model, change a threshold, nor read
protected FIT/DIAG/ORIGINAL source. Both evaluation cohorts are disjoint
from training and all prior exposed science. Guard is examined only after
the 12 signed coefficients have been committed as a content-addressed file.
"""
from __future__ import annotations
import hashlib,importlib.util,json,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
F90_METHOD_BLOB="0b689d66135a246987b20e189b9724b1c0715c25"
F90_POLICY_BLOB="56d1c1c81faf432c7f2eb33e6ce45e3513a9c9ae"
F90_PREREG_BLOB="9cf022d8646779cfe15d3f655b9b40154bf18b7c"
VALID_SEEDS=range(-5721,-5729,-1)
GUARD_SEEDS=range(-5741,-5757,-1)
FAMILIES=(-2,-1)

def gitblob(path):
    b=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

def source_exact(name,path,sha):
    assert gitblob(path)==sha,("F90_EVAL_FROZEN_SOURCE_DRIFT",name)
    spec=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec)
    sys.modules[name]=obj
    spec.loader.exec_module(obj)
    return obj

def source_metadata():
    assert gitblob(HERE/"prereg.json")==F90_PREREG_BLOB
    assert gitblob(HERE/"frozen-policy.json")==F90_POLICY_BLOB
    policy=json.loads((HERE/"frozen-policy.json").read_text())
    prereg=json.loads((HERE/"prereg.json").read_text())
    assert policy["method_git_blob"]==F90_METHOD_BLOB
    assert policy["stage"]=="TRAINED_WEIGHTS_FROZEN_BEFORE_ANY_VALIDATION_OR_GUARD"
    assert policy["train_run_id"]==38970900000
    assert prereg["cohorts"]["validate"]["seed_start"]==-5721
    assert prereg["cohorts"]["guard"]["seed_start"]==-5741
    weights=tuple(policy["weights_int8"])
    assert len(weights)==12 and all(type(w) is int and -96<=w<=96 for w in weights)
    assert hashlib.sha256(bytes(w%256 for w in weights)).hexdigest()==policy["weights_sha256"]
    assert policy["weights_sha256"]=="a96034934bc09736a513a1f7695cae6a7b67b470c12e883d0f17b5d722969ff0"
    return weights,prereg

def aggregate(rows,subset):
    chosen=[r for r in rows if subset(r)]
    return dict(cases=len(chosen),
       correct={model:sum(r[model+"_correct"] for r in chosen) for model in ("f60","f83","f90")},
       rescues_over_F60=sum(not r["f60_correct"] and r["f90_correct"] for r in chosen),
       regressions_from_F60=sum(r["f60_correct"] and not r["f90_correct"] for r in chosen),
       learned_interventions=sum(r["f90_interventions"] for r in chosen))

def evaluate(mode):
    weights,prereg=source_metadata()
    seeds=VALID_SEEDS if mode=="validation" else GUARD_SEEDS
    config=prereg["cohorts"]["validate" if mode=="validation" else "guard"]
    assert list(seeds)==list(range(config["seed_start"],config["seed_stop_exclusive"],config["step"]))
    F90=source_exact("f90_eval_method_exact",HERE/"temporal_credit.py",F90_METHOD_BLOB)
    F89R=F90.load_checked("f90_eval_F89R",ROOT/"20261016-y-f89r"/"graded_exchange.py",F90.F89R_METHOD_BLOB)
    F88=F89R.load_exact("f90_eval_F88",ROOT/"20261016-y-f88"/"frontier.py",F89R.F88_BLOB)
    F87=F88.load_exact("f90_eval_F87",ROOT/"20261016-y-f87b"/"bridge_reserve.py",F88.F87B_BLOB)
    F86=F87.load("f90_eval_F86",ROOT/"20261016-y-f86"/"queryblind_retention.py",F87.F86_SHA)
    F85=F86.load_exact("f90_eval_F85",ROOT/"20261016-y-f85"/"global_solver.py",F86.F85_METHOD_BLOB)
    F84=F85.checked_loader("f90_eval_F84",ROOT/"20261016-y-f84"/"forensic_reachability.py",F85.F84_SHA)
    F83=F84.load_f83()
    frozen_f83=F84.assert_frozen()
    pack=F83.M.PACK
    F62=F83.M.F62
    rows=[]
    for seed in seeds:
        for family in FAMILIES:
            public,q,meta=F83.M.SOURCE.source(seed,family)
            assert F84.independently_resolve_public(public,q)[0]=={q["answer"]}
            control_f60=F84.audit_f60(F83,public,q)
            control_f83,trace83,_=F83.online(public,frozen_f83,True,True)
            cert83=F83.M.AUDITOR.verify(public,q,trace83)
            assert cert83["prefixes"]==72 and cert83["max_payload_bytes"]<=144
            learned,trace90,stats=F90.online(public,weights,pack,F62,True)
            cert90=F83.M.AUDITOR.verify(public,q,trace90)
            assert cert90["prefixes"]==72 and cert90["max_payload_bytes"]<=144
            record=dict(
                seed=seed,family=family,arrival_regime=meta["arrival_regime"],
                question_type=meta["question_type"],
                f90_interventions=stats["interventions"],
                f90_alternatives_scored=stats["alternatives_scored"],
                f90_max_retained_bytes=cert90["max_payload_bytes"])
            for name,stored in (("f60",control_f60),("f83",control_f83),("f90",learned)):
                prediction,account=F85.solve_global(stored,
                    {"start":q["start"],"ops":q["ops"]},pack)
                assert prediction is None or prediction==q["answer"], "INVALID_SOURCE_PREDICTION"
                assert not account["resource_cap_triggered"]
                assert account["persistent_memory_bytes"]<=144
                record[name+"_correct"]=int(prediction==q["answer"])
            record["f90_original_greedy_correct"]=int(
                pack.solve(learned,q)==q["answer"])
            rows.append(record)
    assert len(rows)==config["cases"]
    strata={}
    for regime in ("original","local_rotate4"):
        strata[regime]={}
        for kind in ("within_component_4_steps","crosslink_reach_6_steps"):
            strata[regime][kind]=aggregate(rows,lambda x:x["arrival_regime"]==regime
                                              and x["question_type"]==kind)
            assert strata[regime][kind]["cases"]>0
    six=aggregate(rows,lambda x:x["question_type"]=="crosslink_reach_6_steps")
    total=aggregate(rows,lambda x:True)
    supported=(six["rescues_over_F60"]>0
        and total["regressions_from_F60"]==0)
    return dict(
        schema="yggdrasil.f90.temporal-credit.frozen-"+mode+".v1",
        stage="FROZEN_SYNTHETIC_VALIDATION_ONLY" if mode=="validation"
              else "ONE_TIME_NEW_NEGATIVE_SYNTHETIC_GUARD",
        classification=("synthetic_mechanism_supported" if supported else
           "synthetic_negative"),
        mode=mode,frozen_weights_sha256="a96034934bc09736a513a1f7695cae6a7b67b470c12e883d0f17b5d722969ff0",
        cases=len(rows),six_step_cases=six["cases"],scores=total["correct"],
        six_step_rescues_from_F60=six["rescues_over_F60"],
        F60_correct_case_regressions=total["regressions_from_F60"],
        learned_interventions=total["learned_interventions"],
        by_arrival_regime_and_type=strata,
        max_persistent_memory_bytes=max(r["f90_max_retained_bytes"] for r in rows),
        extra_frozen_model_parameters_bytes=12,
        exact_72_causal_prefixes_verified=True,
        no_protected_train_or_original=True,
        no_guard_as_training=True,no_test_time_refit=True,
        no_DIAG=True,no_FIT=True,no_F3=True,
        independent_science_accepted=False,
        optimizer_promotion=False,controller_mutation=False,
        rows=rows
    )
if __name__=="__main__":
    if sys.argv[1:]==["--frozen-validation-only"]:
        print(json.dumps(evaluate("validation"),sort_keys=True))
    elif sys.argv[1:]==["--frozen-disjoint-guard-only"]:
        print(json.dumps(evaluate("guard"),sort_keys=True))
    else:
        raise SystemExit("F90 evaluator refuses all train, protected science, or unspecified source")

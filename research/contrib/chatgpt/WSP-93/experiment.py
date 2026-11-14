"""WSP93 source-blind public evaluation of interpretable character evidence binding.

Prediction controls receive only a real passage and human question, never
selected answer labels or arbitrary answer-choice lists. Original public
negative is a legitimate scientific result, not a failing engineering test.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from source import CORPUS,LABELS,verify
from weights import (DirectBinding,ConventionalLogistic,AnchorRetrieval,
                     SymbolicTypeControl,RandomCandidate,spans,proof,canonical)
SPEC=json.loads((HERE/"prereg.json").read_text(encoding="utf-8"))
T=SPEC["criteria"]

def sha(x:object)->str:
    return hashlib.sha256(canonical(x).encode("ascii")).hexdigest()

def score_label(pred:dict|None,label:dict)->bool:
    return pred is not None and pred["answer"]==label["answer_text"]

def validated_proof(pred:dict|None,row:dict)->bool:
    if pred is None:return False
    a,b=pred["start"],pred["end"]
    return (type(a) is int and type(b) is int and
            0<=a<b<=len(row["context"]) and
            row["context"][a:b]==pred["answer"] and
            pred["qa_id"]==row["qa_id"] and
            pred["article_url"]==row["article_url"] and
            pred["article_title"]==row["article_title"] and
            pred["context_sha256"]==row["context_sha256"])

def evaluate(*,reserved:bool)->dict:
    start=time.process_time_ns()
    source_receipt=verify()
    source=json.loads(CORPUS.read_text(encoding="utf-8"))
    labels=json.loads(LABELS.read_text(encoding="utf-8"))
    train=[r for r in source["records"] if r["cohort"]=="training"]
    cohort="reserved" if reserved else "public"
    public=[r for r in source["records"] if r["cohort"]==cohort]
    if len(train)!=72 or len(public)!=(32 if reserved else 24):
        raise ValueError("frozen article/cohort count mismatch")
    train_labels={x["qa_id"]:x for x in labels["labels"] if x["cohort"]=="training"}
    if len(train_labels)!=72:raise ValueError("training source labels missing")

    first=train[:48];added=train[48:]
    model=DirectBinding()
    t=time.process_time_ns()
    for row in first:model.observe(row,train_labels[row["qa_id"]])
    initial_cpu=time.process_time_ns()-t
    before=[model.answer(x) for x in first]
    before_snapshot=model.snapshot()
    t=time.process_time_ns()
    for row in added:model.observe(row,train_labels[row["qa_id"]])
    added_cpu=time.process_time_ns()-t
    after=[model.answer(x) for x in first]
    fit=[model.answer(x) for x in train]
    fit_exact=sum(score_label(p,train_labels[q["qa_id"]]) for q,p in zip(train,fit))
    retained_exact=sum(score_label(p,train_labels[q["qa_id"]]) for q,p in zip(first,after))
    initial_exact=sum(score_label(p,train_labels[q["qa_id"]]) for q,p in zip(first,before))

    ordinary=ConventionalLogistic()
    t=time.process_time_ns()
    ordinary.fit([(r,train_labels[r["qa_id"]]) for r in train])
    ordinary_cpu=time.process_time_ns()-t
    trained_fit=sum(score_label(ordinary.answer(q),train_labels[q["qa_id"]])
                    for q in train)
    controls={
        "direct_binding":lambda q:model.answer(q),
        "ordinary_logistic":lambda q:ordinary.answer(q),
        "question_ablated":lambda q:model.answer(q,ablate=True),
        "anchor_retrieval":lambda q:AnchorRetrieval().answer(q),
        "symbolic_type":lambda q:SymbolicTypeControl().answer(q),
        "random_candidate":lambda q:RandomCandidate().answer(q),
    }
    t=time.process_time_ns()
    predictions={name:[f(q) for q in public] for name,f in controls.items()}
    inference_cpu=time.process_time_ns()-t
    snapshot=model.snapshot()
    frozen_pred_sha=sha({
        "cohort":cohort,"source_sha256":source_receipt["source_records_sha256"],
        "outputs":{name:[(r["answer"],r["start"],r["end"])
                         if r is not None else None for r in arr]
                   for name,arr in predictions.items()},
        "before":tuple(x["answer"] if x else None for x in before),
        "after":tuple(x["answer"] if x else None for x in after),
    })
    restored=DirectBinding.restore(snapshot)
    cold=(restored.snapshot()==snapshot and
          [restored.answer(q) for q in public]==predictions["direct_binding"] and
          DirectBinding.restore(before_snapshot).snapshot()==before_snapshot)
    corrupted=json.loads(snapshot);name=next(iter(corrupted["payload"]["weights"]))
    corrupted["payload"]["weights"][name]+=0.25
    tamper=False
    try:DirectBinding.restore(json.dumps(corrupted))
    except ValueError:tamper=True
    invalid=[
        {**public[0],"context":"altered unverified source"},
        {**public[0],"question":""},
        {**public[0],"context_sha256":"bad source content checksum"},
    ]
    unknown_confident=sum(model.answer(q) is not None for q in invalid)

    # The evaluator does not consult public/reserved answer labels until
    # *all* original candidate/control outputs are committed above.
    gold={x["qa_id"]:x for x in labels["labels"] if x["cohort"]==cohort}
    if len(gold)!=len(public):raise ValueError("sealed source labels missing")
    accuracy={name:sum(score_label(p,gold[q["qa_id"]])
                       for q,p in zip(public,output))
              for name,output in predictions.items()}
    proofs=sum(validated_proof(p,q) and score_label(p,gold[q["qa_id"]])
               for q,p in zip(public,predictions["direct_binding"]))
    coverage=sum(any(a==gold[q["qa_id"]]["answer_start"] and
                     v==gold[q["qa_id"]]["answer_text"]
                     for a,b,v in spans(q["context"])) for q in public)
    per_question=[{
        "qa_id":q["qa_id"],"article_title":q["article_title"],
        "question":q["question"],"expected":gold[q["qa_id"]]["answer_text"],
        "predictions":{name:(arr[i]["answer"] if arr[i] else None)
                       for name,arr in predictions.items()},
        "answer_reachable":any(a==gold[q["qa_id"]]["answer_start"] and
                                value==gold[q["qa_id"]]["answer_text"]
                                for a,b,value in spans(q["context"]))
    } for i,q in enumerate(public)]
    return {
        "schema":"wsp93.question-evidence-binding-result.v1",
        "cohort":"RESERVED_DEV_FIRST_USE" if reserved else "PUBLIC_FIXTURE",
        "source_sha256":source_receipt["source_records_sha256"],
        "label_sha256":source_receipt["labels_sha256"],
        "questions":len(public),"article_count":len({r["article_title"] for r in public}),
        "exact":accuracy,"source_proof_correct":proofs,
        "source_answer_reachable":coverage,
        "original_fit":initial_exact,"final_fit":fit_exact,
        "old_exact_retained":retained_exact,
        "ordinary_training_exact":trained_fit,
        "program_edits":model.observed,
        "program_skipped_unreachable":model.skipped_unreachable,
        "operator_weights":len(model.weights),
        "unknown_confident":unknown_confident,
        "cold_restore":cold,"tamper_rejected":tamper,
        "initial_edit_cpu_ns":initial_cpu,
        "new_edit_cpu_ns":added_cpu,
        "ordinary_fit_cpu_ns":ordinary_cpu,
        "all_methods_inference_cpu_ns":inference_cpu,
        "whole_cpu_ns":time.process_time_ns()-start,
        "prediction_sha256_before_scoring":frozen_pred_sha,
        "per_question":per_question,
        "interpretation":"Disjoint SQuAD TRAIN article subsets, one publisher and supplied relevant passages. No general intelligence claim."
    }

def classify(q:dict,*,reserved:bool)->dict:
    r=q["exact"]
    checks={
        "exact_fixed_source_size":q["questions"]==(32 if reserved else 24),
        "train_learning":q["final_fit"]>=T["train_min_correct"],
        "cold_retention":q["old_exact_retained"]>=T["retention_min_correct"],
        "trained_control_fit":q["ordinary_training_exact"]>=T["strong_conventional_min_train_correct"],
        "source_gold_reachable":q["source_answer_reachable"]/q["questions"]>=T["min_gold_span_coverage_fraction"],
        "source_proofs":q["source_proof_correct"]==r["direct_binding"],
        "unknown_input_abstention":q["unknown_confident"]==0,
        "cold_snapshot":q["cold_restore"],
        "tamper_rejection":q["tamper_rejected"],
        "all_controls_reported":len(r)==6,
        "measured_resources":q["whole_cpu_ns"]>0 and
            q["operator_weights"]>0 and q["ordinary_fit_cpu_ns"]>=0,
    }
    if reserved:
        checks.update({
            "reserved_cross_article_transfer":r["direct_binding"]>=T["reserved_min_exact"],
            "vs_ablated":r["direct_binding"]-r["question_ablated"]>=T["reserved_advantage_vs_ablated"],
            "vs_conventional":r["ordinary_logistic"]-r["direct_binding"]<=T["reserved_max_gap_to_conventional"],
        })
    else:
        checks.update({
            "public_positive_transfer":r["direct_binding"]>=T["public_min_exact"],
            "over_random":r["direct_binding"]-r["random_candidate"]>=T["public_advantage_vs_random"],
            "question_conditioning_matters":r["direct_binding"]-r["question_ablated"]>=T["public_advantage_vs_question_ablated"],
            "within_conventional":r["ordinary_logistic"]-r["direct_binding"]<=T["max_public_gap_to_conventional"],
        })
    if reserved:classification=T["reserved_positive"] if all(checks.values()) else T["reserved_negative"]
    else:classification=T["public_positive"] if all(checks.values()) else T["public_negative"]
    return {**q,"checks":checks,"passed_checks":sum(checks.values()),
            "total_checks":len(checks),"classification":classification,
            "scientific_acceptance":"UNVERIFIED",
            "independent_domain_transfer":False,
            "LLM_class_general_reasoning":False,"deployment":"NONE"}

def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--public-fixtures-only",action="store_true")
    g.add_argument("--reserved-dev-first-use",action="store_true")
    args=p.parse_args()
    report=classify(evaluate(reserved=args.reserved_dev_first_use),
                    reserved=args.reserved_dev_first_use)
    print("WSP93_RESULT="+canonical(report),flush=True)

if __name__=="__main__":main()

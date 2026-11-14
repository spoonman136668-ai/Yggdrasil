"""WSP92 frozen SQuAD broad-question reading and direct weight editing.

The evaluator passes ONLY source texts/questions into the candidate and all
other methods. Original training labels teach the candidate and fully trained
SGD. Public or reserved labels are consulted ONLY AFTER method predictions
have been committed to a deterministic SHA256 output record.
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
from weights import (
    DirectQuestionSpanWriter,FullyTrainedLogistic,RetrievalCharControl,
    SymbolicCueControl,RandomSpanControl,span_candidates,canonical,
)
SPEC=json.loads((HERE/"prereg.json").read_text(encoding="utf-8"))
FROZEN=SPEC["frozen"]

def sha(x:object)->str:
    return hashlib.sha256(canonical(x).encode("ascii")).hexdigest()

def normalize(s:str|None)->str|None:
    if s is None:return None
    # Reporting ONLY; frozen strict exact remains primary.
    return " ".join(re.sub(r"[^\w ]+","",s.casefold()).split())

def proof(pred:dict|None,row:dict)->bool:
    if pred is None:return False
    a,b=pred.get("start"),pred.get("end")
    return (type(a) is int and type(b) is int and 0<=a<b<=len(row["context"]) and
            row["context"][a:b]==pred.get("answer") and
            pred.get("qa_id")==row["qa_id"] and
            pred.get("article_title")==row["article_title"] and
            pred.get("article_url")==row["article_url"] and
            pred.get("context_sha256")==row["context_sha256"] and
            hashlib.sha256(row["context"].encode("utf-8")).hexdigest()==
                row["context_sha256"])

def records(dataset:dict,cohort:str)->list[dict]:
    return [x for x in dataset["records"] if x["cohort"]==cohort]

def train_input(labels:dict)->dict[str,dict]:
    return {x["qa_id"]:x for x in labels["labels"] if x["cohort"]=="training"}

def evaluate(*,reserved:bool)->dict:
    start=time.process_time_ns()
    source_receipt=verify()
    corpus=json.loads(CORPUS.read_text(encoding="utf-8"))
    # Only *training* annotations are accessed here. Public/reserved
    # annotations remain off limits until all output predictions are SHA'd.
    all_labels=json.loads(LABELS.read_text(encoding="utf-8"))
    train_labels=train_input(all_labels)
    train=records(corpus,"training")
    selected=records(corpus,"reserved" if reserved else "public")
    if len(train)!=128 or len(selected)!=(50 if reserved else 24):
        raise ValueError("sample counts disagree with frozen SQuAD manifest")
    first=train[:96];added=train[96:]

    direct=DirectQuestionSpanWriter()
    t=time.process_time_ns()
    for item in first:
        direct.observe(item,train_labels[item["qa_id"]])
    initial_cpu=time.process_time_ns()-t
    first_before=[direct.answer(q) for q in first]
    early_restore=direct.snapshot()

    t=time.process_time_ns()
    for item in added:
        direct.observe(item,train_labels[item["qa_id"]])
    incremental_cpu=time.process_time_ns()-t
    first_after=[direct.answer(q) for q in first]
    # Reuse exactly identical deterministic post-update predictions for the
    # first 96 source questions; avoid redundant document-span rescoring.
    train_predictions=first_after+[direct.answer(q) for q in added]
    training_exact=sum(
        pred is not None and pred["answer"]==train_labels[q["qa_id"]]["answer_text"]
        for q,pred in zip(train,train_predictions))
    original_train_exact=sum(
        p is not None and p["answer"]==train_labels[q["qa_id"]]["answer_text"]
        for q,p in zip(first,first_before))
    retained_exact=sum(
        p is not None and p["answer"]==train_labels[q["qa_id"]]["answer_text"]
        for q,p in zip(first,first_after))

    ordinary=FullyTrainedLogistic()
    t=time.process_time_ns()
    ordinary.fit([(q,train_labels[q["qa_id"]]) for q in train])
    ordinary_fit_cpu=time.process_time_ns()-t
    ordinary_train=[ordinary.answer(q) for q in train]
    ordinary_training_exact=sum(
        p is not None and p["answer"]==train_labels[q["qa_id"]]["answer_text"]
        for q,p in zip(train,ordinary_train))

    shuffled=DirectQuestionSpanWriter()
    for q in train:
        truth=train_labels[q["qa_id"]]
        pool=[(a,b,text) for a,b,text in span_candidates(q["context"])
              if not (a==truth["answer_start"] and text==truth["answer_text"])]
        if not pool:
            raise ValueError("no nonanswer source candidates for shuffled negative")
        ordered=sorted(pool,key=lambda p:hashlib.sha256(
            ("WSP92/false/"+q["qa_id"]+"/"+str(p[0])).encode("ascii")).digest())
        a,b,text=ordered[0]
        shuffled.observe(q,{"answer_start":a,"answer_text":text})

    methods={
        "direct_numeric":direct,
        "fully_trained_logistic":ordinary,
        "char_retrieval":RetrievalCharControl(),
        "symbolic_cue":SymbolicCueControl(),
        "shuffled_label_writer":shuffled,
        "random_source_span":RandomSpanControl(),
    }
    t=time.process_time_ns()
    predictions={k:[m.answer(item) for item in selected] for k,m in methods.items()}
    eval_cpu=time.process_time_ns()-t
    frozen_pred_hash=sha({
        "source_records_sha256":source_receipt["source_records_sha256"],
        "cohort":"reserved" if reserved else "public",
        "predictions":{k:[(x["answer"],x["start"],x["end"]) if x is not None else None
                           for x in arr] for k,arr in predictions.items()},
    })
    new_state=direct.snapshot()
    restored=DirectQuestionSpanWriter.restore(new_state)
    cold_exact=(restored.snapshot()==new_state and
                [restored.answer(item) for item in selected]==predictions["direct_numeric"] and
                DirectQuestionSpanWriter.restore(early_restore).snapshot()==early_restore)
    corrupt=json.loads(new_state)
    k=next(iter(corrupt["payload"]["weights"]))
    corrupt["payload"]["weights"][k]+=1.0
    tamper_rejected=False
    try:DirectQuestionSpanWriter.restore(json.dumps(corrupt))
    except ValueError:tamper_rejected=True

    unknown=dict(selected[0])
    unknown["context"]="This unrelated paragraph contains no valid answer source."
    # An unchanged context hash must be rejected.
    unknown_predictions=(direct.answer(unknown),
                         direct.answer({**selected[0],"question":""}),
                         direct.answer({**selected[0],"context":""}))
    unknown_confident=sum(x is not None for x in unknown_predictions)

    # Score only after *every model's output* was frozen above.
    answer_labels={x["qa_id"]:x for x in all_labels["labels"]
                   if x["cohort"]==("reserved" if reserved else "public")}
    if len(answer_labels)!=len(selected):
        raise ValueError("public/reserved sealed label count mismatch")
    results={}
    normalized_results={}
    for name,arr in predictions.items():
        results[name]=sum(p is not None and
            p["answer"]==answer_labels[q["qa_id"]]["answer_text"]
            for q,p in zip(selected,arr))
        normalized_results[name]=sum(p is not None and
            normalize(p["answer"])==normalize(answer_labels[q["qa_id"]]["answer_text"])
            for q,p in zip(selected,arr))
    proof_correct=sum(proof(p,q) and
                      p["answer"]==answer_labels[q["qa_id"]]["answer_text"]
                      for q,p in zip(selected,predictions["direct_numeric"]))
    cover=sum(any(
        a==answer_labels[q["qa_id"]]["answer_start"] and
        value==answer_labels[q["qa_id"]]["answer_text"]
        for a,b,value in span_candidates(q["context"])) for q in selected)
    errors=[]
    for q,p in zip(selected,predictions["direct_numeric"]):
        truth=answer_labels[q["qa_id"]]
        if p is not None and p["answer"]==truth["answer_text"]:
            continue
        errors.append({
            "qa_id":q["qa_id"],"article_title":q["article_title"],
            "question":q["question"],"expected_answer":truth["answer_text"],
            "expected_start":truth["answer_start"],
            "predicted_answer":p["answer"] if p is not None else None,
            "predicted_start":p["start"] if p is not None else None,
            "annotation_is_reachable":any(
                a==truth["answer_start"] and val==truth["answer_text"]
                for a,b,val in span_candidates(q["context"])),
        })
    return {
        "schema":"wsp92.human-multitopic-source-qa-dev.v1",
        "cohort":"RESERVED_DEV_FIRST_USE" if reserved else "PUBLIC_FIXTURE",
        "source_sha256":source_receipt["source_records_sha256"],
        "label_sha256":source_receipt["labels_sha256"],
        "questions":len(selected),
        "different_article_titles":len({q["article_title"] for q in selected}),
        "correct_exact":results,"correct_normalized":normalized_results,
        "candidate_source_proof_correct":proof_correct,
        "oracle_candidate_reachable":cover,
        "original_train_exact":original_train_exact,
        "final_train_exact":training_exact,"retained_old_exact":retained_exact,
        "conventional_train_exact":ordinary_training_exact,
        "unknown_confident":unknown_confident,
        "cold_snapshot_exact":cold_exact,
        "tamper_rejected":tamper_rejected,
        "source_provenance_preserved":all(q["article_url"] and
           q["wikipedia_contributors_url"] and q["context_sha256"]
           for q in selected),
        "numerical_weight_slots":len(direct.weights),
        "supervised_training_questions":direct.observed,
        "first_96_direct_write_cpu_ns":initial_cpu,
        "next_32_direct_write_cpu_ns":incremental_cpu,
        "fully_trained_logistic_cpu_ns":ordinary_fit_cpu,
        "all_methods_eval_cpu_ns":eval_cpu,
        "whole_process_cpu_ns":time.process_time_ns()-start,
        "frozen_predictions_sha256":frozen_pred_hash,
        "errors":errors,
        "status_note":"Original SQuAD public dev set is a development source, NOT sealed independent held-out science; relevant paragraph is given."
    }

def classify(q:dict,*,reserved:bool)->dict:
    t=FROZEN;r=q["correct_exact"]
    checks={
        "proper_source_size":q["questions"]==(50 if reserved else 24),
        "training_source_fit":q["final_train_exact"]>=t["min_candidate_training_fit"],
        "conventional_training_fit":q["conventional_train_exact"]>=t["min_conventional_training_fit"],
        "cold_original_answer_retention":q["retained_old_exact"]>=t["min_old_answer_retention"],
        "source_proof_on_correct":q["candidate_source_proof_correct"]==r["direct_numeric"],
        "no_unsupported_answers":q["unknown_confident"]==0,
        "cold_restore":q["cold_snapshot_exact"],
        "state_corruption_detected":q["tamper_rejected"],
        "complete_control_reporting":len(r)==6,
        "CPU_state_and_source":q["whole_process_cpu_ns"]>0 and
            q["fully_trained_logistic_cpu_ns"]>=0 and
            q["numerical_weight_slots"]>0 and q["supervised_training_questions"]==128 and
            q["source_provenance_preserved"],
    }
    if reserved:
        checks.update({
            "cross_article_QA":r["direct_numeric"]>=t["min_candidate_reserved_exact"],
            "beats_random":r["direct_numeric"]-r["random_source_span"]>=t["min_candidate_advantage_over_random"],
            "gap_to_conventional":r["fully_trained_logistic"]-r["direct_numeric"]<=
                t["max_candidate_gap_to_logistic"],
            "source_answer_is_eligible":q["oracle_candidate_reachable"]/q["questions"]>=
                t["source_alignment_coverage_min"],
        })
    else:
        checks["public_fixture_nontrivial"]=r["direct_numeric"]>=t["min_candidate_public_exact"]
    classification=(
        "DEV_CROSS_ARTICLE_QA_MECHANISM_FEASIBLE" if all(checks.values()) else
        "DEV_CROSS_ARTICLE_QA_MECHANISM_NEGATIVE") if reserved else (
        "PUBLIC_FIXTURE_FEASIBLE" if all(checks.values()) else "PUBLIC_FIXTURE_NEGATIVE")
    return {**q,"checks":checks,"passed_checks":sum(checks.values()),
        "total_checks":len(checks),"classification":classification,
        "scientific_acceptance":"UNVERIFIED",
        "independent_publisher_transfer":False,
        "modern_pretrained_neural_reader_comparison":False,
        "general_intelligence_or_LLM_equivalence":False,"deployment":"NONE"}

def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--public-fixtures-only",action="store_true")
    g.add_argument("--reserved-dev-first-use",action="store_true")
    a=p.parse_args()
    result=classify(evaluate(reserved=a.reserved_dev_first_use),
                    reserved=a.reserved_dev_first_use)
    print("WSP92_RESULT="+canonical(result),flush=True)

if __name__=="__main__":
    main()

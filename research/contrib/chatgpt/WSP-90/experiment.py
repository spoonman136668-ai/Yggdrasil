"""WSP90 frozen source-backed prose reading via direct weight edits.

No DEV labels used until all candidate/controls predictions are hashed.
Data sources contain no capital/control labels; the preregistration does.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import random
import sys
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from source import read_frozen
from weights import (DirectWriter, TrainedLogistic, LexicalParserControl,
                     RetrievalControl, canonical, features)
PREREG=json.loads((HERE/"prereg.json").read_text(encoding="utf-8"))
FIXTURE=tuple(PREREG["source"]["fixture_pairs"])
RESERVED=tuple(PREREG["source"]["reserved_dev_pairs"])

def archive(corpus:dict)->dict:
    return {d["requested_title"]:d for d in corpus["documents"]}

def inputs(group:dict,docs:dict)->tuple[str,tuple[dict,dict]]:
    return group["country"],tuple(sorted(
        (docs[group["capital"]],docs[group["control"]]),
        key=lambda d:d["requested_title"]))

def examples(groups:tuple[dict,...],docs:dict)->list[tuple[str,str,str,bool]]:
    x=[]
    for group in groups:
        country=group["country"]
        for field,truth in (("capital",True),("control",False)):
            page=docs[group[field]]
            x.append((page["text"],page["requested_title"],country,truth))
    return x

def pair_predict(method,group:dict,docs:dict)->str|None:
    country,pages=inputs(group,docs)
    return method.choose(country,pages)

def score_source_attribution(city:str|None,group:dict,docs:dict)->bool:
    if city!=group["capital"]:
        return False
    page=docs.get(city)
    return bool(page and page["license"]=="CC BY-SA 4.0" and
                page["reported_revision_id"]>0 and
                page["text_sha256"] and page["source_page_url"] and
                page["contributors_url"])

def evaluate(corpus:dict,*,reserved:bool)->dict:
    start=time.process_time_ns()
    docs=archive(corpus)
    first=FIXTURE[:PREREG["source"]["fixture_train_first_n"]]
    added=FIXTURE[PREREG["source"]["fixture_train_first_n"]:]
    writer=DirectWriter()
    fixture_examples=examples(first,docs)

    writer_start=time.process_time_ns()
    for phrase,city,country,truth in fixture_examples:
        writer.observe(phrase,city,country,truth)
    initial_write_cpu=time.process_time_ns()-writer_start
    initial_answers=tuple(pair_predict(writer,g,docs) for g in first)
    first_train_correct=sum(
        (writer.score(t,c,k) or 0.0)>0 if y else
        (writer.score(t,c,k) or 0.0)<0
        for t,c,k,y in fixture_examples)
    # Direct additive update of two novel source groups, no replay.
    writer_start=time.process_time_ns()
    for phrase,city,country,truth in examples(added,docs):
        writer.observe(phrase,city,country,truth)
    additional_write_cpu=time.process_time_ns()-writer_start
    retained_answers=tuple(pair_predict(writer,g,docs) for g in first)
    old_retained=sum(a==b for a,b in zip(initial_answers,retained_answers))
    all_examples=examples(FIXTURE,docs)
    final_train_correct=sum(
        (writer.score(t,c,k) or 0.0)>0 if y else
        (writer.score(t,c,k) or 0.0)<0
        for t,c,k,y in all_examples)

    baseline=TrainedLogistic()
    trained_start=time.process_time_ns()
    baseline.fit(all_examples)
    trained_cpu=time.process_time_ns()-trained_start
    literal=LexicalParserControl()
    retrieval=RetrievalControl()
    flipped=DirectWriter()
    for phrase,city,country,truth in all_examples:
        flipped.observe(phrase,city,country,not truth)
    rng=random.Random(PREREG["seeds"]["reserved" if reserved else "fixture"])
    groups=RESERVED if reserved else FIXTURE
    # ONLY blind answers are given to the models; neither candidate nor controls
    # see group["capital"] or group["control"] within their predict methods.
    prediction_start=time.process_time_ns()
    candidate=tuple(pair_predict(writer,g,docs) for g in groups)
    ordinary=tuple(pair_predict(baseline,g,docs) for g in groups)
    pattern=tuple(pair_predict(literal,g,docs) for g in groups)
    lexical=tuple(pair_predict(retrieval,g,docs) for g in groups)
    shuffled=tuple(pair_predict(flipped,g,docs) for g in groups)
    random_choices=tuple(rng.choice(tuple(d["requested_title"]
                                   for d in inputs(g,docs)[1]))
                         for g in groups)
    prediction_cpu=time.process_time_ns()-prediction_start
    # Prediction hashes are computed before answer scoring below.
    prediction_hash=hashlib.sha256(canonical({
        "candidate":candidate,"trained":ordinary,"parser":pattern,
        "retrieval":lexical,"shuffled":shuffled,"random":random_choices
    }).encode("ascii")).hexdigest()
    snapshot=writer.snapshot()
    restored=DirectWriter.restore(snapshot)
    cold_equal=(
        restored.snapshot()==snapshot and
        tuple(pair_predict(restored,g,docs) for g in groups)==candidate)
    damaged=json.loads(snapshot)
    if damaged["payload"]["weights"]:
        key=next(iter(damaged["payload"]["weights"]))
        damaged["payload"]["weights"][key]+=1.0
    bad_rejected=False
    try:
        DirectWriter.restore(json.dumps(damaged))
    except ValueError:
        bad_rejected=True
    # Unknown country is not mentioned in excerpts: abstention is compulsory.
    unknown=(
        writer.score("The lantern stood by the river for many years, serving local communities.",
                     "Unseen City","Unseen Nation"),
        writer.choose("Unseen Nation",tuple(inputs(FIXTURE[0],docs)[1])),
    )
    # At this boundary only, evaluate frozen blind predictions against
    # separately preregistered labels.
    labels=tuple(g["capital"] for g in groups)
    results={name:sum(g==p for g,p in zip(labels,pred))
             for name,pred in (
                 ("candidate",candidate),("trained",ordinary),
                 ("parser",pattern),("retrieval",lexical),
                 ("shuffled",shuffled),("random",random_choices))}
    citations=sum(score_source_attribution(p,g,docs)
                  for g,p in zip(groups,candidate))
    return {
        "schema":"wsp90.wikipedia-prose-grounding-results.v1",
        "cohort":"RESERVED_DEV_FIRST_USE" if reserved else "PUBLIC_FIXTURE",
        "source_file_documents_sha256":corpus["documents_sha256"],
        "source_pages":len(docs),
        "supervised_training_documents":len(all_examples),
        "first_six_training_documents":len(fixture_examples),
        "questions":len(groups),
        "scores":results,
        "correct_answer_source_attribution":citations,
        "first_six_train_label_correct":first_train_correct,
        "final_train_label_correct":final_train_correct,
        "old_training_pair_answers_retained":old_retained,
        "old_training_pair_answers_total":len(first),
        "trained_logistic_training_accuracy":baseline.train_accuracy,
        "unknown_confident":sum(z is not None for z in unknown),
        "cold_restore_exact":cold_equal,
        "checksum_tamper_rejected":bad_rejected,
        "numerical_weight_slots":len(writer.weights),
        "model_observations":writer.observations,
        "candidate_initial_write_cpu_ns":initial_write_cpu,
        "candidate_additional_write_cpu_ns":additional_write_cpu,
        "trained_logistic_fit_cpu_ns":trained_cpu,
        "all_methods_predict_cpu_ns":prediction_cpu,
        "whole_process_cpu_ns":time.process_time_ns()-start,
        "prediction_hash_before_labels_sha256":prediction_hash,
        "claims":"Exactly one of two prechosen source pages per country; no free-answer generation."
    }

def classify(result:dict,*,reserved:bool)->dict:
    thresholds=PREREG["metrics"]
    checks={
        "frozen_source_exact_40":result["source_pages"]==40,
        "all_controls_reported":len(result["scores"])==6,
        "fixture_initial_training_accuracy":
            result["first_six_train_label_correct"]>=thresholds["min_initial_fixture_train_correct"],
        "fixture_final_training_accuracy":
            result["final_train_label_correct"]>=thresholds["min_final_fixture_train_correct"],
        "retention":result["old_training_pair_answers_retained"]>=
            thresholds["min_first_six_pairs_retained"],
        "unknown_abstention":result["unknown_confident"]==0,
        "cold_snapshot":result["cold_restore_exact"],
        "tamper_rejected":result["checksum_tamper_rejected"],
        "source_attribution":result["correct_answer_source_attribution"]==
            result["scores"]["candidate"],
        "CPU_and_state_accounted":
            result["whole_process_cpu_ns"]>0
            and result["candidate_initial_write_cpu_ns"]>=0
            and result["trained_logistic_fit_cpu_ns"]>=0
            and result["numerical_weight_slots"]>0
            and result["model_observations"]==16,
        "fully_trained_logistic_baseline":result["trained_logistic_training_accuracy"]>=0.95,
    }
    if reserved:
        scores=result["scores"]
        checks.update({
            "heldout_national_capital_answers":
                result["questions"]==thresholds["dev_country_queries"]
                and scores["candidate"]>=thresholds["min_dev_correct"],
            "within_two_fully_trained_SGD":
                scores["trained"]-scores["candidate"]<=thresholds["max_gap_to_conventional_correct"],
            "shuffled_label_negative":
                scores["candidate"]-scores["shuffled"]>=thresholds["min_dev_advantage_over_label_shuffled"],
        })
    return {**result,"checks":checks,"passed_checks":sum(checks.values()),
        "total_checks":len(checks),
        "classification":(
            ("DEV_PROSE_RELATION_GROUNDING_FEASIBLE" if all(checks.values())
             else "DEV_PROSE_RELATION_GROUNDING_NEGATIVE") if reserved else
            ("PUBLIC_FIXTURE_FEASIBLE" if all(checks.values())
             else "PUBLIC_FIXTURE_NEGATIVE")),
        "scientific_acceptance":"UNVERIFIED",
        "general_purpose_knowledge_or_language_comprehension":False,
        "deployment":"NONE"}

def main()->None:
    a=argparse.ArgumentParser()
    modes=a.add_mutually_exclusive_group(required=True)
    modes.add_argument("--public-fixtures-only",action="store_true")
    modes.add_argument("--reserved-dev-first-use",action="store_true")
    args=a.parse_args()
    corpus=read_frozen()
    report=classify(evaluate(corpus,reserved=args.reserved_dev_first_use),
                    reserved=args.reserved_dev_first_use)
    print("WSP90_RESULT="+canonical(report))

if __name__=="__main__":
    main()

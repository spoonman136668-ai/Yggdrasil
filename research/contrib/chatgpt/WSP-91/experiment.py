"""Frozen free-span reading experiment; no DEV scoring in ordinary fixture CI.

Article text in captured CC BY-SA Wikipedia source snapshot. Training labels
are prospectively listed in prereg and passed only for 12 training articles.
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
from weights import (DirectSpanWriter, TrainedSpanLogistic,
                     SymbolicParser, LexicalCue, spans, canonical)
PROTOCOL=json.loads((HERE/"prereg.json").read_text(encoding="utf-8"))
GROUPS=PROTOCOL["source"]
TRAIN=tuple(GROUPS["training"])
PUBLIC=tuple(GROUPS["public_fixture"])
DEV=tuple(GROUPS["reserved_dev"])
RELATIONS=("symbol","atomic_number")

def articles(corpus:dict)->dict[str,dict]:
    return {row["requested_title"]:row for row in corpus["documents"]}

def answer(row:dict,relation:str)->str:
    return str(row["symbol"] if relation=="symbol" else row["atomic_number"])

def training_records(rows:tuple[dict,...],docs:dict)->tuple[tuple[str,str,str],...]:
    return tuple((docs[row["title"]]["text"],relation,answer(row,relation))
                 for row in rows for relation in RELATIONS)

def questions(rows:tuple[dict,...])->tuple[tuple[str,str],...]:
    return tuple((x["title"],r) for x in rows for r in RELATIONS)

def predict(method,docs:dict,items:tuple[tuple[str,str],...]):
    return tuple(method.extract(docs[title],relation) for title,relation in items)

def values(predictions):
    return tuple(x["value"] if x is not None else None for x in predictions)

def training_exact(method,docs,rows):
    items=questions(rows)
    return sum((p is not None and p["value"]==answer(row,rel))
               for row in rows for rel,p in zip(RELATIONS,
                   predict(method,docs,tuple((row["title"],r) for r in RELATIONS))))

def proof(proposal:dict|None, source:dict)->bool:
    if proposal is None:
        return False
    required=("value","start","end","page_id","reported_revision_id",
              "source_page_url","source_text_sha256")
    if any(k not in proposal for k in required):
        return False
    s,e=proposal["start"],proposal["end"]
    return (type(s) is int and type(e) is int and
            0<=s<e<=len(source["text"]) and
            source["text"][s:e]==proposal["value"] and
            proposal["page_id"]==source["page_id"] and
            proposal["reported_revision_id"]==source["reported_revision_id"] and
            proposal["source_page_url"]==source["source_page_url"] and
            proposal["source_text_sha256"]==source["text_sha256"] and
            source["license"]=="CC BY-SA 4.0")

class RandomSpanControl:
    def __init__(self,seed:int):
        self.rng=random.Random(seed)
    def extract(self,article:dict,relation:str)->dict|None:
        pool=spans(article["text"],relation)
        if not pool:
            return None
        start,end,value=self.rng.choice(pool)
        return {"value":value,"start":start,"end":end,
                "page_id":article["page_id"],
                "reported_revision_id":article["reported_revision_id"],
                "source_page_url":article["source_page_url"],
                "source_text_sha256":article["text_sha256"]}

def frozen_hash(obj:object)->str:
    return hashlib.sha256(canonical(obj).encode("ascii")).hexdigest()

def evaluate(corpus:dict,*,reserved:bool)->dict:
    start_cpu=time.process_time_ns()
    docs=articles(corpus)
    first=TRAIN[:8]
    additional=TRAIN[8:]
    early=training_records(first,docs)
    added=training_records(additional,docs)
    writer=DirectSpanWriter()

    begin=time.process_time_ns()
    for text,relation,truth in early:
        writer.observe(text,relation,truth)
    candidate_initial_write_cpu=time.process_time_ns()-begin
    early_questions=questions(first)
    initial_predictions=predict(writer,docs,early_questions)
    initial_exact=training_exact(writer,docs,first)
    snapshot_first=writer.snapshot()

    begin=time.process_time_ns()
    for text,relation,truth in added:
        writer.observe(text,relation,truth)
    candidate_incremental_write_cpu=time.process_time_ns()-begin
    retained_predictions=predict(writer,docs,early_questions)
    retained_correct=sum(
        output is not None and output["value"]==answer(row,relation)
        for row in first for relation,output in zip(RELATIONS,
            predict(writer,docs,tuple((row["title"],r) for r in RELATIONS))))
    final_training_exact=training_exact(writer,docs,TRAIN)

    conventional=TrainedSpanLogistic()
    begin=time.process_time_ns()
    conventional.fit(early+added)
    conventional_train_cpu=time.process_time_ns()-begin
    conventional_training_exact=training_exact(conventional,docs,TRAIN)
    parser=SymbolicParser()
    retrieval=LexicalCue()
    # The preregistration freezes the protocol SHA but does not list
    # a random-control seed. Derive it prospectively from that immutable
    # commit and distinct cohort names; NEVER from outcomes or labels.
    cohort_name="reserved" if reserved else "fixture"
    seed_bytes=hashlib.sha256(("WSP91|span-control|"+cohort_name+
                              "|698c3ba125b94880271d68713d20326ffeab95fe").encode("ascii")).digest()
    rng=RandomSpanControl(int.from_bytes(seed_bytes[:8],"big"))
    pool=DEV if reserved else PUBLIC
    queries=questions(pool)

    begin=time.process_time_ns()
    models={
        "direct_numeric":predict(writer,docs,queries),
        "fully_trained_SGD":predict(conventional,docs,queries),
        "symbolic_regex":predict(parser,docs,queries),
        "literal_cue":predict(retrieval,docs,queries),
        "random_source_span":predict(rng,docs,queries),
    }
    eval_cpu=time.process_time_ns()-begin
    snapshot_final=writer.snapshot()
    restore=DirectSpanWriter.restore(snapshot_final)
    cold_exact=(
        snapshot_final==restore.snapshot() and
        values(predict(restore,docs,queries))==values(models["direct_numeric"])
        and values(predict(DirectSpanWriter.restore(snapshot_first),docs,early_questions))==
            values(initial_predictions))
    corrupted=json.loads(snapshot_final)
    weight_head=corrupted["payload"]["weights"]["symbol"]
    if weight_head:
        key=next(iter(weight_head))
        weight_head[key]+=3.0
    tamper=False
    try:
        DirectSpanWriter.restore(json.dumps(corrupted))
    except ValueError:
        tamper=True
    unknown_page={**docs[TRAIN[0]["title"]],"text":"This is prose without digits."}
    unknowns=(
        writer.extract(unknown_page,"atomic_number"),
        writer.extract(docs[TRAIN[0]["title"]],"unregistered_relation"),
        writer.extract({},"symbol"),
    )
    unknown_confident=sum(x is not None for x in unknowns)
    prediction_hash=frozen_hash({
        "methods":{k:values(p) for k,p in models.items()},
        "initial":values(initial_predictions),
        "after_added":values(retained_predictions),
        "unknown_confident":unknown_confident,
        "snapshot_sha256":hashlib.sha256(snapshot_final.encode("ascii")).hexdigest(),
    })

    # At this point only, the evaluator looks at reserved answer labels
    # in the frozen preregistration to score previously-frozen predictions.
    answer_map={(row["title"],rel):answer(row,rel)
                for row in pool for rel in RELATIONS}
    correct={method:sum(p is not None and p["value"]==answer_map[q]
                        for p,q in zip(predictions,queries))
             for method,predictions in models.items()}
    proof_count=sum(
        p is not None and p["value"]==answer_map[q] and proof(p,docs[q[0]])
        for q,p in zip(queries,models["direct_numeric"]))
    per_question=[{
        "article":title,"relation":rel,
        "expected":answer_map[(title,rel)],
        "predicted":{method:(p[i]["value"] if p[i] is not None else None)
                     for method,p in models.items()},
        "numeric_source_span":[models["direct_numeric"][i]["start"],
                               models["direct_numeric"][i]["end"]]
                              if models["direct_numeric"][i] is not None else None
    } for i,(title,rel) in enumerate(queries)]
    cpu=time.process_time_ns()-start_cpu
    return {
        "schema":"wsp91.free-span-from-real-prose-development.v1",
        "cohort":"RESERVED_DEV_FIRST_USE" if reserved else "PUBLIC_FIXTURE",
        "source_documents_sha256":corpus["documents_sha256"],
        "total_source_articles":len(docs),
        "supervised_training_articles":len(TRAIN),
        "total_queries":len(queries),
        "correct_counts":correct,
        "numeric_correct_source_proofs":proof_count,
        "first_training_exact":initial_exact,
        "final_training_exact":final_training_exact,
        "first_16_fields_retained_exact":retained_correct,
        "initial_to_incremental_same_answers":sum(
            (a is not None and b is not None and a["value"]==b["value"])
            for a,b in zip(initial_predictions,retained_predictions)),
        "trained_conventional_train_exact":conventional_training_exact,
        "unknown_confident":unknown_confident,
        "cold_restore":cold_exact,
        "tamper_detected":tamper,
        "numeric_occupied_weights":writer.occupied_weights(),
        "candidate_observed_supervised_fields":writer.observed_fields,
        "candidate_initial_weight_edit_CPU_ns":candidate_initial_write_cpu,
        "candidate_incremental_edit_CPU_ns":candidate_incremental_write_cpu,
        "trained_ordinary_SGD_fit_CPU_ns":conventional_train_cpu,
        "all_methods_eval_CPU_ns":eval_cpu,
        "whole_process_CPU_ns":cpu,
        "predictions_frozen_before_label_scoring_sha256":prediction_hash,
        "source_span_proof_definition":"Exact raw substring offsets plus captured page, revision and SHA256; not independent semantic entailment.",
        "per_question":per_question,
    }

def classify(report:dict,*,reserved:bool)->dict:
    t=PROTOCOL["protocol"]["thresholds"]
    correct=report["correct_counts"]
    checks={
        "frozen_source_36_articles":report["total_source_articles"]==36,
        "candidate_initial_source_fit":report["first_training_exact"]>=t["min_initial_training_exact"],
        "candidate_final_source_fit":report["final_training_exact"]>=t["min_final_training_exact"],
        "old_reading_skill_retained":report["first_16_fields_retained_exact"]>=t["min_old_training_retention"],
        "fully_trained_ordinary_baseline":report["trained_conventional_train_exact"]>=
            t["trained_baseline_training_exact_min"],
        "unknown_abstention":report["unknown_confident"]==t["unknown_confident_answers"],
        "cold_restore_exact":report["cold_restore"],
        "tamper_rejection":report["tamper_detected"],
        "source_span_proof":report["numeric_correct_source_proofs"]==correct["direct_numeric"],
        "all_controls_reported":len(correct)==5,
        "whole_cpu_and_state_count":(
            report["whole_process_CPU_ns"]>0 and
            report["candidate_initial_weight_edit_CPU_ns"]>=0 and
            report["trained_ordinary_SGD_fit_CPU_ns"]>=0 and
            report["candidate_observed_supervised_fields"]==24 and
            report["numeric_occupied_weights"]>0),
    }
    if reserved:
        checks.update({
            "reserved_free_answer_exact":report["total_queries"]==32 and
                correct["direct_numeric"]>=t["min_reserved_exact"],
            "within_fully_trained_SGD":correct["fully_trained_SGD"]-
                correct["direct_numeric"]<=t["max_gap_vs_fully_trained_SGD_answers"],
            "within_symbolic":correct["symbolic_regex"]-
                correct["direct_numeric"]<=t["max_gap_vs_symbolic_answers"],
            "beats_random_source_spans":correct["direct_numeric"]-
                correct["random_source_span"]>=t["min_reserved_advantage_vs_random_answers"],
        })
    else:
        checks["public_fixture_exact"]=correct["direct_numeric"]>=t["min_public_fixture_correct"]
    classification=(
        ("DEV_FREE_SPAN_READING_FEASIBLE" if all(checks.values())
         else "DEV_FREE_SPAN_READING_NEGATIVE")
        if reserved else
        ("PUBLIC_FIXTURE_FEASIBLE" if all(checks.values())
         else "PUBLIC_FIXTURE_NEGATIVE"))
    return {**report,"checks":checks,"passed_checks":sum(checks.values()),
            "total_checks":len(checks),"classification":classification,
            "scientific_acceptance":"UNVERIFIED",
            "general_knowledge_or_LLM_equivalence":False,
            "deployment":"NONE"}

def main()->None:
    parser=argparse.ArgumentParser()
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--public-fixtures-only",action="store_true")
    group.add_argument("--reserved-dev-first-use",action="store_true")
    opts=parser.parse_args()
    corpus=read_frozen()
    report=classify(evaluate(corpus,reserved=opts.reserved_dev_first_use),
                    reserved=opts.reserved_dev_first_use)
    print("WSP91_RESULT="+canonical(report),flush=True)

if __name__=="__main__":
    main()

"""WSP111 sealed two-generation, unnamed relational category induction.

The experimental task supplies raw relations and observable consequences but
NO named new relation predicates, NO correct latent class IDs and NO count of
hidden classes to any learner. The dynamic invented predicates are written
directly into sparse numeric associative weights. Each model receives exactly
the same 3000 two-intervention feedback examples. Heldout consequences remain
in oracle.py, and the evaluator may read them only after all model prediction
records and new parameter layers are SHA256-sealed.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
import math
from pathlib import Path
import sys
import time

import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from world import N_GROUPS,N_SUPPORT,N_TEST,N_INPUT_FACTS,original_facts
from native import NativeRelationInventor,effect_signature
from controls import IndependentSymbolicInventor,ConventionalInventor


def accuracy_metrics(predicted,truth,width):
    if len(predicted)!=len(truth):
        raise ValueError("incomplete heldout evidence")
    exact_correct=sum(a==b for a,b in zip(predicted,truth))
    bit_rows={}
    for bit in range(width):
        tp=sum(bool(a&(1<<bit)) and bool(b&(1<<bit)) for a,b in zip(predicted,truth))
        fp=sum(bool(a&(1<<bit)) and not bool(b&(1<<bit)) for a,b in zip(predicted,truth))
        fn=sum(not bool(a&(1<<bit)) and bool(b&(1<<bit)) for a,b in zip(predicted,truth))
        tn=len(truth)-tp-fp-fn
        precision=tp/(tp+fp) if tp+fp else 0.
        recall=tp/(tp+fn) if tp+fn else 0.
        bit_rows[str(bit)]={
            "tp":tp,"fp":fp,"fn":fn,"tn":tn,
            "precision":precision,"recall":recall,
            "f1":2*precision*recall/(precision+recall) if precision+recall else 0.,
            "accuracy":(tp+tn)/len(truth),
        }
    return {
        "n":len(truth),"exact_correct":exact_correct,
        "exact_accuracy":exact_correct/len(truth),
        "confusion":{
            str(actual):{str(pred):sum(a==pred and b==actual for a,b in zip(predicted,truth))
                         for pred in sorted(set(predicted))}
            for actual in sorted(set(truth))
        },
        "bit_metrics":bit_rows,
        "positive_effect_bits_predicted":sum(int(k).bit_count() for k in predicted),
        "positive_effect_bits_actual":sum(int(k).bit_count() for k in truth),
    }


def adjusted_rand_index(actual,predicted):
    """Permutation-invariant partition recovery with no class-label matching."""
    if len(actual)!=len(predicted) or len(actual)<2:
        raise ValueError("ARI needs matching group partitions")
    cells=Counter(zip(actual,predicted))
    rows=Counter(actual)
    cols=Counter(predicted)
    choose2=lambda n:n*(n-1)/2.
    n=len(actual)
    observed=sum(choose2(x) for x in cells.values())
    row_pairs=sum(choose2(x) for x in rows.values())
    col_pairs=sum(choose2(x) for x in cols.values())
    expectation=row_pairs*col_pairs/choose2(n)
    denominator=(row_pairs+col_pairs)/2.-expectation
    return (observed-expectation)/denominator if denominator else 1.


def train_and_discover(feedback,raw):
    times={}
    source,relation,target=raw
    t=time.process_time()
    direct=NativeRelationInventor()
    direct.program_original(source,relation,target)
    old_original_sha=direct.original_sha256()
    times["direct_original_one_million_program_cpu"]=time.process_time()-t
    t=time.process_time()
    symbolic=IndependentSymbolicInventor()
    symbolic.load_facts(source,relation,target)
    times["symbolic_original_one_million_load_cpu"]=time.process_time()-t
    t=time.process_time()
    direct.program_first_operator(feedback)
    direct.infer_first()
    times["direct_first_learning_and_invented_relations_cpu"]=time.process_time()-t
    t=time.process_time()
    symbolic.learn_first(feedback)
    symbolic.infer_first()
    times["symbolic_first_learning_and_invented_relations_cpu"]=time.process_time()-t
    t=time.process_time()
    conventional=ConventionalInventor(symbolic)
    conventional.learn_first(feedback)
    conventional.infer_first()
    times["conventional_first_learning_and_invented_relations_cpu"]=time.process_time()-t
    t=time.process_time()
    direct.program_second_operator(feedback)
    direct.infer_second()
    times["direct_second_learning_and_invented_relations_cpu"]=time.process_time()-t
    t=time.process_time()
    symbolic.learn_second(feedback)
    symbolic.infer_second()
    times["symbolic_second_learning_and_invented_relations_cpu"]=time.process_time()-t
    t=time.process_time()
    conventional.learn_second(feedback)
    conventional.infer_second()
    times["conventional_second_learning_and_invented_relations_cpu"]=time.process_time()-t

    if (len(direct.original_keys)!=N_INPUT_FACTS or
        len(symbolic.facts)!=N_INPUT_FACTS or
        len(direct.derived1)!=N_GROUPS or len(direct.derived2)!=N_GROUPS or
        len(symbolic.derived1)!=N_GROUPS or len(symbolic.derived2)!=N_GROUPS or
        len(conventional.derived1)!=N_GROUPS or len(conventional.derived2)!=N_GROUPS):
        raise AssertionError("one-million source or invented relational facts missing")
    if direct.original_sha256()!=old_original_sha:
        raise AssertionError("direct programming overwrote previous raw knowledge")
    if (direct.first_signatures!=symbolic.first_signatures or
        direct.second_signatures!=symbolic.second_signatures):
        raise AssertionError("numeric and independent symbolic inventor discovered different categories")
    for head in (*conventional.head1,*conventional.head2):
        if head.gradient_inf is None or not head.gradient_inf<=1e-8 or head.steps>100:
            raise AssertionError("fully optimized conventional control not converged")
    return direct,symbolic,conventional,times,old_original_sha


def execute():
    start=time.monotonic()
    cpu=time.process_time()
    t=time.process_time()
    raw=original_facts()
    source_elapsed=time.process_time()-t
    from oracle import training_feedback
    feedback=training_feedback()
    if (len(feedback)!=N_SUPPORT or
        [x[0] for x in feedback]!=list(range(N_SUPPORT))):
        raise AssertionError("frozen first-use support group sequence drift")
    direct,symbolic,conventional,times,old_sha=train_and_discover(feedback,raw)
    times["original_fact_generation_cpu"]=source_elapsed
    preds={name:[] for name in ("direct","symbolic","conventional","no_discovery","rotated_binding")}
    t=time.process_time()
    # Negative controls are derived only from actual train-programmed model
    # operators, before any withheld true effect is accessed.
    for g in range(N_SUPPORT,N_GROUPS):
        d=direct.predictions(g)
        s=symbolic.predictions(g)
        c=conventional.predictions(g)
        if d!=s:
            raise AssertionError("numeric and independent symbolic relational inference diverged")
        a,b,third=direct.chain(g)
        kind=4*a+b-4
        wrong_first=effect_signature(direct.operator1[(kind+1)%16])
        if wrong_first not in direct.first_signatures:
            raise AssertionError("negative control used unknown invented first relation")
        wrong_first_index=direct.first_signatures.index(wrong_first)
        wrong_second=effect_signature(direct.operator2[
            wrong_first_index,(third-10+1)%4])
        preds["direct"].append(d)
        preds["symbolic"].append(s)
        preds["conventional"].append(c)
        preds["no_discovery"].append((0,0))
        preds["rotated_binding"].append((wrong_first,wrong_second))
    times["all_arms_heldout_preoracle_predictions_cpu"]=time.process_time()-t

    # Sealing MUST precede any withheld oracle effect or hidden signature reads.
    state=direct.checkpoint()
    state_parts=state["parts"]
    sealed={
        "raw_million_numerical_weights_sha256":old_sha,
        "training_feedback_sha256":sha256(json.dumps(
            feedback,separators=(",",":")).encode("ascii")).hexdigest(),
        "first_unknown_class_operator_sha256":sha256(direct.operator1.tobytes()).hexdigest(),
        "second_unknown_class_operator_sha256":sha256(direct.operator2.tobytes()).hexdigest(),
        "first_invented_relation_weights_sha256":sha256(direct.derived1.tobytes()).hexdigest(),
        "second_invented_relation_weights_sha256":sha256(direct.derived2.tobytes()).hexdigest(),
        "cold_snapshot_sha256":state["sha256"],
        "all_arms_heldout_predictions_sha256":sha256(json.dumps(
            preds,separators=(",",":"),sort_keys=True).encode("ascii")).hexdigest(),
    }
    t=time.process_time()
    restored=NativeRelationInventor.cold_restore(state)
    if (restored.original_sha256()!=old_sha or
        not np.array_equal(restored.original_keys,direct.original_keys) or
        not np.array_equal(restored.operator1,direct.operator1) or
        not np.array_equal(restored.operator2,direct.operator2) or
        not np.array_equal(restored.derived1,direct.derived1) or
        not np.array_equal(restored.derived2,direct.derived2)):
        raise AssertionError("previous knowledge or new category weights lost across cold restoration")
    for g in range(N_SUPPORT,N_GROUPS):
        if restored.predictions(g)!=preds["direct"][g-N_SUPPORT]:
            raise AssertionError("cold restored invented categories changed predictions")
    changed={"schema":state["schema"],"maps":state["maps"],
             "parts":dict(state_parts),"sha256":state["sha256"]}
    blob=bytearray(changed["parts"]["derived2"])
    blob[0]^=7
    changed["parts"]["derived2"]=bytes(blob)
    rejected=False
    try:
        NativeRelationInventor.cold_restore(changed)
    except ValueError:
        rejected=True
    if not rejected:
        raise AssertionError("tampered discovered second relation parameter accepted")
    times["full_million_weight_cold_restore_and_22000_prediction_replay_cpu"]=time.process_time()-t

    # First original heldout effect oracle access is intentionally below.
    from oracle import effect_one,effect_two,hidden_signature
    true_one=[effect_one(g) for g in range(N_SUPPORT,N_GROUPS)]
    true_two=[effect_two(g) for g in range(N_SUPPORT,N_GROUPS)]
    latent_classes=[hidden_signature(g) for g in range(N_SUPPORT,N_GROUPS)]
    metrics={
        arm:{
            "first_3bit_effect":accuracy_metrics([x[0] for x in records],true_one,3),
            "second_2bit_effect":accuracy_metrics([x[1] for x in records],true_two,2),
            "invented_first_class_ari_vs_private_latent_equivalence":
                adjusted_rand_index(latent_classes,[x[0] for x in records]),
        } for arm,records in preds.items()
    }
    if metrics["direct"]!=metrics["symbolic"]:
        raise AssertionError("numeric must match independent symbolic on unseen original effects")
    if not (metrics["direct"]["first_3bit_effect"]["exact_accuracy"]>
            metrics["rotated_binding"]["first_3bit_effect"]["exact_accuracy"] and
            metrics["direct"]["second_2bit_effect"]["exact_accuracy"]>
            metrics["rotated_binding"]["second_2bit_effect"]["exact_accuracy"]):
        raise AssertionError("rotated semantic negative did not degrade both discoveries")
    if not (
        metrics["no_discovery"]["first_3bit_effect"]["exact_accuracy"]<
            metrics["direct"]["first_3bit_effect"]["exact_accuracy"] and
        metrics["no_discovery"]["second_2bit_effect"]["exact_accuracy"]<
            metrics["direct"]["second_2bit_effect"]["exact_accuracy"]
    ):
        raise AssertionError("no-discovery negative not discriminative")
    if direct.original_sha256()!=old_sha:
        raise AssertionError("original million knowledge entries mutated in evaluation")

    return {
        "schema":"wsp111.million-native-weights-dynamic-relation-invention-dev.v1",
        "classification":"DEV_UNKNOWN_RELATION_CATEGORY_INDUCTION_PARITY_NOT_SCIENTIFIC_PASS",
        "scientific_pass":False,
        "direct_weight_superiority":False,
        "real_open_world_predicate_semantics":False,
        "source_million_factual_weights":N_INPUT_FACTS,
        "source_native_parameter_bytes":direct.original_keys.nbytes+direct.original_weights.nbytes,
        "train_feedback_intervention_groups":N_SUPPORT,
        "unfamiliar_heldout_entities_groups":N_TEST,
        "unknown_first_relation_categories_invented":len(direct.first_signatures),
        "unknown_second_relation_categories_invented":len(direct.second_signatures),
        "invented_first_sensory_signatures":list(direct.first_signatures),
        "invented_second_sensory_signatures":list(direct.second_signatures),
        "original_first_and_second_relation_templates_preprovided":False,
        "first_direct_operator_float32_parameter_count":direct.operator1.size,
        "second_direct_operator_float32_parameter_count":direct.operator2.size,
        "new_first_relation_parameter_entries":len(direct.derived1),
        "new_second_relation_parameter_entries":len(direct.derived2),
        "original_million_facts_preserved":True,
        "cold_restore_all_weights_and_both_derived_generations":True,
        "modified_second_relation_snapshot_rejected":True,
        "independent_symbolic_original_fact_set_entries":len(symbolic.facts),
        "conventional_gradient_residuals":[head.gradient_inf
            for head in (*conventional.head1,*conventional.head2)],
        "conventional_newton_steps":[head.steps
            for head in (*conventional.head1,*conventional.head2)],
        "conventional_training_accuracies":[head.train_accuracy
            for head in (*conventional.head1,*conventional.head2)],
        "heldout_metrics":metrics,
        "prescore_sha256_receipts":sealed,
        "per_arm_stage_cpu_seconds":times,
        "whole_process_cpu_seconds":time.process_time()-cpu,
        "whole_process_wall_seconds":time.monotonic()-start,
        "limitations":"Causal sensory effect outputs (3 bits/2 bits) and input relation-pair family supplied; categories induced from 3000 labeled responses within same known source vocab; heldout entities new but true mechanisms shared, deterministic synthetic noise, unrelated distractor facts dominate 1m memory, native sparse associative weights not dense Yggdrasil model; no autonomous active intervention choice or AGI demonstrated.",
    }


if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--frozen-unknown-relation-invention-dev",action="store_true",required=True)
    a.parse_args()
    result=execute()
    print("WSP111_UNKNOWN_RELATION_DEV="+json.dumps(
        result,sort_keys=True,separators=(",",":")),flush=True)

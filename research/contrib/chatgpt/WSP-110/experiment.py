"""WSP110 preregistered one-million-parameter fact and operator discovery DEV.

A native sparse fact parameter memory is directly programmed with 1,000,000
observed facts. A first learned operator predicts relation X from raw chains;
those predictions are written into numeric derived-weight memory. A *second*
learned operator composes newly inferred X with a third original relation to
predict relation Y, without reading any withheld X or Y truth during inference.

All heldout predictions, operators, training feedback and source weights are
SHA256-sealed before hidden_x / hidden_y are called for test entities.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import time

import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from world import (
    N_GROUPS,N_SUPPORT,N_TEST,N_INPUT_FACTS,original_facts,
    support_feedback,hidden_x,hidden_y,heldout_groups,
)
from native_weights import NativeSparseWeightMemory
from controls import SymbolicAssociationControl,ConventionalOperatorControl,L2,TOL


def _metrics(predicted,truth):
    a=np.asarray(list(predicted),dtype=np.bool_)
    y=np.asarray(truth,dtype=np.bool_)
    if a.shape!=y.shape or a.ndim!=1:
        raise ValueError("heldout prediction source/answer mismatch")
    tp=int(np.count_nonzero(a & y))
    fp=int(np.count_nonzero(a & ~y))
    fn=int(np.count_nonzero(~a & y))
    tn=int(np.count_nonzero(~a & ~y))
    total=len(a)
    precision=tp/(tp+fp) if tp+fp else 0.
    recall=tp/(tp+fn) if tp+fn else 0.
    return {"n":total,"tp":tp,"fp":fp,"fn":fn,"tn":tn,
            "accuracy":(tp+tn)/total,
            "precision":precision,
            "recall":recall,
            "f1":(2*precision*recall/(precision+recall)
                  if precision+recall else 0.),
            "actual_positive":int(np.count_nonzero(y)),
            "predicted_positive":int(np.count_nonzero(a))}


def execute():
    started=time.monotonic()
    cpu=time.process_time()
    times={}
    t=time.process_time()
    sources,relations,targets=original_facts()
    times["generated_million_source_cpu_seconds"]=time.process_time()-t
    if len(sources)!=N_INPUT_FACTS or len(set(int(r) for r in relations))<19:
        raise AssertionError("frozen million-fact source / distractors malformed")
    t=time.process_time()
    native=NativeSparseWeightMemory()
    native.program_million(sources,relations,targets)
    original_digest=native.original_digest()
    times["direct_fact_programming_cpu_seconds"]=time.process_time()-t
    t=time.process_time()
    symbolic=SymbolicAssociationControl()
    symbolic.load_facts(sources,relations,targets)
    times["symbolic_fact_loading_cpu_seconds"]=time.process_time()-t
    feedback=support_feedback()
    if len(feedback)!=N_SUPPORT:
        raise AssertionError("exact observed support count changed")
    feedback_receipt=sha256(json.dumps(feedback,
        separators=(",",":")).encode("ascii")).hexdigest()
    t=time.process_time()
    native.program_operator_weights(feedback)
    times["direct_operator_programming_cpu_seconds"]=time.process_time()-t
    t=time.process_time()
    symbolic.observe(feedback)
    times["symbolic_operator_induction_cpu_seconds"]=time.process_time()-t
    t=time.process_time()
    conventional=ConventionalOperatorControl(symbolic)
    conventional.learn(feedback)
    times["conventional_fully_fitted_operator_cpu_seconds"]=time.process_time()-t

    # Independent composition rounds. No learner ever receives heldout oracle
    # X/Y labels; stage two must consume newly predicted stage-one X values.
    t=time.process_time()
    native.infer_first_round()
    times["direct_first_round_cpu_seconds"]=time.process_time()-t
    t=time.process_time()
    native.infer_second_round()
    times["direct_second_round_cpu_seconds"]=time.process_time()-t
    t=time.process_time()
    symbolic.infer_first()
    symbolic.infer_second()
    times["symbolic_both_rounds_cpu_seconds"]=time.process_time()-t
    t=time.process_time()
    conventional.infer_first()
    conventional.infer_second()
    times["conventional_both_rounds_cpu_seconds"]=time.process_time()-t

    if native.original_digest()!=original_digest:
        raise AssertionError("learning derived facts mutated original source parameters")
    first_weights=native.stage1_operator.tolist()
    second_weights=native.stage2_operator.tolist()
    predictions={
        "direct":[],
        "symbolic":[],
        "conventional":[],
        "no_operator":[],
        "rotated_binding_negative":[],
    }
    rotated1=np.roll(native.stage1_operator,1)
    rotated2=np.roll(native.stage2_operator,1)
    for g in heldout_groups():
        d=native.predictions(g)
        s=symbolic.predictions(g)
        c=conventional.predictions(g)
        a,b,k=native.get_chain(g)
        wrong_x=bool(rotated1[a*4+b-4]>0.5)
        wrong_y=bool(wrong_x and rotated2[k-10]>0.5)
        predictions["direct"].append(d)
        predictions["symbolic"].append(s)
        predictions["conventional"].append(c)
        predictions["no_operator"].append((False,False))
        predictions["rotated_binding_negative"].append((wrong_x,wrong_y))
        if d!=s:
            raise AssertionError("direct numeric weights and independently induced symbolic rules diverged")

    # Seal ALL heldout operator states and both discovery rounds before oracle.
    sealed={
        "observed_support_sha256":feedback_receipt,
        "original_native_million_fact_sha256":original_digest,
        "direct_stage1_operator_sha256":sha256(native.stage1_operator.tobytes()).hexdigest(),
        "direct_stage2_operator_sha256":sha256(native.stage2_operator.tobytes()).hexdigest(),
        "new_x_parameter_sha256":sha256(native.derived_x_keys.tobytes()).hexdigest(),
        "new_y_parameter_sha256":sha256(native.derived_y_keys.tobytes()).hexdigest(),
        "heldout_predictions_sha256":sha256(json.dumps(
            predictions,sort_keys=True,separators=(",",":")).encode("ascii")).hexdigest(),
    }
    checkpoint=native.checkpoint()
    restored=NativeSparseWeightMemory.cold_restore(checkpoint)
    if restored.original_digest()!=original_digest:
        raise AssertionError("cold native weights source changed")
    if not (np.array_equal(restored.stage1_operator,native.stage1_operator)
            and np.array_equal(restored.stage2_operator,native.stage2_operator)
            and np.array_equal(restored.derived_x_keys,native.derived_x_keys)
            and np.array_equal(restored.derived_y_keys,native.derived_y_keys)):
        raise AssertionError("cold restoration not exact after both discovery rounds")
    for g in heldout_groups():
        if restored.predictions(g)!=native.predictions(g):
            raise AssertionError("cold heldout prediction changed")
    tampered={"schema":checkpoint["schema"],
        "parts":dict(checkpoint["parts"]),"sha256":checkpoint["sha256"]}
    corrupted=bytearray(tampered["parts"]["operator1"])
    corrupted[0]^=1
    tampered["parts"]["operator1"]=bytes(corrupted)
    tamper_rejected=False
    try:
        NativeSparseWeightMemory.cold_restore(tampered)
    except ValueError:
        tamper_rejected=True
    if not tamper_rejected:
        raise AssertionError("tampering with discovered operators was accepted")

    # This is the FIRST and only heldout answer read in the qualified source.
    truth_x=np.asarray([hidden_x(g) for g in heldout_groups()],dtype=np.bool_)
    truth_y=np.asarray([hidden_y(g) for g in heldout_groups()],dtype=np.bool_)
    scores={
        arm:{
            "relation_x":_metrics((p[0] for p in preds),truth_x),
            "relation_y":_metrics((p[1] for p in preds),truth_y),
        }
        for arm,preds in predictions.items()
    }
    if not (scores["direct"]==scores["symbolic"] and
            scores["direct"]["relation_x"]["n"]==N_TEST and
            scores["direct"]["relation_y"]["n"]==N_TEST):
        raise AssertionError("semantic parity or 22000 heldout cases missing")
    if (scores["rotated_binding_negative"]["relation_x"]["f1"] >=
            scores["direct"]["relation_x"]["f1"]):
        # Negative controls must be genuinely discriminative, not retrospectively tuned.
        raise AssertionError("shuffled relation bindings did not hurt learned composition")
    if len(native.derived_x_keys)==0 or len(native.derived_y_keys)==0:
        raise AssertionError("no new knowledge programmed in either discovery round")
    if native.original_digest()!=original_digest:
        raise AssertionError("original million weights changed after scoring")

    return {
        "schema":"wsp110.million-native-sparse-facts-two-round-operator-induction-dev.v1",
        "status":"DEV_ONLY_NOT_SCIENTIFIC_PASS",
        "scientific_pass":False,
        "direct_weight_superiority":False,
        "native_dense_neural_weight_programming":False,
        "fully_autonomous_unknown_relation_discovery":False,
        "pretrained_external_knowledge_used":False,
        "protected_original_first_use":False,
        "source_million_facts":int(native.keys.size),
        "source_native_parameter_bytes":native.original_storage_bytes(),
        "initial_training_groups":N_SUPPORT,
        "heldout_novel_entity_groups":N_TEST,
        "raw_input_chain_edges":3*N_GROUPS,
        "raw_input_isolated_distractors":N_INPUT_FACTS-3*N_GROUPS,
        "direct_compositional_operator_parameters":len(first_weights)+len(second_weights),
        "stage1_direct_operator_weights":first_weights,
        "stage2_direct_operator_weights":second_weights,
        "stage1_correctly_inferred_new_associations":scores["direct"]["relation_x"]["tp"],
        "stage1_false_inferred_associations":scores["direct"]["relation_x"]["fp"],
        "stage2_correctly_inferred_new_associations":scores["direct"]["relation_y"]["tp"],
        "stage2_false_inferred_associations":scores["direct"]["relation_y"]["fp"],
        "total_stage1_stored_new_weights":len(native.derived_x_keys),
        "total_stage2_stored_new_weights":len(native.derived_y_keys),
        "source_million_facts_unchanged_after_both_rounds":True,
        "native_weight_cold_restoration":True,
        "tampered_checkpoint_rejected":tamper_rejected,
        "symbolic_million_fact_count":len(symbolic.facts),
        "conventional_head1_gradient_inf":conventional.first.gradient_inf,
        "conventional_head2_gradient_inf":conventional.second.gradient_inf,
        "conventional_head1_newton_steps":conventional.first.steps,
        "conventional_head2_newton_steps":conventional.second.steps,
        "conventional_head1_training_accuracy":conventional.first.train_accuracy,
        "conventional_head2_training_accuracy":conventional.second.train_accuracy,
        "source_and_predictions_sealed_before_test_oracle":sealed,
        "heldout_metrics":scores,
        "stage_cpu_seconds":times,
        "total_cpu_seconds":time.process_time()-cpu,
        "total_wall_seconds":time.monotonic()-started,
        "limitations":"Synthetic known three-relation chain family; target X,Y meanings and allowable pair/conditional templates supplied; labeled training oracle supervision; sparse native parameter table, not dense neural AGI; independent strong symbolic and conventional controls required.",
    }


if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--frozen-million-native-operator-dev",action="store_true",required=True)
    a.parse_args()
    result=execute()
    print("WSP110_MILLION_OPERATOR_DEV="+json.dumps(result,sort_keys=True,separators=(",",":")),flush=True)

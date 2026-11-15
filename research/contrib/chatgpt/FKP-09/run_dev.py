"""FKP-09 frozen public DEV: 64-input observational action-consequence learning.
Run only after exact-source Linux+Windows preflight. Never protected first-use.
No post-result tuning or promotion to native Yggdrasil.
"""
from __future__ import annotations
import hashlib
import json
import statistics
import time

from source import Source,ORIGINALS,REVISIONS,NEGATIVES,PAID,HELD,context_slot
from model import (SharedWeights,ConventionalIncremental,direct_solve,
                   conventional_exact_solve,predict_program,replay_counts,
                   RAW_BYTES,CHECKPOINT_BYTES)

PREFIXES=(16,32,64,128)
assert len(ORIGINALS)==24 and len(REVISIONS)==8 and len(NEGATIVES)==8

def run():
    start=time.perf_counter()
    owner=Source()
    memory=SharedWeights()
    conventional=ConventionalIncremental()
    sealed=[]; histories={}
    receipt=hashlib.sha256()
    source_wall=0.0; direct_fit_wall=0.0
    conventional_exact_wall=0.0;direct_update_wall=0.0
    incremental_update_wall=0.0;candidate_predict_wall=0.0
    control_predict_wall=0.0
    total_paid=0; rank128=[]; changed=0; negative_abstentions=0
    unaffected_before={}; no_collateral=True; all_counts_match=True

    for seed in (*ORIGINALS,*REVISIONS,*NEGATIVES):
        t=time.perf_counter()
        view=owner.view(seed)
        evidence=tuple((x,owner.observe(seed,x)) for x in view.choices)
        source_wall+=time.perf_counter()-t
        assert len(evidence)==PAID and owner.charged(seed)==PAID
        total_paid+=PAID
        prefix_records=[]
        for budget in PREFIXES:
            t=time.perf_counter()
            status,p,rank=direct_solve(evidence[:budget])
            direct_fit_wall+=time.perf_counter()-t
            t=time.perf_counter()
            ctrl_status,ctrl_p,ctrl_rank=conventional_exact_solve(evidence[:budget])
            conventional_exact_wall+=time.perf_counter()-t
            assert (status,p,rank)==(ctrl_status,ctrl_p,ctrl_rank)
            t=time.perf_counter()
            predicted=tuple(predict_program(p,x) for x in view.held) if p is not None else None
            candidate_predict_wall+=time.perf_counter()-t
            t=time.perf_counter()
            conventional_pred=tuple(predict_program(ctrl_p,x) for x in view.held) if ctrl_p is not None else None
            control_predict_wall+=time.perf_counter()-t
            assert predicted==conventional_pred
            prefix_records.append((budget,status,rank,predicted))
        final=prefix_records[-1]
        rank128.append((seed,final[1],final[2]))
        if seed in NEGATIVES:
            if final[1]=="INCONSISTENT" and final[3] is None:
                negative_abstentions+=1
        else:
            if final[1]!="EXACT" or final[3] is None:
                raise AssertionError("FKP09_SOURCE_NOT_IDENTIFIABLE_AT_128")
            slot=context_slot(seed)
            if seed in REVISIONS:
                old=memory.program(slot)
            else:
                old=None
            if seed == REVISIONS[0]:
                unaffected_before={i:memory.program(i) for i in range(8,24)}
            t=time.perf_counter();memory.update(slot,direct_solve(evidence)[1])
            direct_update_wall+=time.perf_counter()-t
            t=time.perf_counter();conventional.update(slot,final_program := direct_solve(evidence)[1])
            incremental_update_wall+=time.perf_counter()-t
            if old is not None and old!=final_program:
                changed+=1
            no_collateral &= all(memory.program(i)==p for i,p in unaffected_before.items())
            all_counts_match &= (tuple(memory.counts)==replay_counts(memory.all_programs())==
                                 tuple(conventional.counts))
        for budget,status,rank,pred in prefix_records:
            receipt.update(seed.to_bytes(2,"big")+budget.to_bytes(2,"big"))
            receipt.update(status.encode("ascii"))
            receipt.update(b"?" if pred is None else bytes(pred))
        sealed.append((seed,view.held,tuple(prefix_records)))
        histories[seed]=hashlib.sha256(
            b"".join(x.to_bytes(8,"little")+bytes((y,)) for x,y in evidence)
        ).hexdigest()

    # No held answers have been accessed; all predictions are frozen.
    prediction_sha256=receipt.hexdigest()
    outcome_rows=[]
    t=time.perf_counter()
    for seed,held,prefix_records in sealed:
        actual=owner.held_dev(seed,held)
        for budget,status,rank,pred in prefix_records:
            matches=(sum(x==y for x,y in zip(pred,actual)) if pred is not None else 0)
            outcome_rows.append({"seed":seed,"prefix":budget,"status":status,
                "rank":rank,"covered":int(pred is not None),
                "accuracy_all_held":matches/HELD})
    scoring_wall=time.perf_counter()-t
    t=time.perf_counter();snapshot=memory.snapshot();restored=SharedWeights.restore(snapshot)
    cold_wall=time.perf_counter()-t
    assert restored.snapshot()==snapshot
    assert all(restored.program(i)==memory.program(i) for i in range(32))
    assert all(restored.program(i)==p for i,p in unaffected_before.items())
    tampered=bytearray(snapshot);tampered[10]^=1
    try:SharedWeights.restore(bytes(tampered))
    except ValueError:tamper_rejected=True
    else:raise AssertionError("FKP09_CORRUPTION_ACCEPTED")

    exact_rows=[r for r in outcome_rows if r["prefix"]==128 and r["seed"] not in NEGATIVES]
    avg=statistics.mean(r["accuracy_all_held"] for r in exact_rows)
    negative_confident=sum(r["covered"] for r in outcome_rows
                           if r["seed"] in NEGATIVES and r["prefix"]==128)
    # Both share identical genuine source acquisition and development source.
    # Equal-information conventional incremental can reuse SAME optimized fit.
    candidate_whole=source_wall+direct_fit_wall+direct_update_wall+candidate_predict_wall+cold_wall+scoring_wall
    conventional_whole=source_wall+direct_fit_wall+incremental_update_wall+control_predict_wall+cold_wall+scoring_wall
    ratio=candidate_whole/conventional_whole
    mechanism=(avg>=.99 and changed==8 and no_collateral and all_counts_match and
               negative_abstentions==8 and negative_confident==0 and tamper_rejected)
    # Exact same-information GF2 is a prediction tie; no 5pp superiority.
    # Only a replicated >=2x whole-process win could justify next scientific gate.
    qualifies_cost=ratio<=0.5
    return {
        "schema":"fkp09.public-dev-inplace-shared-weight.v1",
        "preregistered":True,"protected_first_use":False,
        "dev_original_consumed":True,"worlds":40,"paid_actions":total_paid,
        "held_predictions_per_arm_per_budget":40*HELD,
        "held_predictions_per_arm_all_budgets":40*HELD*len(PREFIXES),
        "contexts_current":24,"repaired_current_slots":changed,
        "unaffected_current_contexts_preserved":len(unaffected_before),
        "no_collateral_forgetting":no_collateral,
        "shared_replay_exact":all_counts_match,
        "negative_out_of_family_abstained":negative_abstentions,
        "negative_confident_acceptances":negative_confident,
        "source_full_rank":rank128,
        "accuracy_128_known_family":avg,
        "strong_conventional_exact_accuracy_128":avg,
        "exact_control_accuracy_advantage":0.0,
        "raw_learned_weight_bytes":len(memory.raw_weights()),
        "checkpoint_bytes":len(snapshot),
        "cold_restore_bit_exact":True,"tamper_rejected":tamper_rejected,
        "prediction_sealed_sha256":prediction_sha256,
        "paid_evidence_sha256_by_world":histories,
        "wall_seconds":{
            "source_paid":source_wall,"candidate_all_fits":direct_fit_wall,
            "reference_exact_fits":conventional_exact_wall,
            "direct_updates":direct_update_wall,
            "optimized_conventional_updates":incremental_update_wall,
            "candidate_predict":candidate_predict_wall,
            "control_predict":control_predict_wall,
            "cold_checkpoint":cold_wall,"held_scoring":scoring_wall,
            "candidate_matched_whole":candidate_whole,
            "optimized_conventional_matched_whole":conventional_whole,
            "candidate_to_optimized_conventional":ratio,
            "total_run":time.perf_counter()-start
        },
        "mechanism_gate_dev":mechanism,
        "science_unique_gain_dev":bool(mechanism and qualifies_cost),
        "scientific_pass":False,
        "classification":("DEV_MECHANISM_PASS_NO_NATIVE_SCIENCE"
                          if mechanism else "DEV_NO_GO_MECHANISM"),
        "per_world_prefix_accuracy":outcome_rows
    }

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))

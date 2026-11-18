"""Read-only receipt audit for CKAD25-X. Does not import native learner or scorer.

Reconstructs held truth from captured deterministic seed, source-only class
coefficients and input roster, and recomputes EVERY source-evaluated metric.
It does not execute original scientific first-use or change preregistered gates.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import random
from pathlib import Path


def check(ok,label):
    if not ok:raise ValueError("CKAD25X_AUDIT_"+label)


def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode("ascii")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def roster(seed):
    masks=list(range(16))
    key=digest(canonical(["CKAD25-X-HIDDEN-SOURCE-ROSTER",seed]))
    random.Random(int(key[:16],16)).shuffle(masks)
    return masks[:12],masks[12:]


def truth(weight,mask):
    features=sum(1<<i for i in range(16) if (mask&i)==i)
    return (weight&features).bit_count()&1


def audit(raw):
    d=json.loads(raw)
    check(raw==canonical(d),"NONCANONICAL_ORIGINAL_BYTES")
    check(d["schema"]=="yggdrasil.ckad25x.active-native-causal-discrimination.v1","SCHEMA")
    check(d["science_seeds"]==[65021,65027,65033,65039],"SEED_ROSTER")
    check(d["first_use_scored"] is True,"PROSPECTIVE_ONLY")
    check(d["native_source_free_training_observations"]==160,"SOURCE_BUDGET")
    check(d["phase_policy_revealed_target_observations"]==320,"DIAGNOSTIC_BUDGET")
    check(d["held_phase_cases_per_policy"]==80,"HELD_PHASE_BUDGET")
    check(d["distinct_held_world_outcomes_per_policy"]==64,"HELD_UNIQUE_LABELS")
    check(d["A_repeat_is_not_fresh_held_evidence"] is True,"REPEAT_ACCOUNTING")
    check(d["original_protected_world_calls"]==0 and d["native_owner_first_use"] is False,
          "NO_PROTECTED_SOURCE")
    check(d["scientific_pass"] is False and d["conventional_superiority"] is False,
          "FALSE_SCIENTIFIC_ACCEPTANCE")
    check(d["accepted_main_mutated"] is False and d["forge_dispatch"] is False
          and d["accepted_native"] is False and d["native_promotion"] is False
          and d["deployment"] is False,"FALSE_PRODUCTION_AUTHORITY")
    check(len(d["per_phase_policy"])==80,"ORIGINAL_CASES")
    check(set(d["source_retention_by_seed"])=={"65021","65027","65033","65039"},
          "NATIVE_RETENTION_ROSTER")
    methods={"native_recall","exact_continuous","exact_hard","logistic","forest",
             "no_memory","fixed_A","recent_B","privileged_oracle"}
    policies={"native_active","fixed","random","conventional_eig"}
    snapshots={}
    counts={}
    for seed in d["science_seeds"]:
        source,held=roster(seed)
        entry=d["source_retention_by_seed"][str(seed)]
        check(entry["source_train_sha256"]==digest(canonical(source))
              and entry["held_mask_sha256"]==digest(canonical(held))
              and entry["native_old_and_compiled_retained"] is True,"SOURCE_STATE_"+str(seed))
        ws=entry["source_family_coefficients_evaluator_only"]
        check(len(ws)==4 and [v.bit_count() for v in ws]==[3,3,4,5],
              "SOURCE_CLASS_"+str(seed))
        snapshots[seed]=(source,held,ws)
    for row in d["per_phase_policy"]:
        seed,phase,policy=row["seed"],row["phase"],row["policy"]
        check(seed in snapshots and 0<=phase<5 and policy in policies,"CASE_ID")
        tag=(seed,phase,policy)
        check(tag not in counts,"DUPLICATED_CASE")
        counts[tag]=True
        source,held,ws=snapshots[seed]
        kind=("A","B","A","C","D")[phase]
        coeff={"A":ws[0],"B":ws[1],"C":ws[2],"D":ws[3]}[kind]
        check(row["evaluator_only_hidden_world"]==kind and
              row["A_return_is_duplicate_held_not_new_sample"] is (phase==2),
              "HIDDEN_REGIME_METADATA")
        chosen=row["target_source_probe_masks"]
        check(len(chosen)==4 and len(set(chosen))==4 and set(chosen).issubset(source)
              and not set(chosen)&set(held),"DO_ACTION_LEAKAGE")
        probes=[[mask&7,mask>>3,truth(coeff,mask)] for mask in chosen]
        check(row["target_revealed_probes_sha256"]==digest(canonical(probes)),
              "ORIGINAL_TARGET_OBSERVATIONS")
        check(row["common_held_mask_sha256"]==digest(canonical(held)),
              "CONSISTENT_HELD")
        labels=[truth(coeff,mask) for mask in held]
        check(row["held_truth_sha256"]==digest(canonical(labels)),
              "ORIGINAL_HELD_EVALUATOR")
        for slot in (1,2):
            src=[[m&7,m>>3,truth(ws[slot-1],m)] for m in source]
            check(row["source_fit_"+("A" if slot==1 else "B")+"_sha256"]==digest(canonical(src)),
                  "SOURCE_FIT_"+str(slot))
        check(set(row["metrics"])==methods,"METHOD_ROSTER")
        for method,m in row["metrics"].items():
            vals=m["held_predictions"]
            check(len(vals)==4,"HELD_OUTPUT_COUNT")
            ps=[]
            for p in vals:
                check(type(p) is list and len(p)==2 and p[1]>0,"PREDICTION_ENCODING")
                value=float(p[0]/p[1])
                check(0<=value<=1,"PREDICTION_BOUNDS")
                ps.append(value)
            brier=sum((p-y)**2 for p,y in zip(ps,labels))/4
            answered=sum(p in (0.,1.) for p in ps)
            good=sum(p in (0.,1.) and int(p)==y for p,y in zip(ps,labels))
            bad=sum(p in (0.,1.) and int(p)!=y for p,y in zip(ps,labels))
            check(abs(brier-m["brier"])<=1e-8 and answered==m["answered"]
                  and good==m["correct_answered"]
                  and bad==m["incorrect_answered"],"EVALUATOR_PARITY_"+method)
        check(row["metrics"]["native_recall"]["held_predictions"]==
              row["metrics"]["exact_hard"]["held_predictions"],"CONVENTIONAL_HARD_PARITY")
    check(len(counts)==80,"MISSING_CASES")
    means={}
    for policy in policies:
        means[policy]={}
        cases=[x for x in d["per_phase_policy"] if x["policy"]==policy]
        check(len(cases)==20,"ARM_IMBALANCE")
        for method in methods:
            value=sum(x["metrics"][method]["brier"] for x in cases)/20
            check(abs(value-d["held_brier_by_policy_method"][policy][method])<=1e-8,
                  "AGGREGATE_BRIER_"+policy+"_"+method)
            means[policy][method]=round(value,9)
    candidate=[x for x in d["per_phase_policy"] if x["policy"]=="native_active"]
    old=[x for x in candidate if x["phase"] in (0,1,2)]
    novel=[x for x in candidate if x["phase"] in (3,4)]
    return_ok=sum(x["selected_native_slot"]==1 for x in candidate if x["phase"]==2)
    correct_regimes=sum(x["selected_native_slot"]== (2 if x["phase"]==1 else 1) for x in old)
    fam_answered=sum(x["metrics"]["native_recall"]["answered"] for x in old)
    fam_bad=sum(x["metrics"]["native_recall"]["incorrect_answered"] for x in old)
    nov_brier=sum(x["metrics"]["native_recall"]["brier"] for x in novel)/8
    nov_bad=sum(x["metrics"]["native_recall"]["incorrect_answered"] for x in novel)
    check(return_ok==d["candidate_return_A_seeds_correct"] and
          correct_regimes==d["candidate_familiar_regimes_correct"] and
          fam_answered==d["candidate_known_confident_answered"] and
          fam_bad==d["candidate_known_confident_wrong"] and
          abs(nov_brier-d["candidate_novel_brier"])<1e-8 and
          nov_bad==d["candidate_novel_confident_wrong"],"AGGREGATE_CUSTODY")
    gates=d["frozen_gates"]
    check(all(gates[k] for k in gates if k!="native_beats_random_by_0_04"),
          "NONFAIL_GATES")
    check(gates["native_beats_random_by_0_04"] is False and
          d["development_disposition"]=="DEVELOPMENT_NO_GO","PRESERVE_NO_GO")
    check(means["native_active"]["native_recall"]==0.133888889 and
          means["random"]["native_recall"]==0.140138889 and
          means["fixed"]["native_recall"]==0.175,"ORIGINAL_METRIC_ID")
    return {"original_sha256":digest(raw),"arm_brier":{k:v["native_recall"] for k,v in means.items()},
            "return_A_recognized":return_ok,"novel_brier":round(nov_brier,9),
            "development_disposition":d["development_disposition"],
            "all_80_case_metrics_reconstructed_without_generator":True,
            "protected_source_actions":0}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("original",type=Path)
    args=p.parse_args()
    report=audit(args.original.read_bytes())
    print("CKAD25X_INDEPENDENT_SOURCE_ONLY_ORIGINAL_SCORE_AUDIT_PASS")
    print(json.dumps(report,sort_keys=True))


if __name__=="__main__":main()

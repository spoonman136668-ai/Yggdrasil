"""Independent read-only custody and evaluator reconstruction for CKAD25-AC.

No import of CKAD25-AC scorer, prior study or NativeCumulativeLearner.
Regenerates observable histories, hidden negative permutations and every
paid-action/held result from frozen provenance, independent of original code.
Does NOT retrain or re-score original source-first-use cohort.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import itertools
import json
import random
from pathlib import Path

SEEDS=(78101,78119,78139,78157,78179,78203,78233,78251,
       78277,78299,78317,78341,78367,78383,78407,78431)
CONDITIONS=("STABLE","REASSIGNED")
ARMS=("native_beta_memory","independent_exact_conventional_beta",
      "fixed_address","seeded_uniform_two","permutation_marginalized_bayes")
SHIFT={0,1,3,4,5,7}


def check(ok,tag):
    if not ok:raise ValueError("CKAD25AC_INDEPENDENT_AUDIT_"+tag)


def canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,
                      allow_nan=False).encode("ascii")


def sha(x):
    return hashlib.sha256(x).hexdigest()


def rng(family,tag,*args):
    h=sha(canon([family,tag,*args]))
    return random.Random(int(h[:16],16))


def law(weight,mask):
    row=sum(1<<j for j in range(16) if (mask&j)==j)
    return (row&weight).bit_count()&1


def batch(weight,ids,fault=None):
    return [[k&7,k>>3,law(weight,k)^(k==fault)] for k in ids]


def source_split(seed):
    a=list(range(16))
    rng("CKAD25-AB","public-roster",seed).shuffle(a)
    return a[:12],sorted(a[12:])


def models_fit(rows):
    obs=[(sum(1<<j for j in range(16)
              if ((c|(a<<3))&j)==j),y) for c,a,y in rows]
    return tuple(mask for n in range(4)
                 for group in itertools.combinations(range(16),n)
                 for mask in [sum(1<<k for k in group)]
                 if all((mask&f).bit_count()%2==y for f,y in obs))


def replay_prior(history,candidates,weight):
    counts={x:0 for x in candidates}
    fail={x:0 for x in candidates}
    for packet in history:
        for c,a,y in packet:
            k=c|(a<<3)
            check(k in counts,"HISTORY_CANDIDATE_PUBLIC")
            counts[k]+=1
            fail[k]+=int(y!=law(weight,k))
    p={x:Fraction(1+fail[x],2+counts[x]) for x in candidates}
    return sorted(candidates,key=lambda k:(-p[k],k))[:2]


def metric(p,held):
    vals=[float(x) for x in p]
    return {
        "brier":round(sum((x-y)**2 for x,y in zip(vals,held))/2,9),
        "confident_wrong":sum(x in (0,1) and int(x)!=y for x,y in zip(vals,held)),
        "confident":sum(x in (0,1) for x in vals),
        "held_fractions":[[x.numerator,x.denominator] for x in p]
    }


def audit(raw):
    d=json.loads(raw)
    check(canon(d)==raw,"CANONICAL_BYTES")
    check(d["schema"]=="yggdrasil.ckad25ac.identity-mutation-location-reassignment.v1",
          "ORIGINAL_SCHEMA")
    check(d["seeds"]==list(SEEDS) and d["scored_original"] is True,"ORIGINAL_SEEDS")
    check(d["source_checkpoint_sha256"]=="c52681bf26f08817b3747647472913fa792da2de33f74b8fa7c0f2b0e78c119f",
          "ORIGINAL_NATIVE_CHECKPOINT")
    check(d["parent_scoring_source_sha256"]=="00d17c1f0b5b74084484d359d1abea41f2ecd4fc1f7ed1b9a65e4919556dbeca",
          "PARENT_EXECUTABLE_DRIFT")
    check(d["genuine_source_actions"]==8352
          and d["held_conditional_predictions"]==2560
          and d["distinct_evaluator_labels"]==1024
          and d["no_true_role_or_mapping_supplied_to_native"] is True
          and d["full_action_semantics_remapped"] is False
          and d["latent_role_reassigned_no_mapping_sensor"] is True,
          "ACTION_SOURCE_BUDGET")
    check(d["scientific_pass"] is False and d["conventional_superiority"] is False
          and d["universal_OOD_safety"] is False
          and d["protected_owner_first_use"] is False
          and d["accepted_main_changed"] is False
          and d["forge_dispatch"] is False and d["merge"] is False
          and d["deployment"] is False,
          "UNAUTHORIZED_SCIENTIFIC_PROMOTION")
    recorded=d["policy_world_cases"]
    check(len(recorded)==1280 and len(d["per_seed_provenance"])==16,"CASE_ROSTER")
    bykey={}
    for row in recorded:
        k=(row["seed"],row["stage"],row["condition"],row["arm"])
        check(k not in bykey and row["seed"] in SEEDS
              and type(row["stage"]) is int and 0<=row["stage"]<8
              and row["condition"] in CONDITIONS and row["arm"] in ARMS,
              "DUPLICATE_OR_UNKNOWN_CASE")
        bykey[k]=row
    derived={c:{a:[] for a in ARMS} for c in CONDITIONS}
    natural=0
    for seed in SEEDS:
        fit,candidates=source_split(seed)
        rec=d["per_seed_provenance"][str(seed)]
        weights=rec["evaluator_only_weights"]
        check(set(weights)=={"A","B","C"} and
              len(set(weights.values()))==3 and
              all(type(x) is int and x.bit_count()==3 for x in weights.values()),
              "AUTHENTIC_SOURCE_GRAMMAR")
        check(rec["source_pool_sha256"]==sha(canon(fit))
              and rec["candidate_pool_sha256"]==sha(canon(candidates))
              and len(set(fit+candidates))==16
              and not (set(fit)&set(candidates)),"FIT_HELD_SEPARATION")
        check(all(models_fit(batch(weights[k],fit))==(weights[k],)
                  for k in ("A","B","C")),"SOURCE_COMMITTEE_INDEPENDENT_FIT")
        four=rec["source_four_public_diagnostics"]
        check(len(four)==4 and len(set(four))==4
              and set(four).issubset(fit)
              and len(rec["native_causal_committee_sha256"])==3
              and all(len(x)==64 for x in rec["native_causal_committee_sha256"]),
              "SOURCE_COLD_AND_IDENTITY_PROBES")
        for x,y in itertools.combinations(("A","B","C"),2):
            check(any(law(weights[x],mask)!=law(weights[y],mask)
                      for mask in four),"REAL_SOURCE_ID_DISCRIMINATES")
        hidden=rng("CKAD25-AC","recurrent-role",seed)
        hot=candidates[hidden.randrange(4)]
        check(rec["evaluator_only_hotspot"]==hot,"EVALUATOR_HIDDEN_ROLE_SHA")
        history=[]
        faults=[]
        actually=False
        for i in range(3):
            role=(hot if hidden.random()<.75 else
                  hidden.choice([x for x in candidates if x!=hot]))
            probe=list(candidates)
            rng("CKAD25-AC","past-probes",seed,i).shuffle(probe)
            observed=batch(weights["C"],probe[:2],role)
            check(rec["historical_witnesses"][i]==observed,
                  "REAL_HISTORY_WITNESS_"+str(i))
            history.append(observed)
            faults.append(role)
            actually|=(role==hot and hot in probe[:2])
        check(rec["historical_evaluator_fault_roles"]==faults
              and rec["hotspot_actually_witnessed"] is actually
              and len(rec["historical_cold_sha256"])==64,
              "HISTORY_CUSTODY")
        natural+=int(actually)
        selected=replay_prior(history,candidates,weights["C"])
        check(rec["native_beta_selected"]==selected
              and rec["conventional_beta_selected"]==selected,
              "INDEPENDENT_NATIVE_CONVENTIONAL_PRIOR_PARITY")
        expected_marginal=[[k,1,4] for k in candidates]
        check(rec["identity_blind_marginal"]==expected_marginal,
              "EXACT_UNIFORM_MARGINALIZED_24_BIJECTIONS")
        worlds=rec["worlds_evaluator_only"]
        check(len(worlds)==8,"FROZEN_WORLD_COUNT")
        for stage in range(8):
            shifted=stage in SHIFT
            role=(hot if hidden.random()<.75 else
                  hidden.choice([x for x in candidates if x!=hot])) if shifted else None
            shuffle=list(candidates)
            rng("CKAD25-AC","hidden-target-reassignment",seed,stage).shuffle(shuffle)
            mapping=dict(zip(candidates,shuffle))
            world=worlds[stage]
            check(world["stage"]==stage and world["changed"] is shifted
                  and world["hidden_prior_role"]==role
                  and world["hidden_reassignment"]==[mapping[k] for k in candidates],
                  "HIDDEN_PERMUTATION_INDEPENDENT_REPLAY")
            for condition in CONDITIONS:
                fault=(role if condition=="STABLE" else
                       mapping[role] if shifted else None)
                common=batch(weights["C"],four,fault)
                check(common==batch(weights["C"],four),
                      "COMMON_NEW_SOURCE_ID_CANNOT_REVEAL_MAPPING")
                for arm in ARMS:
                    row=bykey[(seed,stage,condition,arm)]
                    if arm in ("native_beta_memory","independent_exact_conventional_beta"):
                        chosen=selected
                    elif arm in ("fixed_address","permutation_marginalized_bayes"):
                        chosen=sorted(candidates)[:2]
                    else:
                        choice=list(candidates)
                        rng("CKAD25-AC","uniform-probes",seed,stage,condition).shuffle(choice)
                        chosen=choice[:2]
                    held=sorted(set(candidates)-set(chosen))
                    witnessed=batch(weights["C"],chosen,fault)
                    ys=[law(weights["C"],k)^(k==fault) for k in held]
                    detected=fault in chosen
                    predictions=([Fraction(1,2)]*2 if detected else
                                 [Fraction(law(weights["C"],k),1) for k in held])
                    check(row["evaluator_only_shifted"] is shifted
                          and row["evaluator_only_role"]==role
                          and row["evaluator_only_visible_fault"]==fault
                          and row["selected_visible_masks"]==chosen
                          and row["remaining_held_visible_masks"]==held
                          and row["source_inference_slot"]==3
                          and row["source_inference_status"]=="RECALLED"
                          and row["actual_four_source_sha256"]==sha(canon(common))
                          and row["actual_two_interventions_sha256"]==sha(canon(witnessed))
                          and row["remaining_held_truth_sha256"]==sha(canon(ys)),
                          "HELD_LABEL_AND_CHARGED_SOURCE")
                    check(row["detected"] is detected
                          and row["witness_status"]==("FALSIFIED" if detected else "CONSISTENT")
                          and row["metric"]==metric(predictions,ys)
                          and row["cold_retained"] is True
                          and len(row["target_cold_sha256"])==64
                          and row["paid_source_actions"]==4
                          and row["paid_interventions"]==2,
                          "EVALUATOR_HELD_PREDICTION_AND_COLD")
                    derived[condition][arm].append(row)
    check(len(bykey)==1280,"ALL_CASES_RECONSTRUCTED")
    summaries={}
    for condition in CONDITIONS:
        summaries[condition]={}
        for arm in ARMS:
            rows=derived[condition][arm]
            changed=[x for x in rows if x["evaluator_only_shifted"]]
            stable=[x for x in rows if not x["evaluator_only_shifted"]]
            check(len(rows)==128 and len(changed)==96 and len(stable)==32,
                  "EXACT_WORLD_SOURCE_CASES")
            m={"shifted_detected":sum(x["detected"] for x in changed),
               "shifted_total":96,
               "detection_rate":round(sum(x["detected"] for x in changed)/96,9),
               "stationary_false_alarms":sum(x["detected"] for x in stable),
               "conditional_held_brier":round(sum(x["metric"]["brier"] for x in rows)/128,9),
               "conditional_confident_wrong":sum(x["metric"]["confident_wrong"] for x in rows),
               "paid_actions":sum(x["paid_source_actions"]+x["paid_interventions"]
                                  for x in rows)}
            check(m==d["condition_arms"][condition][arm],
                  "FROZEN_ORIGINAL_SUMMARY_"+arm)
            summaries[condition][arm]=m
    stable=summaries["STABLE"]["native_beta_memory"]
    moved=summaries["REASSIGNED"]["native_beta_memory"]
    gates={
        "all_native_committee_and_source_history_retain_exact_cold":
            all(x["cold_retained"] for x in recorded),
        "exact_original_action_budget":
            len(SEEDS)==16 and
            all(s["paid_actions"]==768 for cs in summaries.values() for s in cs.values()),
        "organically_witnessed_role_eight_sixteen":natural>=8,
        "stable_learned_intervention_advantage":
            all(stable["detection_rate"]>=summaries["STABLE"][arm]["detection_rate"]+.08-1e-12
                for arm in ("fixed_address","seeded_uniform_two"))
            and stable["stationary_false_alarms"]==0,
        "reassigned_transfer_advantage":
            all(moved["detection_rate"]>=summaries["REASSIGNED"][arm]["detection_rate"]+.08-1e-12
                for arm in ("fixed_address","seeded_uniform_two"))
            and moved["detection_rate"]>=stable["detection_rate"]-.08-1e-12
            and moved["stationary_false_alarms"]==0,
        "conventional_no_information_leak":
            all(summaries[c]["native_beta_memory"]==
                summaries[c]["independent_exact_conventional_beta"] for c in CONDITIONS)
            and all(d["per_seed_provenance"][str(seed)]["native_beta_selected"]==
                    d["per_seed_provenance"][str(seed)]["conventional_beta_selected"]
                    for seed in SEEDS),
        "no_false_alarms":
            all(v["stationary_false_alarms"]==0 for c in summaries.values() for v in c.values()),
        "permutation_marginal_calibration":
            all(x["paid_actions"]==768 for x in summaries["REASSIGNED"].values())
    }
    check(gates==d["frozen_gates"] and
          d["development_disposition"]=="DEVELOPMENT_NO_GO" and
          gates["stable_learned_intervention_advantage"] is False and
          gates["reassigned_transfer_advantage"] is False,
          "FROZEN_NO_GO_MUST_PRESERVE_FAILURES")
    return {"original_sha256":sha(raw),"evaluator_cases":len(bykey),
            "witnessed_source_outcomes":8352,"held_predictions":2560,
            "organic_hotspot_witnessed_seeds":natural,
            "rates":{c:{a:s["detection_rate"] for a,s in v.items()}
                     for c,v in summaries.items()},
            "development":"DEVELOPMENT_NO_GO","scientific_pass":False}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("original",type=Path)
    proof=audit(p.parse_args().original.read_bytes())
    print("CKAD25AC_INDEPENDENT_1280_ACTION_AND_HELD_AUDIT_PASS")
    print(json.dumps(proof,sort_keys=True))


if __name__=="__main__":
    main()

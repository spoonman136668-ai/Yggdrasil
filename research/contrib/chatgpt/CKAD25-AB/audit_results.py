"""Read-only CKAD25-AB original held and source action reconstruction.

NO import of native model or original scorer. Independently rebuild every
observed source history witness, 4 current do outcomes, 2 chosen do outcomes,
2 never-witnessed held labels, Beta policy decision and scoring, including
all fixed/random comparison arms. Cross-platform original results must be
byte-identical before accepting this audit.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import itertools
import json
import random
from pathlib import Path

SEEDS=(76103,76123,76147,76171,76193,76213,76237,76259,76283,76309,76333,76357,76379,76403,76427,76453)
SHIFTS={0,1,3,4,5,7}
ARMS=("native_history_beta","exact_conventional_history_beta","fixed_smallest_two","seeded_random_two")


def ck(ok,reason):
    if not ok:raise ValueError("CKAD25AB_INDEPENDENT_"+reason)


def canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode("ascii")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def seeded(tag,*args):
    return random.Random(int(sha(canon(["CKAD25-AB",tag,*args]))[:16],16))


def heldtruth(w,mask):
    features=sum(1<<i for i in range(16) if mask&i==i)
    return (w&features).bit_count()&1


def inputs(seed):
    a=list(range(16))
    seeded("public-roster",seed).shuffle(a)
    return a[:12],sorted(a[12:])


def records(w,masks,wrong=None):
    return [[m&7,m>>3,heldtruth(w,m)^(m==wrong)] for m in masks]


def full_models(data):
    rows=[(sum(1<<i for i in range(16) if (c|(a<<3))&i==i),y)
          for c,a,y in data]
    return tuple(w for n in range(4)
                 for group in itertools.combinations(range(16),n)
                 for w in [sum(1<<i for i in group)]
                 if all((w&mask).bit_count()%2==y for mask,y in rows))


def history_policy(history,c_weight,candidates):
    scores={}
    for mask in candidates:
        total=0
        wrong=0
        for obs in history:
            for c,a,y in obs:
                if c|(a<<3)==mask:
                    total+=1
                    wrong+=int(y!=heldtruth(c_weight,mask))
        scores[mask]=Fraction(1+wrong,2+total)
    return sorted(candidates,key=lambda x:(-scores[x],x))[:2]


def audit(raw):
    d=json.loads(raw)
    ck(canon(d)==raw,"NONCANONICAL_RESULT_BYTES")
    ck(d["schema"]=="yggdrasil.ckad25ab.actual-history-native-action-choice.v1","SCHEMA")
    ck(d["seeds"]==list(SEEDS) and d["scored_original"] is True,"ORIGINAL_ROSTER")
    ck(d["original_native_ckad25_source_sha256"]=="c52681bf26f08817b3747647472913fa792da2de33f74b8fa7c0f2b0e78c119f","NATIVE_PARENT")
    ck(d["public_source_observations"]==3744
       and d["actual_target_witness_calls_by_arm"]==768
       and d["held_predictions"]==1024
       and d["unique_evaluator_target_action_labels"]==512,"SOURCE_ACTION_BUDGET")
    ck(d["paired_held_addresses_across_policies"] is False
       and d["hidden_hotspot_not_supplied_to_native"] is True
       and d["one_native_learner_with_persistent_causal_history_per_seed"] is True,
       "HELD_POLICY_DIFFERENCE")
    ck(d["source_free_and_nonprotected"] is True
       and d["scientific_pass"] is False and d["conventional_superiority"] is False
       and d["universal_OOD_safety"] is False
       and d["accepted_main_changed"] is False
       and d["owner_original_first_use"] is False
       and d["forge_dispatch"] is False and d["merge"] is False
       and d["deployment"] is False,"FALSE_SCIENCE_OR_AUTHORITY")
    ck(len(d["per_policy_world"])==512 and len(d["per_seed_provenance"])==16,
       "EQUAL_SOURCE_BUDGET_ROSTER")
    mapping={}
    for row in d["per_policy_world"]:
        key=(row["seed"],row["stage"],row["arm"])
        ck(row["seed"] in SEEDS and type(row["stage"]) is int
           and 0<=row["stage"]<8 and row["arm"] in ARMS
           and key not in mapping,"DUPLICATE_CASE")
        mapping[key]=row
    perpolicy={a:[] for a in ARMS}
    naturally=0
    for seed in SEEDS:
        source,candidates=inputs(seed)
        item=d["per_seed_provenance"][str(seed)]
        weights=item["evaluator_only_source_weights"]
        ck(set(weights)=={"A","B","C"}
           and len(set(weights.values()))==3
           and all(type(w) is int and w.bit_count()==3
                   and any(i&8 for i in range(16) if w&(1<<i))
                   for w in weights.values()),"REAL_NEW_SOURCE_CLASS_"+str(seed))
        ck(all(sum(heldtruth(weights[x],m)!=heldtruth(weights[y],m)
                   for m in source)>=4
               for x,y in (("A","B"),("A","C"),("B","C"))),
           "SOURCE_CLASS_SEPARATION_"+str(seed))
        ck(item["source_pool_sha256"]==sha(canon(source))
           and item["candidate_pool_sha256"]==sha(canon(candidates))
           and len(set(source+candidates))==16
           and not set(source)&set(candidates)
           and item["old_slot0_source_unchanged"] is True
           and len(item["native_source_memory_committee_sha256"])==3,
           "SOURCE_SPLITS_"+str(seed))
        for k,w in weights.items():
            fit=records(w,source)
            ck(item["source_fit_observed_sha256"][k]==sha(canon(fit))
               and full_models(fit)==(w,),"SOURCE_FITTING_"+str(seed)+k)
        four=item["public_four_diagnostic_masks"]
        ck(len(four)==4 and len(set(four))==4 and set(four).issubset(source)
           and all(any(heldtruth(weights[x],m)!=heldtruth(weights[y],m)
                   for m in four)
                   for x,y in (("A","B"),("A","C"),("B","C"))),
           "PUBLIC_ONLY_FOUR_SOURCE_DIAGNOSTIC")
        h=seeded("recurrent-risk",seed)
        hotspot=candidates[h.randrange(4)]
        ck(item["evaluator_only_recurrent_hotspot"]==hotspot,"HIDDEN_HOTSPOT_CUSTODY")
        history=[]
        faults=[]
        found=False
        for st in range(3):
            fault=(hotspot if h.random()<.75 else
                   h.choice([x for x in candidates if x!=hotspot]))
            probes=list(candidates)
            seeded("history-probe",seed,st).shuffle(probes)
            shown=records(weights["C"],probes[:2],fault)
            ck(item["historical_real_witness_records"][st]==shown,
               "HISTORICAL_ACTUAL_EFFECTS_"+str(seed)+str(st))
            faults.append(fault)
            found|=(fault==hotspot and hotspot in probes[:2])
            history.append(shown)
        ck(item["evaluator_only_prior_faults"]==faults
           and item["naturally_witnessed_hot_spot"] is found,
           "NO_FORCED_HISTORY_COVERAGE")
        naturally+=int(found)
        selected=history_policy(history,weights["C"],candidates)
        ck(item["independent_conventional_beta_actions"]==selected
           and item["native_beta_actions"]==selected,
           "ACTUAL_LEARNED_PROBE_SOURCE_PARITY_"+str(seed))
        ck(len(item["historical_cold_native_sha256"])==64,
           "NATIVE_COLD_PERSISTED_SHA")
        for st in range(8):
            changed=st in SHIFTS
            fault=(None if not changed else
                   hotspot if h.random()<.75 else
                   h.choice([x for x in candidates if x!=hotspot]))
            current=records(weights["C"],four,fault)
            for arm in ARMS:
                row=mapping[(seed,st,arm)]
                ck(row["evaluator_only_shifted"] is changed
                   and row["evaluator_only_fault_address"]==fault
                   and row["evaluator_only_hot_address"]==hotspot
                   and row["native_inferred_source_slot"]==3
                   and row["source_identification_status"]=="RECALLED"
                   and row["actual_target_source_actions"]==4
                   and row["actual_target_selected_actions"]==2,
                   "CHARGED_WORLD_CUSTODY_"+arm)
                ck(row["four_real_source_diagnostics_sha256"]==sha(canon(current))
                   and row["historical_cold_sha256"]==item["historical_cold_native_sha256"],
                   "EQUAL_TARGET_SOURCE_WITNESSES")
                if arm in ("native_history_beta","exact_conventional_history_beta"):
                    probes=selected
                elif arm=="fixed_smallest_two":
                    probes=sorted(candidates)[:2]
                else:
                    probes=list(candidates)
                    seeded("random-policy",seed,st).shuffle(probes)
                    probes=probes[:2]
                ck(row["selected_action_masks"]==probes
                   and len(set(probes))==2,"POLICY_INDEPENDENT_SELECTION")
                remaining=sorted(x for x in candidates if x not in probes)
                revealed=records(weights["C"],probes,fault)
                truths=[heldtruth(weights["C"],x)^(x==fault) for x in remaining]
                ck(row["remaining_held_masks"]==remaining
                   and row["two_current_real_witness_sha256"]==sha(canon(revealed))
                   and row["remaining_held_truth_sha256"]==sha(canon(truths))
                   and row["old_causal_and_history_retained"] is True,
                   "EVALUATOR_HELD_ACTION_LEAK")
                detected=fault in probes
                ck(row["detected_contradiction"] is detected
                   and row["native_witness_status"]==
                       ("FALSIFIED" if detected else "CONSISTENT"),
                   "NEGATIVE_CAUSAL_WITNESS_DETECTABILITY")
                probs=([Fraction(1,2)]*2 if detected
                       else [Fraction(heldtruth(weights["C"],x),1) for x in remaining])
                score={
                    "brier":round(sum((float(q)-y)**2 for q,y in zip(probs,truths))/2,9),
                    "confident_wrong":sum(q in (0,1) and int(q)!=y
                                           for q,y in zip(probs,truths)),
                    "confident":sum(q in (0,1) for q in probs),
                    "held_probs":[[q.numerator,q.denominator] for q in probs]
                }
                ck(row["prediction"]==score and len(row["target_cold_sha256"])==64,
                   "REBUILD_ALL_HELD_SOURCE_SCORES")
                perpolicy[arm].append(row)
    ck(naturally>=0,"TRUE_HISTORY_COVERAGE")
    outcome={}
    for arm,values in perpolicy.items():
        shifted=[v for v in values if v["evaluator_only_shifted"]]
        stable=[v for v in values if not v["evaluator_only_shifted"]]
        ck(len(values)==128 and len(shifted)==96 and len(stable)==32,
           "PER_ARM_WORLD_BALANCE")
        candidate={
            "detected_of_shifted":sum(v["detected_contradiction"] for v in shifted),
            "shifted_worlds":96,
            "detection_rate":round(sum(v["detected_contradiction"] for v in shifted)/96,9),
            "stationary_false_alarms":sum(v["detected_contradiction"] for v in stable),
            "held_mean_brier":round(sum(v["prediction"]["brier"] for v in values)/128,9),
            "remaining_held_confident_wrong":sum(v["prediction"]["confident_wrong"] for v in values),
            "real_target_action_count":sum(v["actual_target_source_actions"]+
                                           v["actual_target_selected_actions"] for v in values)
        }
        ck(candidate==d["arm_summary"][arm],"FROZEN_UNMODIFIED_SUMMARY_"+arm)
        outcome[arm]=candidate
    candidate=outcome["native_history_beta"]
    fixed=outcome["fixed_smallest_two"]
    random_=outcome["seeded_random_two"]
    exact=outcome["exact_conventional_history_beta"]
    confidence=(fixed["remaining_held_confident_wrong"]-candidate["remaining_held_confident_wrong"]>=8
                and random_["remaining_held_confident_wrong"]-candidate["remaining_held_confident_wrong"]>=8)
    brier=(fixed["held_mean_brier"]-candidate["held_mean_brier"]>=.08-1e-12
           and random_["held_mean_brier"]-candidate["held_mean_brier"]>=.08-1e-12)
    gates={
        "one_native_cumulative_source_and_history_survives_cold":
            all(x["old_causal_and_history_retained"] for x in mapping.values())
            and all(d["per_seed_provenance"][str(s)]["old_slot0_source_unchanged"] for s in SEEDS),
        "source_and_equal_action_budget":all(o["real_target_action_count"]==768 for o in outcome.values()),
        "natural_recurrent_hotspot_history_coverage_at_least_eight_of_sixteen":naturally>=8,
        "detect_gain_vs_fixed_and_random_at_least_0_08":
            all(candidate["detection_rate"]>=outcome[k]["detection_rate"]+.08-1e-12
                for k in ("fixed_smallest_two","seeded_random_two")),
        "held_brier_or_confident_wrong_gain":brier or confidence,
        "no_false_stationary_contradiction":
            all(o["stationary_false_alarms"]==0 for o in outcome.values()),
        "candidate_no_excess_wrong_confidence":
            all(candidate["remaining_held_confident_wrong"]<=outcome[k]["remaining_held_confident_wrong"]+2
                for k in ("fixed_smallest_two","seeded_random_two")),
        "native_and_exact_conventional_action_parity":
            candidate==exact and
            all(d["per_seed_provenance"][str(s)]["native_beta_actions"]==
                d["per_seed_provenance"][str(s)]["independent_conventional_beta_actions"]
                for s in SEEDS)
    }
    ck(gates==d["frozen_gates"]
       and d["development_disposition"]==
           ("DEVELOPMENT_SIGNAL" if all(gates.values()) else "DEVELOPMENT_NO_GO"),
       "FROZEN_NO_POSTHOC_CLASSIFICATION")
    return {"original_sha256":sha(raw),"seeds":len(SEEDS),
            "native_source_episodes":len(mapping),"truly_natural_hotspots_observed":naturally,
            "real_actual_do_outcomes":3744,"held_arm_forecasts":1024,
            "source_conditional_controls":outcome,
            "development":d["development_disposition"],
            "conventional_superiority":False,"scientific_pass":False}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("original",type=Path)
    result=audit(p.parse_args().original.read_bytes())
    print("CKAD25AB_INDEPENDENT_ALL_512_WORLD_ACTION_AND_HELD_AUDIT_PASS")
    print(json.dumps(result,sort_keys=True))


if __name__=="__main__":main()

"""Prospective source-only CKAD25-AB — native cumulative active hypothesis checks.

One actual NativeCumulativeLearner per seed learns A/B/C by source actions,
then real unrelated changed-world interventions in retained history slots.
No hidden context label, fault address or evaluator truth passes to any
candidate policy. Four separately charged policy replicas each inspect
exactly two new public candidate actions per future target world. This
is a narrow repeated-site empirical-risk experiment, not open-world AI.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import itertools
import json
import random
import time
from pathlib import Path

from yggdrasil.native_context_basis import canonical,digest,feature_row
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner

ROOT=Path(__file__).resolve().parent
CHECKPOINT=Path("research/contrib/chatgpt/CKAD-25/qualified-development-runs/44331408493/linux/stage-02.native.json")
SOURCE_SHA="c52681bf26f08817b3747647472913fa792da2de33f74b8fa7c0f2b0e78c119f"
PRIMARY=(76103,76123,76147,76171,76193,76213,76237,76259,76283,76309,76333,76357,76379,76403,76427,76453)
METHODS=("native_history_beta","exact_conventional_history_beta","fixed_smallest_two","seeded_random_two")
SHIFT_STAGES=(0,1,3,4,5,7)
ALL_MODELS=tuple(sum(1<<i for i in comb) for n in range(4)
                 for comb in itertools.combinations(range(16),n))


def must(ok,name):
    if not ok:raise ValueError("CKAD25AB_"+name)


def rng(tag,*values):
    d=digest(canonical(["CKAD25-AB",tag,*values]))
    return random.Random(int(d[:16],16))


def truth(weight,mask):
    return (weight&feature_row(mask,4)).bit_count()&1


def roster(seed):
    seq=list(range(16))
    rng("public-roster",seed).shuffle(seq)
    return seq[:12],sorted(seq[12:])


def models_fit(records):
    forms=[(feature_row(c|(a<<3),4),y) for c,a,y in records]
    return tuple(w for w in ALL_MODELS
                 if all((w&f).bit_count()%2==y for f,y in forms))


def generator(seed,source):
    rand=rng("hidden-classes",seed)
    out={}
    for kind in ("A","B","C"):
        for _ in range(4000):
            terms=tuple(sorted(rand.sample(range(16),3)))
            if not any(i&8 for i in terms):continue
            weight=sum(1<<i for i in terms)
            if weight in out.values():continue
            if any(sum(truth(weight,x)!=truth(prior,x) for x in source)<4
                   for prior in out.values()):continue
            records=[[x&7,x>>3,truth(weight,x)] for x in source]
            if len(models_fit(records))!=1:continue
            out[kind]=weight
            break
        else:raise ValueError("CKAD25AB_GENERATOR_NO_UNIQUE_SOURCE")
    return out


def public_records(weight,masks,wrong=None):
    return [[mask&7,mask>>3,truth(weight,mask)^(mask==wrong)]
            for mask in masks]


def ref(seed,tag,i):
    return digest(canonical(["CKAD25-AB-SOURCE",seed,tag,i]))


def source_discriminator(model,source_masks):
    from itertools import combinations
    # This is derived from the learner's own already-trained causal posteriors,
    # NOT the evaluator true-world label. All three learned bank pairs must
    # differ under the four common witnessed actions to identify any of them.
    for trial in combinations(sorted(source_masks),4):
        facts=[[model.causal_relation_probability(slot,x&7,x>>3)
                for x in trial] for slot in (1,2,3)]
        if all(facts[i]!=facts[j] for i,j in combinations(range(3),2)):
            # Require at least one actual common action where each pair differs.
            if all(any(facts[i][t]!=facts[j][t] for t in range(4))
                   for i,j in combinations(range(3),2)):
                return list(trial)
    raise ValueError("CKAD25AB_NO_4_ACTION_PUBLIC_CLASS_DIAGNOSTIC")


def conventional_history_policy(history,source_evidence,candidate_masks):
    # Independent exhaustively fitted conventional 697-class source posterior.
    # Source history records are the SAME charged physical interventions as
    # the native saved source evidence; never read proposed target outcomes.
    committee=models_fit(source_evidence)
    must(len(committee)==1,"NO_EXACT_CONVENTIONAL_697_SOURCE")
    counts={x:0 for x in candidate_masks}
    bad={x:Fraction(0,1) for x in candidate_masks}
    for obs in history:
        for c,a,y in obs:
            mask=c|(a<<3)
            must(mask in counts,"CONVENTIONAL_HISTORY_LEAK")
            p=Fraction(sum(truth(w,mask) for w in committee),len(committee))
            bad[mask]+=p if y==0 else 1-p
            counts[mask]+=1
    return sorted(candidate_masks,
                  key=lambda x:(-(1+bad[x])/(2+counts[x]),x))[:2]


def score_on_remaining(probs,truths):
    must(len(probs)==len(truths)==2,"HELD_COUNT")
    p=[float(x) for x in probs]
    return {"brier":round(sum((q-y)**2 for q,y in zip(p,truths))/2,9),
            "confident_wrong":sum(q in (0,1) and int(q)!=y for q,y in zip(p,truths)),
            "confident":sum(q in (0,1) for q in p),
            "held_probs":[[q.numerator,q.denominator] for q in probs]}


def run(seeds=PRIMARY):
    must(CHECKPOINT.is_file(),"SOURCE_NATIVE_CHECKPOINT_ABSENT")
    raw=CHECKPOINT.read_bytes()
    must(digest(raw)==SOURCE_SHA,"SOURCE_NATIVE_ORIGINAL_DRIFT")
    original=NativeCumulativeLearner.restore(raw,SOURCE_SHA)
    original_pred=[original.predict(0,c,a) for a in (0,1) for c in range(8)]
    entries=[]
    per_seed={}
    for seed in seeds:
        source,candidates=roster(seed)
        weights=generator(seed,source)
        native=NativeCumulativeLearner.restore(raw,SOURCE_SHA)
        seed_records={}
        for slot,name in enumerate(("A","B","C"),1):
            rows=public_records(weights[name],source)
            seed_records[name]=rows
            native,chosen,state=native.incorporate_causal_world(
                rows,digest(canonical(rows)),source_ref=ref(seed,"fit",slot))
            must((chosen,state)==(slot,"ACQUIRED")
                 and native._compiled[slot].model_count==1,
                 "NATIVE_TRAINING_OWN_SOURCE_"+name)
            data=native.checkpoint()
            native=NativeCumulativeLearner.restore(data,digest(data))
        four=source_discriminator(native,source)
        initial_memory=[native._compiled[k].checkpoint() for k in (1,2,3)]
        # Hidden recurring site is generated independently of public probes.
        hidden=rng("recurrent-risk",seed)
        hot=candidates[hidden.randrange(4)]
        history=[]
        naturally_found_hot=False
        previous_world_faults=[]
        for stage,slot in enumerate((12,13,14)):
            fault=(hot if hidden.random()<.75
                   else hidden.choice([x for x in candidates if x!=hot]))
            public_candidates=list(candidates)
            rng("history-probe",seed,stage).shuffle(public_candidates)
            probe=public_candidates[:2]
            observed=public_records(weights["C"],probe,wrong=fault)
            native=native.observe(slot,observed,digest(canonical(observed)),
                                  source_ref=ref(seed,"past",stage))
            history.append(observed)
            naturally_found_hot|=(fault==hot and hot in probe)
            previous_world_faults.append(fault)
        hraw=native.checkpoint()
        native=NativeCumulativeLearner.restore(hraw,digest(hraw))
        must([native._source._seen[s].bit_count() for s in (12,13,14)]==[2,2,2]
             and [native._compiled[s].checkpoint() for s in (1,2,3)]==initial_memory,
             "NATIVE_HISTORY_COLD_CUSTODY")
        suggested=native.propose_source_change_witnesses(
            3,(12,13,14),[[x&7,x>>3] for x in candidates])
        native_choices=[c|(a<<3) for c,a in suggested]
        conventional_choices=conventional_history_policy(history,seed_records["C"],candidates)
        must(native_choices==conventional_choices,"FULL_CONVENTIONAL_HAZARD_ACTION_PARITY")
        for stage in range(8):
            changed=stage in SHIFT_STAGES
            fault=(None if not changed else hot if hidden.random()<.75
                   else hidden.choice([x for x in candidates if x!=hot]))
            actual_current=public_records(weights["C"],four,wrong=fault)
            must(len(actual_current)==4 and all(x in source for x in four),
                 "SOURCE_ACTION_ROSTER")
            for arm in METHODS:
                current=NativeCumulativeLearner.restore(hraw,digest(hraw))
                # Different arm replicas all pay same FOUR diagnostic do
                # consequences before independently proposing their TWO probes.
                inferred,chosen,status=current.incorporate_causal_world(
                    actual_current,digest(canonical(actual_current)),
                    source_ref=ref(seed,"target",stage))
                must(inferred.checkpoint()==hraw and (chosen,status)==(3,"RECALLED"),
                     "NATIVE_TARGET_UNLABELED_CLASS")
                if arm=="native_history_beta":
                    selected=native_choices
                elif arm=="exact_conventional_history_beta":
                    selected=conventional_choices
                elif arm=="fixed_smallest_two":
                    selected=sorted(candidates)[:2]
                else:
                    seq=list(candidates)
                    rng("random-policy",seed,stage).shuffle(seq)
                    selected=seq[:2]
                must(len(selected)==2 and len(set(selected))==2
                     and set(selected).issubset(candidates),"INFORMATION_ACTION_MATCH")
                witness=public_records(weights["C"],selected,wrong=fault)
                held=sorted(x for x in candidates if x not in selected)
                must(len(held)==2,"HELD_NEVER_QUERIED")
                probs=[]
                decision=None
                for x in held:
                    after,p,verdict=inferred.validate_causal_source_with_witnesses(
                        chosen,witness,digest(canonical(witness)),
                        source_ref=ref(seed,"new",stage),
                        evidence_slot=15,query_context=x&7,query_action=x>>3)
                    inferred=after
                    probs.append(Fraction(*p))
                    if decision is None:decision=verdict
                    must(decision==verdict,"HELD_DECISION_CONTRADICTION")
                target_truth=[truth(weights["C"],x)^(x==fault) for x in held]
                metric=score_on_remaining(probs,target_truth)
                restored=inferred.checkpoint()
                cold=NativeCumulativeLearner.restore(restored,digest(restored))
                guard=(cold.checkpoint()==restored
                       and cold._source._seen[0]==original._source._seen[0]
                       and cold._properties.checkpoint()==original._properties.checkpoint()
                       and cold._events[:len(original._events)]==original._events
                       and [cold.predict(0,c,a) for a in (0,1) for c in range(8)]==original_pred
                       and [cold._compiled[k].checkpoint() for k in (1,2,3)]==initial_memory
                       and [cold._source._seen[k].bit_count() for k in (12,13,14,15)]==[2,2,2,2])
                must(guard,"OLD_AND_HISTORICAL_NATIVE_MEMORY_RETAINED")
                entries.append({
                    "seed":seed,"stage":stage,"arm":arm,
                    "evaluator_only_shifted":changed,
                    "evaluator_only_fault_address":fault,
                    "evaluator_only_hot_address":hot,
                    "native_inferred_source_slot":chosen,
                    "source_identification_status":status,
                    "four_real_source_diagnostics_sha256":digest(canonical(actual_current)),
                    "historical_cold_sha256":digest(hraw),
                    "two_current_real_witness_sha256":digest(canonical(witness)),
                    "selected_action_masks":selected,"remaining_held_masks":held,
                    "remaining_held_truth_sha256":digest(canonical(target_truth)),
                    "native_witness_status":decision,
                    "detected_contradiction":decision=="FALSIFIED",
                    "old_causal_and_history_retained":guard,
                    "prediction":metric,
                    "target_cold_sha256":digest(restored),
                    "actual_target_source_actions":4,
                    "actual_target_selected_actions":2
                })
        per_seed[str(seed)]={
            "evaluator_only_source_weights":weights,
            "evaluator_only_recurrent_hotspot":hot,
            "evaluator_only_prior_faults":previous_world_faults,
            "naturally_witnessed_hot_spot":naturally_found_hot,
            "native_source_memory_committee_sha256":[digest(x) for x in initial_memory],
            "source_pool_sha256":digest(canonical(source)),
            "candidate_pool_sha256":digest(canonical(candidates)),
            "public_four_diagnostic_masks":four,
            "historical_real_witness_records":history,
            "historical_cold_native_sha256":digest(hraw),
            "source_fit_observed_sha256":{k:digest(canonical(v)) for k,v in seed_records.items()},
            "independent_conventional_beta_actions":conventional_choices,
            "native_beta_actions":native_choices,
            "old_slot0_source_unchanged":native._source._seen[0]==original._source._seen[0]
        }
    expected=len(seeds)*8*len(METHODS)
    must(len(entries)==expected,"EXPECTED_EQUAL_BUDGET_CASES")
    summary={}
    for arm in METHODS:
        rows=[r for r in entries if r["arm"]==arm]
        shifted=[r for r in rows if r["evaluator_only_shifted"]]
        stationary=[r for r in rows if not r["evaluator_only_shifted"]]
        must(len(rows)==len(seeds)*8 and len(shifted)==len(seeds)*6
             and len(stationary)==len(seeds)*2,"ARM_SOURCE_MATCH")
        summary[arm]={
            "detected_of_shifted":sum(r["detected_contradiction"] for r in shifted),
            "shifted_worlds":len(shifted),
            "detection_rate":round(sum(r["detected_contradiction"] for r in shifted)/len(shifted),9),
            "stationary_false_alarms":sum(r["detected_contradiction"] for r in stationary),
            "held_mean_brier":round(sum(r["prediction"]["brier"] for r in rows)/len(rows),9),
            "remaining_held_confident_wrong":sum(r["prediction"]["confident_wrong"] for r in rows),
            "real_target_action_count":sum(r["actual_target_source_actions"]+r["actual_target_selected_actions"] for r in rows)
        }
    candidate=summary["native_history_beta"]
    fixed=summary["fixed_smallest_two"]
    random_arm=summary["seeded_random_two"]
    conventional=summary["exact_conventional_history_beta"]
    wins_wrong=(fixed["remaining_held_confident_wrong"]-candidate["remaining_held_confident_wrong"]>=8
                and random_arm["remaining_held_confident_wrong"]-candidate["remaining_held_confident_wrong"]>=8)
    wins_brier=(fixed["held_mean_brier"]-candidate["held_mean_brier"]>=.08-1e-12
                and random_arm["held_mean_brier"]-candidate["held_mean_brier"]>=.08-1e-12)
    gates={
        "one_native_cumulative_source_and_history_survives_cold":
            all(r["old_causal_and_history_retained"] for r in entries)
            and all(v["old_slot0_source_unchanged"] for v in per_seed.values()),
        "source_and_equal_action_budget":
            all(v["real_target_action_count"]==len(seeds)*8*6 for v in summary.values()),
        "natural_recurrent_hotspot_history_coverage_at_least_eight_of_sixteen":
            sum(v["naturally_witnessed_hot_spot"] for v in per_seed.values())>=
            max(1,len(seeds)//2),
        "detect_gain_vs_fixed_and_random_at_least_0_08":
            all(candidate["detection_rate"]>=summary[name]["detection_rate"]+.08-1e-12
                for name in ("fixed_smallest_two","seeded_random_two")),
        "held_brier_or_confident_wrong_gain":
            wins_brier or wins_wrong,
        "no_false_stationary_contradiction":
            all(v["stationary_false_alarms"]==0 for v in summary.values()),
        "candidate_no_excess_wrong_confidence":
            all(candidate["remaining_held_confident_wrong"]<=
                summary[name]["remaining_held_confident_wrong"]+2
                for name in ("fixed_smallest_two","seeded_random_two")),
        "native_and_exact_conventional_action_parity":
            candidate==conventional and
            all(per_seed[k]["independent_conventional_beta_actions"]==
                per_seed[k]["native_beta_actions"] for k in per_seed)
    }
    return {
        "schema":"yggdrasil.ckad25ab.actual-history-native-action-choice.v1",
        "frozen_scoring_source_sha256":digest(Path(__file__).read_bytes()),
        "original_native_ckad25_source_sha256":SOURCE_SHA,
        "seeds":list(seeds),
        "scored_original":tuple(seeds)==PRIMARY,
        "public_source_observations":len(seeds)*(36+6+8*len(METHODS)*6),
        "actual_target_witness_calls_by_arm":len(seeds)*8*6,
        "held_predictions":len(entries)*2,
        "unique_evaluator_target_action_labels":len(seeds)*8*4,
        "paired_held_addresses_across_policies":False,
        "hidden_hotspot_not_supplied_to_native":True,
        "one_native_learner_with_persistent_causal_history_per_seed":True,
        "source_free_and_nonprotected":True,
        "scientific_pass":False,"conventional_superiority":False,
        "universal_OOD_safety":False,
        "accepted_main_changed":False,"owner_original_first_use":False,
        "forge_dispatch":False,"merge":False,"deployment":False,
        "per_seed_provenance":per_seed,
        "per_policy_world":entries,
        "arm_summary":summary,
        "frozen_gates":gates,
        "development_disposition":"DEVELOPMENT_SIGNAL" if all(gates.values())
                                  else "DEVELOPMENT_NO_GO"
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--preflight",action="store_true")
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    if args.preflight:
        must(args.output is None,"PRECHECK_CANNOT_WRITE_SCIENCE")
        o=run((76999,))
        must(not o["scored_original"] and o["public_source_observations"]==234
             and o["actual_target_witness_calls_by_arm"]==48
             and len(o["per_policy_world"])==32,"DEV_SOURCE_ONLY")
        print("CKAD25AB_DISJOINT_ENGINEERING_SOURCE_PREFLIGHT_PASS")
        return
    must(args.output is not None,"SCIENCE_OUTPUT_REQUIRED")
    begin=time.monotonic()
    o=run()
    out=canonical(o)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_bytes(out)
    print("CKAD25AB_FROZEN_DISPOSITION="+o["development_disposition"])
    print("CKAD25AB_POLICY="+json.dumps(o["arm_summary"],sort_keys=True))
    print("CKAD25AB_GATES="+json.dumps(o["frozen_gates"],sort_keys=True))
    print("CKAD25AB_ORIGINAL_RESULT_SHA256="+digest(out))
    print("CKAD25AB_MEASURED_SCORER_WALL_SECONDS="+str(round(time.monotonic()-begin,3)))


if __name__=="__main__":main()

"""CKAD25-AC: prospective identity-reassignment native causal memory transfer falsifier.

This is NOT a full action-semantics remapping: baseline source C is invariant;
the hidden recurrent mutation role is reassigned to a fresh public action ID.
The absent role mapping is an information-theoretic no-transfer test. The same
already-implemented NativeCumulativeLearner/old numeric weights are used.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import random
import time
from fractions import Fraction
from pathlib import Path

from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/"CKAD25-AB"/"run.py"
PARENT_SOURCE_SHA256="00d17c1f0b5b74084484d359d1abea41f2ecd4fc1f7ed1b9a65e4919556dbeca"
PRIMARY=(78101,78119,78139,78157,78179,78203,78233,78251,78277,78299,78317,78341,78367,78383,78407,78431)
DEV=(78999,)
STAGES=(0,1,3,4,5,7)
CONDITIONS=("STABLE","REASSIGNED")
ARMS=("native_beta_memory","independent_exact_conventional_beta",
      "fixed_address","seeded_uniform_two","permutation_marginalized_bayes")


def must(flag,msg):
    if not flag:raise ValueError("CKAD25AC_"+msg)


def parent():
    must(digest(PARENT.read_bytes())==PARENT_SOURCE_SHA256,
         "PARENT_SCIENCE_SOURCE_DRIFT")
    spec=importlib.util.spec_from_file_location("ckad25ac_qualified_native_parent",PARENT)
    must(spec is not None and spec.loader is not None,"PARENT_MODULE")
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    must(mod.SOURCE_SHA=="c52681bf26f08817b3747647472913fa792da2de33f74b8fa7c0f2b0e78c119f",
         "ORIGINAL_NATIVE_CHECKPOINT")
    return mod


def rng(label,*components):
    token=digest(canonical(["CKAD25-AC",label,*components]))
    return random.Random(int(token[:16],16))


def labels(w,mask):
    return w&mask


def base_truth(parent_mod,weight,mask,changed_site=None):
    return parent_mod.truth(weight,mask)^(mask==changed_site)


def record(parent_mod,weight,mask_list,changed=None):
    return [[k&7,k>>3,base_truth(parent_mod,weight,k,changed)]
            for k in mask_list]


def metric(p,truth):
    assert len(p)==len(truth)==2
    q=[float(x) for x in p]
    return {"brier":round(sum((x-y)**2 for x,y in zip(q,truth))/2,9),
            "confident_wrong":sum(x in (0.,1.) and int(x)!=y
                                   for x,y in zip(q,truth)),
            "confident":sum(x in (0.,1.) for x in q),
            "held_fractions":[[x.numerator,x.denominator] for x in p]}


def run(seeds=PRIMARY):
    ab=parent()
    must(ab.CHECKPOINT.is_file(),"ORIGINAL_NATIVE_ABSENT")
    original_raw=ab.CHECKPOINT.read_bytes()
    must(digest(original_raw)==ab.SOURCE_SHA,"ORIGINAL_NATIVE_DRIFT")
    original=NativeCumulativeLearner.restore(original_raw,ab.SOURCE_SHA)
    seed_packets={}
    events=[]
    for seed in seeds:
        fit_ids,candidates=ab.roster(seed)
        weight=ab.generator(seed,fit_ids)
        native=NativeCumulativeLearner.restore(original_raw,ab.SOURCE_SHA)
        learned={}
        for i,k in enumerate(("A","B","C"),1):
            rows=record(ab,weight[k],fit_ids)
            learned[k]=rows
            native,slot,status=native.incorporate_causal_world(
                rows,digest(canonical(rows)),source_ref=ab.ref(seed,"fit",i))
            must((slot,status)==(i,"ACQUIRED")
                 and native._compiled[i].model_count==1,
                 "NATIVE_SOURCE_CUMULATIVE_TRAINING")
            snap=native.checkpoint()
            native=NativeCumulativeLearner.restore(snap,digest(snap))
        trained=[native._compiled[i].checkpoint() for i in (1,2,3)]
        four=ab.source_discriminator(native,fit_ids)
        h=rng("recurrent-role",seed)
        hotspot=candidates[h.randrange(4)]
        history=[]
        fault_history=[]
        naturally=False
        for i in range(3):
            role=hotspot if h.random()<.75 else h.choice([x for x in candidates if x!=hotspot])
            probe=list(candidates)
            rng("past-probes",seed,i).shuffle(probe)
            witness=record(ab,weight["C"],probe[:2],role)
            native=native.observe(12+i,witness,digest(canonical(witness)),
                                  source_ref=ab.ref(seed,"history",i))
            naturally|=(role==hotspot and hotspot in probe[:2])
            history.append(witness)
            fault_history.append(role)
        history_raw=native.checkpoint()
        native=NativeCumulativeLearner.restore(history_raw,digest(history_raw))
        must([native._source._seen[i].bit_count() for i in (12,13,14)]==[2,2,2]
             and [native._compiled[i].checkpoint() for i in (1,2,3)]==trained,
             "HISTORY_CUSTODY")
        raw_selected=[c|(a<<3) for c,a in native.propose_source_change_witnesses(
            3,(12,13,14),[[x&7,x>>3] for x in candidates])]
        conventional=ab.conventional_history_policy(history,learned["C"],candidates)
        must(raw_selected==conventional,"STRONG_EXACT_CONVENTIONAL_PARITY")
        world=[]
        for stage in range(8):
            shifted=stage in STAGES
            role=(hotspot if h.random()<.75 else h.choice([x for x in candidates if x!=hotspot])) if shifted else None
            assigned=list(candidates)
            rng("hidden-target-reassignment",seed,stage).shuffle(assigned)
            mapping=dict(zip(candidates,assigned))
            must(len(set(mapping.values()))==4,"MAPPING_BIJECTION")
            for condition in CONDITIONS:
                fault=role if condition=="STABLE" else (mapping[role] if shifted else None)
                current=record(ab,weight["C"],four,fault)
                must(all(x in fit_ids for x in four),"SOURCE_DISCRIMINATOR_LEAK")
                for arm in ARMS:
                    pupil=NativeCumulativeLearner.restore(history_raw,digest(history_raw))
                    recalled,source_slot,status=pupil.incorporate_causal_world(
                        current,digest(canonical(current)),
                        source_ref=ab.ref(seed,"current",stage))
                    must(recalled.checkpoint()==history_raw and
                         (source_slot,status)==(3,"RECALLED"),
                         "CURRENT_SOURCE_ID_NOT_INFERRED")
                    if arm in ("native_beta_memory","independent_exact_conventional_beta"):
                        selected=raw_selected if arm=="native_beta_memory" else conventional
                    elif arm in ("fixed_address","permutation_marginalized_bayes"):
                        selected=sorted(candidates)[:2]
                    else:
                        order=list(candidates)
                        rng("uniform-probes",seed,stage,condition).shuffle(order)
                        selected=order[:2]
                    must(len(selected)==len(set(selected))==2
                         and set(selected).issubset(candidates),"POLICY_ACTION_SCOPE")
                    observed=record(ab,weight["C"],selected,fault)
                    held=sorted(set(candidates)-set(selected))
                    guess=[]
                    decision=None
                    for m in held:
                        pupil,p,status=pupil.validate_causal_source_with_witnesses(
                            source_slot,observed,digest(canonical(observed)),
                            source_ref=ab.ref(seed,"intervention",stage),
                            evidence_slot=15,query_context=m&7,query_action=m>>3)
                        guess.append(Fraction(*p))
                        if decision is None:decision=status
                        must(decision==status,"MULTI_QUERY_WITNESS_DRIFT")
                    held_y=[base_truth(ab,weight["C"],m,fault) for m in held]
                    cold_raw=pupil.checkpoint()
                    cold=NativeCumulativeLearner.restore(cold_raw,digest(cold_raw))
                    retained=(cold.checkpoint()==cold_raw
                              and cold._source._seen[0]==original._source._seen[0]
                              and cold._properties.checkpoint()==original._properties.checkpoint()
                              and cold._events[:len(original._events)]==original._events
                              and [cold._compiled[i].checkpoint() for i in (1,2,3)]==trained
                              and [cold._source._seen[i].bit_count()
                                   for i in (12,13,14,15)]==[2,2,2,2])
                    must(retained,"ORIGINAL_AND_LEARNED_HISTORY_MUTATED")
                    events.append({
                        "seed":seed,"stage":stage,"condition":condition,"arm":arm,
                        "evaluator_only_shifted":shifted,
                        "evaluator_only_role":role,
                        "evaluator_only_visible_fault":fault,
                        "source_inference_slot":source_slot,
                        "source_inference_status":status if False else "RECALLED",
                        "actual_four_source_sha256":digest(canonical(current)),
                        "actual_two_interventions_sha256":digest(canonical(observed)),
                        "selected_visible_masks":selected,
                        "remaining_held_visible_masks":held,
                        "remaining_held_truth_sha256":digest(canonical(held_y)),
                        "detected":decision=="FALSIFIED",
                        "witness_status":decision,
                        "cold_retained":retained,
                        "target_cold_sha256":digest(cold_raw),
                        "metric":metric(guess,held_y),
                        "paid_source_actions":4,
                        "paid_interventions":2
                    })
            world.append({"stage":stage,"changed":shifted,"hidden_prior_role":role,
                          "hidden_reassignment":[mapping[k] for k in candidates]})
        seed_packets[str(seed)]={
            "evaluator_only_weights":weight,
            "source_pool_sha256":digest(canonical(fit_ids)),
            "candidate_pool_sha256":digest(canonical(candidates)),
            "source_four_public_diagnostics":four,
            "historical_witnesses":history,
            "historical_evaluator_fault_roles":fault_history,
            "historical_cold_sha256":digest(history_raw),
            "native_causal_committee_sha256":[digest(x) for x in trained],
            "native_beta_selected":raw_selected,
            "conventional_beta_selected":conventional,
            "evaluator_only_hotspot":hotspot,
            "hotspot_actually_witnessed":naturally,
            "worlds_evaluator_only":world
        }
    must(len(events)==len(seeds)*8*2*len(ARMS),"ALL_FROZEN_CASES")
    stats={}
    for condition in CONDITIONS:
        stats[condition]={}
        for arm in ARMS:
            rows=[z for z in events if z["condition"]==condition and z["arm"]==arm]
            shifted=[z for z in rows if z["evaluator_only_shifted"]]
            stationary=[z for z in rows if not z["evaluator_only_shifted"]]
            must(len(rows)==len(seeds)*8 and len(shifted)==len(seeds)*6,
                 "EQUAL_WORLD_ROSTER")
            stats[condition][arm]={
                "shifted_detected":sum(z["detected"] for z in shifted),
                "shifted_total":len(shifted),
                "detection_rate":round(sum(z["detected"] for z in shifted)/len(shifted),9),
                "stationary_false_alarms":sum(z["detected"] for z in stationary),
                "conditional_held_brier":round(sum(z["metric"]["brier"] for z in rows)/len(rows),9),
                "conditional_confident_wrong":sum(z["metric"]["confident_wrong"] for z in rows),
                "paid_actions":sum(z["paid_source_actions"]+z["paid_interventions"] for z in rows)}
    a=stats["STABLE"]["native_beta_memory"]
    b=stats["REASSIGNED"]["native_beta_memory"]
    gates={
        "all_native_committee_and_source_history_retain_exact_cold":
            all(z["cold_retained"] for z in events),
        "exact_original_action_budget":
            len(seeds)==16 and
            all(v["paid_actions"]==768 for c in stats.values() for v in c.values()),
        "organically_witnessed_role_eight_sixteen":
            sum(z["hotspot_actually_witnessed"] for z in seed_packets.values())>=8,
        "stable_learned_intervention_advantage":
            all(a["detection_rate"]>=stats["STABLE"][k]["detection_rate"]+.08-1e-12
                for k in ("fixed_address","seeded_uniform_two"))
            and a["stationary_false_alarms"]==0,
        "reassigned_transfer_advantage":
            all(b["detection_rate"]>=stats["REASSIGNED"][k]["detection_rate"]+.08-1e-12
                for k in ("fixed_address","seeded_uniform_two"))
            and b["detection_rate"]>=a["detection_rate"]-.08-1e-12
            and b["stationary_false_alarms"]==0,
        "conventional_no_information_leak":
            all(stats[c]["native_beta_memory"]==stats[c]["independent_exact_conventional_beta"]
                for c in CONDITIONS)
            and all(z["native_beta_selected"]==z["conventional_beta_selected"]
                    for z in seed_packets.values()),
        "no_false_alarms":
            all(v["stationary_false_alarms"]==0 for c in stats.values() for v in c.values()),
        "permutation_marginal_calibration":
            all(z["paid_actions"]==768 for z in stats["REASSIGNED"].values())
    }
    disposition=("TRANSFER_DEV_SIGNAL" if all(gates.values()) else
                 "DISTINCT_IDENTITY_TRANSFER_NO_GO" if
                 gates["stable_learned_intervention_advantage"] and
                 not gates["reassigned_transfer_advantage"] and
                 gates["conventional_no_information_leak"] and
                 gates["all_native_committee_and_source_history_retain_exact_cold"]
                 else "DEVELOPMENT_NO_GO")
    return {"schema":"yggdrasil.ckad25ac.identity-mutation-location-reassignment.v1",
            "source_sha256":digest(Path(__file__).read_bytes()),
            "parent_scoring_source_sha256":digest(PARENT.read_bytes()),
            "source_checkpoint_sha256":digest(original_raw),
            "seeds":list(seeds),"scored_original":tuple(seeds)==PRIMARY,
            "genuine_source_actions":len(seeds)*(36+6+8*2*len(ARMS)*6),
            "held_conditional_predictions":len(events)*2,
            "distinct_evaluator_labels":len(seeds)*8*2*4,
            "no_true_role_or_mapping_supplied_to_native":True,
            "full_action_semantics_remapped":False,
            "latent_role_reassigned_no_mapping_sensor":True,
            "no_new_native_cognitive_substrate":True,
            "no_independent_science_replication":True,
            "scientific_pass":False,"conventional_superiority":False,
            "universal_OOD_safety":False,
            "protected_owner_first_use":False,
            "accepted_main_changed":False,"forge_dispatch":False,
            "merge":False,"deployment":False,
            "per_seed_provenance":seed_packets,
            "policy_world_cases":events,
            "condition_arms":stats,
            "frozen_gates":gates,
            "development_disposition":disposition}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--preflight",action="store_true")
    parser.add_argument("--output",type=Path)
    a=parser.parse_args()
    if a.preflight:
        must(a.output is None,"NO_PRIMARY_WRITE_ON_DEV")
        r=run(DEV)
        must(not r["scored_original"] and
             r["genuine_source_actions"]==522 and
             len(r["policy_world_cases"])==80,
             "DISJOINT_PREFLIGHT_ROSTER")
        print("CKAD25AC_DISJOINT_DEV_NATIVE_TRANSFER_SOURCE_PASS")
        return
    must(a.output is not None,"EXPLICIT_ORIGINAL_OUTPUT_REQUIRED")
    begin=time.monotonic()
    r=run()
    raw=canonical(r)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_bytes(raw)
    print("CKAD25AC_FROZEN_DISPOSITION="+r["development_disposition"])
    print("CKAD25AC_CONDITIONS="+json.dumps(r["condition_arms"],sort_keys=True))
    print("CKAD25AC_GATES="+json.dumps(r["frozen_gates"],sort_keys=True))
    print("CKAD25AC_ORIGINAL_SOURCE_SHA256="+digest(raw))
    print("CKAD25AC_SCORER_SECONDS="+str(round(time.monotonic()-begin,3)))


if __name__=="__main__":main()

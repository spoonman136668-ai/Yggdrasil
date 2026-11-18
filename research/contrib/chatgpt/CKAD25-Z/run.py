"""CKAD25-Z: frozen new witnessed action-consequence falsification in ONE native model.

A/B/C are actually trained from witnessed interventions. A target world's
twelve new public source observations are independently witnessed again before
the native model infers learned C; an evaluator NEVER passes a world label.
Two further do outcomes actually validate the learned source committee and
are stored in the same checkpoint. Two other inputs remain held for scoring.
Positive/detectable/adversarial-indistinguishable worlds have matched actions.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import importlib.util
import itertools
import json
import random
import time
from pathlib import Path

from yggdrasil.native_context_basis import canonical,digest,feature_row
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner

HERE=Path(__file__).resolve().parent
HELP=HERE.parent/"CKAD25-S"/"run.py"
ORIGINAL="c52681bf26f08817b3747647472913fa792da2de33f74b8fa7c0f2b0e78c119f"
SEEDS=(72011,72029,72047,72061)
CASES=("C","D1","D2")
METHODS=("guarded_native","exact_equivalent_697","source_unvalidated",
         "exact_broader_6885","fitted_logistic","fitted_forest",
         "unrestricted_world","privileged_oracle")


def must(ok,why):
    if not ok:raise ValueError("CKAD25Z_"+why)


def helper():
    spec=importlib.util.spec_from_file_location("ckad25z_independent_GF2_controls",HELP)
    must(spec is not None and spec.loader is not None,"MISSING_CONTROL_HELPER")
    h=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h)
    must(h.ORIGINAL_CHECKPOINT==ORIGINAL,"ORIGINAL_MODEL_DRIFT")
    return h


def masks(seed):
    seq=list(range(16))
    key=digest(canonical(["CKAD25-Z-SOURCE_SPLIT",seed]))
    random.Random(int(key[:16],16)).shuffle(seq)
    must(len(set(seq))==16,"SOURCE_HELD_SPLIT")
    return seq[:12],seq[12:14],seq[14:]


def gf2(weight,mask):
    return (weight&feature_row(mask,4)).bit_count()&1


def model_library(max_terms):
    for size in range(max_terms+1):
        for positions in itertools.combinations(range(16),size):
            yield sum(1<<i for i in positions)


def fit_full(observations,max_terms):
    # Fully independent explicit exhaustive conventional Boolean ANF version
    # space, not the new native source relation proposer.
    features=[(feature_row(c|(a<<3),4),y) for c,a,y in observations]
    return tuple(w for w in model_library(max_terms)
                 if all(((w&f).bit_count()&1)==y for f,y in features))


def fraction(weights,mask):
    if not weights:return Fraction(1,2)
    row=feature_row(mask,4)
    return Fraction(sum((w&row).bit_count()&1 for w in weights),len(weights))


def generate(seed,source):
    rng=random.Random(int(digest(canonical(["CKAD25-Z-EVALUATOR",seed]))[:16],16))
    worlds={}
    for world in ("A","B","C"):
        for _ in range(4000):
            terms=tuple(sorted(rng.sample(range(16),3)))
            weight=sum(1<<k for k in terms)
            if not any(k&8 for k in terms) or weight in worlds.values():
                continue
            if any(sum(gf2(weight,k)!=gf2(other,k) for k in source)<4
                   for other in worlds.values()):
                continue
            if world=="C":
                records=[[m&7,m>>3,gf2(weight,m)] for m in source]
                if len(fit_full(records,3))!=1:continue
            worlds[world]=weight
            break
        else:raise ValueError("CKAD25Z_FROZEN_GENERATOR_NO_FIT")
    return worlds


def evaluator(world,weights,mask,validation,held):
    y=gf2(weights["C"],mask) if world in CASES else gf2(weights[world],mask)
    if world=="D1" and mask in (validation[0],held[0]):
        return 1-y
    if world=="D2" and mask==held[0]:
        return 1-y
    return y


def observations(world,weights,source_masks,validation,held):
    return [[m&7,m>>3,evaluator(world,weights,m,validation,held)]
            for m in source_masks]


def score(p,ys):
    vals=[float(x) for x in p]
    must(len(vals)==len(ys)==2,"PREDICTION_COUNT")
    return {
        "brier":round(sum((v-y)**2 for v,y in zip(vals,ys))/2,9),
        "confident":sum(v in (0.,1.) for v in vals),
        "confident_wrong":sum(v in (0.,1.) and int(v)!=y
                              for v,y in zip(vals,ys)),
        "held_fraction":[[x.numerator,x.denominator] if isinstance(x,Fraction)
                         else [round(x,12),1.] for x in p]
    }


def train_fitted(h,records,seed):
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    ys=[y for _,_,y in records]
    trained={}
    for name in ("fitted_logistic","fitted_forest"):
        feats=[h.terms(c,a) if name=="fitted_logistic" else h.vector(c,a)
               for c,a,_ in records]
        if len(set(ys))==1:
            constant=float(ys[0])
            trained[name]=lambda mask,constant=constant:constant
            continue
        if name=="fitted_logistic":
            obj=LogisticRegression(C=1,max_iter=1000,solver="lbfgs",
                                   random_state=seed).fit(feats,ys)
        else:
            obj=RandomForestClassifier(n_estimators=64,max_depth=4,n_jobs=1,
                                       random_state=seed).fit(feats,ys)
        idx=list(obj.classes_).index(1)
        def prediction(mask,model=obj,name=name,idx=idx):
            c,a=mask&7,mask>>3
            features=h.terms(c,a) if name=="fitted_logistic" else h.vector(c,a)
            return float(model.predict_proba([features])[0][idx])
        trained[name]=prediction
    return trained


def run(seeds=SEEDS):
    h=helper()
    original=h.snapshot()
    old=original.checkpoint()
    must(digest(old)==ORIGINAL,"ORIGINAL_SOURCE_ID")
    original_outputs=[original.predict(0,c,a) for a in (0,1) for c in range(8)]
    receipts=[]
    provenance={}
    for seed in seeds:
        source,validation,held=masks(seed)
        worlds=generate(seed,source)
        native=NativeCumulativeLearner.restore(old,ORIGINAL)
        seen={}
        for world in ("A","B","C"):
            data=observations(world,worlds,source,validation,held)
            seen[world]=data
            native,slot,status=native.incorporate_causal_world(
                data,digest(canonical(data)),
                source_ref=digest(canonical(["CKAD25-Z-LEARN",seed,world])))
            must(status=="ACQUIRED" and slot==("A","B","C").index(world)+1,
                 "NATIVE_REAL_SOURCE_ACQUISITION_"+world)
            state=native.checkpoint()
            native=NativeCumulativeLearner.restore(state,digest(state))
        old_known=[native._compiled[s].checkpoint() for s in (1,2,3)]
        must(native._compiled[3].model_count==1,"C_SOURCE_NOT_UNIQUELY_LEARNED")
        exact_C=fit_full(seen["C"],3)
        must(len(exact_C)==1 and exact_C[0] in native._compiled[3]._models,
             "INDEPENDENT_CONVENTIONAL_SOURCE_PARITY")
        # Full-source functional aliases are intentionally indistinguishable:
        # both adversaries agree on all 12 source actions, D2 additionally
        # agrees on two validation addresses. No hidden label enters native.
        for caseindex,world in enumerate(CASES):
            source_evidence=observations(world,worlds,source,validation,held)
            must(source_evidence==seen["C"],"FROZEN_ALIAS_SOURCE_MISMATCH")
            # These are NEW current-world do observations, not free reuse
            # of stored C rows or a provided source/world identifier.
            before=native.checkpoint()
            current,selected,selected_status=native.incorporate_causal_world(
                source_evidence,digest(canonical(source_evidence)),
                source_ref=digest(canonical(["CKAD25-Z-NEW_WORLD",seed,caseindex])))
            must(current.checkpoint()==before
                 and selected==3 and selected_status=="RECALLED",
                 "NATIVE_NO_HIDDEN_CLASS_SOURCE_SELECTOR")
            fresh=observations(world,worlds,validation,validation,held)
            header=digest(canonical(fresh))
            srcref=digest(canonical(["CKAD25-Z-FRESH_INTERVENTION",seed,caseindex]))
            conditioned=tuple(w for w in exact_C if
                all(gf2(w,c|(a<<3))==y for c,a,y in fresh))
            exact5=fit_full(source_evidence+fresh,5)
            fitted=train_fitted(h,source_evidence+fresh,seed)
            # Every input to the native model is a public witness with a
            # digest, not evaluator world ID, weights, or any held output.
            forecasts={m:[] for m in METHODS}
            statuses=[]
            for mask in held:
                updated,fraction_native,decision=current.validate_causal_source_with_witnesses(
                    selected,fresh,header,source_ref=srcref,
                    evidence_slot=12+caseindex,
                    query_context=mask&7,query_action=mask>>3)
                current=updated
                statuses.append(decision)
                forecasts["guarded_native"].append(Fraction(*fraction_native))
                forecasts["exact_equivalent_697"].append(fraction(conditioned,mask))
                forecasts["source_unvalidated"].append(
                    Fraction(*current.causal_relation_probability(selected,mask&7,mask>>3)))
                forecasts["exact_broader_6885"].append(fraction(exact5,mask))
                forecasts["fitted_logistic"].append(fitted["fitted_logistic"](mask))
                forecasts["fitted_forest"].append(fitted["fitted_forest"](mask))
                forecasts["unrestricted_world"].append(Fraction(1,2))
                forecasts["privileged_oracle"].append(
                    evaluator(world,worlds,mask,validation,held))
            must(len(set(statuses))==1
                 and forecasts["guarded_native"]==forecasts["exact_equivalent_697"],
                 "NATIVE_VS_INDEPENDENT_697_PARITY")
            raw=current.checkpoint()
            cold=NativeCumulativeLearner.restore(raw,digest(raw))
            preserve=(cold.checkpoint()==raw and original.checkpoint()==old
                and cold._properties.checkpoint()==original._properties.checkpoint()
                and cold._source._seen[0]==original._source._seen[0]
                and cold._events[:len(original._events)]==original._events
                and [cold.predict(0,c,a) for a in (0,1) for c in range(8)]==original_outputs
                and [cold._compiled[s].checkpoint() for s in (1,2,3)]==old_known
                and [cold._source._seen[12+i].bit_count()
                     for i in range(caseindex+1)]==[2]*(caseindex+1)
                and not any(cold._quarantined[s] for s in (1,2,3)))
            must(preserve,"NATIVE_WITNESSED_COLD_OR_SOURCE_ERASURE")
            native=cold
            y=[evaluator(world,worlds,mask,validation,held) for mask in held]
            results={m:score(x,y) for m,x in forecasts.items()}
            receipts.append({
                "seed":seed,"episode":caseindex,"evaluator_only_world":world,
                "actual_source_actions":12,"actual_new_validation_actions":2,
                "native_learned_source_slot":selected,
                "native_source_selection":selected_status,
                "native_validation_status":statuses[0],
                "original_12_witness_sha256":digest(canonical(source_evidence)),
                "new_2_witness_sha256":header,
                "source_mask_sha256":digest(canonical(source)),
                "validation_mask_sha256":digest(canonical(validation)),
                "held_mask_sha256":digest(canonical(held)),
                "held_truth_sha256":digest(canonical(y)),
                "evidence_native_slot":12+caseindex,
                "post_validation_cold_checkpoint_sha256":digest(raw),
                "old_causal_memories_and_source_retained":preserve,
                "conventional_697_source_survivors_before":len(exact_C),
                "conventional_697_source_survivors_after":len(conditioned),
                "strong_conventional_6885_survivors_after":len(exact5),
                "prediction_metrics":results
            })
        must([native._source._seen[s].bit_count() for s in (1,2,3)]==[12,12,12],
             "LEARNED_SOURCE_MEMORIES_CORRUPTED")
        provenance[str(seed)]={
            "A_B_C_compiled_sha256":[digest(x) for x in old_known],
            "source_split_sha256":digest(canonical(source)),
            "validation_split_sha256":digest(canonical(validation)),
            "held_split_sha256":digest(canonical(held)),
            "original_old_source_unchanged":native._source._seen[0]==original._source._seen[0],
            "source_weights_evaluator_only":worlds,
            "source_preserved_after_three_new_worlds":True,
            "end_native_checkpoint_sha256":digest(native.checkpoint()),
            "native_witness_evidence_counts":[native._source._seen[s].bit_count()
                                               for s in (12,13,14)]
        }
    must(len(receipts)==len(seeds)*len(CASES),"EXPECTED_FROZEN_EPISODES")
    arms={m:round(sum(r["prediction_metrics"][m]["brier"] for r in receipts)/len(receipts),9)
          for m in METHODS}
    by_world={w:{m:round(sum(r["prediction_metrics"][m]["brier"]
                            for r in receipts if r["evaluator_only_world"]==w)/len(seeds),9)
                 for m in METHODS} for w in CASES}
    detection=[r for r in receipts if r["evaluator_only_world"]=="D1"]
    consistent=[r for r in receipts if r["evaluator_only_world"]=="C"]
    indistinguishable=[r for r in receipts if r["evaluator_only_world"]=="D2"]
    g={
        "original_and_A_B_C_persist_with_cold_witnesses":
            all(x["old_causal_memories_and_source_retained"] for x in receipts)
            and all(p["native_witness_evidence_counts"]==[2,2,2]
                    for p in provenance.values()),
        "all_new_actions_are_real_and_held_separate":
            all(r["actual_source_actions"]==12 and
                r["actual_new_validation_actions"]==2 for r in receipts),
        "falsifies_every_truly_detectable_D1":
            all(r["native_validation_status"]=="FALSIFIED" for r in detection),
        "D1_safe_Brier_and_no_confident_wrong":
            by_world["D1"]["guarded_native"]<=.27 and
            sum(r["prediction_metrics"]["guarded_native"]["confident_wrong"]
                for r in detection)==0,
        "never_falsifies_in_class_C":
            all(r["native_validation_status"]=="CONSISTENT" for r in consistent)
            and by_world["C"]["guarded_native"]<=by_world["C"]["source_unvalidated"]+.025,
        "D2_reveals_information_theoretic_alias":
            all(r["native_validation_status"]=="CONSISTENT" for r in indistinguishable)
            and (sum(r["prediction_metrics"]["guarded_native"]["confident_wrong"]
                     for r in indistinguishable)>=1
                 or by_world["D2"]["guarded_native"]>.25),
        "overall_held_Brier_gain_vs_unvalidated_at_least_0_05":
            arms["guarded_native"]<=arms["source_unvalidated"]-.05+1e-12,
        "candidate_within_0_05_of_best_conventional_equal_info":
            arms["guarded_native"]<=min(arms[k] for k in
                ("exact_broader_6885","fitted_logistic","fitted_forest"))+.05+1e-12,
        "exact_697_conventional_native_output_parity":
            all(r["prediction_metrics"]["guarded_native"]["held_fraction"]==
                r["prediction_metrics"]["exact_equivalent_697"]["held_fraction"]
                for r in receipts)
    }
    return {
        "schema":"yggdrasil.ckad25z.native-falsifying-witness.v1",
        "executed_source_sha256":digest(Path(__file__).read_bytes()),
        "independent_conventional_helper_sha256":digest(HELP.read_bytes()),
        "original_native_source_sha256":ORIGINAL,
        "science_seeds":list(seeds),
        "scored_original_primary":tuple(seeds)==SEEDS,
        "genuine_source_free_action_consequences":len(seeds)*(36+3*14),
        "held_phase_predictions":len(seeds)*3*2,
        "alias_worlds_not_independent_families":True,
        "one_native_tokenless_learner_per_seed":True,
        "native_source_weights_learned_from_real_actions":True,
        "source_family_labels_not_passed_to_native":True,
        "original_owner_science_first_use":False,
        "accepted_main_changed":False,
        "frozen_seeds_source_history":provenance,
        "per_seed_world":receipts,
        "mean_brier":arms,
        "by_world_brier":by_world,
        "gates":g,
        "development_disposition":"BOUNDED_DETECTION_SIGNAL" if all(g.values())
                                  else "DEVELOPMENT_NO_GO",
        "universal_OOD_safety":False,
        "information_theoretic_alias_D2_unresolved":True,
        "scientific_pass":False,"conventional_superiority":False,
        "forge_dispatch":False,"native_promotion":False,"merge":False,
        "deployment":False
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--preflight",action="store_true")
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    if args.preflight:
        must(args.output is None,"DISJOINT_PRECHECK_CANNOT_WRITE_PRIMARY")
        r=run((72999,))
        must(r["scored_original_primary"] is False
             and r["genuine_source_free_action_consequences"]==78
             and len(r["per_seed_world"])==3,
             "DISJOINT_DEV_WIRING_FAILED")
        print("CKAD25Z_DISJOINT_SOURCE_ENGINEERING_PREFLIGHT_PASS")
        return
    must(args.output is not None,"EXPLICIT_PRIMARY_RESULT_REQUIRED")
    start=time.monotonic()
    outcome=run()
    raw=canonical(outcome)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_bytes(raw)
    print("CKAD25Z_FROZEN_DISPOSITION="+outcome["development_disposition"])
    print("CKAD25Z_OVERALL_BRIER="+json.dumps(outcome["mean_brier"],sort_keys=True))
    print("CKAD25Z_BY_WORLD="+json.dumps(outcome["by_world_brier"],sort_keys=True))
    print("CKAD25Z_GATES="+json.dumps(outcome["gates"],sort_keys=True))
    print("CKAD25Z_RESULT_SHA256="+digest(raw))
    print("CKAD25Z_CPU_SCORER_WALL_SECONDS="+str(round(time.monotonic()-start,3)))


if __name__=="__main__":main()

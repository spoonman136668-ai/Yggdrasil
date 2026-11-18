"""CKAD25-Y -- original witnessed native causal-memory acquisition and recall.

The *same* NativeCumulativeLearner receives genuine input/action/outcome rows,
infers whether an earlier source relation still explains them, and actually
trains a new native slot for previously unknown classes from twelve witnesses.
Strong conventional exact class, switching Markov, fitted RF/logistic and
memoryless controls see precisely the same observations. Source worlds are
small synthetic Boolean functions, not accepted source-owner environments.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import importlib.util
import itertools
import json
import math
import random
import time
from pathlib import Path

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner

HERE=Path(__file__).resolve().parent
HELP=HERE.parent/"CKAD25-S"/"run.py"
ORIGINAL="c52681bf26f08817b3747647472913fa792da2de33f74b8fa7c0f2b0e78c119f"
SEEDS=(68011,68023,68041,68059)
PHASES=("A","B","A","C","D","C","A","B")
PROBES=(12,12,4,12,12,4,4,4)
METHODS=("native","conventional_exact","conventional_markov","memoryless_exact",
         "logistic_source","forest_source","recent_native","no_memory","privileged_oracle")


def must(flag,label):
    if not flag: raise ValueError("CKAD25Y_"+label)


def controls():
    spec=importlib.util.spec_from_file_location("ckad25y_conventional_controls",HELP)
    must(spec is not None and spec.loader is not None,"MISSING_INDEPENDENT_CONTROL")
    h=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h)
    must(h.ORIGINAL_CHECKPOINT==ORIGINAL and h.SEEDS==(1103,2207,3301),
         "EXACT_REFERENCE_DRIFT")
    return h


def math_truth(weights,mask):
    features=sum(1<<i for i in range(16) if (mask&i)==i)
    return (weights&features).bit_count()&1


def public_roster(seed):
    seq=list(range(16))
    key=digest(canonical(["CKAD25-Y-PUBLIC-16",seed]))
    random.Random(int(key[:16],16)).shuffle(seq)
    must(len(set(seq))==16,"SOURCE_DISJOINTNESS")
    return seq[:12],seq[12:]


def world_roster(seed,train):
    generator=random.Random(int(digest(canonical(["CKAD25-Y-PRIVATE-FUNCTIONS",seed]))[:16],16))
    selected={}
    for label,size in (("A",3),("B",3),("C",3),("D",5),("P",2),("Q",2)):
        for _ in range(4000):
            terms=tuple(sorted(generator.sample(range(16),size)))
            if label in ("A","B","C") and not any(t&8 for t in terms):
                continue
            weight=sum(1<<i for i in terms)
            if weight in selected.values():continue
            if label in ("B","C") and any(sum(
                    math_truth(weight,m)!=math_truth(selected[other],m)
                    for m in train)<4 for other in selected if other in ("A","B","C")):
                continue
            selected[label]=weight
            break
        else:raise ValueError("CKAD25Y_UNDERPOWERED_GENERATOR")
    must([selected[k].bit_count() for k in ("A","B","C","D","P","Q")]
         ==[3,3,3,5,2,2],"PRIVATE_GENERATOR_GRAMMAR")
    return selected


def observed(weights,masks):
    return [[m&7,m>>3,math_truth(weights,m)] for m in masks]


def source_ref(seed,stage):
    return digest(canonical(["CKAD25-Y-PUBLIC-SOURCE",seed,stage]))


def exact_fit(h,records):
    # Independently fitted entire conventional 697-element GF2 weight prior.
    data=[(h.terms(c,a),y) for c,a,y in records]
    surviving=[]
    for size in range(4):
        for positions in itertools.combinations(range(16),size):
            if all((sum(feat[j] for j in positions)&1)==y for feat,y in data):
                surviving.append(positions)
    return tuple(surviving)


def exact_fraction(h,models,mask):
    if not models:return Fraction(1,2)
    terms=h.terms(mask&7,mask>>3)
    return Fraction(sum(sum(terms[j] for j in model)&1 for model in models),len(models))


def likelihood(bank,records):
    prob=Fraction(1,1)
    for c,a,y in records:
        p=bank(c|(a<<3))
        prob*=p if y else 1-p
    return prob


def independent_route(h,banks,records,prior=None):
    available={slot:models for slot,models in banks.items() if models}
    if prior is None:
        weights={slot:likelihood(
            lambda mask,models=models:exact_fraction(h,models,mask),records)
            for slot,models in available.items()}
        unknown=Fraction(1,2)**len(records)
    else:
        proposal=prior(available)
        weights={slot:proposal[slot]*likelihood(
            lambda mask,models=models:exact_fraction(h,models,mask),records)
            for slot,models in available.items()}
        unknown=proposal["unknown"]*Fraction(1,2)**len(records)
    total=sum(weights.values(),unknown)
    must(total>0,"CONVENTIONAL_POSTERIOR_ZERO")
    if not weights:return None,weights,unknown
    selected=max(weights,key=lambda slot:(weights[slot],-slot))
    return (selected if weights[selected]/total>=Fraction(9,10) else None),weights,unknown


def fitted(h,records,seed):
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    y=[r[2] for r in records]
    result={}
    for method in ("logistic_source","forest_source"):
        use_terms=(method=="logistic_source")
        x=[h.terms(c,a) if use_terms else h.vector(c,a) for c,a,_ in records]
        if len(set(y))==1:
            q=float(y[0])
            result[method]=lambda mask,q=q:q
            continue
        if use_terms:
            model=LogisticRegression(C=1,max_iter=1000,solver="lbfgs",
                                     random_state=seed).fit(x,y)
        else:
            model=RandomForestClassifier(n_estimators=64,max_depth=4,n_jobs=1,
                                         random_state=seed).fit(x,y)
        positive=list(model.classes_).index(1)
        def predict(mask,model=model,use_terms=use_terms,positive=positive):
            c,a=mask&7,mask>>3
            row=h.terms(c,a) if use_terms else h.vector(c,a)
            return float(model.predict_proba([row])[0][positive])
        result[method]=predict
    return result


def fitted_route(banks,records,method):
    available={s:classifier[method] for s,classifier in banks.items()}
    score={s:1. for s in available}
    for slot,pred in available.items():
        for c,a,y in records:
            p=pred(c|(a<<3))
            score[slot]*=p if y else 1-p
    unknown=.5**len(records)
    if not score:return None
    best=max(score,key=lambda slot:(score[slot],-slot))
    return best if score[best]/(sum(score.values())+unknown)>=.9 else None


def assess(pred,truth):
    probs=[float(v) for v in pred]
    return {
        "brier":round(sum((p-y)**2 for p,y in zip(probs,truth))/4,9),
        "confident":sum(p in (0.,1.) for p in probs),
        "confident_wrong":sum(p in (0.,1.) and int(p)!=y for p,y in zip(probs,truth)),
        "held_fractions":[[v.numerator,v.denominator] if isinstance(v,Fraction)
                           else [round(v,12),1.] for v in pred]
    }


def full_score(seeds=SEEDS):
    h=controls()
    parent=h.snapshot()
    native_source=parent.checkpoint()
    must(digest(native_source)==ORIGINAL,"ORIGINAL_NATIVE_PIN")
    old_preds=[parent.predict(0,c,a) for a in (0,1) for c in range(8)]
    rows=[]
    retained={}
    for seed in seeds:
        pool,held=public_roster(seed)
        worlds=world_roster(seed,pool)
        current=NativeCumulativeLearner.restore(native_source,ORIGINAL)
        conventional={}
        markov={}
        fitted_banks={}
        last_known=None
        prior_state=None
        transitions={}
        source_events=[]
        original_memories={}
        for stage,(label,budget) in enumerate(zip(PHASES,PROBES)):
            # Every learner gets exactly these fresh witnessed observations.
            inputs=pool[:budget]
            evidence=observed(worlds[label],inputs)
            checksum=digest(canonical(evidence))
            current,slot,status=current.incorporate_causal_world(
                evidence,checksum,source_ref=source_ref(seed,stage))
            # Independent conventional dynamic archive fits the same new source
            # consequences, or restores a previously learned source.
            chosen,weights,other=independent_route(h,conventional,evidence)
            if chosen is None and budget==12:
                chosen=next(k for k in range(1,10) if k not in conventional)
                conventional[chosen]=exact_fit(h,evidence)
                must(len(conventional[chosen])==current._compiled[chosen].model_count,
                     "SOURCE_CONVENTIONAL_COUNT_DRIFT")
                fitted_banks[chosen]=fitted(h,evidence,seed)
            must(slot==chosen and status==(
                 "RECALLED" if chosen is not None and chosen in original_memories else
                 "ABSTAIN" if chosen is None else
                 "INCOMPATIBLE" if not conventional[chosen] else "ACQUIRED"),
                 "NATIVE_VS_INDEPENDENT_STATE_ROUTING")
            if status in ("ACQUIRED","INCOMPATIBLE"):
                original_memories[slot]=current._compiled[slot].checkpoint()
            if slot is not None and current._compiled[slot].model_count>0:
                last_known=slot
            # Separate learned-transition Bayesian Markov filter. Infer a
            # source archive and fit prior transition frequencies online; no
            # hidden law identity or evaluator family label admitted.
            def transition_prior(known):
                keys=list(sorted(known))
                if not keys:return {"unknown":Fraction(1,1)}
                from_state=prior_state
                counts=transitions.get(from_state,{})
                total=sum(counts.get(k,0)+1 for k in keys)+counts.get("unknown",0)+1
                out={k:Fraction(counts.get(k,0)+1,total) for k in keys}
                out["unknown"]=Fraction(counts.get("unknown",0)+1,total)
                return out
            # Markov baseline must use its own archive, updated only after
            # observing the SAME source packet; past labels are inferred.
            hmmslot,_,_=independent_route(h,markov,evidence,transition_prior)
            if hmmslot is None and budget==12:
                hmmslot=next(k for k in range(1,10) if k not in markov)
                markov[hmmslot]=exact_fit(h,evidence)
            transitions.setdefault(prior_state,{})
            transition_key=hmmslot if hmmslot is not None else "unknown"
            transitions[prior_state][transition_key]=transitions[prior_state].get(transition_key,0)+1
            prior_state=hmmslot

            # The original model actually retains new source states in its
            # checkpoint; restart after every episode without replaying labels.
            cold_raw=current.checkpoint()
            current=NativeCumulativeLearner.restore(cold_raw,digest(cold_raw))
            old_integrity=(parent.checkpoint()==native_source
                and current._properties.checkpoint()==parent._properties.checkpoint()
                and current._source._seen[0]==parent._source._seen[0]
                and current._hypotheses[0].checkpoint()==parent._hypotheses[0].checkpoint()
                and current._events[:len(parent._events)]==parent._events
                and [current.predict(0,c,a) for a in (0,1) for c in range(8)]==old_preds
                and all(current._compiled[k].checkpoint()==memory
                        for k,memory in original_memories.items())
                and not any(current._quarantined[k] for k in original_memories))
            must(old_integrity,"ORIGINAL_AND_NEW_COLD_RETENTION")

            # Explicit P/Q interference after D's actual source evidence.
            if stage==4:
                for pressure,kind in ((10,"P"),(11,"Q")):
                    extra=observed(worlds[kind],pool[:8])
                    current=current.observe(pressure,extra,digest(canonical(extra)),
                                            source_ref=source_ref(seed,20+pressure))
                pressure_raw=current.checkpoint()
                current=NativeCumulativeLearner.restore(pressure_raw,digest(pressure_raw))
                must(all(current._compiled[k].checkpoint()==memory
                         for k,memory in original_memories.items()),
                     "INTERFERENCE_ERASED_SOURCE_MEMORY")

            # Evaluate four withheld actions, never supply held labels to
            # model, source admission or independent baseline training.
            pred={k:[] for k in METHODS}
            selected=slot
            for mask in held:
                c,a=mask&7,mask>>3
                native_p=(Fraction(*current.causal_relation_probability(slot,c,a))
                          if slot is not None else Fraction(1,2))
                conventional_p=(exact_fraction(h,conventional[chosen],mask)
                                if chosen is not None else Fraction(1,2))
                must(native_p==conventional_p,"NATIVE_CONVENTIONAL_HELD_PARITY")
                markov_p=(exact_fraction(h,markov[hmmslot],mask)
                          if hmmslot is not None else Fraction(1,2))
                pred["native"].append(native_p)
                pred["conventional_exact"].append(conventional_p)
                pred["conventional_markov"].append(markov_p)
                pred["memoryless_exact"].append(exact_fraction(h,exact_fit(h,evidence),mask))
                for method in ("logistic_source","forest_source"):
                    # Fully trained conventional bank, its own source memory,
                    # class readout from same current evidence, no world label.
                    fit_slot=fitted_route(fitted_banks,evidence,method)
                    if fit_slot is None and budget==12:
                        # The conventional bank has trained its latest new
                        # source from these same 12 actual witnesses.
                        fit_slot=chosen
                    pred[method].append(fitted_banks[fit_slot][method](mask)
                                        if fit_slot in fitted_banks else .5)
                pred["recent_native"].append(
                    Fraction(*current.causal_relation_probability(last_known,c,a))
                    if last_known is not None else Fraction(1,2))
                pred["no_memory"].append(.5)
                # Privileged oracle is evaluator-only and never provided to
                # candidate/controls, used solely for an unattainable ceiling.
                oracle_slot={"A":1,"B":2,"C":3}.get(label)
                pred["privileged_oracle"].append(
                    Fraction(*current.causal_relation_probability(oracle_slot,c,a))
                    if oracle_slot is not None and current._compiled[oracle_slot] is not None
                    else Fraction(1,2))
            truth=[math_truth(worlds[label],mask) for mask in held]
            scores={method:assess(values,truth) for method,values in pred.items()}
            rows.append({
                "seed":seed,"episode":stage,"evaluator_only_world":label,
                "witnesses":budget,"source_witness_sha256":checksum,
                "source_input_sha256":digest(canonical(inputs)),
                "held_input_sha256":digest(canonical(held)),
                "held_truth_sha256":digest(canonical(truth)),
                "source_ref":source_ref(seed,stage),
                "native_slot":selected,"native_verdict":status,
                "conventional_slot":chosen,"markov_slot":hmmslot,
                "repeat_held_retention_not_independent":stage in (2,5,6,7),
                "native_source_cold_sha256":digest(current.checkpoint()),
                "native_original_and_learned_retained":old_integrity,
                "native_compiled_model_count":(
                    current._compiled[slot].model_count if slot is not None else None),
                "metrics":scores
            })
            source_events.append([stage,budget,status,slot])
        retained[str(seed)]={
            "event_log":source_events,
            "final_native_sha256":digest(current.checkpoint()),
            "original_old_model_unchanged":(
                current._properties.checkpoint()==parent._properties.checkpoint()
                and current._source._seen[0]==parent._source._seen[0]),
            "native_A_B_C_source_banks":[current._source._seen[i].bit_count() for i in (1,2,3)],
            "native_A_B_C_compiled_sha256":[digest(current._compiled[i].checkpoint())
                                               for i in (1,2,3)],
            "pressure_source_rows":[current._source._seen[i].bit_count() for i in (10,11)],
            "generator_laws_evaluator_only":[worlds[i] for i in ("A","B","C","D")],
            "source_pool_sha256":digest(canonical(pool)),
            "held_pool_sha256":digest(canonical(held))
        }
    must(len(rows)==len(seeds)*8,"EXPECTED_PHASE_COUNT")
    means={method:round(sum(row["metrics"][method]["brier"] for row in rows)/len(rows),9)
           for method in METHODS}
    returns=[r for r in rows if r["episode"] in (2,5,6,7)]
    unknown=[r for r in rows if r["episode"]==4]
    correct_returns=sum(r["native_slot"]=={"A":1,"B":2,"C":3}[r["evaluator_only_world"]]
                        for r in returns)
    return_brier=sum(r["metrics"]["native"]["brier"] for r in returns)/len(returns)
    memoryless_return_brier=sum(r["metrics"]["memoryless_exact"]["brier"]
                               for r in returns)/len(returns)
    unknown_brier=sum(r["metrics"]["native"]["brier"] for r in unknown)/len(unknown)
    wrong_unknown=sum(r["metrics"]["native"]["confident_wrong"] for r in unknown)
    return_scores={k:round(sum(r["metrics"][k]["brier"] for r in returns)/len(returns),9)
                   for k in METHODS}
    gates={
        "all_four_native_learn_unseen_source_C":
            all(r["native_verdict"]=="ACQUIRED" and r["native_slot"]==3
                for r in rows if r["episode"]==3),
        "source_old_and_learned_retained_with_pressure":
            all(r["native_original_and_learned_retained"] for r in rows)
            and all(v["original_old_model_unchanged"] and
                    v["native_A_B_C_source_banks"]==[12,12,12] and
                    v["pressure_source_rows"]==[8,8] for v in retained.values()),
        "return_state_identified_at_least_10_of_16":correct_returns>=10,
        "native_return_brier_beats_memoryless_exact_by_0_05":
            return_brier<=memoryless_return_brier-.05+1e-12,
        "novel_D_brier_le_0_27":unknown_brier<=.27+1e-12,
        "novel_D_confident_wrong_le_1":wrong_unknown<=1,
        "exact_native_conventional_parity_all_128":
            all(r["metrics"]["native"]["held_fractions"]==
                r["metrics"]["conventional_exact"]["held_fractions"] for r in rows),
        "candidate_within_0_01_of_conventional_dynamic":
            means["native"]<=means["conventional_exact"]+.01+1e-12,
        "candidate_within_0_03_of_markov":
            means["native"]<=means["conventional_markov"]+.03+1e-12,
        "candidate_within_0_03_of_strong_fitted_models":
            means["native"]<=min(means["forest_source"],means["logistic_source"])+.03+1e-12
    }
    return {
        "schema":"yggdrasil.ckad25y.native-contradiction-state-acquisition.v1",
        "source_sha256":digest(Path(__file__).read_bytes()),
        "independent_control_sha256":digest(HELP.read_bytes()),
        "original_native_source_sha256":ORIGINAL,
        "seeds":list(seeds),"scored_original":tuple(seeds)==SEEDS,
        "source_free_observations":len(seeds)*80,
        "held_phase_predictions":len(seeds)*8*4,
        "unique_held_world_labels":len(seeds)*4*4,
        "native_model_from_actual_source":True,
        "hidden_regime_labels_unavailable_to_candidate":True,
        "one_cumulative_native_learner_per_seed":True,
        "original_protected_source_actions":0,
        "original_owner_first_use":False,
        "per_seed_state":retained,
        "per_episode":rows,
        "mean_brier":means,
        "return_brier":return_scores,
        "return_states_correct":correct_returns,
        "novel_D_brier":round(unknown_brier,9),
        "novel_D_confident_wrong":wrong_unknown,
        "gates":gates,
        "disposition":"DEVELOPMENT_SIGNAL" if all(gates.values()) else "DEVELOPMENT_NO_GO",
        "scientific_pass":False,"conventional_superiority":False,
        "accepted_main_changed":False,"native_owner_promoted":False,
        "forge_dispatch":False,"deployment":False
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--preflight",action="store_true")
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    if args.preflight:
        must(args.output is None,"PREFLIGHT_NO_PRIMARY_RESULT")
        r=full_score((68999,))
        must(r["scored_original"] is False and r["source_free_observations"]==80,
             "DISJOINT_DEV_PRECHECK")
        print("CKAD25Y_SOURCE_ONLY_DISJOINT_WIRING_PREFLIGHT_PASS")
        return
    must(args.output is not None,"ORIGINAL_RESULT_PATH")
    before=time.monotonic()
    result=full_score()
    raw=canonical(result)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_bytes(raw)
    print("CKAD25Y_FROZEN_DISPOSITION="+result["disposition"])
    print("CKAD25Y_OVERALL_BRIER="+json.dumps(result["mean_brier"],sort_keys=True))
    print("CKAD25Y_RETURN_BRIER="+json.dumps(result["return_brier"],sort_keys=True))
    print("CKAD25Y_RETURN_RECOGNITION="+str(result["return_states_correct"]))
    print("CKAD25Y_NOVEL_D="+str(result["novel_D_brier"]))
    print("CKAD25Y_GATES="+json.dumps(result["gates"],sort_keys=True))
    print("CKAD25Y_ORIGINAL_RESULT_SHA256="+digest(raw))
    print("CKAD25Y_MEASURED_SOURCE_SECONDS="+str(round(time.monotonic()-before,3)))


if __name__=="__main__":
    main()

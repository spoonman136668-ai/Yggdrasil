"""Independent read-only CKAD25-Y source and state-custody auditor.

Does NOT import the native learner, experiment scorer or scikit-learn.
It reconstructs source-only revealed outcomes, every held source truth and
every held metric, then independently re-fits full 697-weight GF2 source
hypotheses to verify native-source selection and predictions.
"""
from __future__ import annotations
import argparse
from fractions import Fraction
import hashlib
import itertools
import json
import random
from pathlib import Path

SEEDS=(68011,68023,68041,68059)
PHASES=("A","B","A","C","D","C","A","B")
BUDGETS=(12,12,4,12,12,4,4,4)
METHODS={"native","conventional_exact","conventional_markov","memoryless_exact",
         "logistic_source","forest_source","recent_native","no_memory","privileged_oracle"}


def check(flag,label):
    if not flag:raise ValueError("CKAD25Y_INDEPENDENT_AUDIT_"+label)


def canon(o):
    return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode("ascii")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def src_masks(seed):
    x=list(range(16))
    r=random.Random(int(sha(canon(["CKAD25-Y-PUBLIC-16",seed]))[:16],16))
    r.shuffle(x)
    return x[:12],x[12:]


def true_output(weights,mask):
    f=sum(1<<i for i in range(16) if i&mask==i)
    return (weights&f).bit_count()&1


def GF2_fit(records):
    f=[(sum(1<<j for j in range(16) if j&(c|(a<<3))==j),y)
       for c,a,y in records]
    alive=[]
    for size in range(4):
        for slots in itertools.combinations(range(16),size):
            w=sum(1<<i for i in slots)
            if all((w&features).bit_count()%2==y for features,y in f):
                alive.append(w)
    return tuple(alive)


def evidence_fraction(models,mask):
    if not models:return Fraction(1,2)
    features=sum(1<<i for i in range(16) if i&mask==i)
    return Fraction(sum((w&features).bit_count()%2 for w in models),len(models))


def classify(models,observations):
    probabilities={}
    for slot,weights in models.items():
        if not weights:continue
        score=Fraction(1,1)
        for c,a,y in observations:
            p=evidence_fraction(weights,c|(a<<3))
            score*=p if y else 1-p
        probabilities[slot]=score
    denominator=sum(probabilities.values(),Fraction(1,2)**len(observations))
    if not probabilities:return None
    top=max(probabilities,key=lambda z:(probabilities[z],-z))
    return top if probabilities[top]/denominator>=Fraction(9,10) else None


def audit(raw):
    data=json.loads(raw)
    check(canon(data)==raw,"NONCANONICAL")
    check(data["schema"]=="yggdrasil.ckad25y.native-contradiction-state-acquisition.v1","SCHEMA")
    check(tuple(data["seeds"])==SEEDS and data["scored_original"] is True,"ORIGINAL_SEEDS")
    check(data["source_free_observations"]==320 and data["held_phase_predictions"]==128
          and data["unique_held_world_labels"]==64,"ACTION_HELD_BUDGET")
    check(data["original_protected_source_actions"]==0
          and data["original_owner_first_use"] is False
          and data["accepted_main_changed"] is False
          and data["forge_dispatch"] is False and data["native_owner_promoted"] is False
          and data["deployment"] is False
          and data["scientific_pass"] is False
          and data["conventional_superiority"] is False,
          "ISOLATION_SCIENTIFIC_BOUNDARY")
    check(len(data["per_episode"])==32 and len(data["per_seed_state"])==4,
          "ORIGINAL_STAGE_COUNT")
    checked=[]
    for seed in SEEDS:
        key=str(seed)
        state=data["per_seed_state"][key]
        pool,held=src_masks(seed)
        check(state["source_pool_sha256"]==sha(canon(pool))
              and state["held_pool_sha256"]==sha(canon(held))
              and len(set(pool+held))==16,"SOURCE_SPLIT_"+key)
        true_laws=dict(zip(("A","B","C","D"),state["generator_laws_evaluator_only"]))
        check([true_laws[k].bit_count() for k in ("A","B","C","D")]==[3,3,3,5],
              "TRUE_GENERATOR_CLASS_"+key)
        source_memory={}
        stream=sorted((x for x in data["per_episode"] if x["seed"]==seed),
                      key=lambda x:x["episode"])
        check(len(stream)==8,"PER_SEED_EPISODES_"+key)
        for episode,row in enumerate(stream):
            label=PHASES[episode]
            budget=BUDGETS[episode]
            check(row["episode"]==episode and row["evaluator_only_world"]==label
                  and row["witnesses"]==budget
                  and row["repeat_held_retention_not_independent"] is (episode in (2,5,6,7)),
                  "EPISODE_ID_"+key)
            observed=[[mask&7,mask>>3,true_output(true_laws[label],mask)]
                      for mask in pool[:budget]]
            check(row["source_witness_sha256"]==sha(canon(observed))
                  and row["source_input_sha256"]==sha(canon(pool[:budget]))
                  and row["held_input_sha256"]==sha(canon(held))
                  and row["source_ref"]==sha(canon(["CKAD25-Y-PUBLIC-SOURCE",seed,episode])),
                  "SOURCE_CUSTODY_"+key)
            selected=classify(source_memory,observed)
            if selected is None and budget==12:
                selected=next(i for i in range(1,10) if i not in source_memory)
                source_memory[selected]=GF2_fit(observed)
                expected_status="ACQUIRED" if source_memory[selected] else "INCOMPATIBLE"
            else:
                expected_status="RECALLED" if selected is not None else "ABSTAIN"
            check(row["native_slot"]==selected and row["conventional_slot"]==selected
                  and row["native_verdict"]==expected_status,
                  "NATIVE_SOURCE_RECONSTRUCTION_"+key+str(episode))
            check(row["native_compiled_model_count"]==
                  (len(source_memory[selected]) if selected is not None else None),
                  "NATIVE_NUMERIC_MODEL_COUNT_"+key+str(episode))
            labels=[true_output(true_laws[label],mask) for mask in held]
            check(row["held_truth_sha256"]==sha(canon(labels)),"HELD_TRUTH_"+key+str(episode))
            check(row["native_original_and_learned_retained"] is True,
                  "COLD_RESTORE_"+key+str(episode))
            check(set(row["metrics"])==METHODS,"EQUAL_INFORMATION_MODEL_ROSTER")
            for name,metric in row["metrics"].items():
                predictions=[]
                fractions=metric["held_fractions"]
                check(len(fractions)==4,"HELD_COUNT_"+name)
                for q in fractions:
                    check(type(q) is list and len(q)==2 and
                          type(q[0]) in (float,int) and type(q[1]) in (float,int)
                          and 0<q[1] and 0<=q[0]<=q[1],"HELD_PROBABILITY_ENCODING")
                    predictions.append(q[0]/q[1])
                brier=sum((p-y)**2 for p,y in zip(predictions,labels))/4
                confident=sum(p in (0.,1.) for p in predictions)
                wrong=sum(p in (0.,1.) and int(p)!=y for p,y in zip(predictions,labels))
                check(abs(brier-metric["brier"])<=1e-8
                      and confident==metric["confident"]
                      and wrong==metric["confident_wrong"],
                      "EVALUATOR_METRICS_"+key+str(episode)+"_"+name)
            direct=[evidence_fraction(source_memory[selected],mask)
                    if selected is not None else Fraction(1,2) for mask in held]
            native=[Fraction(*pair) for pair in row["metrics"]["native"]["held_fractions"]]
            check(native==direct and
                  row["metrics"]["native"]["held_fractions"]==
                  row["metrics"]["conventional_exact"]["held_fractions"],
                  "INDEPENDENT_697_RULE_PARITY_"+key+str(episode))
            checked.append(row)
        check(state["native_A_B_C_source_banks"]==[12,12,12]
              and state["pressure_source_rows"]==[8,8]
              and state["original_old_model_unchanged"] is True
              and len(state["native_A_B_C_compiled_sha256"])==3,
              "FINAL_SOURCE_RETENTION_"+key)
    mean={}
    for method in METHODS:
        predicted=sum(r["metrics"][method]["brier"] for r in checked)/len(checked)
        check(abs(predicted-data["mean_brier"][method])<=1e-8,
              "MEAN_BRIER_"+method)
        returners=[r for r in checked if r["episode"] in (2,5,6,7)]
        return_avg=sum(r["metrics"][method]["brier"] for r in returners)/len(returners)
        check(abs(return_avg-data["return_brier"][method])<=1e-8,
              "RETURN_BRIER_"+method)
        mean[method]=round(predicted,9)
    check(data["disposition"] in ("DEVELOPMENT_SIGNAL","DEVELOPMENT_NO_GO")
          and data["disposition"]==("DEVELOPMENT_SIGNAL"
              if all(data["gates"].values()) else "DEVELOPMENT_NO_GO"),
          "FROZEN_CLASSIFICATION")
    return {"result_sha256":sha(raw),"metrics":mean,
            "return_correct":data["return_states_correct"],
            "novel_D_brier":data["novel_D_brier"],
            "disposition":data["disposition"],
            "source_only_episodes_reconstructed":len(checked),
            "protected_first_use":False}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("original",type=Path)
    path=p.parse_args().original
    result=audit(path.read_bytes())
    print("CKAD25Y_INDEPENDENT_697_RULE_AND_EVALUATOR_AUDIT_PASS")
    print(json.dumps(result,sort_keys=True))


if __name__=="__main__":main()

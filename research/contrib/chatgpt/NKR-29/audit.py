"""Retrospective bounded learning from already-consumed public feedback.

No environment import/action, model replacement or repaired-label rescoring.
A stochastic surprise is not proof that a causal law or fact was incorrect.
"""
from __future__ import annotations
import argparse
from fractions import Fraction
import importlib.util
import json
import os
from pathlib import Path
import platform
import struct
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT))
spec=importlib.util.spec_from_file_location("nkr19_feedback_source",HERE.parent/"NKR-19/audit.py")
source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
from yggdrasil.public_causal_cells import PublicCausalCells

CAPS=(28,14,7)
RANDOM_SEEDS=(701,702,703)
ARMS=("frozen","all_feedback","error_only")+tuple("random_matched_"+str(s) for s in RANDOM_SEEDS)
SEEDS=source.SEEDS
canon=source.canon
sha=source.sha

def need(ok,reason):
    if not ok: raise ValueError("NKR29_"+reason)

def wrong_confident(probability,outcome):
    return ((probability>=Fraction(3,4) and outcome==0) or
            (probability<=Fraction(1,4) and outcome==1))

def probabilities(bank,worlds=range(4)):
    return [source.native_probability(bank,w,t,b,a)
            for w in worlds for t in (0,1) for b in (0,1) for a in (0,1)]

def counts(bank):
    return struct.unpack(">"+"H"*64,bank.snapshot()[4:-32])

def initial(data):
    bank=PublicCausalCells()
    for w,seed in enumerate(SEEDS):
        need(len(data[seed])==31,"SOURCE_EVENT_COUNT")
        for row in data[seed][:24]:
            source.update(bank,w,row)
    need(sum(counts(bank))==192,"INITIAL_KNOWLEDGE_COUNT")
    return bank

def arm_state(data,checkpoint):
    return {"bank":PublicCausalCells.restore(checkpoint),
            "evidence":[list(data[s][:24]) for s in SEEDS],
            "learned":{(w,i) for w in range(4) for i in range(24)},
            "updates":0,"retention_readouts":0,"repair_ids":[],
            "scores":[[],[]],"confident_misses":0,"trace":[]}

def row_valid(row):
    return (type(row) is dict and
        set(row)=={"before","action","reward","after","terminated","truncated"} and
        all(type(row[k]) is int and row[k] in (0,1)
            for k in ("before","action","reward","after")) and
        all(type(row[k]) is bool for k in ("terminated","truncated")))

def learn(state,data,world,index,available,cap):
    # Admission before any source-row lookup, posterior change or ledger change.
    need(type(world) is int and 0<=world<4 and
         type(index) is int and 0<=index<31,"EVENT_ID")
    key=(world,index)
    need(key in available,"FUTURE_FEEDBACK_REJECTED")
    need(key not in state["learned"],"DUPLICATE_EVENT_REJECTED")
    need(type(cap) is int and 0<cap<=28 and state["updates"]<cap,"REPAIR_BUDGET")
    row=data[SEEDS[world]][index]
    need(row_valid(row),"PUBLIC_ROW")
    bank=state["bank"]
    others=[w for w in range(4) if w!=world]
    old=probabilities(bank,others)
    source.update(bank,world,row)
    need(probabilities(bank,others)==old,"UNRELATED_WORLD_INTERFERENCE")
    state["retention_readouts"]+=len(old)
    state["learned"].add(key)
    state["evidence"][world].append(dict(row))
    state["repair_ids"].append(list(key))
    state["updates"]+=1

def verify_final(state,base_counts):
    bank=state["bank"];cold=PublicCausalCells.restore(bank.snapshot())
    need(cold.snapshot()==bank.snapshot() and probabilities(cold)==probabilities(bank),
         "COLD_RESTORATION")
    expected=[[[0,0] for a in range(2)] for cell in range(16)]
    for w,rows in enumerate(state["evidence"]):
        for row in rows:
            for target,name in enumerate(("reward","after")):
                expected[w*4+target*2+row["before"]][row["action"]][row[name]]+=1
    flat=tuple(n for cell in expected for action in cell for n in action)
    actual=counts(cold)
    need(actual==flat,"INDEPENDENT_OBSERVATION_LEDGER")
    need(all(new>=old for new,old in zip(actual,base_counts)) and
         sum(actual)==192+2*state["updates"],"OLD_OBSERVATIONS_LOST_OR_DUPLICATED")
    reward,after=state["scores"]
    pooled=reward+after
    return {"updates_events":state["updates"],"outcome_counter_increments":2*state["updates"],
            "retained_original_counter_increments":192,"retained_original_events":96,
            "unrelated_posterior_readouts_retained":state["retention_readouts"],
            "cold_checkpoint_hex":cold.snapshot().hex(),
            "cold_checkpoint_sha256":sha(cold.snapshot()),"checkpoint_bytes":len(cold.snapshot()),
            "repair_event_ids":state["repair_ids"],"confident_misses":state["confident_misses"],
            "scores":{"reward":source.rational(sum(reward)/len(reward)),
                      "after":source.rational(sum(after)/len(after)),
                      "pooled":source.rational(sum(pooled)/len(pooled))},
            "scored_outputs":len(pooled),"prediction_trace_sha256":sha(canon(state["trace"])),
            "pre_final_round_prediction_sha256":sha(canon(state["trace"][:24]))}

def qscore(arm):
    d=arm["scores"]["pooled"]
    return Fraction(d["numerator"],d["denominator"])

def run_scale(data,cap):
    need(cap in CAPS and type(cap) is int,"CAP")
    frozen=initial(data);checkpoint=frozen.snapshot();base_counts=counts(frozen)
    arms={name:arm_state(data,checkpoint) for name in ARMS}
    available={(w,i) for w in range(4) for i in range(24)}
    for index in range(24,31):
        for world,seed in enumerate(SEEDS):
            row=data[seed][index]
            predictions={}
            # Predictor sees current public state/action and its learned past only.
            for name,state in arms.items():
                native=[source.native_probability(state["bank"],world,t,
                            row["before"],row["action"]) for t in (0,1)]
                exact=[source.conventional(state["evidence"][world],row,target,"exact_beta")
                       for target in ("reward","after")]
                need(native==exact,"STRONG_CONTROL_PARITY")
                predictions[name]=native
                for t,target in enumerate(("reward","after")):
                    state["scores"][t].append((native[t]-row[target])**2)
                    state["confident_misses"]+=wrong_confident(native[t],row[target])
                state["trace"].append([world,index,[[p.numerator,p.denominator] for p in native]])
            # Feedback becomes available ONLY after all arms have forecast/scored.
            available.add((world,index))
            if arms["all_feedback"]["updates"]<cap:
                learn(arms["all_feedback"],data,world,index,available,cap)
            gated=arms["error_only"]
            trigger=(gated["updates"]<cap and any(
                wrong_confident(predictions["error_only"][t],row[target])
                for t,target in enumerate(("reward","after"))))
            if trigger:
                learn(gated,data,world,index,available,cap)
                for random_seed in RANDOM_SEEDS:
                    state=arms["random_matched_"+str(random_seed)]
                    choices=[i for w,i in available if w==world and (w,i) not in state["learned"]]
                    need(choices,"NO_AVAILABLE_RANDOM_WITNESS")
                    chosen=min(choices,key=lambda i:sha(canon(
                        [random_seed,cap,world,index,i])))
                    learn(state,data,world,chosen,available,cap)
            for random_seed in RANDOM_SEEDS:
                state=arms["random_matched_"+str(random_seed)]
                need(state["updates"]==gated["updates"],"RANDOM_ACTUAL_BUDGET_DRIFT")
                need([sum(w==j for w,i in state["repair_ids"]) for j in range(4)]==
                     [sum(w==j for w,i in gated["repair_ids"]) for j in range(4)],
                     "RANDOM_WORLD_BUDGET_DRIFT")
    need(frozen.snapshot()==checkpoint and arms["frozen"]["bank"].snapshot()==checkpoint,
         "FROZEN_BASELINE_REWRITTEN")
    out={name:verify_final(state,base_counts) for name,state in arms.items()}
    random_mean=sum(qscore(out["random_matched_"+str(s)]) for s in RANDOM_SEEDS)/3
    return {"maximum_repair_events":cap,"initial_checkpoint_hex":checkpoint.hex(),
            "initial_checkpoint_sha256":sha(checkpoint),"arms":out,
            "error_only_gain_vs_frozen":source.rational(qscore(out["frozen"])-qscore(out["error_only"])),
            "error_only_gain_vs_matched_random_mean":source.rational(random_mean-qscore(out["error_only"])),
            "all_feedback_gain_vs_frozen":source.rational(qscore(out["frozen"])-qscore(out["all_feedback"])),
            "random_matched_actual_events":out["error_only"]["updates_events"],
            "strong_equivalent_control_gain":0}

def stable(result):
    d=json.loads(json.dumps(result))
    for key in ("wall_seconds","environment","source_candidate_sha"): d.pop(key,None)
    return d

def run(data):
    start=time.monotonic();before=sha(canon(data))
    scales={str(cap):run_scale(data,cap) for cap in CAPS}
    old=json.loads((HERE.parent/"NKR-19/result.json").read_text())
    old_score=old["scales"]["24"]["scores"]["native_beta"]["pooled"]
    need(qscore(scales["28"]["arms"]["frozen"])==
         Fraction(old_score["numerator"],old_score["denominator"]),"ORIGINAL_FROZEN_SCORE_DRIFT")
    top=scales["28"]
    gain1=top["error_only_gain_vs_frozen"];gain2=top["error_only_gain_vs_matched_random_mean"]
    passed=(Fraction(gain1["numerator"],gain1["denominator"])>=Fraction(1,200) and
            Fraction(gain2["numerator"],gain2["denominator"])>=Fraction(1,200))
    need(sha(canon(data))==before,"PUBLIC_SOURCE_MUTATION")
    return {"schema":"yggdrasil.nkr29.consumed-feedback-repair.result.v1",
            "classification":"DEV_SELECTIVE_REPAIR_SUPPORTED" if passed else "DEV_SELECTIVE_REPAIR_NO_GO",
            "engineering_contract_pass":True,"scientific_pass":False,"accepted_native":False,
            "source_zip_sha256":source.ZIP_PIN,"source_transition_pins":list(source.PINS),
            "cached_original_events":124,"initial_distinct_training_events":96,
            "feedback_distinct_already_consumed_events":28,"scored_outputs_per_arm":56,
            "new_original_source_actions":0,"fresh_heldout_claim":False,"new_operator_learned":False,
            "native_learned_bytes":128,"native_checkpoint_bytes":164,
            "descending_caps":list(CAPS),"random_seeds":list(RANDOM_SEEDS),"scales":scales,
            "native_vs_exact_control_gain":0,"wall_seconds":time.monotonic()-start}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-zip",required=True);p.add_argument("--output",required=True)
    p.add_argument("--verify-env",action="store_true");args=p.parse_args()
    result=run(source.load_source(args.source_zip))
    result["source_candidate_sha"]=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    result["environment"]={"python":sys.version,"platform":platform.platform()}
    need(result["wall_seconds"]<=120,"AUDIT_TIME_BUDGET")
    result["stable_sha256"]=sha(canon(stable(result)))
    if args.verify_env:
        need(stable(result)==stable(json.loads(os.environ["NKR29_EXPECTED_RESULT"])),"WINDOWS_REPLICATION")
    Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"],"a") as f:
            f.write("result="+json.dumps(result,separators=(",",":"),sort_keys=True)+"\n")
    print("NKR29_ACTUAL_FEEDBACK_REPAIR="+json.dumps(result,sort_keys=True),flush=True)

if __name__=="__main__": main()

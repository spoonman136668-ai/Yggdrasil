"""Evaluator-only nominal-source calibration of frozen native checkpoints.

No training, original source simulation, source oracle given to a learner,
heldout first-use or conversion of analytic expectations into earned rewards.
"""
from __future__ import annotations
import argparse
from fractions import Fraction
import hashlib
import itertools
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT))
from yggdrasil.public_causal_cells import PublicCausalCells
CAPS=(28,14,7)
SOURCE_BLOB="6264ec5450754c009e98c3e85f6d5927ece0a9ab"

def need(ok,reason):
    if not ok: raise ValueError("NKR30_"+reason)

def canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode("ascii")

def sha(raw): return hashlib.sha256(raw).hexdigest()
def qdoc(q): return {"numerator":q.numerator,"denominator":q.denominator,"value":float(q)}
def fraction(d): return Fraction(d["numerator"],d["denominator"])

def kernel():
    weights=((Fraction(1,10),Fraction(9,10)),
             (Fraction(9,10),Fraction(1,10)),
             (Fraction(9,10),Fraction(1,10)))
    answer={}
    for state,action in itertools.product((0,1),repeat=2):
        reward=after=total=Fraction(0)
        for u1,u2,u3 in itertools.product((0,1),repeat=3):
            mass=weights[0][u1]*weights[1][u2]*weights[2][u3]
            y=state^action^u1^u3
            nxt=u1^u2^(state|action)
            reward+=mass*y;after+=mass*nxt;total+=mass
        need(total==1,"KERNEL_MASS")
        answer[state,action]=(reward,after)
    return answer

def risk(p,q):
    need(isinstance(p,Fraction) and isinstance(q,Fraction) and 0<=p<=1 and 0<=q<=1,"PROBABILITY")
    loss=q*(1-p)**2+(1-q)*p**2
    floor=q*(1-q);excess=(p-q)**2
    need(loss==floor+excess,"PROPER_SCORE_IDENTITY")
    return loss,floor,excess

def inspect_checkpoint(checkpoint_hex,expected_sha,nominal):
    need(type(checkpoint_hex) is str and len(checkpoint_hex)==328,"CHECKPOINT_HEX")
    try: raw=bytes.fromhex(checkpoint_hex)
    except ValueError as exc: raise ValueError("NKR30_CHECKPOINT_HEX") from exc
    need(type(expected_sha) is str and sha(raw)==expected_sha,"CHECKPOINT_PIN")
    bank=PublicCausalCells.restore(raw)
    rows=[];losses=[];floors=[];excesses=[];by_target=[[],[]]
    for world,target,state,action in itertools.product(range(4),(0,1),(0,1),(0,1)):
        slot=world*4+target*2+state
        address,retained=(slot-7,True) if slot>=7 else (slot,False)
        p=Fraction(*bank.outcome_probability(address,action,retained=retained))
        q=nominal[state,action][target]
        loss,floor,excess=risk(p,q)
        rows.append([world,target,state,action,p.numerator,p.denominator,q.numerator,q.denominator])
        losses.append(loss);floors.append(floor);excesses.append(excess)
        by_target[target].append(loss)
    need(bank.snapshot()==raw,"EVALUATOR_MUTATED_LEARNED_MEMORY")
    mean=lambda values:sum(values)/len(values)
    return {"checkpoint_sha256":sha(raw),"scored_conditions":32,
            "expected_brier":qdoc(mean(losses)),
            "irreducible_noise_floor":qdoc(mean(floors)),
            "excess_calibration_error":qdoc(mean(excesses)),
            "reward_expected_brier":qdoc(mean(by_target[0])),
            "after_expected_brier":qdoc(mean(by_target[1])),
            "condition_probabilities":rows,"prediction_table_sha256":sha(canon(rows))}

def run():
    start=time.monotonic()
    paths=(HERE.parent/"NKR-23/result.json",HERE.parent/"NKR-29/result.json")
    raw=[p.read_bytes() for p in paths]
    prior,repair=[json.loads(r) for r in raw]
    need(prior["source_blob"]==SOURCE_BLOB and prior["nominal_iid_scm_assumption_explicit"] is True
         and prior["model_learned_source_equations"] is False,"ORIGINAL_NOMINAL_KERNEL_PROVENANCE")
    nominal=kernel()
    need(len(prior["kernel"])==4,"KERNEL_ROWS")
    for row in prior["kernel"]:
        expected=nominal[row["state"],row["action"]]
        need(expected==(fraction(row["reward_probability"]),
                        fraction(row["next_state_one_probability"])),"INDEPENDENT_SOURCE_DERIVATION")
    need(repair["schema"]=="yggdrasil.nkr29.consumed-feedback-repair.result.v1"
         and repair["scientific_pass"] is False and repair["accepted_native"] is False
         and repair["new_original_source_actions"]==0,"FROZEN_REPAIR_RESULT")
    curves={}
    for cap in CAPS:
        source=repair["scales"][str(cap)]
        arms={}
        for name,arm in source["arms"].items():
            arms[name]=inspect_checkpoint(arm["cold_checkpoint_hex"],arm["cold_checkpoint_sha256"],nominal)
            arms[name]["retrospective_events_added"]=arm["updates_events"]
        frozen=fraction(arms["frozen"]["expected_brier"])
        curves[str(cap)]={"arms":arms,
            "error_only_risk_change_vs_frozen":qdoc(fraction(arms["error_only"]["expected_brier"])-frozen),
            "all_feedback_risk_change_vs_frozen":qdoc(fraction(arms["all_feedback"]["expected_brier"])-frozen)}
    widest=curves["28"]
    diagnostic=(fraction(widest["error_only_risk_change_vs_frozen"])>0 and
                fraction(widest["all_feedback_risk_change_vs_frozen"])<=-Fraction(1,1000))
    need(all(p.read_bytes()==old for p,old in zip(paths,raw)),"OLD_EVIDENCE_MUTATED")
    return {"schema":"yggdrasil.nkr30.nominal-feedback-calibration.result.v1",
            "classification":"DIAG_SELECTIVE_CALIBRATION_DAMAGE_SUPPORTED" if diagnostic else "DIAG_MIXED",
            "source_blob":SOURCE_BLOB,"original_kernel_file_sha256":sha(raw[0]),
            "original_feedback_file_sha256":sha(raw[1]),
            "nominal_iid_assumption":True,"uniform_condition_weighting":True,
            "source_equations_available_to_learner":False,"new_training_performed":False,
            "earned_rewards_measured":False,"new_original_source_actions":0,
            "scientific_pass":False,"accepted_native":False,
            "condition_count_per_checkpoint":32,"descending_caps":list(CAPS),
            "curves":curves,"all_old_evidence_unchanged":True,
            "wall_seconds":time.monotonic()-start}

def stable(result):
    d=json.loads(json.dumps(result))
    for k in ("wall_seconds","environment","source_candidate_sha"): d.pop(k,None)
    return d

def main():
    p=argparse.ArgumentParser();p.add_argument("--output",required=True)
    p.add_argument("--verify-env",action="store_true");args=p.parse_args()
    result=run()
    result["source_candidate_sha"]=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    result["environment"]={"python":sys.version,"platform":platform.platform()}
    need(result["wall_seconds"]<=60,"TIME_BUDGET")
    result["stable_sha256"]=sha(canon(stable(result)))
    if args.verify_env:
        need(stable(result)==stable(json.loads(os.environ["NKR30_EXPECTED_RESULT"])),"WINDOWS_DRIFT")
    Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"],"a") as f:
            f.write("result="+json.dumps(result,separators=(",",":"),sort_keys=True)+"\n")
    print("NKR30_NOMINAL_CALIBRATION="+json.dumps(result,sort_keys=True),flush=True)

if __name__=="__main__": main()

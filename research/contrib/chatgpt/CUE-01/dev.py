"""CUE-01 already-exposed NKR-11 mechanical source-only readout evaluation.

This evaluator owns the source oracle, target world identity and independent
symbolic baseline. The native router sees none of them; it sees only a sealed
native memory bank plus true public context-action-consequence observations.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from yggdrasil.native_action_cue_router import ALL_ACTIONS, propose, select
from yggdrasil.native_cumulative_action_bank import NativeCumulativeActionBank
from yggdrasil.native_intervention_repair import (
    NativeInterventionRepair, canonical, digest,
)
from yggdrasil.public_causal_cells import PublicCausalCells

FIXTURE = ROOT / "research/contrib/chatgpt/NKR-11/experiment.py"
_spec = importlib.util.spec_from_file_location("cue01_reused_nkr11_world",FIXTURE)
study = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(study)
LIMIT = 8
UNKNOWN_MASKS = (3,5,6,9)


def slotaddress(slot):
    return (slot,False) if slot < 7 else (slot-7,True)


def build_bank():
    bank = NativeCumulativeActionBank()
    refs = {}
    source = []
    for wid in range(12):
        env = study.ComputationalEnvironment(wid)
        old = study.collect_warmup(env)
        warm = study.evidence(f"warm-bundle-world-{wid:02d}",old)
        x, retained = slotaddress(wid)
        bank,_ = bank.install_public(x,warm,digest(warm),retained=retained)
        separate = NativeInterventionRepair.from_warmup(warm,digest(warm))
        rows = study.collect_paired_interventions(env)
        changed = study.evidence(f"repair-bundle-world-{wid:02d}",rows)
        bank,_ = bank.repair_public(x,changed,digest(changed),retained=retained)
        separate,_ = separate.stage_public_interventions(changed,digest(changed))
        refs[wid] = separate
        source.extend([[wid,"warm",old],[wid,"repair",rows]])
    return bank,refs,digest(canonical(source))


def _prediction(ref,slot,x,a):
    return ref[slot].predict(x,a)["public_outcome"]


def symbolic_decide(models,cues):
    """Independent exact-enumeration equality control, no router import."""
    remain=[]
    for s,model in sorted(models.items()):
        wrong=False; unknown=False
        for x,a,y in cues:
            predicted=model.predict(x,a)["public_outcome"]
            if predicted is None:
                unknown=True
            elif predicted!=y:
                wrong=True;break
        if not wrong:remain.append((s,unknown))
    if len(remain)==1 and len(cues)>=4 and not remain[0][1]:
        return remain[0][0],tuple(s for s,_ in remain)
    return None,tuple(s for s,_ in remain)


def symbolic_query(models,cues):
    """Separate, independently written exhaustive balanced-partition policy."""
    _,remain=symbolic_decide(models,cues)
    if not remain or len(cues)>=LIMIT:return None
    seen={(x,a) for x,a,_ in cues}
    options=[]
    for x,a in ALL_ACTIONS:
        if (x,a) in seen:continue
        vals=[_prediction(models,s,x,a) for s in remain]
        if len(remain)>1:
            split=min(vals.count(0),vals.count(1))
            score=(split,len(vals)-vals.count(None),-vals.count(None))
        else:
            trueval=vals[0]
            contradictions=(sum(int(_prediction(models,s,x,a)!=trueval)
                                for s in models if s not in remain
                                and _prediction(models,s,x,a) is not None)
                            if trueval is not None else 0)
            score=(contradictions,int(trueval is not None),-vals.count(None))
        options.append((score,x,a))
    if not options:return None
    maximum=max(v for v,_,_ in options)
    if len(remain)>1 and maximum[0]==0:return None
    return min((x,a) for score,x,a in options if score==maximum)


def fixed_actions():
    return ALL_ACTIONS[:LIMIT]


def random_actions():
    return tuple(sorted(ALL_ACTIONS,key=lambda t:(
        hashlib.sha256(f"CUE01|fixed-random-policy|{t[0]}|{t[1]}".encode("ascii")).digest(),t
    )))[:LIMIT]


def evaluate_one(bank,refs,outcome,policy):
    cues=[];before=bank.checkpoint()
    for index in range(LIMIT):
        if policy=="active":
            proposed=propose(bank,cues)
            if proposed["context"] is None:break
            x,a=proposed["context"],proposed["action"]
        elif policy=="strong_symbolic":
            action=symbolic_query(refs,cues)
            if action is None:break
            x,a=action
        elif policy=="fixed":
            x,a=fixed_actions()[index]
        elif policy=="random":
            x,a=random_actions()[index]
        else:raise ValueError("Unknown arm")
        observation=outcome(x,a) # Actual public environment action.
        cues.append((x,a,observation))
    if policy=="strong_symbolic":
        chosen,remain=symbolic_decide(refs,cues)
        classification="PROVISIONAL_UNVERIFIED_SLOT_MATCH" if chosen is not None else "ABSTAIN"
    else:
        decision=select(bank,cues)
        chosen=decision["provisional_slot"]
        remain=tuple(decision["remaining_slots"])
        classification=decision["classification"]
        if decision["native_accepted"] or decision["scientific_pass"]:
            raise AssertionError("No scientific or native promotion is permitted")
    if bank.checkpoint()!=before:
        raise AssertionError("Read-only retrieval changed stored native bytes")
    return {"slot":chosen,"remaining":list(remain),"classification":classification,
            "actions_used":len(cues),"public_cues":[list(t) for t in cues],
            "native_accepted":False}


def unknown_outcome(index,x,a):
    base=(x&(1<<(index%4))).bit_count()&1
    interaction=int((x&UNKNOWN_MASKS[index])==UNKNOWN_MASKS[index])
    return base ^ (a&interaction)


def run():
    t0=time.perf_counter()
    bank,refs,source_digest=build_bank()
    before=bank.checkpoint()
    bank=NativeCumulativeActionBank.restore(before,bank.checkpoint_sha256)
    methods=("active","strong_symbolic","fixed","random")
    metrics={m:{"correct":0,"wrong":0,"abstained":0,"probes":0,
                "per_world":[]} for m in methods}
    traces=[]
    for target in range(12):
        for method in methods:
            env=study.ComputationalEnvironment(target)
            r=evaluate_one(bank,refs,env.intervene,method)
            chosen=r["slot"]
            metrics[method]["correct"]+=int(chosen==target)
            metrics[method]["wrong"]+=int(chosen is not None and chosen!=target)
            metrics[method]["abstained"]+=int(chosen is None)
            metrics[method]["probes"]+=r["actions_used"]
            metrics[method]["per_world"].append(r["actions_used"])
            traces.append(["known",target,method,r])
    negative={"source_worlds":len(UNKNOWN_MASKS),"provisional_false_matches":0,
              "abstained":0,"probes":0,"native_acceptances":0}
    for i in range(len(UNKNOWN_MASKS)):
        r=evaluate_one(bank,refs,lambda x,a:unknown_outcome(i,x,a),"active")
        negative["provisional_false_matches"]+=int(r["slot"] is not None)
        negative["abstained"]+=int(r["slot"] is None)
        negative["probes"]+=r["actions_used"]
        negative["native_acceptances"]+=int(r["native_accepted"])
        traces.append(["unknown",i,"active",r])
    controls_equal=(metrics["active"]==metrics["strong_symbolic"])
    correct=metrics["active"]["correct"]
    gates={
        "known_public_cue_identity_at_least_10_of_12":correct>=10,
        "no_wrong_provisional_old_world_slot":metrics["active"]["wrong"]==0,
        "all_known_and_unknown_budget_at_most_8":
            all(max(m["per_world"])<=LIMIT for m in metrics.values()) and
            negative["probes"]<=4*LIMIT,
        "exact_same_results_as_independent_strong_symbolic":controls_equal,
        "provisional_never_accepted":negative["native_acceptances"]==0,
        "native_checkpoint_unchanged":bank.checkpoint()==before,
        "no_scientific_firstuse":True,
    }
    return {
       "schema":"yggdrasil.cue01.sourceonly-development-result.v1",
       "classification":("ENGINEERING_DEV_PASS_SCIENCE_UNVERIFIED"
                         if all(gates.values()) else "ENGINEERING_DEV_NO_GO_NO_SCIENCE"),
       "known_worlds":12, "negative_out_of_family_worlds":4,
       "max_paid_public_probes_per_episode":LIMIT,
       "policies":metrics, "out_of_family_negative":negative,
       "frozen_gates":gates,"cold_native_bank_checkpoint_bytes":bank.checkpoint_bytes,
       "cold_native_bank_sha256":bank.checkpoint_sha256,
       "native_memory_unchanged":bank.checkpoint()==before,
       "source_public_sha256":source_digest,
       "trace_sha256":digest(canonical(traces)),
       "source_realness":"PREVIOUSLY_EXPOSED_SYNTHETIC_FIXTURE_ONLY",
       "scientific_first_use_consumed":0,"accepted_native_changed":False,
       "elapsed_seconds":round(time.perf_counter()-t0,6),
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-dev",action="store_true")
    p.add_argument("--primary",action="store_true")
    args=p.parse_args()
    if args.primary:p.error("CUE01 SCIENTIFIC FIRST USE DISARMED")
    if not args.source_dev:p.error("Only --source-dev is eligible")
    print("CUE01_DEV="+json.dumps(run(),sort_keys=True),flush=True)


if __name__=="__main__":main()

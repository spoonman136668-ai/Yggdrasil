"""WSP135 source-safe diagnostic: 32-query exact oracle identifiability.

An upper bound with grammar SUPPLIED to oracle. Not a trained native model,
not novel-operator discovery, not independent scientific first-use.
"""
from hashlib import sha256
import json
import random
import time
import tracemalloc
import source as S
import oracle as O
import controls as C

ARMS=("ADAPTIVE_ORACLE","FIXED32_ORACLE","RANDOM32_ORACLE","NO_UPDATE")
GROUPS=("known","unfamiliar")
FIELDS=("correct","wrong_confident","abstained","held","source_calls")

def score_blank():
    return {group:{arm:{f:0 for f in FIELDS} for arm in ARMS} for group in GROUPS}
def total(dst,part):
    for k in FIELDS:dst[k]+=part[k]
def _policy_random(view):
    key="WSP135|PUBLIC_POLICY|"+str(view.law_id)
    rng=random.Random(int.from_bytes(sha256(key.encode()).digest(),"big"))
    return rng.sample(range(64),32)
def run_development():
    wall=time.perf_counter()
    cpu=time.process_time()
    tracemalloc.start()
    if S.ALLOWED & S.PROTECTED:raise AssertionError("WSP135_PROTECTED_COHORT_OVERLAP")
    candidates=O.candidate_bank()
    independent=C.independent_bank()
    if candidates!=independent:raise AssertionError("WSP135_ORACLE_INDEPENDENT_BANK_MISMATCH")
    oracle=O.ExactOracle(candidates)
    bank_set=set(candidates)
    score=score_blank()
    survivors={group:{a:[] for a in ARMS if a!="NO_UPDATE"} for group in GROUPS}
    transcripts=[]
    predictions=[]
    true_law_membership=0
    for seed in (*range(178000,178064),*range(179000,179032)):
        v=S.world(seed)
        condition=v.cohort
        if condition not in GROUPS or len(v.legal)!=64 or len(v.records)!=64:
            raise AssertionError("WSP135_INVALID_PUBLIC_ACTIONS")
        random_schedule=_policy_random(v)
        custodians={a:S.Custodian(v,seed) for a in ARMS}
        states={a:oracle.begin() for a in ARMS if a!="NO_UPDATE"}
        outcome={}
        held_preds={}
        for arm in ARMS:
            cu=custodians[arm]
            state=states.get(arm)
            for step in range(32):
                if arm=="ADAPTIVE_ORACLE":x=state.adaptive_action()
                elif arm=="RANDOM32_ORACLE":x=random_schedule[step]
                else:x=step
                if type(x) is not int or not 0<=x<64:
                    raise AssertionError("WSP135_INVALID_ACTION_POLICY")
                e=cu.query(v.subject(x))
                if state is not None:state.observe(x,e.effect)
            if state is not None:
                if state.restore().snapshot()!=state.snapshot():
                    raise AssertionError("WSP135_COLD_VERSION_SPACE_DRIFT")
                if state.alive==0:raise AssertionError("WSP135_SOURCE_NOT_IN_GENERAL_GRAMMAR")
            held=cu.held()
            if len(held)!=32 or len(cu.events)!=32:
                raise AssertionError("WSP135_ACTIONS_NOT_EXACTLY_32")
            pred={subject:(state.infer(x) if state is not None else None)
                  for subject,x in held}
            held_preds[arm]=pred
            outcome[arm]=cu.score_once(pred)
            total(score[condition][arm],outcome[arm])
            if state is not None:survivors[condition][arm].append(state.alive.bit_count())
        # Source/evaluator-only membership check AFTER 32 actions and scores.
        truth=S._truth(seed)
        truthword=sum(z<<x for x,z in enumerate(truth))
        if truthword not in bank_set:
            raise AssertionError("WSP135_TRUE_CAUSAL_LAW_NOT_IN_ORACLE_GRAMMAR")
        true_law_membership+=1
        if any(outcome[a]["wrong_confident"] for a in ARMS if a!="NO_UPDATE"):
            raise AssertionError("WSP135_SOURCE_INFORMED_ORACLE_FALSE_CONFIDENCE")
        transcripts.append([seed,condition,[[a,custodians[a].receipt,
                             [[ev[2],ev[3]] for ev in custodians[a].events]]
                              for a in ARMS]])
        predictions.append([seed,condition,[[a,outcome[a]] for a in ARMS]])
    known=score["known"]["ADAPTIVE_ORACLE"]
    unfamiliar=score["unfamiliar"]["ADAPTIVE_ORACLE"]
    identifiable=(known["correct"]*100>=95*2048
                  and unfamiliar["correct"]*100>=95*1024
                  and not known["wrong_confident"]
                  and not unfamiliar["wrong_confident"]
                  and true_law_membership==96)
    other=max(score["unfamiliar"]["FIXED32_ORACLE"]["correct"],
              score["unfamiliar"]["RANDOM32_ORACLE"]["correct"])
    gain=100*(unfamiliar["correct"]-other)/1024
    active_value=gain>=5
    _,peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
      "schema":"wsp135.identifiability-public-dev-result.v1",
      "status":"IDENTIFIABLE_WITH_GIVEN_GRAMMAR" if identifiable else "UNDERIDENTIFIED_WITH_GIVEN_GRAMMAR",
      "active_policy_gain_pass":active_value,
      "active_policy_gain_pp_over_strongest_fixed_random":gain,
      "scientific_pass":False,"native_admission":False,"original_first_use":False,
      "source_safe_only":True,"source_grammar_given_to_oracle":True,
      "source_true_law_membership_count":true_law_membership,
      "source_worlds":{"known":64,"unfamiliar":32},
      "source_calls_per_world_arm":32,
      "oracle_unique_truth_tables":len(candidates),
      "independent_oracle_bank_match":True,
      "oracle_bank_sha256":oracle.bank_hash,
      "scores":score,
      "survivor_counts":survivors,
      "action_transcript_sha256":S.digest(transcripts),
      "score_sha256":S.digest(predictions),
      "resource":{"whole_process_cpu_seconds":round(time.process_time()-cpu,3),
                  "whole_process_wall_seconds":round(time.perf_counter()-wall,3),
                  "tracemalloc_peak_bytes":peak,
                  "energy":"UNQUALIFIED"},
      "interpretation":"The oracle has the complete general source grammar; this diagnoses information sufficiency under that strong prior ONLY and cannot establish direct-weight learning, novel unsupplied primitives, real causal grounding, or AGI."
    }
if __name__=="__main__":
    print("WSP135_SOURCE_SAFE_JSON="+S.canonical(run_development()))

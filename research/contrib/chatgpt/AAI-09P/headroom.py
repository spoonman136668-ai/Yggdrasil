"""AAI-09P: exact benchmark headroom from public official NS-Gym Bridge mechanics.

ANALYTIC ONLY: never samples science worlds, trains a model, or accesses
private env state. Known-law Bayesian oracle is a privileged *upper-bound*
design diagnostic, not a matched-information learner.
Preregistration: f19dd32f20bf05ae5e72fc913303843050a9217d.
"""
from __future__ import annotations

import hashlib
import json
import math
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREREG_SHA = "f19dd32f20bf05ae5e72fc913303843050a9217d"
UPSTREAM_SHA = "127df4b714fe4fcf680721d8e9278a96090acd7e"
MAP = ("HHHHHHHH", "FFFFFHHH", "GFHFSFFG", "FFFFFHHH", "HHHHHHHH")
ACTION_STEPS = {0:(0,-1), 1:(1,0), 2:(0,1), 3:(-1,0)}
ACTIONS = {"RIGHT":2, "UP":3}
LAWS = {
    "dev":{"A":(.94,.035,.025), "B":(.03,.49,.48)},
    "transfer":{"A":(.90,.06,.04), "B":(.05,.47,.48)},
}
PRIOR_RETURN = .2
BUDGETS = (0,1,2,4)
CHECK_BUDGETS = (2,4)

def published_transition(row,col,action):
    """Independent, literal 5x8 public map. Not the simulator's private state."""
    dr,dc=ACTION_STEPS[action]
    r,c=row+dr,col+dc
    if not 0<=r<len(MAP) or not 0<=c<len(MAP[0]):
        r,c=row,col
    tile=MAP[r][c]
    return (r,c,1 if tile=="G" else -1 if tile=="H" else 0)

def source_basis():
    assert MAP[2][4]=="S"
    row,col=2,4
    for a in (2,0,2):
        row,col,reward=published_transition(row,col,a)
        assert reward==0
    assert (row,col)==(2,5)
    data={}
    for label,a in ACTIONS.items():
        outcomes=[published_transition(row,col,k)
                  for k in (a,(a+1)%4,(a-1)%4)]
        data[label]={
            "states":[r*len(MAP[0])+c for r,c,_ in outcomes],
            "rewards":[v for _,_,v in outcomes],
        }
    assert data["RIGHT"]["rewards"]==[0,-1,-1]
    assert data["UP"]["rewards"]==[-1,0,0]
    return data

def binomial_mass(n,k,p):
    return comb(n,k)*p**k*(1-p)**(n-k)

def posterior(n,k,p_a,p_b,prior=PRIOR_RETURN):
    likelihood_a=binomial_mass(n,k,p_a)
    likelihood_b=binomial_mass(n,k,p_b)
    combined=prior*likelihood_a+(1-prior)*likelihood_b
    assert combined>0
    return prior*likelihood_a/combined

def oracle_right(n,k,p_a,p_b,prior=PRIOR_RETURN):
    q=posterior(n,k,p_a,p_b,prior)
    expected_p=q*p_a+(1-q)*p_b
    return expected_p>=.5

def exact_condition(n,p_condition,p_a,p_b,prior=PRIOR_RETURN):
    p_right=sum(binomial_mass(n,k,p_condition)
                for k in range(n+1) if oracle_right(n,k,p_a,p_b,prior))
    # Official map: right -> -1+p; up -> -p. Both are actual expected reward.
    reward=p_right*(-1+p_condition)+(1-p_right)*(-p_condition)
    return {
        "n":n,
        "choose_right_prob":round(p_right,12),
        "expected_official_reward":round(reward,12),
        "correct_decision_probability":round(p_right if p_condition==p_a else 1-p_right,12),
    }

def total_variation_binomial(n,p_a,p_b):
    return .5*sum(abs(binomial_mass(n,k,p_a)-binomial_mass(n,k,p_b))
                  for k in range(n+1))

def inspect_exact():
    basis=source_basis()
    detail={}
    checks={}
    for split,law in LAWS.items():
        p_a=law["A"][0]
        p_b=law["B"][0]
        for name,P in law.items():
            assert len(P)==3 and all(x>=0 for x in P) and math.isclose(sum(P),1,abs_tol=1e-12)
        assert p_a>.5>p_b
        out={"laws":{"A":list(law["A"]),"B":list(law["B"])},
             "action_margin":{"A":round(2*p_a-1,12),"B":round(1-2*p_b,12)},
             "oracle_prior_return":PRIOR_RETURN,"budgets":{}}
        for n in BUDGETS:
            a=exact_condition(n,p_a,p_a,p_b)
            b=exact_condition(n,p_b,p_a,p_b)
            out["budgets"][str(n)]={
                "return_A":a,"hold_B":b,
                "total_variation_forward_evidence":round(total_variation_binomial(n,p_a,p_b),12),
                "Bayes_action_by_forward_count":["RIGHT" if oracle_right(n,k,p_a,p_b) else "UP"
                                                 for k in range(n+1)]
            }
        out["zero_probe_same_action"]=(
            out["budgets"]["0"]["return_A"]["choose_right_prob"]==
            out["budgets"]["0"]["hold_B"]["choose_right_prob"])
        for n in CHECK_BUDGETS:
            now=out["budgets"][str(n)]
            baseline=out["budgets"]["0"]
            gain=now["return_A"]["expected_official_reward"]-baseline["return_A"]["expected_official_reward"]
            hold_loss=baseline["hold_B"]["expected_official_reward"]-now["hold_B"]["expected_official_reward"]
            out[f"n{n}_return_gain"]=round(gain,12)
            out[f"n{n}_hold_loss"]=round(hold_loss,12)
            checks[f"{split}_return_gain_n{n}"]=gain>=.20
            checks[f"{split}_hold_loss_n{n}"]=hold_loss<=.02
            checks[f"{split}_normalization_n{n}"]=all(
                math.isclose(sum(binomial_mass(n,k,p) for k in range(n+1)),1,abs_tol=1e-12)
                for p in (p_a,p_b))
        checks[f"{split}_action_utility_margin"]=min(2*p_a-1,1-2*p_b)>=.20
        checks[f"{split}_zero_probe_nonidentifiable"]=out["zero_probe_same_action"]
        checks[f"{split}_onehot_geometry"]=basis["RIGHT"]["rewards"]==[0,-1,-1] and basis["UP"]["rewards"]==[-1,0,0]
        detail[split]=out
    checks["no_first_use_science"]=True
    result={
        "schema":"yggdrasil.contrib.aai09p.analytic-headroom.v1",
        "prereg_sha":PREREG_SHA,
        "upstream_source_sha":UPSTREAM_SHA,
        "worlds_executed":0,
        "scientific_first_use":False,
        "method":"EXACT_BINOMIAL_ENUMERATION_NOT_LEARNER_EXPERIMENT",
        "published_map_geometry":basis,
        "splits":detail,
        "checks":checks,
        "analytic_classification":("ANALYTIC_HEADROOM_PASS_PENDING_OFFICIAL_SOURCE"
                                  if all(checks.values()) else "HEADROOM_REJECTED"),
        "science_claim":"NONE. Oracle has privileged true A/B likelihoods and selected prior; no learned model, transfer, novelty or AGI shown.",
    }
    return result

def deterministic_bytes(data):
    return (json.dumps(data,sort_keys=True,separators=(",",":"))+"\n").encode("utf-8")

if __name__=="__main__":
    data=inspect_exact()
    raw=deterministic_bytes(data)
    print("AAI09P_ANALYTIC_SHA256="+hashlib.sha256(raw).hexdigest())
    print(json.dumps(data,indent=2,sort_keys=True))
    if not all(data["checks"].values()):
        raise SystemExit(2)

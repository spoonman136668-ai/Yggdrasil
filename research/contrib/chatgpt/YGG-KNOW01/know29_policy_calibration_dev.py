"""KNOW29: prospective source-only prior calibration of myopic EVI vs entropy.

Protocol FIRST at a0b3c666cb9573aa62cbf32a66e960f7ad342d5c.
Do not run proof in focused tests. No native or protected original-world actions.
"""
from __future__ import annotations
import hashlib, json, math, random, time
from pathlib import Path
from unknown_action_affordance_dev import (
    ALL_MAPS, JointHypothesis, Passive, fit_source,
    digest, expected_brier, P_TRUE, P_FALSE)
from know27_online_action_policy_dev import COST, choose, expected_variance_reduction

SCHEMA="yggdrasil.know29.policy-prior-calibration-result.dev.v1"
PROTO="yggdrasil.know29.policy-prior-calibration-prospective-dev.v1"
PREREG="a0b3c666cb9573aa62cbf32a66e960f7ad342d5c"
PREREG_BLOB="4dc40db53b7f2e8a4db38fd58912b7df7c47000d"
MODE="engineering_fixture_only"
MATCH=(15011,15017,15023,15029,15031,15037,15041,15047)
SHIFT=(15101,15107,15113,15121,15127,15131,15139,15149)
COHORTS=("model_prior_matched","structured_shift")
ARMS=("fit_evi","fit_entropy","nofit_entropy","fit_cyclic","fit_random",
      "privileged_known_map_entropy","passive_p05")
N=32
PREFIX="know29:private:"

def require(ok,tag):
    if not ok: raise ValueError("YGG_KNOW29_"+tag)

def protocol():
    raw=Path(__file__).with_name("know29_policy_calibration_protocol.json").read_bytes()
    blob=hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")+b"\0"+raw).hexdigest()
    require(blob==PREREG_BLOB,"FROZEN_PREREG")
    p=json.loads(raw)
    require(p["schema"]==PROTO and
            p["worlds"]["cohorts"]["model_prior_matched"]["seeds"]==list(MATCH)
            and p["worlds"]["cohorts"]["structured_shift"]["seeds"]==list(SHIFT)
            and p["worlds"]["actions_per_policy_per_cohort"]==768
            and p["authority"]["source_mode"]==MODE
            and p["first_use"].startswith("Only new synthetic HELD"),
            "PROTOCOL_DRIFT")
    return p

def bits_shift(k,c):
    require(type(k) is int and k in range(4) and
            type(c) is int and c in range(8),"SHIFT")
    x0,x1,x2=c&1,(c>>1)&1,(c>>2)&1
    return (x0^(x1|x2),x2^(x0&x1),((1^x0)&x1)^x2,(x0|x1)&x2)[k]

def source_identity(cohort,mid,seed):
    require(cohort in COHORTS and type(mid) is int and mid in range(3)
            and type(seed) is int and
            seed in (MATCH if cohort==COHORTS[0] else SHIFT),"HELD_IDENTITY")

def hash8(text):
    require(type(text) is str and text.startswith(PREFIX),"HASH_DOMAIN")
    return int.from_bytes(hashlib.sha256(text.encode("ascii")).digest()[:8],"big")

def private_world(cohort,mid,seed,prior):
    """Evaluator only: no mapping or law enters public policy interface."""
    source_identity(cohort,mid,seed)
    require(type(prior) is list and len(prior)==6
            and all(type(x) is float and 0<x<1 for x in prior)
            and abs(sum(prior)-1)<1e-10,"MAP_PRIOR")
    idx=(MATCH if cohort==COHORTS[0] else SHIFT).index(seed)
    r=hash8(f"{PREFIX}map:v1:{mid}:{idx}")/(1<<64)
    cumul=0.; mapidx=5
    for j,p in enumerate(prior):
        cumul+=p
        if r<cumul: mapidx=j; break
    if cohort=="model_prior_matched":
        law=hash8(f"{PREFIX}law:v1:{mid}:{seed}")%256
    else:
        law=sum(bits_shift(idx%4,c)<<c for c in range(8))
    return mapidx,law

def witnessed(cohort,mid,seed,t,a,private,*,mode=MODE):
    source_identity(cohort,mid,seed)
    require(mode==MODE and type(t) is int and t in range(N)
            and type(a) is int and a in range(4)
            and type(private) is tuple and len(private)==2
            and type(private[0]) is int and private[0] in range(6)
            and type(private[1]) is int and 0<=private[1]<256,
            "ONE_WITNESSED_ACTION")
    mapidx,law=private
    target=(t%4)^ALL_MAPS[mapidx][a]
    q=P_TRUE if (law>>target)&1 else P_FALSE
    return int(hash8(f"{PREFIX}coin:v1:{cohort}:{mid}:{seed}:{t}")/(1<<64)<q)

def model_for(arm,prior,private=None):
    require(arm in ARMS and type(prior) is list and len(prior)==6,"MODEL_ARM")
    if arm=="privileged_known_map_entropy":
        require(type(private) is tuple and len(private)==2,"PRIVILEGED_MAPPING")
        idx=private[0]
        p=[0.]*6;p[idx]=1.
        return JointHypothesis(p,allowed=(idx,))
    require(private is None,"PRIVILEGED_LEAK")
    if arm=="passive_p05":return Passive()
    return JointHypothesis([1/6.]*6 if arm=="nofit_entropy" else prior)

def public_choice(arm,m,c,t,rng):
    require(arm in ARMS and type(c) is int and c in range(4)
            and type(t) is int and t in range(N),"POLICY_SOURCE")
    if arm=="passive_p05":return 0
    if arm in ("fit_entropy","nofit_entropy","privileged_known_map_entropy"):
        return choose("fit_entropy",m,c,t)
    if arm=="fit_evi":return choose("fit_evi",m,c,t)
    if arm=="fit_cyclic":return choose("fit_cyclic",m,c,t)
    require(arm=="fit_random" and isinstance(rng,random.Random),"RANDOM_SOURCE")
    return choose("fit_random",m,c,t,rng=rng)

def myopic_identity(prior):
    """Independent two-outcome EVI calculation without held source."""
    m=JointHypothesis(list(prior)); maxerr=0.; n=0
    for _ in range(2):
        t=len(m.events);c=t%4
        old=[m.prob(j,0) for j in range(4,8)]
        implementation=expected_variance_reduction(m,c)
        frozen=m.checkpoint();frozen_hash=digest(frozen)
        for action in range(4):
            py=m.prob(c,action); predicted=[]
            for y in (0,1):
                child=JointHypothesis.restore(frozen,frozen_hash)
                child.observe(t,c,action,y)
                predicted.append([child.prob(j,0) for j in range(4,8)])
            expected=sum(
                py*(predicted[1][j]-old[j])**2+
                (1-py)*(predicted[0][j]-old[j])**2
                for j in range(4))/4-(COST if action else 0)
            maxerr=max(maxerr,abs(expected-implementation[action]));n+=1
        m.observe(t,c,0,1)
    require(n==8 and maxerr<=1e-10,"MYOPIC_IDENTITY")
    return {"action_cases":n,"max_abs_error":maxerr}

def run_world(cohort,mid,seed,arm,prior,public_index):
    require(arm in ARMS and type(public_index) is int
            and public_index>=0,"WORLD_POLICY")
    private=private_world(cohort,mid,seed,prior)
    m=model_for(arm,prior,private if arm=="privileged_known_map_entropy" else None)
    rng=random.Random(271828+101*public_index)
    actions=[]
    for t in range(N):
        c=t%4
        a=public_choice(arm,m,c,t,rng)
        y=witnessed(cohort,mid,seed,t,a,private)
        m.observe(t,c,a,y)
        actions.append(a)
    raw=m.checkpoint()
    if isinstance(m,JointHypothesis):
        cold=JointHypothesis.restore(raw,digest(raw))
        require(cold.checkpoint()==raw and
                [cold.prob(c,0) for c in range(4,8)]==
                [m.prob(c,0) for c in range(4,8)],"COLD_FUNCTIONAL")
    law=private[1]
    high=sum(expected_brier(m.prob(c,0),
             P_TRUE if (law>>c)&1 else P_FALSE)
             for c in range(4,8))/4
    active=sum(a!=0 for a in actions)
    require(len(actions)==N and 0<=high<=1 and math.isfinite(high),"BUDGET")
    return {"high":high,"net":high+COST*active/N,"active":active,"bytes":len(raw)}

def proof():
    t0=time.monotonic()
    protocol()
    fitted={};history={}
    for mid in range(3):
        prior,archived=fit_source(mid)
        fitted[mid]=prior
        history[mid]=[(r["raw"],r["source_sha"],r["readout_high"]) for r in archived]
    identity=myopic_identity(fitted[0])
    metrics={}
    for ci,cohort in enumerate(COHORTS):
        seeds=MATCH if ci==0 else SHIFT
        policies={}
        for arm in ARMS:
            rows=[(mid,run_world(cohort,mid,seed,arm,fitted[mid],
                                ci*24+mid*8+si))
                  for mid in range(3) for si,seed in enumerate(seeds)]
            require(len(rows)==24,"HELD_COUNT")
            avg=lambda name:sum(v[name] for _,v in rows)/24
            policies[arm]={
                "high_expected_brier":round(avg("high"),8),
                "net_high_brier":round(avg("net"),8),
                "actions_per_policy":24*N,
                "total_active":sum(v["active"] for _,v in rows),
                "average_checkpoint_bytes":round(avg("bytes"),2),
                "per_map_group_net_high_brier":[round(
                    sum(v["net"] for i,v in rows if i==mid)/8,8)
                    for mid in range(3)]
            }
        metrics[cohort]=policies
    for mid,archive in history.items():
        require(len(archive)==3,"HISTORICAL_FIT")
        for raw,sha,old in archive:
            cold=JointHypothesis.restore(raw,sha)
            require(cold.checkpoint()==raw and
                    [cold.prob(c,0) for c in range(4,8)]==old,
                    "OLD_FIT_READOUT_CHANGED")
    match=metrics["model_prior_matched"]
    shift=metrics["structured_shift"]
    matched_gain=round(match["fit_entropy"]["net_high_brier"]-
                       match["fit_evi"]["net_high_brier"],8)
    shifted_gain=round(shift["fit_evi"]["net_high_brier"]-
                       shift["fit_entropy"]["net_high_brier"],8)
    h={
      "H1_myopic_utility_identity":identity["max_abs_error"]<=1e-10,
      "H2_prior_matched_evi_gain_005":matched_gain>=.005,
      "H3_structured_shift_entropy_gain_005":shifted_gain>=.005,
      "H4_fairness_cost_custody":all(
          metrics[cohort][arm]["actions_per_policy"]==768
          for cohort in COHORTS for arm in ARMS)
    }
    hit=int(h["H2_prior_matched_evi_gain_005"])+int(h["H3_structured_shift_entropy_gain_005"])
    return {
      "schema":SCHEMA,"prereg_commit":PREREG,"prereg_blob":PREREG_BLOB,
      "source_mode":MODE,"fit_actions_per_map_group":108,
      "synthetic_worlds_per_cohort":24,"actions_per_policy_per_cohort":768,
      "high_eval_queries_per_policy_per_cohort":96,
      "metrics":metrics,"math_control":identity,"frozen_hypotheses":h,
      "prior_matched_evi_net_gain":matched_gain,
      "structured_shift_entropy_net_gain":shifted_gain,
      "development_verdict":(
          "MECHANISM_CALIBRATION_SUPPORTED_DEV" if all(h.values())
          else "MIXED_CALIBRATION_DEV" if hit else "CALIBRATION_DEV_NO_GO"),
      "engineering_gate":"SOURCE_ONLY_CHECKS_PASSED",
      "scientific_gate":"SCIENCE_NO_GO_SYNTHETIC_NOT_NATIVE",
      "accepted_native_modified":False,"original_first_use_426":False,
      "deployment":"NONE","isolated_wall_seconds":round(time.monotonic()-t0,6)
    }

if __name__=="__main__":
    print(json.dumps(proof(),sort_keys=True))

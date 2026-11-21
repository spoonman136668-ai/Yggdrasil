"""KNOW30: preregistered source-blind receding two-step causal interventions.

Frozen protocol Git SHA effc0078a561fcc7c5a2584c95f75a97388a1ae5.
Only a dedicated post-regression GitHub job may call proof() and consume new
synthetic HELD observations. Unit tests use math-only fabricated posteriors.
Nothing touches Yggdrasil native checkpoints or protected #426 first use.
"""
from __future__ import annotations
import copy
import hashlib
import json
import math
import random
import time
from pathlib import Path

from unknown_action_affordance_dev import (
    ALL_MAPS, JointHypothesis, fit_source, digest,
    P_TRUE, P_FALSE, expected_brier,
)
from know27_online_action_policy_dev import COST, choose, expected_variance_reduction

SCHEMA="yggdrasil.know30.two-step-policy-result.dev.v1"
PROTO="yggdrasil.know30.receding-two-step-vs-entropy-frozen-dev.v1"
PREREG="effc0078a561fcc7c5a2584c95f75a97388a1ae5"
PREREG_BLOB="bd804e6a94debb4b314d9d6a86af179bb44de1a2"
MODE="engineering_fixture_only"
MATCH=(16011,16017,16019,16021,16027,16033)
SHIFT=(16111,16117,16121,16127,16139,16141)
COHORTS=("prior_matched","structured_shift")
ARMS=("fit_lookahead2","fit_entropy_compute_matched",
      "fit_entropy_fast","fit_myopic_evi","fit_cyclic",
      "fit_random","nofit_entropy","privileged_correct_map_entropy")
N=32
DOMAIN="know30:private:"

def require(ok,tag):
    if not ok: raise ValueError("YGG_KNOW30_"+tag)

def protocol():
    raw=Path(__file__).with_name("know30_two_step_planning_protocol.json").read_bytes()
    blob=hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")+b"\0"+raw).hexdigest()
    require(blob==PREREG_BLOB,"PREREG_BLOB")
    d=json.loads(raw)
    require(d["schema"]==PROTO and
            d["held"]["prior_matched"]["seeds"]==list(MATCH)
            and d["held"]["structured_shift"]["seeds"]==list(SHIFT)
            and d["held"]["actions_per_arm_per_cohort"]==576
            and d["held"]["high_scorer_queries_per_arm_per_cohort"]==72
            and d["held"]["cost_per_nonzero_action"]==COST
            and d["provenance"]["original_first_use_426"] is False
            and d["first_use"].startswith("No newly reserved cohorts"),
            "FROZEN_PROTOCOL")
    return d

def high_uncertainty(model):
    """Posterior expected next Bernoulli Brier, NOT hidden held score."""
    require(isinstance(model,JointHypothesis),"POSTERIOR")
    high=[model.prob(c,0) for c in range(4,8)]
    return sum(p*(1-p) for p in high)/4

def clone_hypothesis(model,t,c,a,y):
    """A counterfactual disposable *model* updated with an imagined outcome.
    No simulator/source/evaluator oracle is read by the planner.
    """
    require(isinstance(model,JointHypothesis) and type(t) is int
            and t==len(model.events) and 0<=t<N
            and c==t%4 and type(a) is int and a in range(4)
            and type(y) is int and y in (0,1),"HYPOTHETICAL_UPDATE")
    child=copy.deepcopy(model)
    child.observe(t,c,a,y)
    require(len(model.events)==t and len(child.events)==t+1,
            "NO_HYPOTHETICAL_LEAK")
    return child

def horizon2_values(model,t):
    """Exact Bellman expected terminal posterior-Brier reduction, net costs.

    First action gain = existing verified myopic EVI. Its two possible
    witnessed outcomes feed a disposable Bayes clone each. Branchwise
    second action is exact optimal myopic EVI. No true law/map is passed.
    """
    require(type(t) is int and 0<=t<31 and
            isinstance(model,JointHypothesis)
            and len(model.events)==t,"TWO_STEP_CLOCK")
    c=t%4; nxt=(t+1)%4
    first=expected_variance_reduction(model,c)
    scores=[]
    for a in range(4):
        py=model.prob(c,a)
        after0=clone_hypothesis(model,t,c,a,0)
        after1=clone_hypothesis(model,t,c,a,1)
        next0=max(expected_variance_reduction(after0,nxt))
        next1=max(expected_variance_reduction(after1,nxt))
        scores.append(first[a]+(1-py)*next0+py*next1)
    return scores

def planner_action(model,t):
    require(type(t) is int and 0<=t<N and len(model.events)==t,
            "PLANNER_CLOCK")
    if t==N-1:
        return choose("fit_evi",model,t%4,t)
    vals=horizon2_values(model,t)
    return max(range(4),key=lambda a:(vals[a],-a))

def independent_bellman_certificate():
    """Independent enumeration of both imagined outcomes for both actions.

    No synthetic HELD source is opened. This is a mathematical identity
    over one virgin, public equal-prior Bayes model.
    """
    m=JointHypothesis([1/6.]*6)
    t=0;c=t%4;nxt=(t+1)%4
    baseline=high_uncertainty(m)
    computed=horizon2_values(m,t)
    maximum_error=0.
    for a in range(4):
        py=m.prob(c,a)
        post=[]
        for y in (0,1):
            z=clone_hypothesis(m,t,c,a,y)
            inner=[]
            for b in range(4):
                p2=z.prob(nxt,b)
                future=[]
                for y2 in (0,1):
                    q=clone_hypothesis(z,t+1,nxt,b,y2)
                    future.append(high_uncertainty(q))
                inner.append((1-p2)*future[0]+p2*future[1]+
                             (COST if b else 0.))
            post.append(min(inner))
        brute=baseline-((COST if a else 0.)+
                        (1-py)*post[0]+py*post[1])
        maximum_error=max(maximum_error,abs(brute-computed[a]))
    require(maximum_error<=1e-10,"INDEPENDENT_TWO_REWARD_BELLMAN")
    myopic=choose("fit_evi",m,c,0)
    optimal=max(range(4),key=lambda a:(computed[a],-a))
    require(computed[optimal]>=computed[myopic]-1e-12,
            "TWO_STEP_OPTIMALITY")
    return {"first_actions":4,"second_actions":4,"outcome_branches":4,
            "max_abs_error":maximum_error,"optimal_action":optimal,
            "myopic_action":myopic}

def h64(text):
    require(type(text) is str and text.startswith(DOMAIN),"PRIVATE_DOMAIN")
    return int.from_bytes(hashlib.sha256(text.encode("ascii")).digest()[:8],"big")

def frozen_source_ids(cohort,mid,seed):
    require(cohort in COHORTS and type(mid) is int and mid in range(3)
            and type(seed) is int and
            seed in (MATCH if cohort==COHORTS[0] else SHIFT),
            "FROZEN_SOURCE_ID")

def structured_bit(rule,c):
    require(type(rule) is int and rule in range(4)
            and type(c) is int and c in range(8),"STRUCTURED_RULE")
    x0,x1,x2=c&1,(c>>1)&1,(c>>2)&1
    return (x0^(x1|x2),x2^(x0&x1),((1^x0)&x1)^x2,
            (x0|x1)&x2)[rule]

def private_world(cohort,mid,seed,prior):
    """Evaluator-only private mapping, law. No policy path accepts them."""
    frozen_source_ids(cohort,mid,seed)
    require(type(prior) is list and len(prior)==6 and
            all(type(z) is float and 0<z<1 for z in prior)
            and abs(sum(prior)-1)<1e-10,"SOURCE_PRIOR")
    u=h64(f"{DOMAIN}map:v1:{cohort}:{mid}:{seed}")/(1<<64)
    total=0.;idx=5
    for j,p in enumerate(prior):
        total+=p
        if u<total:
            idx=j;break
    if cohort=="prior_matched":
        law=h64(f"{DOMAIN}law:v1:{mid}:{seed}")%256
    else:
        ordinal=SHIFT.index(seed)
        law=sum(structured_bit(ordinal%4,c)<<c for c in range(8))
    return idx,law

def witness(cohort,mid,seed,t,action,private,*,source_mode=MODE):
    frozen_source_ids(cohort,mid,seed)
    require(source_mode==MODE and type(t) is int and t in range(N)
            and type(action) is int and action in range(4)
            and type(private) is tuple and len(private)==2
            and type(private[0]) is int and private[0] in range(6)
            and type(private[1]) is int and 0<=private[1]<=255,
            "WITNESS_BOUNDARY")
    map_id,law=private
    effect=(t%4)^ALL_MAPS[map_id][action]
    p=P_TRUE if (law>>effect)&1 else P_FALSE
    u=h64(f"{DOMAIN}coin:v1:{cohort}:{mid}:{seed}:{t}")/(1<<64)
    return int(u<p)

def make_model(arm,prior,private=None):
    require(arm in ARMS and type(prior) is list and len(prior)==6,"MODEL_POLICY")
    if arm=="privileged_correct_map_entropy":
        require(type(private) is tuple and len(private)==2,"PRIVILEGED_CONTROL")
        idx=private[0]
        p=[0.]*6;p[idx]=1.
        return JointHypothesis(p,allowed=(idx,))
    require(private is None,"PRIVATE_MODEL_LEAK")
    return JointHypothesis([1/6.]*6 if arm=="nofit_entropy" else prior)

def public_action(arm,model,t,rng):
    """Any arm receives *only* posterior, public time and public RNG."""
    require(arm in ARMS and type(t) is int and 0<=t<N
            and isinstance(model,JointHypothesis)
            and len(model.events)==t,"ACTION_SOURCE")
    c=t%4
    planned=arm in ("fit_lookahead2","fit_entropy_compute_matched")
    if planned and t<31:
        v=horizon2_values(model,t)
        if arm=="fit_lookahead2":
            return max(range(4),key=lambda a:(v[a],-a)),1
    if arm in ("fit_entropy_compute_matched","fit_entropy_fast",
               "nofit_entropy","privileged_correct_map_entropy"):
        return choose("fit_entropy",model,c,t),int(planned and t<31)
    if arm=="fit_lookahead2":
        return choose("fit_evi",model,c,t),0
    if arm=="fit_myopic_evi":
        return choose("fit_evi",model,c,t),0
    if arm=="fit_cyclic":
        return choose("fit_cyclic",model,c,t),0
    require(arm=="fit_random" and isinstance(rng,random.Random),"PUBLIC_RNG")
    return choose("fit_random",model,c,t,rng=rng),0

def run_world(cohort,mid,seed,arm,prior,index):
    require(arm in ARMS and type(index) is int and index>=0,
            "WORLD")
    private=private_world(cohort,mid,seed,prior)
    model=make_model(arm,prior,private if arm=="privileged_correct_map_entropy" else None)
    rng=random.Random(271828+101*index)
    actions=[];calls=0;start=time.perf_counter()
    for t in range(N):
        a,planning=public_action(arm,model,t,rng)
        y=witness(cohort,mid,seed,t,a,private)
        model.observe(t,t%4,a,y)
        actions.append(a);calls+=planning
    elapsed=time.perf_counter()-start
    raw=model.checkpoint()
    cold=JointHypothesis.restore(raw,digest(raw))
    require(cold.checkpoint()==raw and
            [cold.prob(c,0) for c in range(4,8)]==
            [model.prob(c,0) for c in range(4,8)],
            "COLD_SOURCE_FUNCTIONAL")
    law=private[1]
    high=sum(expected_brier(model.prob(c,0),
             P_TRUE if (law>>c)&1 else P_FALSE)
             for c in range(4,8))/4
    nonzero=sum(a!=0 for a in actions)
    require(len(actions)==N and 0<=high<=1 and
            math.isfinite(high) and math.isfinite(elapsed),
            "ACTION_SOURCE_BUDGET")
    return {"high":high,"net":high+COST*nonzero/N,
            "nonzero":nonzero,"deliberations":calls,
            "checkpoint_bytes":len(raw),"wall_seconds":elapsed}

def proof():
    start=time.perf_counter()
    protocol()
    priors={};archive={}
    for mid in range(3):
        prior,history=fit_source(mid)
        priors[mid]=prior
        archive[mid]=[(h["raw"],h["source_sha"],h["readout_high"])
                      for h in history]
    certificate=independent_bellman_certificate()
    scores={}
    for k,cohort in enumerate(COHORTS):
        seeds=MATCH if k==0 else SHIFT
        data={}
        for arm in ARMS:
            rows=[(mid,run_world(cohort,mid,seed,arm,priors[mid],
                                 k*18+mid*6+si))
                  for mid in range(3)
                  for si,seed in enumerate(seeds)]
            require(len(rows)==18,"HELD_WORLD_COUNT")
            avg=lambda field:sum(x[field] for _,x in rows)/18
            data[arm]={
                "high_expected_brier":round(avg("high"),8),
                "net_high_brier":round(avg("net"),8),
                "nonzero_actions":sum(x["nonzero"] for _,x in rows),
                "witnessed_actions":18*N,
                "high_score_queries":18*4,
                "deliberation_calls":sum(x["deliberations"] for _,x in rows),
                "mean_checkpoint_bytes":round(avg("checkpoint_bytes"),2),
                "total_wall_seconds":round(sum(x["wall_seconds"] for _,x in rows),5),
                "map_group_net_high_brier":[round(
                    sum(x["net"] for i,x in rows if i==mid)/6,8)
                    for mid in range(3)]
            }
        scores[cohort]=data
    for mid,items in archive.items():
        require(len(items)==3,"FIT_ARCHIVE")
        for raw,sha,old in items:
            cold=JointHypothesis.restore(raw,sha)
            require(cold.checkpoint()==raw and
                    [cold.prob(c,0) for c in range(4,8)]==old,
                    "OLD_FIT_ARCHIVE")
    margins={}
    for cohort in COHORTS:
        data=scores[cohort]
        v=data["fit_lookahead2"]["net_high_brier"]
        margins[cohort]={
            "gain_vs_entropy_matched":round(
                data["fit_entropy_compute_matched"]["net_high_brier"]-v,8),
            "gain_vs_entropy_fast":round(
                data["fit_entropy_fast"]["net_high_brier"]-v,8),
            "gain_vs_myopic_evi":round(
                data["fit_myopic_evi"]["net_high_brier"]-v,8)
        }
    budgets=all(scores[cohort][arm]["witnessed_actions"]==576
                and scores[cohort][arm]["high_score_queries"]==72
                for cohort in COHORTS for arm in ARMS)
    equal_calls=all(
        scores[cohort]["fit_lookahead2"]["deliberation_calls"]==
        scores[cohort]["fit_entropy_compute_matched"]["deliberation_calls"]==18*31
        for cohort in COHORTS)
    h={
        "H1_two_reward_bellman_identity":certificate["max_abs_error"]<=1e-10,
        "H2_prior_matched_gain_vs_entropy_005":
            margins["prior_matched"]["gain_vs_entropy_matched"]>=.005,
        "H3_structured_gain_vs_entropy_005":
            margins["structured_shift"]["gain_vs_entropy_matched"]>=.005,
        "H4_both_gain_vs_myopic_003":all(
            margins[c]["gain_vs_myopic_evi"]>=.003 for c in COHORTS),
        "H5_budgets_cold_and_deliberation":bool(budgets and equal_calls),
    }
    return {
      "schema":SCHEMA,"prereg_commit":PREREG,"prereg_blob":PREREG_BLOB,
      "source_mode":MODE,"cohorts":list(COHORTS),
      "historical_FIT_witnesses_per_mapping_group":108,
      "worlds_per_cohort":18,"witnesses_per_arm_per_cohort":576,
      "score_queries_per_arm_per_cohort":72,
      "math_certificate":certificate,"metrics":scores,"margins":margins,
      "hypotheses":h,
      "development_verdict":(
          "DEV_SUPPORTED_SYNTHETIC_ONLY" if all(h.values()) else
          "DEV_MIXED_SYNTHETIC" if
          (h["H2_prior_matched_gain_vs_entropy_005"] or
           h["H3_structured_gain_vs_entropy_005"] or
           h["H4_both_gain_vs_myopic_003"]) else "DEV_NO_GO"),
      "engineering_gate":"SOURCE_ONLY_CONTROLLED",
      "scientific_gate":"SCIENTIFIC_NO_GO_SYNTHETIC_NOT_NATIVE",
      "accepted_native_modified":False,"original_first_use_426":False,
      "deployment":"NONE","proof_wall_seconds":round(time.perf_counter()-start,5)
    }

if __name__=="__main__":
    print("YGG_KNOW30_RECEIPT="+json.dumps(proof(),sort_keys=True))

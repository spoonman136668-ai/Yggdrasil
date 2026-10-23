#!/usr/bin/env python3
"""CS01: source-first external original MDP fixed-policy falsifier, public only."""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from fractions import Fraction as F
from pathlib import Path
import sys
from isolated_original_mdp_import import original_mdp_classes
from preflight_original_dtr import PIN, BLOBS, command

FIRST="c93e78d04c3361b797efd691de3ffa39141ccc5e"
MDP_BLOB="6264ec5450754c009e98c3e85f6d5927ece0a9ab"
SOURCES={**BLOBS,"causal_gym/envs/mdp.py":MDP_BLOB}
SEEDS=(930301,930302)
POLICIES=("state_feedback","fixed_0","fixed_1")
STEPS=30
P1,P2,P3=F(9,10),F(1,10),F(1,10)

def check(cond,msg):
    if not cond: raise RuntimeError(msg)

def js(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)
def sha(x):
    return hashlib.sha256(js(x).encode()).hexdigest()
def binary(x):
    try: b=int(x)
    except (TypeError,ValueError): raise RuntimeError("NONBINARY_ORIGINAL_PUBLIC_VALUE")
    check(b in (0,1) and x==b,"NONBINARY_ORIGINAL_PUBLIC_VALUE")
    return b
def source(root):
    rev=command(["git","rev-parse","HEAD"],root)
    check(rev["exit"]==0 and rev["stdout"].strip()==PIN,"SOURCE_COMMIT_DRIFT")
    for path,expected in sorted(SOURCES.items()):
        x=command(["git","hash-object","--",path],root)
        check(x["exit"]==0 and x["stdout"].strip()==expected,"SOURCE_BLOB_DRIFT:"+path)
    diff=command(["git","diff","--exit-code","--","causal_gym","setup.py"],root)
    check(diff["exit"]==0,"SOURCE_WORKTREE_MODIFIED")
    return {"commit":PIN,"source_blobs":SOURCES}
def original_equations(s,x,u1,u2,u3):
    # Verifier-only, must be reconciled with actual original MDPSCM.step.
    return ((u1^u2)^(s|x)),(s^x^u1^u3)
def modelcheck(MDPSCM):
    rows=[]
    for s,x,u1,u2,u3 in itertools.product((0,1),repeat=5):
        env=MDPSCM()
        env.s=s
        ns,y,terminated,truncated,info=env.step(x,u1,u2,u3)
        expected_s,expected_y=original_equations(s,x,u1,u2,u3)
        check((binary(ns),binary(y))==(expected_s,expected_y),
              "ORIGINAL_MDP_MECHANISM_MISMATCH")
        check(terminated is False and truncated is False and info=={},
              "SOURCE_MECHANISM_RESULT_DRIFT")
        rows.append({"s":s,"x":x,"u1":u1,"u2":u2,"u3":u3,
                     "next_state":binary(ns),"reward":binary(y)})
    check(len(rows)==32,"EXHAUSTIVE_32_CASE_DRIFT")
    return rows
def law():
    exo=[]
    for u1,u2,u3 in itertools.product((0,1),repeat=3):
        f=lambda p,u:p if u else (1-p)
        exo.append((u1,u2,u3,f(P1,u1)*f(P2,u2)*f(P3,u3)))
    check(sum(e[3] for e in exo)==1,"INVALID_EXOGENOUS_DISTRIBUTION")
    r={}
    t={}
    for s,x in itertools.product((0,1),repeat=2):
        r[s,x]=sum((w*original_equations(s,x,a,b,c)[1] for a,b,c,w in exo),F(0))
        t[s,x]=sum((w*original_equations(s,x,a,b,c)[0] for a,b,c,w in exo),F(0))
    check(r=={(0,0):F(41,50),(0,1):F(9,50),
             (1,0):F(9,50),(1,1):F(41,50)},"REWARD_LAW_DRIFT")
    check(t=={(0,0):F(41,50),(0,1):F(9,50),
             (1,0):F(9,50),(1,1):F(9,50)},"TRANSITION_LAW_DRIFT")
    return r,t
def decision_certificate():
    reward,transition=law()
    v={0:F(0),1:F(0)}
    fixed={0:{0:F(0),1:F(0)},1:{0:F(0),1:F(0)}}
    per_horizon=[]
    for h in range(1,STEPS+1):
        q={(s,x):reward[s,x]+transition[s,x]*v[1]+
                    (1-transition[s,x])*v[0]
           for s,x in itertools.product((0,1),repeat=2)}
        best={}
        for s in (0,1):
            check(q[s,s]>q[s,1-s],"STATE_FEEDBACK_NOT_UNIQUE_OPTIMUM")
            best[s]=s
        v={s:max(q[s,0],q[s,1]) for s in (0,1)}
        for x in (0,1):
            prior=fixed[x]
            fixed[x]={s:reward[s,x]+transition[s,x]*prior[1]+
                            (1-transition[s,x])*prior[0] for s in (0,1)}
        per_horizon.append(best)
    mean=lambda x:(x[0]+x[1])/2
    qopt=mean(v);c0=mean(fixed[0]);c1=mean(fixed[1])
    check(qopt==F(123,5) and c0==F(15) and c1==F(5663,625),
          "FROZEN_THIRTY_HORIZON_VALUE_DRIFT")
    check(qopt>c0 and qopt>c1 and len(per_horizon)==30,
          "FIXED_POLICY_SHORTCUT_NOT_FALSIFIED")
    ratio=lambda v:{"numerator":v.numerator,"denominator":v.denominator,
                    "decimal":float(v)}
    return {"source_exogenous_law":{"p_u1_1":"9/10","p_u2_1":"1/10",
                                     "p_u3_1":"1/10"},
            "original_source_mechanism_calls":32,
            "expected_step_reward_table":[{"state":s,"action":x,
                                            "reward":ratio(reward[s,x]),
                                            "next_state_one":ratio(transition[s,x])}
                                           for s,x in itertools.product((0,1),repeat=2)],
            "unique_optimal_action_by_public_state":{"0":0,"1":1},
            "unique_state_feedback_at_all_horizons_1_to_30":True,
            "thirty_decision_expected_reward":{
                "public_state_feedback":ratio(qopt),
                "constant_0":ratio(c0),"constant_1":ratio(c1)},
            "fixed_policy_shortcut_falsified_for_these_two_constants":True,
            "finite_sample_learnability_not_established":True}
def source_smoke(MDPPCH,seed,name):
    env=MDPPCH()
    state,info=env.reset(seed=seed)
    check(isinstance(info,dict),"ORIGINAL_RESET_INFO_SHAPE")
    s=binary(state)
    events=[]
    for step in range(STEPS):
        calls=[]
        def act(public_s):
            received=binary(public_s)
            check(received==s,"POLICY_PUBLIC_STATE_CHANGED")
            x=received if name=="state_feedback" else (0 if name=="fixed_0" else 1)
            calls.append((received,x))
            return x
        ns,y,terminated,truncated,raw_info=env.do(act)
        check(len(calls)==1,"PUBLIC_CALLBACK_COUNT_MISMATCH")
        check(terminated is False and truncated is False,
              "MDP_TRUNCATED_BEFORE_PREDECLARED_30")
        check(isinstance(raw_info,dict),"ORIGINAL_RESULT_INFO_INVALID")
        x=calls[0][1]
        ns=binary(ns)
        yy=binary(y)
        events.append({"t":step,"state":s,"action":x,"next_state":ns,"reward":yy})
        s=ns
    check(len(events)==30,"SMOKE_STEP_COUNT_DRIFT")
    return {"seed":seed,"policy":name,"actions":30,"total_reward":sum(e["reward"] for e in events),
            "trace_sha256":sha(events),"public_trace":events}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--upstream",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    root=Path(args.upstream).resolve()
    out=Path(args.out)
    out.mkdir(parents=True,exist_ok=True)
    receipt={"schema":"mass.cs01.original-confounded-mdp-public-discrimination.v1",
             "prereg_first_sha":FIRST,
             "original_source":"CausalAILab/Causal-Gymnasium",
             "public_development_only":True,
             "previous_dtr02_no_gain_preserved":True,
             "actual_yggdrasil_native_learner_tested":False,
             "models_trained":0,"sealed_unfamiliar_source_consumed":False,
             "controller_admission_observed":False,
             "scientific_first_use":False,
             "resource_parity_qualified":False,
             "disposition":"PUBLIC_CS01_SOURCE_DISCRIMINATION_NO_GO"}
    try:
        receipt["source"]=source(root)
        MDPSCM,MDPPCH=original_mdp_classes(root)
        truth=modelcheck(MDPSCM)
        receipt["mechanism_exhaustive32_sha256"]=sha(truth)
        receipt["original_direct_source_mechanism_step_calls"]=32
        receipt["exact_certificate"]=decision_certificate()
        traces=[source_smoke(MDPPCH,s,policy)
                for s in SEEDS for policy in POLICIES]
        receipt["public_source_native_runs"]=traces
        receipt["genuine_public_source_native_episodes"]=len(traces)
        receipt["original_source_native_public_action_calls"]=sum(v["actions"] for v in traces)
        check(len(traces)==6 and receipt["original_source_native_public_action_calls"]==180,
              "PUBLIC_SMOKE_BUDGET_DRIFT")
        receipt["disposition"]="CS01_PUBLIC_STATE_DEPENDENT_OPTIMUM_CERTIFIED"
    except Exception as ex:
        receipt["failure"]=type(ex).__name__+":"+str(ex)[:600]
    finally:
        (out/"cs01-original-mdp-receipt.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print("CS01_DISPOSITION="+receipt["disposition"],flush=True)
    return 0 if receipt["disposition"]=="CS01_PUBLIC_STATE_DEPENDENT_OPTIMUM_CERTIFIED" else 2
if __name__=="__main__":
    sys.exit(main())

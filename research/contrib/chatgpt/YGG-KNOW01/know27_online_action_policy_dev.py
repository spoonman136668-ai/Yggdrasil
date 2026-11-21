"""KNOW27: frozen source-only online opaque action selection and A-B-A interference.
Prereg committed before this code at e48bcdffadec0be864ae6192ce6429a2906a98cf.
Neither protected original first use nor accepted native model is invoked.
"""
from __future__ import annotations
import hashlib
import json
import math
import random
import time
from pathlib import Path
from unknown_action_affordance_dev import (
    ALL_MAPS, TRUE_MAPS, JointHypothesis, Passive, fit_source,
    canonical, digest, expected_brier, P_TRUE, P_FALSE,
)
SCHEMA="yggdrasil.know27.opaque-policy-source-result.v1"
PROTO="yggdrasil.know27.online-opaque-action-selection-prereg.v1"
PREREG="e48bcdffadec0be864ae6192ce6429a2906a98cf"
MODE="engineering_fixture_only"
LAWS=("H0","H1","H2","H3")
SEEDS=(14011,14017)
ABA_SEEDS=(14111,14117)
ARM=("fit_evi","nofit_evi","fit_cyclic","fit_random","fit_entropy",
     "fit_map_x2","known_map_evi","known_family_evi","passive_p05")
COST=.002
N=32

def require(v,tag):
    if not v: raise ValueError("YGG_KNOW27_"+tag)

def protocol():
    d=json.loads(Path(__file__).with_name("know27_online_action_policy_protocol.json").read_text("utf-8"))
    require(d.get("schema")==PROTO
            and d["held_stationary"]["seeds"]==list(SEEDS)
            and d["held_ABA"]["seeds"]==list(ABA_SEEDS)
            and d["held_stationary"]["action_witnesses_per_policy"]==768
            and d["held_ABA"]["action_witnesses_per_policy"]==192
            and d["policy"]["EVI"].startswith("For each candidate action")
            and d["hypotheses"]["H2"].endswith("0.01000.")
            and d["source_mode"]==MODE,"FROZEN_PROTOCOL")
    return d

def true_bit(law,c):
    require(law in LAWS and type(c) is int and 0<=c<8,"PRIVATE_RULE")
    x0,x1,x2=c&1,(c>>1)&1,(c>>2)&1
    if law=="H0": return x0^(x1&x2)
    if law=="H1": return x1^(x0&x2)
    if law=="H2": return 1^(x0&x2)
    return x0^x1

def private_prob(law,c):
    return P_TRUE if true_bit(law,c) else P_FALSE

def law_table(law):
    return sum(true_bit(law,c)<<c for c in range(8))

def source(mid,seed,t,a,kind="stationary",*,source_mode=MODE):
    require(source_mode==MODE
            and type(mid) is int and 0<=mid<3
            and type(seed) is int and
            ((kind=="stationary" and seed in SEEDS) or
             (kind=="ABA" and seed in ABA_SEEDS))
            and type(t) is int and 0<=t<32
            and type(a) is int and 0<=a<4,"FROZEN_SOURCE")
    if kind=="ABA": law="H0" if t<8 or t>=24 else "H2"
    else: law=None
    raw=hashlib.sha256(f"know27:private:outcome:v1:{mid}:{seed}:{t}:{kind}".encode("ascii")).digest()
    coin=int.from_bytes(raw[:8],"big")/2**64
    return law,coin

def witness(mid,seed,law,t,a,kind="stationary",*,source_mode=MODE):
    phase,coin=source(mid,seed,t,a,kind,source_mode=source_mode)
    require((kind=="stationary" and law in LAWS) or
            (kind=="ABA" and law==phase),"FROZEN_LAW")
    c=t%4
    target=c^TRUE_MAPS[mid][a]
    return int(coin<private_prob(law,target))

def target_loss(model,law):
    forecasts=[model.prob(c,0) for c in range(4,8)]
    return sum(expected_brier(p,private_prob(law,c))
               for p,c in zip(forecasts,range(4,8)))/4

def expected_variance_reduction(model,c):
    """Exact posterior E[reduction in Brier] for four latent high forecasts.
    Depends only on 6×256 hypotheses and public c; NEVER simulator private fields.
    """
    require(type(c) is int and 0<=c<4,"PUBLIC_CONTEXT")
    raw,den=model._unnormalized()
    highs=[0.]*4
    q=[0.]*4
    joint=[[0.]*4 for _ in range(4)]
    for rowidx,mapidx in enumerate(model.allowed):
        mapping=ALL_MAPS[mapidx]
        positions=[c^mapping[a] for a in range(4)]
        for h,w in zip(model.laws,raw[rowidx]):
            if not w:continue
            v=w/den
            hi=((h>>4)&1,(h>>5)&1,(h>>6)&1,(h>>7)&1)
            for j,b in enumerate(hi):
                highs[j]+=v*b
            for a,pos in enumerate(positions):
                b=(h>>pos)&1
                if b:
                    q[a]+=v
                    for j,z in enumerate(hi):
                        if z:joint[a][j]+=v
    values=[]
    for a in range(4):
        y=P_FALSE+(P_TRUE-P_FALSE)*q[a]
        var=y*(1-y)
        require(var>0 and math.isfinite(var),"EVI_DENOM")
        e=sum(((P_TRUE-P_FALSE)**2*(joint[a][j]-highs[j]*q[a]))**2 /var
              for j in range(4))/4
        values.append(e-(COST if a else 0))
    return values

def choose(name,model,c,t,*,rng=None,mapped_action=None):
    """Public-only policy interface; no seed, private map ID, law or outcome."""
    require(name in ARM and type(c) is int and 0<=c<4
            and type(t) is int and 0<=t<32,"POLICY")
    if name=="fit_cyclic":return t%4
    if name=="fit_random":
        require(isinstance(rng,random.Random),"PUBLIC_RANDOM")
        return rng.randrange(4)
    if name=="fit_map_x2":
        require(type(mapped_action) is int and 1<=mapped_action<=3,"PUBLIC_FIT_MAP")
        return mapped_action
    if name=="passive_p05":return 0
    if name=="fit_entropy":
        values=[model.prob(c,a)*(1-model.prob(c,a))-(COST if a else 0)
                for a in range(4)]
    else:
        values=expected_variance_reduction(model,c)
    return max(range(4),key=lambda a:(values[a],-a))

def new_model(name,prior,mid):
    require(name in ARM and type(prior) is list and len(prior)==6
            and type(mid) is int and 0<=mid<3,"MODEL")
    if name=="passive_p05":return Passive()
    if name=="nofit_evi":return JointHypothesis([1/6.]*6)
    if name in ("known_map_evi","known_family_evi"):
        idx=ALL_MAPS.index(TRUE_MAPS[mid])
        p=[0.]*6;p[idx]=1.
        m=JointHypothesis(p,allowed=(idx,))
        if name=="known_family_evi":
            # Evaluator-privileged TRUE hidden law family, explicit upper control.
            m.laws=tuple(law_table(law) for law in LAWS)
            m.logw=[[math.log(.25)]*4]
        return m
    return JointHypothesis(prior)

def snapshot(model,*,allow_privileged_family=False):
    if allow_privileged_family:
        return canonical({"privileged_known_law_family":True,
                          "events":model.events,"mapping":model.allowed,
                          "laws":model.laws})
    raw=model.checkpoint()
    if isinstance(model,JointHypothesis):
        cold=JointHypothesis.restore(raw,digest(raw))
        require(cold.checkpoint()==raw and
                [cold.prob(c,0) for c in range(8)]==
                [model.prob(c,0) for c in range(8)],"COLD_FUNCTIONAL")
    return raw

def run_world(name,mid,seed,law,index,prior,*,kind="stationary"):
    require(name in ARM and type(mid) is int and 0<=mid<3
            and type(seed) is int and type(index) is int
            and index>=0 and ((kind=="stationary" and seed in SEEDS
                               and law in LAWS) or
                              (kind=="ABA" and seed in ABA_SEEDS
                               and law=="H0")),"HELD_WORLD")
    model=new_model(name,prior,mid)
    # Public world index is only random policy salt, no law/mapping value enters policy.
    rng=random.Random(271828+101*index)
    guess=None
    if name=="fit_map_x2":
        m=max(range(6),key=lambda i:(prior[i],-i))
        guess=ALL_MAPS[m].index(4)
    rows=[]
    pre_B=None;pre_return=None;return_losses=[]
    high_briers=[]
    for t in range(N):
        c=t%4
        a=choose(name,model,c,t,rng=rng,mapped_action=guess)
        outcome_law=law if kind=="stationary" else ("H0" if t<8 or t>=24 else "H2")
        y=witness(mid,seed,outcome_law,t,a,kind)
        if kind=="ABA" and t>=24:
            return_losses.append(target_loss(model,"H0"))
        model.observe(t,c,a,y)
        rows.append([t,c,a,y])
        if kind=="ABA" and t==7:pre_B=target_loss(model,"H0")
        if kind=="ABA" and t==23:
            pre_return=target_loss(model,"H0")
            warm=snapshot(model,allow_privileged_family=(name=="known_family_evi"))
            if name!="known_family_evi" and isinstance(model,JointHypothesis):
                require(JointHypothesis.restore(warm,digest(warm)).checkpoint()==warm,
                        "PRE_RETURN_COLD")
    require(len(rows)==32 and all(row[:2]==[i,i%4] for i,row in enumerate(rows)),
            "ONE_WITNESS")
    cold=snapshot(model,allow_privileged_family=(name=="known_family_evi"))
    if kind=="stationary":
        high=sum(expected_brier(model.prob(c,0),private_prob(law,c))
                 for c in range(4,8))/4
        low=sum(expected_brier(model.prob(c,0),private_prob(law,c))
                for c in range(4))/4
    else:
        high=sum(return_losses)/8
        low=0
        require(pre_B is not None and pre_return is not None
                and len(return_losses)==8,"ABA_BUDGET")
    return {
        "actions":[r[2] for r in rows],
        "high_brier":high,"low_brier":low,
        "pre_B":pre_B,"pre_return":pre_return,
        "active":sum(r[2]!=0 for r in rows),
        "cost":sum(COST for r in rows if r[2]!=0),
        "bytes":len(cold),"events":len(rows)
    }

def proof():
    t0=time.monotonic()
    protocol()
    fitted={}
    original_receipts={}
    for mid in range(3):
        prior,history=fit_source(mid)
        fitted[mid]=prior
        original_receipts[mid]=[(h["source_sha"],h["readout_high"],h["raw"])
                                for h in history]
        for sha,old_readout,raw in original_receipts[mid]:
            cold=JointHypothesis.restore(raw,sha)
            require([cold.prob(c,0) for c in range(4,8)]==old_readout,
                    "FIT_COLD")
    result={};aba_result={}
    for name in ARM:
        s=[]
        for mid in range(3):
            for li,law in enumerate(LAWS):
                for si,seed in enumerate(SEEDS):
                    index=(mid*8)+(li*2)+si
                    r=run_world(name,mid,seed,law,index,fitted[mid])
                    s.append((mid,li,seed,r))
        require(len(s)==24 and sum(r["events"] for _,_,_,r in s)==768,
                "HELD_BUDGET")
        hi=sum(r["high_brier"] for _,_,_,r in s)/24
        lo=sum(r["low_brier"] for _,_,_,r in s)/24
        cost=sum(r["cost"] for _,_,_,r in s)
        neg=sum(r["high_brier"] for _,li,_,r in s if li==3)/6
        diverse=sum(len(set(a for a in r["actions"][:16] if a!=0))>=2
                    for _,_,_,r in s)
        result[name]={
           "high_expected_brier":round(hi,8),
           "low_expected_brier":round(lo,8),
           "net_high_brier":round(hi+cost/768,8),
           "negative_H3_high_brier":round(neg,8),
           "total_active":sum(r["active"] for _,_,_,r in s),
           "intervention_cost":round(cost,8),
           "diverse_first16":diverse,
           "avg_cold_bytes":round(sum(r["bytes"] for _,_,_,r in s)/24,2)}
        ab=[]
        for mid in range(3):
            for si,seed in enumerate(ABA_SEEDS):
                ab.append(run_world(name,mid,seed,"H0",mid*2+si,
                                    fitted[mid],kind="ABA"))
        require(len(ab)==6 and sum(r["events"] for r in ab)==192,
                "ABA_HELD_BUDGET")
        aba_result[name]={
            "pre_B_A_high_brier":round(sum(r["pre_B"] for r in ab)/6,8),
            "pre_return_A_high_brier":round(sum(r["pre_return"] for r in ab)/6,8),
            "return_A_prequential_high_brier":round(sum(r["high_brier"] for r in ab)/6,8),
            "active":sum(r["active"] for r in ab),
            "cold_bytes_avg":round(sum(r["bytes"] for r in ab)/6,2)}
    # Old FIT original source/function remains unmodified after every simulated held world.
    for mid,rows in original_receipts.items():
        for sha,readout,raw in rows:
            check=JointHypothesis.restore(raw,sha)
            require(check.checkpoint()==raw and
                    [check.prob(c,0) for c in range(4,8)]==readout,
                    "FIT_OLD_WORLD_RETENTION_ARCHIVE")
    fit=result["fit_evi"]
    cyclic=result["fit_cyclic"]
    nofit=result["nofit_evi"]
    random_=result["fit_random"]
    h={
      "H1_fit_vs_cyclic_net_010":
        cyclic["net_high_brier"]-fit["net_high_brier"]>=.01000,
      "H2_fit_vs_noFIT_net_010":
        nofit["net_high_brier"]-fit["net_high_brier"]>=.01000,
      "H3_fit_vs_public_random_net_010":
        random_["net_high_brier"]-fit["net_high_brier"]>=.01000,
      "H4_nontrivial_active_actions_18of24":
        fit["diverse_first16"]>=18,
      "H5_pre_return_A_not_degraded_015":
        (aba_result["fit_evi"]["pre_return_A_high_brier"]-
         aba_result["fit_evi"]["pre_B_A_high_brier"])<=.01500,
      "H6_no_x2_negative_nonregression_010":
        (fit["negative_H3_high_brier"]-
         cyclic["negative_H3_high_brier"])<=.01000
    }
    active_count=sum(h[k] for k in list(h)[:4])
    verdict=("DEV_ONLINE_POLICY_SUPPORTED" if all(h.values())
             else "DEV_MIXED_ONLINE_POLICY" if active_count
             else "DEV_ONLINE_POLICY_NO_GO")
    return {"schema":SCHEMA,"prereg_commit":PREREG,
      "source_mode":MODE,
      "held_stationary_worlds":24,"held_ABA_worlds":6,
      "fit_witnesses_per_mapping":108,
      "held_stationary_actions_per_policy":768,
      "held_ABA_actions_per_policy":192,
      "high_eval_queries_per_policy":96,
      "frozen_cost_per_nonzero_action":COST,
      "fair_vs_privileged": {
          "known_map_evi":"EXTRA_PRIVILEGED_TRUE_MAPPING",
          "known_family_evi":"EXTRA_PRIVILEGED_TRUE_MAPPING_AND_LAW_FAMILY"},
      "metrics":result,"ABA_metrics":aba_result,
      "hypotheses":h,
      "margins":{
       "cyclic_net_gain":round(cyclic["net_high_brier"]-fit["net_high_brier"],8),
       "noFIT_net_gain":round(nofit["net_high_brier"]-fit["net_high_brier"],8),
       "random_net_gain":round(random_["net_high_brier"]-fit["net_high_brier"],8),
       "A_pre_return_degradation":round(
           aba_result["fit_evi"]["pre_return_A_high_brier"]-
           aba_result["fit_evi"]["pre_B_A_high_brier"],8)},
      "verdict":verdict,
      "engineering_gate":"PASS",
      "scientific_gate":"SCIENCE_NO_GO_SYNTHETIC_NOT_NATIVE",
      "accepted_native_modified":False,"protected_original_first_use":False,
      "deployment":"NONE",
      "isolated_wall_seconds":round(time.monotonic()-t0,6)}
if __name__=="__main__":
    print("YGG_KNOW27_RECEIPT="+json.dumps(proof(),sort_keys=True))

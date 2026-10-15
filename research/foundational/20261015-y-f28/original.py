"""Y-F28 conditional downstream information-value learning, DEVELOPMENT ONLY.

A 15-weight train-only policy learns which *second* sensor minimizes future
typed-query error. Only TRAIN data expose all sensor outcomes in a soft-choice
objective. Evaluation actions occur strictly through sensor_custody's physically
metered sequential channel port. F3 source independence is NOT established.
"""
from __future__ import annotations
import json, math, random, time
from dataclasses import asdict
from sensor_custody import (
    PublicSensorInfo, evaluate_policy, static_first, static_second,
    validate_disjoint, action_switch_rate, CustodyViolation,
)
import torch

torch.set_num_threads(1)
torch.manual_seed(2828)
CONDITIONS=("ordinary","missingness","anticorrelation","corrupted-anchor")
MECHANISMS=("mode-hint","directional-reliability")
TRAIN_FAMILIES=(100,101,102,103)
TEST_FAMILIES=(104,105,106,107)
TRAIN_SEEDS=range(141000,141099)
TEST_SEEDS=range(142300,142312)
PUBLIC=PublicSensorInfo((.95,.78,.78,.37),(0.,.14,.14,.1))
NATIVE_BYTES=576
CALIBRATION_BYTES=64

def clamp(x:float)->float:
    return min(.999,max(.001,x))

def cues(seed:int,family:int,role:int,mechanism:int,condition:int,shift:int):
    """Source-born role-bit and observations, never returned to selectors."""
    rng=random.Random(seed*1000003+family*11003+role*7919+mechanism*1009+condition*89+shift*17)
    true_bit=rng.randrange(2)
    mode=rng.randrange(2)
    sign=1 if true_bit else -1
    mode_sign=1 if mode else -1
    # Neither physical first-reading nor provenance carries a true bit label.
    first=clamp(.5+.21*mode_sign+.08*sign+rng.gauss(0,.095))
    if mechanism==1: first=clamp(.5-.18*mode_sign+.1*sign+rng.gauss(0,.10))
    if condition==3:first=clamp(first+rng.gauss(0,.13))
    channels=[first]
    for j in (1,2,3):
        active=(j==1 and mode==0) or (j==2 and mode==1)
        amplitude=.36 if active else (.11 if j==3 else .015)
        noise=.10 if active else .23
        if mechanism==1:amplitude*=.86;noise*=1.16
        observed=clamp(.5+amplitude*sign+rng.gauss(0,noise))
        if condition==1 and j==1 and rng.random()<.40:observed=.5
        if condition==2 and j==2:observed=1-observed
        channels.append(observed)
    return true_bit,tuple(channels),mode

def features(first:float,mechanism:int):
    return torch.tensor([1.,2*first-1,abs(2*first-1),(2*first-1)**2,float(mechanism)],dtype=torch.float32)

def read_bit(first:float,second:float,sensor:int,mechanism:int,condition:int)->float:
    # Shared fixed decoder for all equal-budget arms; no private source mode.
    mode= (first>=.5) if mechanism==0 else (first<.5)
    offset=(.21 if first>=.5 else -.21) if mechanism==0 else (.18 if first>=.5 else -.18)
    first_signal=(first-.5-offset)/.16
    if sensor==2 and condition==2:second=1-second
    # Regime-dependent channel calibration is PUBLIC; a wrong source is weak.
    reliability=1. if ((sensor==1 and not mode) or (sensor==2 and mode)) else .40
    if sensor==3:reliability=.25
    z=.25*first_signal+.75*reliability*(second-.5)*3.
    return 1/(1+math.exp(-max(-20,min(20,z*3))))

def train_policy():
    xs=[];losses=[]
    for seed in TRAIN_SEEDS:
        for family in TRAIN_FAMILIES:
            for mech in range(2):
                for cond in range(4):
                    for role in range(3):
                        bit,vals,_=cues(seed,family,role,mech,cond,seed%4)
                        xs.append(features(vals[0],mech))
                        ps=[read_bit(vals[0],vals[j],j,mech,cond) for j in (1,2,3)]
                        losses.append([-bit*math.log(max(1e-6,p))-(1-bit)*math.log(max(1e-6,1-p)) for p in ps])
    x=torch.stack(xs)
    errors=torch.tensor(losses,dtype=torch.float32)
    # 3 options x 5 public features, 15 independently learned parameters.
    weights=torch.nn.Parameter(torch.zeros((3,5),dtype=torch.float32))
    optimizer=torch.optim.Adam([weights],lr=.045)
    for epoch in range(100):
        optimizer.zero_grad()
        action_prob=torch.softmax(x@weights.T,dim=-1)
        downstream_loss=(action_prob*errors).sum(dim=-1).mean()
        downstream_loss.backward()
        torch.nn.utils.clip_grad_norm_([weights],5.)
        optimizer.step()
    return weights.detach().clone(),float(downstream_loss.detach()),len(xs)

def choose_second(mode,policy,mechanism,condition,public,first):
    if mode=="learned" or mode=="masked_first":
        v=.5 if mode=="masked_first" else first.value
        z=features(v,mechanism)@policy.T
        return 1+int(torch.argmax(z).item())
    if mode=="bayes_adaptive":
        # Mechanistic adaptive information-value control, NOT descriptor oracle.
        regime=(first.value>=.5) if mechanism==0 else (first.value<.5)
        return 2 if regime else 1
    if mode=="conditional_greedy":
        # Does not receive true latent mode; first evidence changes the policy.
        return 2 if first.value>.55 else 1
    if mode=="static_greedy":return static_second(public,first)
    if mode=="fixed_pair":return 3
    raise ValueError("unknown registered method")

def compose(bits,family):
    # Known typed relation operators, same across arms.
    if family%2==0:
        return bool(bits[0]^bits[1]^bits[2])
    return sum(bool(b) for b in bits)>=2

MODES=("learned","bayes_adaptive","conditional_greedy","static_greedy","fixed_pair","masked_first","descriptor_oracle")
FAIR=MODES[1:5]
def score(rows,arm):
    n=len(rows);good=fp=fn=0
    for r in rows:
        ans=r["answers"][arm]
        good+=ans==r["truth"]
        fp+=bool(ans) and not r["truth"]
        fn+=not bool(ans) and r["truth"]
    return dict(total=n,correct=good,accuracy=good/n if n else 0.,fp=int(fp),fn=int(fn))

def original():
    validate_disjoint(dict(seeds=set(TRAIN_SEEDS),entities={100000+i for i in TRAIN_SEEDS},families=set(TRAIN_FAMILIES)),
                      dict(seeds=set(TEST_SEEDS),entities={200000+i for i in TEST_SEEDS},families=set(TEST_FAMILIES)))
    w,loss,ntrain=train_policy()
    rows=[]
    for seed in TEST_SEEDS:
        for fam in TEST_FAMILIES:
            for mech in range(2):
                for cond in range(4):
                    true_bits=[];values=[]
                    for role in range(3):
                        bit,v,_=cues(seed,fam,role,mech,cond,seed%4)
                        true_bits.append(bit);values.append(v)
                    truth=compose(true_bits,fam)
                    answers={"descriptor_oracle":truth}
                    receipts={}
                    for arm in MODES[:-1]:
                        decoded=[]; traces=[]; native=0; calibrator=0
                        for role in range(3):
                            # Pass source values to a private port. The policy callback
                            # cannot access this tuple, role truth or unpurchased values.
                            r=evaluate_policy(values[role],PUBLIC,static_first,
                                lambda pub,first,mode=arm,m=mech,c=cond:choose_second(mode,w,m,c,pub,first),
                                NATIVE_BYTES,CALIBRATION_BYTES)
                            if r.physical_reads!=2:raise CustodyViolation("sensor budget drift")
                            first,second=r.trace
                            decoded.append(read_bit(first.value,second.value,second.sensor,mech,cond)>=.5)
                            traces.append([[t.sensor,round(t.value,8)] for t in r.trace])
                            native+=r.native_bytes;calibrator+=r.calibration_bytes
                        answers[arm]=compose(decoded,fam)
                        receipts[arm]={"purchased_per_role":[2,2,2],"traces":traces,
                                       "native_bytes_per_role":NATIVE_BYTES,
                                       "calibration_bytes_per_role":CALIBRATION_BYTES,
                                       "purchased_target_channels":6}
                    rows.append(dict(seed=seed,family=fam,mechanism=MECHANISMS[mech],
                                     condition=CONDITIONS[cond],truth=truth,
                                     answers=answers,receipts=receipts))
    scores={arm:score(rows,arm) for arm in MODES}
    strata={m+":"+c:{arm:score([r for r in rows if r["mechanism"]==m and r["condition"]==c],arm) for arm in MODES}
            for m in MECHANISMS for c in CONDITIONS}
    if scores["descriptor_oracle"]["correct"]!=len(rows):raise ValueError("source oracle mismatch")
    best=max(scores[a]["accuracy"] for a in FAIR)
    gain=scores["learned"]["accuracy"]-best
    nondegrading=all(strata[k]["learned"]["accuracy"]>=max(strata[k][a]["accuracy"] for a in FAIR) for k in strata)
    # Paired interventions are diagnostic only; not evaluation-label tuning.
    switches=[]
    for mech in range(2):
        for first_a,first_b in ((.28,.72),(.4,.65),(.48,.52)):
            a=evaluate_policy((first_a,.25,.75,.45),PUBLIC,static_first,
               lambda p,r:choose_second("learned",w,mech,0,p,r),NATIVE_BYTES,CALIBRATION_BYTES)
            b=evaluate_policy((first_b,.25,.75,.45),PUBLIC,static_first,
               lambda p,r:choose_second("learned",w,mech,0,p,r),NATIVE_BYTES,CALIBRATION_BYTES)
            switches.extend((a,b))
    switch_rate=action_switch_rate(tuple(switches))
    passed=gain>=.02 and nondegrading and switch_rate>0
    verdict="DEVELOPMENT_CONDITIONAL_INFORMATION_NO_QUALIFIED_GAIN"
    if passed:verdict="DEVELOPMENT_CONDITIONAL_INFORMATION_LEARNED_GAIN"
    return dict(schema="yggdrasil.f28.conditional-downstream-information.development.v1",
                stage="DEVELOPMENT_ONLY",parent="352ec6cb606020f97e6369dcc54d761c1d8dd77e",
                train_families=TRAIN_FAMILIES,test_families=TEST_FAMILIES,
                train_seed_range=[141000,141099],test_seed_range=[142300,142312],
                training_cases=ntrain,training_loss=loss,trained_weights=w.tolist(),
                weight_count=15,mechanisms=MECHANISMS,conditions=CONDITIONS,
                native_state_bytes=576,calibration_bytes_per_role=64,
                actual_reads_per_role=2,read_cost_per_query=6,
                known_structure_decoder=True,truth_unavailable_to_policy=True,
                train_only_all_channel_objective=True,questions=len(rows),
                scores=scores,strata=strata,action_switch_rate=switch_rate,
                rows=rows,registered_verdict=verdict,independent_source_birth=False,
                sealed_first_use=False,accepted_ref_mutation=False,paid_api_calls=0)

if __name__=="__main__":
    print(json.dumps(original(),sort_keys=True,indent=2))

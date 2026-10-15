"""Y-F31 train-only conditional-observation headroom pilot. NO PRIMARY ORIGINAL.

Pilot data and public calibration are disjoint from RESERVED future test seed
ranges. Strong empirical-Brier and Bayesian proxy arms share identical
calibration, physical two-read budget and no evaluation labels at selection.
"""
from __future__ import annotations
import json,math,random
from collections import Counter

PILOT_SEEDS=range(181000,181032)
PILOT_FAMILIES=(150,151,152,153)
RESERVED_TEST_SEEDS=range(182000,182012)
RESERVED_TEST_FAMILIES=(154,155,156,157)
CONDITIONS=("missingness","correlated-anchors","low-coverage","noninformative-first")
REGIMES=(0,1)
ANCHORS=8
ARMS=("conditional_empirical","bayesian_proxy","static","fixed","privileged_oracle")

def make(seed,role,regime,condition,episode):
    rng=random.Random(seed*1000003+role*1777+regime*10919+condition*971+episode*43)
    truth=rng.randrange(2);mode=rng.randrange(2)
    y=2*truth-1
    orientation=-1 if regime==1 else 1
    hint=orientation*(2*mode-1)
    amp=.28 if condition!=3 else .005
    first=min(1.,max(0.,.5+amp*hint+rng.gauss(0,.16 if condition!=3 else .26)))
    readings=[first]
    for j in (1,2,3):
        reliable=(j==1 and mode==0) or (j==2 and mode==1)
        strength=.33 if reliable else .02
        if j==3:strength=.22
        if condition==1 and j==2:
            strength=-.28 if mode==0 else .06
        if condition==0 and j==2 and rng.random()<.22:
            readings.append(.5);continue
        sigma=.17 if reliable else .27
        if condition==2:sigma*=1.3
        value=max(0.,min(1.,.5+y*strength+rng.gauss(0,sigma)))
        readings.append(value)
    return truth,mode,tuple(readings)

def anchors_for(seed,regime,condition):
    return tuple((truth,mode,obs) for i in range(ANCHORS)
             for truth,mode,obs in [make(seed+50000+i*23,i%3,regime,condition,500+i)])

def corr(anchors,first,j):
    weight_sum=total=0.
    for y,_,v in anchors:
        w=math.exp(-8*abs(first-v[0]))
        weight_sum+=w
        total+=w*(2*v[j]-1)*(2*y-1)
    return total/(weight_sum+1e-10)

def decode(first,second,j,anchors):
    r=corr(anchors,first,j)
    z=(2*second-1)*r/(abs(r)+.05)
    return 1/(1+math.exp(-max(-20,min(20,z*5))))

def decision(first,anchors,mode):
    if mode=="fixed":return 3
    if mode=="static":
        return max((1,2,3),key=lambda j:(abs(corr(anchors,.5,j)),-j))
    if mode=="bayesian_proxy":
        return max((1,2,3),key=lambda j:(abs(corr(anchors,first,j)),-j))
    if mode=="conditional_empirical":
        risks=[]
        for j in (1,2,3):
            mass=loss=0.
            for label,_,readings in anchors:
                w=math.exp(-8*abs(first-readings[0]))
                p=decode(readings[0],readings[j],j,anchors)
                loss+=w*(p-label)**2
                mass+=w
            risks.append(loss/(mass+1e-10))
        return (1,2,3)[min(range(3),key=lambda i:(risks[i],i))]
    raise ValueError(mode)

def compose(bits,family):
    if family%2==0:return bool(bits[0]^bits[1]^bits[2])
    return sum(bool(x) for x in bits)>=2

def score(rows,arm):
    n=len(rows);correct=0;fp=0;fn=0
    for row in rows:
        pred=row["answers"][arm];truth=row["truth"]
        correct+=pred==truth
        fp+=bool(pred) and not truth
        fn+=not bool(pred) and truth
    return dict(correct=correct,total=n,accuracy=correct/n,fp=fp,fn=fn)

def information(modepairs):
    n=len(modepairs)
    joint=Counter(modepairs);a=Counter(m for m,s in modepairs);b=Counter(s for m,s in modepairs)
    return sum(c/n*math.log2(c*n/(a[m]*b[s])) for (m,s),c in joint.items() if c)

def run():
    assert not (set(PILOT_SEEDS)&set(RESERVED_TEST_SEEDS))
    assert not (set(PILOT_FAMILIES)&set(RESERVED_TEST_FAMILIES))
    rows=[];pairs=[];first_values=[]
    switches=attempts=0
    for seed in PILOT_SEEDS:
        for family in PILOT_FAMILIES:
            for regime in REGIMES:
                for cond in range(len(CONDITIONS)):
                    calibrators=anchors_for(seed,regime,cond)
                    truebits=[];observations=[]
                    for role in range(3):
                        truth,latent,obs=make(seed,role,regime,cond,10000+role)
                        truebits.append(truth);observations.append(obs)
                        if cond!=3:
                            pairs.append((latent,int(obs[0]>.5)))
                        first_values.append(obs[0])
                    truth=compose(truebits,family)
                    answers={"privileged_oracle":truth};receipt={}
                    for arm in ARMS[:-1]:
                        outputs=[];trace=[]
                        for o in observations:
                            j=decision(o[0],calibrators,arm)
                            # The only target-channel observations passed to decoder
                            # are first and purchased second; never other two readings.
                            p=decode(o[0],o[j],j,calibrators)
                            outputs.append(p>=.5)
                            trace.append((0,j))
                        answers[arm]=compose(outputs,family)
                        receipt[arm]=trace
                    rows.append(dict(seed=seed,family=family,regime=regime,
                                     condition=CONDITIONS[cond],truth=truth,
                                     answers=answers,trace=receipt,
                                     external_calibration_bytes=ANCHORS*5*8,
                                     reads_per_role=2))
                    if cond!=3:
                        for a,b in ((.2,.8),(.35,.65)):
                            switches+=decision(a,calibrators,"conditional_empirical")!=decision(b,calibrators,"conditional_empirical")
                            attempts+=1
    scores={arm:score(rows,arm) for arm in ARMS}
    best=max(scores[a]["accuracy"] for a in ARMS[0:4])
    mi=information(pairs)
    sr=switches/attempts
    eligibility=(1-best>=.04 and best<=.94 and mi>=.015 and sr>=.05)
    return dict(schema="yggdrasil.f31.train-only-headroom-pilot.v1",status="PRE_ORIGINAL_ONLY",
                train_only_seeds=[181000,181032],reserved_test_seeds=[182000,182012],
                pilot_families=PILOT_FAMILIES,reserved_test_families=RESERVED_TEST_FAMILIES,
                conditions=CONDITIONS,regimes=REGIMES,questions=len(rows),
                scores=scores,first_observation_mutual_information_bits=mi,
                empirical_action_switch_rate=sr,matched_target_reads_per_role=2,
                native_state_limit_bytes=576,external_calibration_bytes_per_query=ANCHORS*5*8,
                privileged_reference_correct=len(rows),
                rows=rows,policy_train_not_started=True,reserved_original_not_executed=True,
                sealed_first_use=False,independent_F3_custody=False,accepted_ref_mutation=False,
                verdict="PILOT_HEADROOM_ELIGIBLE_FOR_NEW_SEPARATE_SOURCE_QUALIFICATION" if eligibility else
                "PILOT_HEADROOM_NOT_QUALIFIED_NO_ORIGINAL")
if __name__=="__main__":print(json.dumps(run(),indent=2,sort_keys=True))

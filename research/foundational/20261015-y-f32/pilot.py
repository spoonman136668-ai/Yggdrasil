"""Y-F32 distinct TRAIN-only observability and headroom audit.

No reserved primary-test observations are generated. This is a new pilot,
not a reinterpretation or rerun of the frozen Y-F31 failed pilot.
Public labeled anchors reveal neither latent mode nor test truth; only
empirical calibration of which source has lower Brier loss.
"""
from __future__ import annotations
import json, math, random, importlib.util, sys
from collections import Counter
from pathlib import Path
spec=importlib.util.spec_from_file_location("yf32_custody",Path(__file__).resolve().parents[1]/"20261015-y-f28"/"sensor_custody.py")
custody=importlib.util.module_from_spec(spec);sys.modules[spec.name]=custody;spec.loader.exec_module(custody)

SEEDS=range(183100,183124)
RESERVED=range(184000,184012)
RESERVED_FAMILIES=(174,175,176,177)
REGIMES=(0,1,2)
CONDITIONS=("ordinary","missing","anchor-corruption","low-coverage")
N_ANCHORS=12
def source(seed,role,regime,cond,episode):
    rng=random.Random(seed*1000003+role*9511+regime*10007+cond*997+episode*137)
    label=rng.randrange(2);mode=rng.randrange(2)
    invert= -1 if regime==1 else 1
    amp=.29 if regime!=2 else .035
    first=max(0.,min(1.,.5+invert*(2*mode-1)*amp+rng.gauss(0,.13 if regime!=2 else .23)))
    y=2*label-1
    values=[first]
    for j in (1,2,3):
        useful=(j==1 and mode==0) or (j==2 and mode==1)
        strength=(.38 if useful else -.015) if j!=3 else .20
        noise=.16 if useful else .25
        if cond==1 and j==2 and rng.random()<.19:
            values.append(.5);continue
        if cond==2 and j==2:strength=-strength
        if cond==3:noise*=1.3
        values.append(max(0.,min(1.,.5+y*strength+rng.gauss(0,noise))))
    return label,mode,tuple(values)

def anchors(seed,regime,cond):
    return tuple((t,v) for i in range(N_ANCHORS)
                 for t,_,v in [source(seed+60000+11*i,i%4,regime,cond,1000+i)])

def latent_information(rows):
    # Diagnostic only: latent mode appears here, never in policy signatures.
    n=len(rows); joint=Counter(rows); a=Counter(m for m,x in rows);b=Counter(x for m,x in rows)
    return sum(c/n*math.log2(c*n/(a[m]*b[x])) for (m,x),c in joint.items() if c)

def brier(label,reading):
    return ((reading-.5)*2-label*2+1)**2

def polarity_from_public(refs):
    # Sign of relation between first hint and second-source comparative
    # error, estimated only from 12 public labeled anchors; no latent mode.
    pairs=[]
    for truth,values in refs:
        error1=(values[1]-truth)**2
        error2=(values[2]-truth)**2
        pairs.append(((values[0]-.5),error2-error1))
    covariance=sum(x*y for x,y in pairs)/len(pairs)
    return 1 if covariance>=0 else -1

def empirical_risks(refs,first):
    weights=[math.exp(-8*abs(first-v[0])) for t,v in refs]
    mass=sum(weights)+1.e-12
    return {j:sum(w*(v[j]-t)**2 for (t,v),w in zip(refs,weights))/mass for j in (1,2,3)}

def decide(public,reading,arm):
    if arm=="static":
        return min((1,2,3),key=lambda j:(sum((v[j]-t)**2 for t,v in public)/len(public),j))
    if arm=="empirical":
        rs=empirical_risks(public,reading.value)
        return min((1,2,3),key=lambda j:(rs[j],j))
    if arm=="polarity":
        sign=polarity_from_public(public)
        # Source 1 reliable for latent mode=0. Marker sign maps to mode
        # using TRAIN-only public calibration, never hidden regime name.
        first_positive=(reading.value>=.5)
        return 2 if (first_positive if sign<0 else not first_positive) else 1
    if arm=="fixed":return 3
    raise ValueError("unknown source-selection arm")

def diagnostic():
    assert not set(SEEDS)&set(RESERVED)
    rows=[];latent_pairs=[];per_regime={str(r):[] for r in REGIMES}
    causal_switch=0;attempts=0
    for seed in SEEDS:
        for regime in REGIMES:
            for cond in range(len(CONDITIONS)):
                ref=anchors(seed,regime,cond)
                public=custody.PublicSensorInfo(
                    tuple(sum((v[j]-.5)*(t*2-1) for t,v in ref)/len(ref) for j in range(4)),
                    tuple(sum(v[j]==.5 for t,v in ref)/len(ref) for j in range(4)))
                for role in range(4):
                    truth,latent,tape=source(seed,role,regime,cond,9000+role)
                    if regime!=2:latent_pairs.append((latent,int(tape[0]>=.5)))
                    per_regime[str(regime)].append((latent,int(tape[0]>=.5)))
                    choices={};answers={};receipts={}
                    for arm in ("polarity","empirical","static","fixed"):
                        receipt=custody.evaluate_policy(tape,public,lambda p:0,
                            lambda p,first,method=arm:decide(ref,first,method),576,len(ref)*40)
                        assert receipt.physical_reads==2 and receipt.trace[0].sensor==0
                        choices[arm]=receipt.trace[1].sensor
                        answers[arm]=receipt.trace[1].value>=.5
                        receipts[arm]=[r.sensor for r in receipt.trace]
                    rows.append(dict(seed=seed,regime=regime,condition=CONDITIONS[cond],
                       truth=bool(truth),mode=latent,first=tape[0],polarity=polarity_from_public(ref),
                       choices=choices,answers=answers,receipts=receipts))
                for left,right in ((.2,.8),(.35,.65)):
                    a=custody.PurchasedReading(0,left);b=custody.PurchasedReading(0,right)
                    causal_switch+=decide(ref,a,"polarity")!=decide(ref,b,"polarity")
                    attempts+=1
    n=len(rows)
    scores={}
    for arm in ("polarity","empirical","static","fixed"):
        correct=sum(r["answers"][arm]==r["truth"] for r in rows)
        scores[arm]={"correct":correct,"accuracy":correct/n,"total":n}
    pooled=latent_information(latent_pairs)
    stratified={k:latent_information(v) for k,v in per_regime.items()}
    strong=max(scores[a]["accuracy"] for a in ("empirical","static","fixed"))
    rate=causal_switch/attempts
    information_qualified=(pooled>=.015 and min(stratified["0"],stratified["1"])>=.015)
    # Structural headroom is a separate preregistered requirement, not
    # assumed merely because marker polarity is inferable from calibration.
    eligible=(min(stratified["0"],stratified["1"])>=.015 and
       scores["polarity"]["accuracy"]-strong>=.04 and rate>=.05 and strong<=.94)
    return dict(schema="yggdrasil.f32.train-only-observable-polarity.v1",
       stage="TRAIN_SOURCE_ONLY_NO_RESERVED_ORIGINAL",questions=n,
       seeds=[SEEDS.start,SEEDS.stop],reserved_test_seeds=[RESERVED.start,RESERVED.stop],
       reserved_families=RESERVED_FAMILIES,regimes=REGIMES,conditions=CONDITIONS,
       external_calibration_bytes=480,target_reads_per_role=2,native_core_max_bytes=576,
       public_anchor_count=N_ANCHORS,pooled_mode_marker_mi_bits=pooled,
       conditional_mode_marker_mi_bits=stratified,observable_polarity_switch_rate=rate,
       pooled_information_qualified=information_qualified,
       scores=scores,rows=rows,source_born_independently=False,
       reserved_primary_not_executed=True,accepted_ref_mutation=False,
       verdict="TRAIN_HEADROOM_ELIGIBLE_TO_PREPARE_NEW_ORIGINAL" if eligible else
           "TRAIN_HEADROOM_NOT_QUALIFIED_NO_ORIGINAL")
if __name__=="__main__":print(json.dumps(diagnostic(),sort_keys=True,indent=2))

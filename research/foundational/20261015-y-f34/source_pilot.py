"""Y-F34 independent-mechanism TRAIN-only source feasibility, NOT Y-F34 science.

Public instrument metadata (polarity and calibration) is known; latent mode,
task truth and nonpurchased readings are evaluator-only. Different cohort and
source mechanism from negative Y-F33; primary-original identities are guarded.
Project-authored synthetic generator, not independently controlled F3 custody.
"""
from __future__ import annotations
import importlib.util, math, json, random, sys
from pathlib import Path
from collections import Counter
HERE=Path(__file__).resolve().parent
def _load(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    sys.modules[s.name]=m;s.loader.exec_module(m)
    return m
custody=_load("yf34_sensor_custody",HERE.parent/"20261015-y-f28"/"sensor_custody.py")
independent=_load("yf34_evaluator_private",HERE.parent/"20261015-y-f33"/"evaluator_only.py")
SEEDS=range(211800,211824)
FAMILIES=(190,191,192)
RESERVED_SEEDS=range(212800,212816)
RESERVED_FAMILIES=(194,195,196,197)
CONDITIONS=("ordinary","polarity_reversal","weak_marker","uninformative_marker")
MECHANISMS=("mode_switch","anti_correlated_noisy")
ANCHORS=16
ALLOWED_METHODS=("empirical_brier","polarity_bayesian","calibrated_static","fixed","privileged_oracle")
CORE_BYTES=576
EXTERNAL_ANCHOR_BYTES=ANCHORS*5*8

def physical(seed,role,family,condition,mechanism,episode):
    if seed not in SEEDS or family not in FAMILIES:
        raise ValueError("source identity not authorized, reserved primary-original sources denied")
    g=random.Random(seed*131071+role*617+family*19009+condition*7103+mechanism*311+episode*37)
    truth=g.randrange(2)
    mode=g.randrange(2)
    signal=1 if truth else -1
    polarity=-1 if (family+condition+mechanism)%2 else 1
    if condition==1: polarity=-polarity
    mark_strength=.31 if condition in (0,1) else (.15 if condition==2 else 0.0)
    noise=.095 if condition in (0,1) else .15
    hint=max(0.,min(1.,.5+polarity*(2*mode-1)*mark_strength+g.gauss(0,noise)))
    channels=[hint]
    for j in (1,2,3):
        selected=(j==1 and mode==0) or (j==2 and mode==1)
        amplitude=(.39 if selected else .035)
        if j==3:amplitude=.17
        spread=.12 if selected else .22
        if mechanism==1:
            if j==3:amplitude=.23;spread=.16
            if j==2:amplitude=-amplitude;spread=.15 if selected else .22
            if j==1:spread=.17 if selected else .24
        if condition==2 and j==1:spread+=.07
        if condition==3 and j==3:amplitude=.18
        value=max(0.,min(1.,.5+signal*amplitude+g.gauss(0,spread)))
        channels.append(value)
    return truth,mode,tuple(channels),polarity

def public_reference(seed,family,condition,mechanism):
    # Labeled calibration examples are PUBLIC; per-target hidden mode isn't.
    return tuple((truth,measurements) for i in range(ANCHORS)
          for truth,_,measurements,_ in [physical(seed, i%3,family,condition,mechanism,50000+i*19)])

def calibration(records):
    reliability=[]
    missing=[]
    for j in range(4):
        reliability.append(sum((2*y-1)*(2*v[j]-1) for y,v in records)/len(records))
        missing.append(sum(v[j]==.5 for y,v in records)/len(records))
    return custody.PublicSensorInfo(tuple(reliability),tuple(missing))

def estimate_bit(value,sensor,reliability):
    corr=reliability[sensor]
    z=(2*value-1)*corr/(abs(corr)+.05)
    return 1/(1+math.exp(-max(-20,min(20,5*z))))

def choose(method,first,polarity,anchors,public):
    if method=="fixed":return 3
    if method=="calibrated_static":
        return max((1,2,3),key=lambda j:(abs(public.reliability[j]),-j))
    if method=="polarity_bayesian":
        # Known source polarity is publicly declared instrument metadata, not
        # privileged latent mode; first is the actually bought reading.
        mode_guess=int((first-.5)*polarity>=0)
        return 1 if mode_guess==0 else 2
    if method=="empirical_brier":
        risks=[]
        for j in (1,2,3):
            total=weight_sum=0.
            for truth,vals in anchors:
                w=math.exp(-9*abs(vals[0]-first))
                p=estimate_bit(vals[j],j,public.reliability)
                total+=w*(p-truth)**2
                weight_sum+=w
            risks.append(total/(weight_sum+1.e-12))
        return (1,2,3)[min(range(3),key=lambda idx:(risks[idx],idx))]
    raise ValueError("unknown action policy")

def task(bits,family):
    return bool(bits[0]^bits[1]^bits[2]) if family%2==0 else sum(bool(z) for z in bits)>=2

def count(rows,name):
    n=len(rows);correct=sum(r["predictions"][name]==r["truth"] for r in rows)
    return dict(correct=correct,total=n,accuracy=correct/n,fp=sum(r["predictions"][name] and not r["truth"] for r in rows),
                fn=sum(not r["predictions"][name] and r["truth"] for r in rows))

def group_mi(rows,conditioned):
    # Evaluator-only independent MI formula based on entropy difference.
    def entropy(vals):
        if not vals:return 0.
        counts=Counter(vals);size=len(vals)
        return -sum(v/size*math.log2(v/size) for v in counts.values())
    groups={p:[(m,s) for m,s,p0 in rows if p0==p] for p in (-1,1)} if conditioned else {0:[(m,s) for m,s,p in rows]}
    out=0.
    for a in groups.values():
        if not a:continue
        p=len(a)/len(rows)
        out+=p*(entropy([m for m,s in a])+entropy([s for m,s in a])-entropy(a))
    return out

def train_only():
    assert not set(SEEDS)&set(RESERVED_SEEDS)
    assert not set(FAMILIES)&set(RESERVED_FAMILIES)
    rows=[];evaluator_latent=[]
    switch_count=switch_total=0
    for seed in SEEDS:
      for family in FAMILIES:
       for cond in range(4):
        for mechanism in range(2):
            anchors=public_reference(seed,family,cond,mechanism)
            pub=calibration(anchors)
            target=[physical(seed,r,family,cond,mechanism,9000+r) for r in range(3)]
            first_orientation=target[0][3]
            if not all(t[3]==first_orientation for t in target):raise ValueError("public polarity not stable")
            evaluator_latent.extend((mode,int(values[0]>=.5),int(first_orientation)) for bit,mode,values,pol in target)
            true=task([t[0] for t in target],family)
            predictions={"privileged_oracle":true};receipts={}
            for method in ALLOWED_METHODS[:-1]:
                bits=[];paths=[]
                for truth,mode,values,polarity in target:
                    rec=custody.evaluate_policy(values,pub,lambda _:0,
                         lambda p,f,name=method:choose(name,f.value,first_orientation,anchors,p),
                         CORE_BYTES,EXTERNAL_ANCHOR_BYTES)
                    a,b=rec.trace
                    if rec.physical_reads!=2 or a.sensor!=0 or b.sensor==0:
                        raise ValueError("two read boundary violated")
                    bits.append(estimate_bit(b.value,b.sensor,pub.reliability)>=.5)
                    paths.append((a.sensor,b.sensor))
                predictions[method]=task(bits,family)
                receipts[method]=paths
            if cond!=3:
                for low,high in ((.2,.8),(.35,.65)):
                    switch_count+=choose("empirical_brier",low,first_orientation,anchors,pub)!=choose("empirical_brier",high,first_orientation,anchors,pub)
                    switch_total+=1
            rows.append(dict(seed=seed,family=family,condition=CONDITIONS[cond],mechanism=MECHANISMS[mechanism],
                public_polarity=first_orientation,truth=true,predictions=predictions,physical_receipts=receipts,
                public_reference_anchors=ANCHORS))
    independent_stats=independent.independently_audit({"evaluator_only_private_mode_information":evaluator_latent})
    conditioned_mi=group_mi(evaluator_latent,True)
    pooled_mi=group_mi(evaluator_latent,False)
    if abs(conditioned_mi-independent_stats["conditional_mutual_information_bits"])>1.e-10:
        raise ValueError("independent evaluator conditioned MI disagreement")
    if abs(pooled_mi-independent_stats["pooled_mutual_information_bits"])>1.e-10:
        raise ValueError("independent evaluator pooled MI disagreement")
    # Independent refold predictive logloss uses only already-consumed TRAIN
    # records; reserved original identities are never generated.
    predictive_gain=independent_stats["heldout_conditional_logloss_gain_nats"]
    summary={a:count(rows,a) for a in ALLOWED_METHODS}
    headroom=1-max(summary[a]["accuracy"] for a in ALLOWED_METHODS[:-1])
    rate=switch_count/max(1,switch_total)
    eligible=conditioned_mi>=.02 and predictive_gain>=.01 and headroom>=.04 and rate>=.05
    return dict(schema="yggdrasil.f34.distinct-sensor-train-only.v1",stage="PRE_ORIGINAL_TRAIN_ONLY",
        source_seeds=[SEEDS.start,SEEDS.stop],source_families=FAMILIES,
        reserved_primary_seeds=[RESERVED_SEEDS.start,RESERVED_SEEDS.stop],
        reserved_primary_families=RESERVED_FAMILIES,
        conditions=CONDITIONS,mechanisms=MECHANISMS,
        questions=len(rows),scores=summary,rows=rows,
        conditional_mi_bits=conditioned_mi,pooled_mi_bits=pooled_mi,
        heldout_conditional_logloss_gain_nats=predictive_gain,
        empirical_action_switch_rate=rate,headroom_fraction=headroom,
        evaluator_independent_implementation_agreement=True,
        evaluator_source_independently_controlled_F3=False,
        evaluator_hidden_mode_never_provided_to_action=True,
        exact_two_reads_per_role=True,native_core_576_bytes_assertion_not_python_heap_measurement=True,
        external_anchor_bytes=EXTERNAL_ANCHOR_BYTES,primary_original_not_executed=True,
        verdict="TRAIN_ONLY_DISTINCT_CONDITIONAL_SOURCE_ELIGIBLE" if eligible else "TRAIN_ONLY_DISTINCT_CONDITIONAL_SOURCE_BLOCKED",
        accepted_ref_mutation=False,paid_api_calls=0)
if __name__=="__main__":print(json.dumps(train_only(),sort_keys=True,indent=2))

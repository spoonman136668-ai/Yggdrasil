"""Y-F33 non-consuming TRAIN-only source and information-value feasibility.

Qualified evaluator-only metadata is exported separately, *not* passed to
selection. Reuses prior physical two-channel purchase boundary. This branch
does NOT learn/execute Y-F33 primary original; it tests an alternative source
family with two sensor wiring mechanisms and untouched future test identities.
"""
from __future__ import annotations
import importlib.util
import json
import math
import random
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
PRIOR=HERE.parent/"20261015-y-f32"/"pilot.py"
s=importlib.util.spec_from_file_location("yf33_prior_source",PRIOR)
prior=importlib.util.module_from_spec(s)
sys.modules[s.name]=prior
s.loader.exec_module(prior)
e=importlib.util.spec_from_file_location("yf33_independent_evaluator",HERE/"evaluator_only.py")
evaluator=importlib.util.module_from_spec(e)
sys.modules[e.name]=evaluator
e.loader.exec_module(evaluator)

SEEDS=range(201800,201824)
FAMILIES=(180,181,182)
CONDITIONS=("calibrated_polarity","reversed_public_polarity","weak_marker","noninformative_marker")
MECHANISMS=("mode-conditioned","anti-correlated-auxiliary")
RESERVED_SEEDS=range(202800,202816)
RESERVED_FAMILIES=(184,185,186,187)
ARMS=("conditional_empirical","bayesian_posterior","static","fixed","privileged_oracle")
ANCHORS=12

def source(seed,role,family,condition,mechanism,episode):
    if seed not in SEEDS or family not in FAMILIES:
        raise ValueError("reserved Y-F33 original source identity DENIED")
    truth,mode,base,orientation=prior.obs(seed,role,family+mechanism*10,condition,episode)
    if mechanism==1:
        # Distinct observational mechanism with anti-correlated third channel
        # and an explicitly public polarity descriptor. Latent mode private.
        rng=random.Random(seed*811+role*53+family*31+condition*197+episode*7)
        base=(base[0],base[1],1-base[2],max(0.,min(1.,base[3]+rng.gauss(0,.08))))
        orientation*=-1
    return truth,mode,base,orientation

def anchors(seed,family,condition,mechanism):
    return tuple((truth,readings) for i in range(ANCHORS)
                 for truth,mode,readings,orientation in
                 [source(seed,i%3,family,condition,mechanism,50000+i*17)])

def calibrate(source_anchors):
    r=[];miss=[]
    for j in range(4):
        r.append(sum((2*truth-1)*(2*value[j]-1) for truth,value in source_anchors)/ANCHORS)
        miss.append(sum(value[j]==.5 for _,value in source_anchors)/ANCHORS)
    return prior.custody.PublicSensorInfo(tuple(r),tuple(miss))

def score(rows,arm):
    n=len(rows)
    return dict(correct=sum(r["predictions"][arm]==r["truth"] for r in rows),total=n,
                accuracy=sum(r["predictions"][arm]==r["truth"] for r in rows)/n)

def pilot():
    assert not set(SEEDS)&set(RESERVED_SEEDS)
    assert not set(FAMILIES)&set(RESERVED_FAMILIES)
    rows=[];eval_only=[]
    switched=possible_switches=0
    for seed in SEEDS:
        for family in FAMILIES:
            for condition in range(4):
                for mechanism in range(2):
                    examples=anchors(seed,family,condition,mechanism)
                    pub=calibrate(examples)
                    samples=[source(seed,r,family,condition,mechanism,9000+r) for r in range(3)]
                    public_orientation=samples[0][3]
                    assert all(s[3]==public_orientation for s in samples)
                    for truth,mode,readings,orientation in samples:
                        eval_only.append((int(mode),int(readings[0]>=.5),int(orientation)))
                    query_truth=prior.relation([s[0] for s in samples],family)
                    predictions={"privileged_oracle":query_truth};receipts={}
                    for name in ARMS[:-1]:
                        inferred=[];traces=[]
                        for true_mode,hidden_mode,values,orientation in samples:
                            # Action receives only public metadata, public
                            # train-calibration, and physically bought first value.
                            rec=prior.custody.evaluate_policy(values,pub,lambda _:0,
                                lambda public,first,name=name:prior.choose(
                                    first.value,public_orientation,examples,public,name),
                                576,ANCHORS*5*8)
                            if rec.physical_reads!=2 or rec.trace[0].sensor!=0:
                                raise ValueError("physical budget drift")
                            first,second=rec.trace
                            inferred.append(prior.estimate_bit(first.value,second.value,second.sensor,pub)>=.5)
                            traces.append([first.sensor,second.sensor])
                        predictions[name]=prior.relation(inferred,family)
                        receipts[name]=traces
                    if condition!=3:
                        for low,high in ((.2,.8),(.35,.65)):
                            a=prior.choose(low,public_orientation,examples,pub,"conditional_empirical")
                            b=prior.choose(high,public_orientation,examples,pub,"conditional_empirical")
                            switched+=a!=b
                            possible_switches+=1
                    rows.append(dict(seed=seed,family=family,condition=CONDITIONS[condition],
                        mechanism=MECHANISMS[mechanism],public_orientation=public_orientation,
                        truth=query_truth,predictions=predictions,acquisition_receipts=receipts,
                        public_anchor_count=ANCHORS))
    metrics=evaluator.independently_audit({"evaluator_only_private_mode_information":eval_only})
    expected=prior.mutual_info(eval_only,True)
    if abs(expected-metrics["conditional_mutual_information_bits"])>1e-10:
        raise ValueError("independent MI cross-check mismatch")
    expected_gain=prior.cv_gain(eval_only)
    if abs(expected_gain-metrics["heldout_conditional_logloss_gain_nats"])>1e-10:
        raise ValueError("independent predictive-source cross-check mismatch")
    scores={name:score(rows,name) for name in ARMS}
    headroom=1-max(scores[name]["accuracy"] for name in ARMS[:-1])
    switch=switched/max(1,possible_switches)
    qualified=(metrics["conditional_mutual_information_bits"]>=.02 and
        metrics["heldout_conditional_logloss_gain_nats"]>=.01 and
        switch>=.05 and headroom>=.04 and scores["privileged_oracle"]["correct"]==len(rows))
    return dict(schema="yggdrasil.f33.train-only-dual-implementation-source.v1",
        status="TRAIN_ONLY_QUALIFICATION_NO_SCIENCE_ORIGINAL",
        source_train_seeds=[SEEDS.start,SEEDS.stop],
        reserved_original_seeds=[RESERVED_SEEDS.start,RESERVED_SEEDS.stop],
        source_families=FAMILIES,reserved_original_families=RESERVED_FAMILIES,
        conditions=CONDITIONS,mechanisms=MECHANISMS,questions=len(rows),
        source_private_mode_evaluator_only=True,
        independent_evaluator_algorithm_crosscheck=True,
        independent_source_custody_F3=False,
        native_core_bytes_asserted_not_runtime_measured=576,
        external_reference_calibration_bytes_per_query=ANCHORS*5*8,
        acquired_target_channels_per_role=2,
        scores=scores,headroom_fraction=headroom,
        empirical_action_switch_rate=switch,
        evaluator_metrics=metrics,rows=rows,
        verdict="TRAIN_ONLY_SOURCE_INFORMATION_GATE_ELIGIBLE" if qualified else "TRAIN_ONLY_SOURCE_INFORMATION_GATE_BLOCKED",
        primary_original_not_executed=True,accepted_ref_mutation=False,paid_api_calls=0)

if __name__=="__main__":print(json.dumps(pilot(),indent=2,sort_keys=True))

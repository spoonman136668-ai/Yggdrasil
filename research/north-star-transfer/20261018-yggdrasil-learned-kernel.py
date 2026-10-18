"""Ygg T1: 144-byte learned causal path-retention state — nonconsuming.

A pure public-only kernel to be integrated with exact F62 native legal actions
*after* source and full workload qualification. It does not quietly replace
F60, invoke a future answer oracle or import source generators.
"""
from __future__ import annotations
import math

RECORDS=10
RECORD_BYTES=12
PARAMS=20
HEADER=4
MEMORY=RECORDS*RECORD_BYTES+PARAMS+HEADER
assert MEMORY==144

def need(ok,reason):
    if not ok:raise ValueError("YGG_TRANSFER_"+reason)
def clamp(x):return min(127,max(-128,int(round(x))))
def raw_records(state):
    need(type(state) is bytes and len(state)==MEMORY,"EXACT_NATIVE_PAYLOAD")
    count=state[-4]
    need(count<=RECORDS,"NATIVE_RECORD_CAP")
    return [state[i*12:(i+1)*12] for i in range(count)]

def fit_train_only(samples):
    """Offline TRAIN teacher supplies signed +/- credit; never to online path."""
    need(type(samples) in (tuple,list) and 1<=len(samples)<=8192,
         "TRAIN_CREDIT_INPUT_BOUND")
    w=[0.0]*PARAMS;work=0
    for epoch in range(2):
        for features,label in samples:
            need(len(features)==PARAMS and label in (-1,0,1)
                 and all(type(v) in (float,int) and math.isfinite(v) and abs(v)<=1
                         for v in features),"PUBLIC_FEATURES_OR_CREDIT_BOUND")
            prediction=math.tanh(sum(w[i]*features[i] for i in range(PARAMS)))
            error=prediction-label
            for i in range(PARAMS):
                w[i]-=0.0625*error*features[i]
                work+=1
    packed=bytes(clamp(x*16)&255 for x in w)
    need(len(packed)==20,"TWENTY_LEARNED_BYTES")
    return packed,{"TRAIN_only_teacher_examples":len(samples),
                   "training_parameter_updates":work,
                   "training_temporary_memory_not_resource_qualified":True}

def start(weights):
    need(type(weights) is bytes and len(weights)==PARAMS,
         "LEARNED_WEIGHTS_EXACT")
    return bytes(RECORDS*RECORD_BYTES)+weights+bytes(HEADER)

def public_features(records,arrived,step):
    """No future events, query, answer, graph family or true source relation."""
    need(type(arrived) is bytes and len(arrived)==RECORD_BYTES and
         0<=step<72 and len(records)<=RECORDS,
         "PUBLIC_12_BYTE_EVENT_AND_STEP")
    u,v,role=arrived[:3]
    count=len(records)
    join_left=sum(r[1]==u for r in records)
    join_right=sum(r[0]==v for r in records)
    role_hits=sum(r[2]==role for r in records)
    duplicate=sum(r[:3]==arrived[:3] for r in records)
    backwards=sum(r[0]==v and r[1]==u for r in records)
    structural=[count/10,step/71,int(u==v),join_left/10,join_right/10,
       role_hits/10,duplicate/10,backwards/10,int(role&1),int(role&2),
       int(role&4),int(u&1),int(v&1),int(u&2),int(v&2),
       int(u==0),int(v==0),int(step>=36),int(count>=8),1.0]
    need(len(structural)==PARAMS and all(0<=x<=1 for x in structural),
         "PUBLIC_STRUCTURAL_STATE")
    return tuple(structural)

def signed(weights):
    return [x if x<128 else x-256 for x in weights]

def public_score(state,arrived,step):
    r=raw_records(state)
    features=public_features(r,arrived,step)
    w=signed(state[120:140])
    return sum(a*b for a,b in zip(w,features))/16,features

def propose(state,arrived,step):
    """Advisory learned score only; legal F62 action selection is NOT installed."""
    score,feat=public_score(state,arrived,step)
    return {"public_structural_utility":score,
            "native_action_authorized":False,
            "target_or_future_used":False,
            "score_feature_count":len(feat),
            "native_persistent_bytes":len(state)}

def choose_native_action(*_):
    raise ValueError("YGG_TRANSFER_F62_NATIVE_LEGAL_ACTION_ADAPTER_NOT_QUALIFIED")

def selftest():
    observed=bytes((1,2,3,0,0,0,0,0,0,0,0,0))
    e=[((1.0 if i==19 else (i%5)/5.0 for i in range(20)),1)]
    # Materialize public TRAIN-only supplied features, not native source cases.
    e=[(tuple(e[0][0]),1),(tuple([0.0]*19+[1.0]),-1)]
    w,cost=fit_train_only(e)
    state=start(w)
    need(len(state)==144 and len(w)==20 and cost["training_parameter_updates"]==80,
         "TRUE_RESOURCE_AND_TRAINED_PARAMS")
    obs=propose(state,observed,11)
    need(obs["score_feature_count"]==20 and not obs["native_action_authorized"],
         "NO_SCIENCE_OR_NATIVE_AUTHORITY")
    try:choose_native_action(state,observed,11)
    except ValueError as exc:need("NOT_QUALIFIED" in str(exc),"FAIL_CLOSED")
    else:raise AssertionError("Native action adapter must be blocked")
    print("YGG_T1_LEARNED_PUBLIC_STATE_SELFTEST=PASS")
    print("YGG_T1_PERSISTENT_LAYOUT_BYTES=144")
    print("YGG_T1_REAL_NATIVE_ACTION_ADAPTER=BLOCKED")
    print("YGG_T1_FULL_COMPUTE_AND_TEMP_MEMORY_QUALIFIED=false")
    print("YGG_T1_NEW_SOURCE_CONSUMED=false")
if __name__=="__main__":selftest()

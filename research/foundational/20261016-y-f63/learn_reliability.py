"""F63 learned public-path robustness, unregistered synthetic preflight only.

Learns structural witness reliability under removal of one observed public edge.
No private question, future-event, FIT, DIAG, or original labels.
"""
from __future__ import annotations
import hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
Q=P/"source_engineering.py"
b=Q.read_bytes()
assert hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()=="6bc6517776604e1f9109da2bbcaabb26e30ab4ca"
spec=importlib.util.spec_from_file_location("f63_prototype",Q)
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
f62=m.load("f63_trainonly_f62","source_pilot.py")
packing=f62.codec()
def examples_from_public(public):
    examples=[]
    for stop in (12,24,36,48,60,72):
        observed=public[:stop]
        memory=()
        for event in observed:
            edge=packing.edge_record(event)
            proposals=packing.candidates(list(memory),edge)
            memory=(memory+(edge,))[-12:]
            for _index,rec in proposals:
                if 1<len(rec[2])<=6:
                    features=m.reliability_features(observed,rec)
                    if not features[0]:
                        continue
                    # Stability against one observed edge removal. This is a
                    # public structural label, never the future task answer.
                    probe_indices=(0,len(observed)//2,len(observed)-1)
                    stable=sum(int(m.reliability_features(
                        observed[:idx]+observed[idx+1:],rec)[0])
                        for idx in probe_indices)
                    examples.append((features,stable))
    return examples
def train():
    data=[]
    for seed,family in ((-101,-2),(-102,-1),(-103,-2),(-104,-1),
                        (-105,-2),(-106,-1),(-107,-2),(-108,-1)):
        tagged,_question,_paths,_regime=f62._construct(seed,family)
        data.extend(examples_from_public(tuple(x[:3] for x in tagged)))
    assert data,"SYNTHETIC_RELIABILITY_EXAMPLES_REQUIRED"
    weights=[0.0]*4
    # Fixed, bounded update schedule, no heldout selection or tuning.
    for _ in range(3):
        for features,target in data:
            x=[min(v,16)/16 for v in features]
            predicted=sum(a*b for a,b in zip(weights,x))
            error=target/3-predicted
            for j in range(4):
                weights[j]+=.01*error*x[j]
    quant=tuple(max(-127,min(127,round(v*32))) for v in weights)
    assert len(quant)==4
    for seed,family in ((-109,-2),(-110,-1)):
        tagged,q,_paths,_regime=f62._construct(seed,family)
        public=tuple(row[:3] for row in tagged)
        retained,trace=m.select(public,packing,quant,True)
        auditor=m.load("f63_trainonly_auditor","audit_public.py")
        assert auditor.verify(public,q,trace)["prefixes"]==72
        assert len(retained)*12<=144
    return dict(schema="yggdrasil.f63.synthetic-reliability-training.v1",
         status="UNREGISTERED_SYNTHETIC_ONLY",weights=quant,
         training_examples=len(data),synthetic_training_cases=8,
         synthetic_guard_cases=2,FIT_executed=False,
         validation_executed=False,original_executed=False,independent_F3=False)
if __name__=="__main__":
    assert sys.argv[1:]==["--synthetic-only"]
    print(json.dumps(train(),sort_keys=True))

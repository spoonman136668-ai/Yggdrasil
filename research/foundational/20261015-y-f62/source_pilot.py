"""Y-F62: new causal action-value source and bounded public-only online learner.

Frozen prereg at Git blob f0fffb43fc1f344261c4802d917696aaf4035ce0.
This code is engineering-only. No FIT/DIAG/original execution, validation,
first-use qualification or independent scientific result follows from it.
"""
from __future__ import annotations
import hashlib, importlib.util, json, math, random, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
FIT=range(761000,761016)
TRAIN=range(761000,761008)
VALIDATE=range(761008,761016)
FAMILIES=(1460,1461,1462,1463)
DIAG=range(761100,761116)
ORIGINAL=range(762000,762016)
CAP=12
RECORD_BYTES=12
PARAMS=12
EVENTS=72
F61_WEIGHTS=(39,11,-10,35,17,18,18,28,-7,-83,12,1)
CONTROL_BLOBS={
    "f61":"68827a45543639585da82d05e5d301782fbc79a6",
    "f52_codec":"ef06d80c127ca6dab1e496fb855eb36f0dce6d17",
    "f60":"123dd7e979485ae07664118f948cd651b0386526",
    "f59":"232cf1bca7e2d1df5236ffa85c0a20f13a98a6ae",
    "f58":"f275d28e3755e2c90ea482d076d7401d722d71b8",
}
def _git_blob(path):
    b=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+bytes([0])+b).hexdigest()

def _load_source(name,path,expected_blob):
    if _git_blob(path)!=expected_blob:
        raise AssertionError("FROZEN_HISTORICAL_SOURCE_DRIFT: "+name)
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module

def controls():
    codec_source=HERE.parent/"20261015-y-f52"/"source_pilot.py"
    if _git_blob(codec_source)!=CONTROL_BLOBS["f52_codec"]:
        raise AssertionError("FROZEN_TRANSITIVE_CODEC_SOURCE_DRIFT")
    f60=_load_source("f62_hist_f60",HERE.parent/"20261015-y-f60"/"source_feasibility.py",CONTROL_BLOBS["f60"])
    f59=_load_source("f62_hist_f59",HERE.parent/"20261015-y-f59"/"source_feasibility.py",CONTROL_BLOBS["f59"])
    f58=_load_source("f62_hist_f58",HERE.parent/"20261015-y-f58"/"source_feasibility.py",CONTROL_BLOBS["f58"])
    f61=_load_source("f62_hist_f61",HERE.parent/"20261015-y-f61"/"source_pilot.py",CONTROL_BLOBS["f61"])
    return f60,f59,f58,f61

# The codec's immutable F60 source is SHA-checked before use.
def codec():
    return controls()[0].codec

def _construct(seed,family):
    """Public synthetic stream generator. No scientific read until authorized."""
    rng=random.Random(seed*35771+family*4283+62047)
    used=set()
    def node():
        while True:
            value=rng.randrange(1000,1500000000)
            if value not in used:
                used.add(value)
                return value
    paths=[]
    for _ in range(4):
        nodes=[node() for _ in range(9)]
        if nodes[0]>nodes[-1]:
            nodes.reverse()
        ops=[];edges=[]
        for i in range(8):
            role=rng.choice([r for r in range(4) if not ops or ops[-1][0]!=r])
            direction=1 if rng.random()<.5 else -1
            a,b=nodes[i:i+2]
            edges.append((a,role,b) if direction==1 else (b,role,a))
            ops.append((role,direction))
        paths.append((tuple(nodes),tuple(ops),tuple(edges)))
    distractors=[]
    for _ in range(8):
        ns=[node() for _ in range(4)]
        for j in range(3):
            # Odd-family streams include actual three-leaf public hubs.
            # These are distracting structural alternatives, not truth tags.
            a,b=(ns[0],ns[j+1]) if family%2 else tuple(ns[j:j+2])
            if rng.random()<.5:
                a,b=b,a
            distractors.append((a,rng.randrange(4),b))
    for _ in range(8):
        ns=[node() for _ in range(3)]
        for j in range(2):
            a,b=ns[j:j+2]
            if rng.random()<.5:
                a,b=b,a
            distractors.append((a,rng.randrange(4),b))
    assert len(distractors)==40
    order=list(range(4))
    rng.shuffle(order)
    public=[]
    if family%2==0:
        regime="delayed_public_joins"
        # Four disconnected odd/even portions first, then connectors.
        # All 8 edges of each public component still eventually arrive.
        for k in order:
            public.extend(paths[k][2][::2])
            public.extend(distractors[2*k:2*k+2])
        for k in order:
            public.extend(paths[k][2][1::2])
            public.extend(distractors[8+2*k:8+2*k+2])
        public.extend(distractors[16:])
    else:
        regime="rolling_interleaved_hubs"
        for phase in range(4):
            for k in order:
                public.extend(paths[k][2][2*phase:2*phase+2])
            public.extend(distractors[10*phase:10*phase+10])
    assert len(public)==EVENTS and len(set(public))==EVENTS
    core={e for _,_,edges in paths for e in edges}
    core_tags=[1]*16+[0]*16
    noise_tags=[1]*20+[0]*20
    rng.shuffle(core_tags);rng.shuffle(noise_tags)
    ci=iter(core_tags);ni=iter(noise_tags)
    tagged=tuple((*e,next(ci) if e in core else next(ni)) for e in public)
    selected=paths[rng.randrange(4)]
    hops=(4,6,8)[(seed+family)%3]
    question=dict(start=selected[0][0],ops=selected[1][:hops],
                  answer=selected[0][hops])
    return tagged,question,tuple(paths),regime

def source(seed,family):
    if seed not in FIT or family not in FAMILIES:
        raise ValueError("Y-F62 only disjoint frozen FIT identities allowed")
    return _construct(seed,family)

def synthetic_smoke():
    """Engineering-only synthetic negative seed: never a registered FIT case."""
    return _construct(-71,-2)

def _public_record(event,packing):
    assert len(event)==3, "NO_PUBLIC_TAG_OR_FUTURE_QUERY_ONLINE"
    return packing.edge_record(tuple(event))

def _valid_memory(records,packing):
    assert len(records)<=CAP
    assert all(1<=len(x[2])<=6 for x in records)
    assert all(packing.unpack(packing.pack(*x))==x for x in records)
    assert len(records)*RECORD_BYTES<=144

def _features(records,index,selected,merged,evicted):
    # Online-only candidate features; no question, truth or future events.
    lengths=[len(r[2]) for r in records]
    endpoint_degree={}
    for a,b,_ in records:
        endpoint_degree[a]=endpoint_degree.get(a,0)+1
        endpoint_degree[b]=endpoint_degree.get(b,0)+1
    connectivity=sum(int(endpoint_degree.get(a,0)>1 or
                         endpoint_degree.get(b,0)>1) for a,b,_ in records)
    return (1.0,len(selected[2])/6,int(merged),int(evicted),
            sum(lengths)/72,max(lengths,default=0)/6,
            sum(int(x>=2) for x in lengths)/12,
            sum(int(x>=4) for x in lengths)/12,
            len({x//2 for rec in records for x in rec[2]})/4,
            connectivity/12,index/71,len(records)/12)

def actions(memory,event,index,packing):
    """Enumerate only causal append/merge/evict candidates under exact budget."""
    incoming=_public_record(event,packing)
    source_candidates=[("append",-1,incoming)]
    for old,merged in packing.candidates(list(memory),incoming):
        if 1<len(merged[2])<=6 and merged[0]!=merged[1]:
            source_candidates.append(("merge",old,merged))
    out=[]
    seen=set()
    for action,old,record in source_candidates:
        # Merge consumes one existing record; append never reads discarded state.
        prior=tuple(rec for at,rec in enumerate(memory) if at!=old)
        extended=prior+(record,)
        drops=(-1,) if len(extended)<=CAP else tuple(range(len(extended)))
        for dropped in drops:
            after=tuple(rec for j,rec in enumerate(extended) if j!=dropped)
            if dropped==len(extended)-1:
                # Explicit rejection of incoming candidate is a legitimate
                # evict-current action under the fixed 12-record constraint.
                pass
            key=after
            if key in seen:
                continue
            seen.add(key)
            _valid_memory(after,packing)
            out.append((action,old,dropped,after,
                       _features(after,index,record,action=="merge",dropped>=0)))
    assert out
    return tuple(out)

def _score(weights,features):
    assert len(weights)==PARAMS and all(-127<=w<=127 for w in weights)
    return sum((w/16)*x for w,x in zip(weights,features))

def learned_online(public,weights,packing):
    memory=()
    selected_actions=[]
    for index,event in enumerate(public):
        choices=actions(memory,event,index,packing)
        # Deterministic tie break avoids source-dependent candidate iteration.
        best=max(range(len(choices)),key=lambda j:(_score(weights,choices[j][4]),-j))
        action,old,drop,memory,_=choices[best]
        selected_actions.append((action,old,drop))
    _valid_memory(memory,packing)
    return memory,tuple(selected_actions)

def _f60_step(memory,event,packing):
    incoming=_public_record(event,packing)
    proposals=[(at,merged) for at,merged in packing.candidates(list(memory),incoming)
               if len(merged[2])<=4]
    if proposals:
        old,incoming=max(proposals,key=lambda t:(len(t[1][2]),-t[0]))
        memory=tuple(rec for j,rec in enumerate(memory) if j!=old)
    memory=memory+(incoming,)
    if len(memory)>CAP:
        drop=min(range(len(memory)),key=lambda i:(len(memory[i][2]),i))
        memory=tuple(r for i,r in enumerate(memory) if i!=drop)
    _valid_memory(memory,packing)
    return memory

def _finish_fixed(memory,public_suffix,packing):
    for event in public_suffix:
        memory=_f60_step(memory,event,packing)
    return memory

def train_action_advantage(packing):
    """FIT-TRAIN only; offline future-question supervision, never online leakage.

    Counterfactual labels compare alternative actions at a fixed public prefix
    using the exact same future public suffix under a frozen F60 continuation.
    Only training questions label decisions. Does NOT touch heldout FIT or DIAG.
    """
    examples=[]
    for seed in TRAIN:
        for family in FAMILIES:
            tagged,q,_paths,_regime=source(seed,family)
            public=tuple(event[:3] for event in tagged)
            mem=()
            for index,event in enumerate(public):
                candidates=actions(mem,event,index,packing)
                if index in (11,23,35,47,59,71):
                    # Baseline action is the frozen F60 online step.
                    baseline=_f60_step(mem,event,packing)
                    baseline_terminal=_finish_fixed(baseline,public[index+1:],packing)
                    base=int(packing.solve(baseline_terminal,q)==q["answer"])
                    base_features=_features(baseline,index,
                                            _public_record(event,packing),False,False)
                    for action,old,drop,state,feat in candidates:
                        terminal=_finish_fixed(state,public[index+1:],packing)
                        reward=int(packing.solve(terminal,q)==q["answer"])
                        delta=reward-base
                        if delta:
                            # Preference relative to the actual fixed baseline,
                            # not an always-positive membership label.
                            examples.append((tuple(f-b for f,b in
                                                   zip(feat,base_features)),delta))
                mem=_f60_step(mem,event,packing)
    weights=[0.0]*PARAMS
    for _epoch in range(3):
        for features,delta in examples:
            margin=sum(w*x for w,x in zip(weights,features))
            prediction=math.tanh(margin)
            for j,f in enumerate(features):
                weights[j]+=.04*(delta-prediction)*f
    quant=tuple(max(-127,min(127,round(v*16))) for v in weights)
    assert len(quant)==PARAMS
    return quant,len(examples)

def source_only_manifest():
    return dict(schema="yggdrasil.f62.action-value-engineering-source.v1",
                stage="SOURCE_ONLY_NO_FIT_EXECUTED",
                fit=[FIT.start,FIT.stop],train=[TRAIN.start,TRAIN.stop],
                within_fit_validation=[VALIDATE.start,VALIDATE.stop],
                families=list(FAMILIES),diag=[DIAG.start,DIAG.stop],
                original=[ORIGINAL.start,ORIGINAL.stop],
                train_not_executed=True,validation_not_executed=True,
                diagnostic_not_executed=True,original_not_executed=True,
                max_records=CAP,payload_bytes=CAP*RECORD_BYTES,
                model_bytes=PARAMS,native_576B_not_qualified=True,
                independent_F3=False,policy_promotion=False)
if __name__=="__main__":
    if sys.argv[1:]!=["--source-only"]:
        raise SystemExit("F62 source-only manifest; no FIT/DIAG/original run")
    print(json.dumps(source_only_manifest(),sort_keys=True))

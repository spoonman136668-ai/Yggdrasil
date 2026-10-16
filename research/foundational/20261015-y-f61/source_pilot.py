"""Yggdrasil F61 — FIT-supervised future-query-value retention.

Frozen PREREG identity: yggdrasil.f61.learned-future-task-value-retention.prereg.v1
(blob 67de09eecedfb5285e90a634a3e55aafa3e4a369).

New generator: TRAIN seeds 741000..741007, validation 741008..741015;
families 1420..1423. DIAG 741100..741115 and original 742000..742015
are not available from source() and are never used in this module.

Learned policy sees one public edge and at most twelve 12-byte lossless
records; fitted weights only. No public random tag, core identity or future
question may be an online feature. Model weights are counted separately
from serialized memory, and native total 576B is not established.
"""
from __future__ import annotations
import importlib.util,json,math,random,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
def import_source(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m
    spec.loader.exec_module(m)
    return m
f60=import_source("y61_f60_source",HERE.parent/"20261015-y-f60"/"source_feasibility.py")
f59=import_source("y61_f59_fixed",HERE.parent/"20261015-y-f59"/"source_feasibility.py")
f58=import_source("y61_f58_fixed",HERE.parent/"20261015-y-f58"/"source_feasibility.py")
codec=f60.codec
FIT=range(741000,741016)
TRAIN=range(741000,741008)
VALIDATE=range(741008,741016)
FAMILIES=(1420,1421,1422,1423)
DIAG=range(741100,741116)
ORIGINAL=range(742000,742016)
CAP=12
EVENTS=72
PARAMS=12
ARMS=("learned_query_value_retention","F60_like_fixed_online",
      "frozen_F59_deferred","frozen_F58_frontier",
      "fixed_pair_triple_DAG","FIFO_hash",
      "offline_public_noncompetitive","future_query_oracle_unfair")

def source(seed,family):
    if seed not in FIT or family not in FAMILIES:
        raise ValueError("F61 source allows frozen FIT only; no DIAG or original")
    rng=random.Random(seed*34157+family*4199+61041)
    used=set()
    def node():
        while True:
            v=rng.randrange(1000,1500000000)
            if v not in used:
                used.add(v);return v
    paths=[]
    for k in range(4):
        nodes=[node() for _ in range(9)]
        if nodes[0]>nodes[-1]:nodes.reverse()
        steps=[];edges=[]
        for i in range(8):
            role=rng.choice([r for r in range(4)
                             if not steps or steps[-1][0]!=r])
            direction=1 if rng.random()<.5 else -1
            a,b=nodes[i:i+2]
            edges.append((a,role,b) if direction==1 else (b,role,a))
            steps.append((role,direction))
        paths.append((tuple(nodes),tuple(steps),tuple(edges)))
    distractors=[]
    for k in range(8):
        ns=[node() for _ in range(4)]
        for j in range(3):
            a,b=ns[j:j+2]
            if rng.random()<.5:a,b=b,a
            distractors.append((a,rng.randrange(4),b))
    for k in range(8):
        ns=[node() for _ in range(3)]
        for j in range(2):
            a,b=ns[j:j+2]
            if rng.random()<.5:a,b=b,a
            distractors.append((a,rng.randrange(4),b))
    assert len(distractors)==40
    order=list(range(4));rng.shuffle(order)
    regime=("corridor_with_delayed_noise" if family%2==0
            else "half_frontier_with_late_connector")
    public=[]
    if regime=="corridor_with_delayed_noise":
        for k in order:
            public.extend(paths[k][2])
            public.extend(distractors[3*k:3*k+3])
        public.extend(distractors[12:])
    else:
        for k in order:
            public.extend(paths[k][2][:4])
            public.extend(distractors[2*k:2*k+2])
        for k in order:
            public.extend(paths[k][2][4:])
            public.extend(distractors[8+2*k:8+2*k+2])
        public.extend(distractors[16:])
    assert len(public)==72 and len(set(public))==72
    core={e for _,_,edges in paths for e in edges}
    core_bits=[1]*16+[0]*16;dist_bits=[1]*20+[0]*20
    rng.shuffle(core_bits);rng.shuffle(dist_bits)
    ct=iter(core_bits);dt=iter(dist_bits)
    tagged=tuple((*e,next(ct) if e in core else next(dt)) for e in public)
    chosen=paths[rng.randrange(4)]
    hops=(4,6,8)[(seed+family)%3]
    q=dict(start=chosen[0][0],ops=chosen[1][:hops],
           answer=chosen[0][hops])
    return tagged,q,tuple(paths),regime

def flip(rec):
    a,b,c=rec
    return b,a,tuple(x^1 for x in reversed(c))
def true_path_fragments(paths):
    positive=set()
    for nodes,ops,edges in paths:
        codes=tuple(2*r+(direction==-1) for r,direction in ops)
        for first in range(8):
            for length in range(1,min(6,8-first)+1):
                rec=(nodes[first],nodes[first+length],codes[first:first+length])
                positive.add(rec);positive.add(flip(rec))
    return positive

def features(rec,mem,index):
    a,b,code=rec
    deg_a=sum(int(m[0]==a)+int(m[1]==a) for m in mem)
    deg_b=sum(int(m[0]==b)+int(m[1]==b) for m in mem)
    neighbor=sum(int(m[1]==a or m[0]==b) for m in mem)
    length=len(code)
    return (1.,length/6, int(length>1),int(length>=4),
            min(deg_a,12)/12,min(deg_b,12)/12,
            min(neighbor,12)/12,len({x//2 for x in code})/4,
            sum(x&1 for x in code)/length,index/71,
            (length/6)**2, int(a<b))

def proposals(mem,incoming):
    options=[]
    for old_index,rec in codec.candidates(mem,incoming):
        if 1<len(rec[2])<=6 and rec[0]!=rec[1]:
            options.append((old_index,rec))
    return options

def learn():
    # FIT labels are prospective query-distribution utility: each of four
    # independent eight-hop source components can furnish a future question.
    # No validation query or diagnostic label participates in weight fitting.
    observations=[];positives=0
    for seed in TRAIN:
        for family in FAMILIES:
            public,_future,paths,_regime=source(seed,family)
            truth=true_path_fragments(paths)
            mem=[]
            for index,event in enumerate(public):
                incoming=codec.edge_record(event[:3])
                records=[incoming]+[z for _,z in proposals(mem,incoming)]
                for rec in records:
                    y=int(rec in truth)
                    positives+=y
                    observations.append((features(rec,mem,index),y))
                # Training candidate collection uses *fixed* F60-like state.
                # No FIT label affects the state through action selection.
                offers=proposals(mem,incoming)
                if offers:
                    old,merged=max(offers,key=lambda v:(len(v[1][2]),-v[0]))
                    mem=[z for i,z in enumerate(mem) if i!=old]
                    incoming=merged
                mem.append(incoming)
                if len(mem)>CAP:
                    drop=min(range(len(mem)),key=lambda j:(len(mem[j][2]),j))
                    mem.pop(drop)
    assert positives>0 and len(observations)>1000
    w=[0.]*PARAMS
    for epoch in range(3):
        for feat,y in observations:
            zz=max(-12.,min(12.,sum(v*f for v,f in zip(w,feat))))
            prob=1/(1+math.exp(-zz))
            delta=(prob-y)*(3 if y else 1)
            for i in range(PARAMS):
                w[i]-=.018*(delta*feat[i]+.0002*w[i])
    quant=tuple(max(-127,min(127,round(z*16))) for z in w)
    return quant,len(observations),positives

def learned_online(public,w):
    """Causal bounded retention. Input: public edge stream, frozen int8 only."""
    assert len(w)==PARAMS and all(-127<=x<=127 for x in w)
    memory=[];selection_work=0
    for index,event in enumerate(public):
        assert len(event)==3
        incoming=codec.edge_record(event)
        offers=proposals(memory,incoming)
        selection_work+=len(offers)
        if offers:
            # Include no-merge path. Model learns expected future value of a
            # compressed incoming component versus preserving open fragments.
            alternatives=[(-1,incoming)]+offers
            old,selected=max(alternatives,key=lambda v:(
                sum((weight/16)*f for weight,f in zip(
                    w,features(v[1],memory,index))),
                len(v[1][2]),-v[0]))
            if old>=0:
                memory=[r for i,r in enumerate(memory) if i!=old]
            incoming=selected
        memory.append(incoming)
        if len(memory)>CAP:
            drop=min(range(len(memory)),key=lambda j:(
                sum((weight/16)*f for weight,f in zip(
                    w,features(memory[j],memory,index))),j))
            memory.pop(drop)
        assert len(memory)<=CAP
    return tuple(memory),selection_work

def fixed_online(public,arm):
    assert arm in ARMS[1:6]
    if arm=="F60_like_fixed_online":
        return f60.online_fixed(public)
    if arm=="frozen_F59_deferred":
        return f59.fixed_deferred_component_buffer(public)
    if arm=="frozen_F58_frontier":
        return f58.frontier_online(public)
    if arm=="FIFO_hash":
        memory=[]
        for event in public:
            memory.append(codec.edge_record(event))
            if len(memory)>CAP:
                # Fixed deterministic hash+FIFO public-only reference.
                drop=min(range(len(memory)),key=lambda i:(
                    random.Random(memory[i][0]*31+memory[i][1]*47+61061).random(),i))
                memory.pop(drop)
        return tuple(memory)
    # fixed_pair_triple_DAG: deterministic greedy causal pair/triple.
    memory=[]
    for event in public:
        incoming=codec.edge_record(event)
        options=[(i,z) for i,z in proposals(memory,incoming) if len(z[2])<=3]
        if options:
            old,incoming=max(options,key=lambda v:(len(v[1][2]),-v[0]))
            memory=[v for i,v in enumerate(memory) if i!=old]
        memory.append(incoming)
        if len(memory)>CAP:
            memory.pop(min(range(len(memory)),key=lambda i:(len(memory[i][2]),i)))
    return tuple(memory)

def preflight_train():
    w,examples,positive=learn()
    cases=[]
    for seed,family in ((741000,1420),(741001,1421)):
        public,question,paths,regime=source(seed,family)
        public_only=tuple(event[:3] for event in public)
        actual,_=learned_online(public_only,w)
        fixed=fixed_online(public_only,"F60_like_fixed_online")
        offline=f60.offline_public_witness(public_only)
        assert len(actual)<=CAP and len(fixed)<=CAP and len(offline)==CAP
        for name,mem in (("learned",actual),("fixed",fixed),("offline",offline)):
            assert all(codec.unpack(codec.pack(*r))==r for r in mem)
        cases.append(dict(seed=seed,family=family,regime=regime,
            learned_correct=int(codec.solve(actual,question)==question["answer"]),
            fixed_correct=int(codec.solve(fixed,question)==question["answer"]),
            public_offline_correct=int(codec.solve(offline,question)==question["answer"])))
    return dict(schema="yggdrasil.f61.query-value-fit-train-preflight.v1",
        stage="TRAIN_FIT_ONLY_DIAG_NOT_AUTHORIZED",
        labeled_training_cases=32,training_examples=examples,positive_labels=positive,
        int8_weights=list(w),sample_training_cases=cases,
        validation_seeds_NOT_TOUCHED=[VALIDATE.start,VALIDATE.stop],
        diagnostic_NOT_AUTHORIZED=[DIAG.start,DIAG.stop],
        original_NOT_RESERVED=[ORIGINAL.start,ORIGINAL.stop],
        model_parameter_bytes=PARAMS,retention_record_bytes=12,
        retention_cap_bytes=144,whole_native_576B_unverified=True,
        source_independent_F3=False,accepted_ref_mutation=False,
        live_optimizer_unchanged=True,paid_api_calls=0)
if __name__=="__main__":
    if len(sys.argv)!=2 or sys.argv[1]!="--preflight-train":
        raise SystemExit("F61 only FIT TRAIN preflight authorized; no validation/DIAG/original")
    print(json.dumps(preflight_train(),sort_keys=True))

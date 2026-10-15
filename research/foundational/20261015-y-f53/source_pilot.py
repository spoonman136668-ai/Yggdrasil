"""Y-F53: learned future-task-value graph consolidation within 144 payload bytes.

The model learns from FIT-only labeled full trajectories which compressed
relation-state candidates support potential future questions. At diagnostic
time the policy sees only each public incoming relation and its current
bounded memory. The future question is revealed after the memory is frozen.
This is synthetic science, NOT a native 576-byte residency demonstration.
"""
from __future__ import annotations
import importlib.util,json,math,random,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location("y53_f52_lossless_codec",
                                         HERE.parent/"20261015-y-f52"/"source_pilot.py")
codec=importlib.util.module_from_spec(sp);sys.modules[sp.name]=codec;sp.loader.exec_module(codec)
FIT=range(571000,571016)
DIAG=range(571100,571116)
FIT_FAM=(1000,1001,1002,1003)
DIAG_FAM=(1004,1005,1006,1007)
RESERVED=range(572000,572016)
CAP=12
EVENTS=72
DIMS=9
ARMS=("learned_future_value_consolidation","public_greedy_triple_chunks",
      "public_greedy_pair_chunks","public_connected_component_chunks",
      "public_dag_path_compression","raw_degree","raw_FIFO","public_hash",
      "private_future_query_oracle_unfair")
def source(seed,fam):
    if not ((seed in FIT and fam in FIT_FAM) or
            (seed in DIAG and fam in DIAG_FAM)):
        raise ValueError("unregistered FIT/DIAG, forbidden original or mixed family")
    rng=random.Random(seed*21179+fam*1171+53019)
    seen=set()
    def node():
        while True:
            v=rng.randrange(1000,1500000000)
            if v not in seen:seen.add(v);return v
    public=[];paths=[]
    for part in range(4):
        start=at=node();edges=[];ops=[]
        for j in range(8):
            nxt=node()
            options=[k for k in range(4) if not ops or k!=ops[-1][0]]
            role=rng.choice(options)
            direction=1 if rng.random()<.5 else -1
            edge=(at,role,nxt) if direction==1 else (nxt,role,at)
            public.append(edge);edges.append(edge);ops.append((role,direction))
            at=nxt
        paths.append(dict(start=start,answer=at,ops=tuple(ops),edges=tuple(edges)))
    motifs=[]
    if fam in FIT_FAM:
        # Familiar 2- and 3-link typed DAG motifs, all query-disconnected.
        for k in range(8):
            n=[node() for _ in range(6)]
            motif=((n[0],rng.randrange(4),n[1]),
                   (n[1],rng.randrange(4),n[2]),
                   (n[3],rng.randrange(4),n[4]),
                   (n[4],rng.randrange(4),n[5]))
            public.extend(motif);motifs.append(motif)
        for k in range(4):
            n=[node() for _ in range(3)]
            motif=((n[0],rng.randrange(4),n[1]),(n[1],rng.randrange(4),n[2]))
            public.extend(motif);motifs.append(motif)
    else:
        # Heldout cyclic/cross-role motifs, with mixed inverse orientations.
        for k in range(8):
            n=[node() for _ in range(4)]
            roles=rng.sample(range(4),3)
            motif=((n[0],roles[0],n[1]),(n[1],roles[1],n[2]),
                   (n[2],roles[2],n[0]),(n[2],rng.randrange(4),n[3]))
            public.extend(motif);motifs.append(motif)
        for k in range(4):
            n=[node() for _ in range(3)]
            role=rng.randrange(4)
            motif=((n[1],role,n[0]),(n[1],(role+1)%4,n[2]))
            public.extend(motif);motifs.append(motif)
    assert len(public)==72, len(public)
    rng.shuffle(public)
    selected=paths[rng.randrange(4)]
    n=(4,6,8)[(seed+fam)%3]
    at=selected["start"]
    for role,direction in selected["ops"][:n]:
        matched=[e for e in selected["edges"] if e[1]==role and
                 (e[0] if direction==1 else e[2])==at]
        assert len(matched)==1
        a,r,b=matched[0]
        at=b if direction==1 else a
    future=dict(start=selected["start"],ops=selected["ops"][:n],answer=at)
    # Diagnostic memory policies are passed public ONLY, never paths or
    # future. Frozen truth and FIT-only labels stay outside that interface.
    return tuple(public),future,tuple(paths),tuple(motifs)

def chunk_from_path(path,start,length):
    steps=path["edges"][start:start+length]
    ops=path["ops"][start:start+length]
    if not steps:return None
    current=path["start"]
    for r,d in path["ops"][:start]:
        e=next(e for e in path["edges"] if e[1]==r and
               (e[0] if d==1 else e[2])==current)
        current=e[2] if d==1 else e[0]
    left=current
    for r,d in ops:
        e=next(e for e in steps if e[1]==r and
               (e[0] if d==1 else e[2])==current)
        current=e[2] if d==1 else e[0]
    codes=tuple(2*r+(d==-1) for r,d in ops)
    assert length<=6 and len(codes)==length
    return (left,current,codes)

def features(rec,memory,index):
    base=codec.features(rec,memory,index)
    codes=rec[2]
    distinct=len(set(i//2 for i in codes))/4
    reverse=sum(i&1 for i in codes)/6
    return (*base,distinct,reverse)

def sigmoid(z):
    return 1/(1+math.exp(-max(-15,min(15,z))))
def evaluate(rec,memory,index,mode,w):
    v=features(rec,memory,index)
    if mode=="learned_future_value_consolidation":
        return sigmoid(sum(x*y for x,y in zip(w,v)))
    if mode=="public_greedy_pair_chunks":
        return min(len(rec[2]),2)*4+.01*v[2]+.00001*index
    if mode=="public_greedy_triple_chunks":
        return min(len(rec[2]),3)*4+.01*v[2]+.00001*index
    if mode=="public_connected_component_chunks":
        return 4*v[6]+v[2]+.25*v[1]
    if mode=="public_dag_path_compression":
        return 3*v[1]+v[7]+v[6]
    if mode=="raw_degree":return 4*v[2]+v[6]
    if mode=="raw_FIFO":return index/71
    if mode=="public_hash":return codec.hash_value(rec)
    raise ValueError("unregistered public memory method")

def retain(events,mode,w):
    memory=[]
    for i,e in enumerate(events):
        new=codec.edge_record(e)
        may_merge=mode not in ("raw_degree","raw_FIFO","public_hash")
        if may_merge:
            proposals=codec.candidates(memory,new)
            if mode=="public_greedy_pair_chunks":
                proposals=[p for p in proposals if len(p[1][2])<=2]
            if mode=="public_greedy_triple_chunks":
                proposals=[p for p in proposals if len(p[1][2])<=3]
            if mode=="public_dag_path_compression":
                proposals=[p for p in proposals if len(set(p[1][2]))==len(p[1][2])]
            if proposals:
                k,combined=max(proposals,
                     key=lambda option:(evaluate(option[1],memory,i,mode,w),
                                        len(option[1][2]),-option[0]))
                memory=[r for j,r in enumerate(memory) if j!=k]
                new=combined
        memory.append(new)
        if len(memory)>CAP:
            evict=min(range(len(memory)),
                  key=lambda k:(evaluate(memory[k],memory,i,mode,w),k))
            memory.pop(evict)
        assert len(memory)<=CAP
        # Recompute exact bytes every event. No retained side-car indexes,
        # raw source log or private future query for the runtime memory.
        assert all(codec.unpack(codec.pack(*r))==r for r in memory)
    return tuple(memory)

def training_data():
    data=[]
    for seed in FIT:
      for fam in FIT_FAM:
        events,future,paths,motifs=source(seed,fam)
        # FIT supervision uses all four possible future paths as a prior
        # task distribution. Labels are unavailable on new DIAG sources.
        positive=[]
        for path in paths:
            for start in range(8):
                for width in range(1,min(6,8-start)+1):
                    positive.append(chunk_from_path(path,start,width))
        negatives=[codec.edge_record(edge)
                   for motif in motifs for edge in motif]
        # Sample public memory contexts from encountered stream prefix.
        for j,item in enumerate(positive):
            position=(j*5+seed)%len(events)
            mem=tuple(codec.edge_record(e) for e in events[:position][-CAP:])
            data.append((features(item,mem,position),1.))
        for j,item in enumerate(negatives):
            position=(j*7+seed)%len(events)
            mem=tuple(codec.edge_record(e) for e in events[:position][-CAP:])
            data.append((features(item,mem,position),0.))
    return data

def train():
    data=training_data()
    weights=[0.]*DIMS
    for epoch in range(10):
        for feats,label in data:
            p=sigmoid(sum(x*y for x,y in zip(weights,feats)))
            factor=2. if label else 1.
            for j in range(DIMS):
                weights[j]-=.015*(factor*(p-label)*feats[j]+.0005*weights[j])
    # Retain bounded 8-bit weights for a compact scientific pilot.
    quant=[max(-127,min(127,int(round(w*24)))) for w in weights]
    return tuple(v/24 for v in quant),len(data),quant

def run():
    assert not set(FIT)&set(DIAG) and not set(FIT_FAM)&set(DIAG_FAM)
    assert not set(DIAG)&set(RESERVED)
    weights,nfit,packed=train()
    rows=[]
    for seed in DIAG:
      for family in DIAG_FAM:
        public,future,paths,motifs=source(seed,family)
        scores={};receipts={}
        for arm in ARMS[:-1]:
            stored=retain(public,arm,weights)
            scores[arm]=int(codec.solve(stored,future)==future["answer"])
            receipts[arm]=[codec.pack(*r).hex() for r in stored]
        # Retrieval ablation uses the SAME learned stored memory but removes
        # compressed chain decoding from the query-facing mechanism.
        compressed=[codec.unpack(bytes.fromhex(x)) for x in receipts[ARMS[0]]]
        ablated=int(codec.solve([r for r in compressed if len(r[2])==1],future)==future["answer"])
        querypath=paths[0] if False else None
        original=[]
        at=future["start"]
        for role,direction in future["ops"]:
            match=[e for e in public if e[1]==role and
                   (e[0] if direction==1 else e[2])==at]
            if len(match)!=1:raise AssertionError("future query oracle ambiguous")
            edge=match[0];original.append(codec.edge_record(edge))
            at=edge[2] if direction==1 else edge[0]
        scores[ARMS[-1]]=int(codec.solve(original,future)==future["answer"])
        rows.append(dict(seed=seed,family=family,
          public_events=[list(e) for e in public],
          question=dict(start=future["start"],ops=[list(x) for x in future["ops"]],
                        answer=future["answer"]),
          receipts=receipts,answers=scores,
          retrieval_without_composed_chunks=ablated))
    correct={a:sum(r["answers"][a] for r in rows) for a in ARMS}
    scored={a:dict(correct=correct[a],total=len(rows),accuracy=correct[a]/len(rows)) for a in ARMS}
    by_fam={str(f):{a:sum(r["answers"][a] for r in rows if r["family"]==f)
                 for a in ARMS} for f in DIAG_FAM}
    baseline=max(ARMS[1:-1],key=lambda a:correct[a])
    gain=(correct[ARMS[0]]-correct[baseline])/len(rows)
    ablation=(correct[ARMS[0]]-sum(r["retrieval_without_composed_chunks"] for r in rows))/len(rows)
    family_safe=all(by_fam[str(f)][ARMS[0]]>=max(by_fam[str(f)][a] for a in ARMS[1:-1]) for f in DIAG_FAM)
    accepted=gain>=.05 and ablation>0 and family_safe
    return dict(schema="yggdrasil.f53.future-value-chain-memory.trainonly.v1",
      stage="TRAIN_ONLY_UNSEEN_GRAPH_AND_QUESTION_NO_ORIGINAL",
      fit_seeds=[FIT.start,FIT.stop],fit_families=list(FIT_FAM),
      diagnostic_seeds=[DIAG.start,DIAG.stop],diagnostic_families=list(DIAG_FAM),
      proposed_original_NOT_RESERVED=[RESERVED.start,RESERVED.stop],
      train_examples=nfit,learned_weight_int8=list(packed),
      max_records=CAP,serialized_record_bytes=12,serialized_payload_budget=144,
      decoder_metadata_in_record=True,native_576B_total_unverified=True,
      future_question_hidden_during_retention=True,cases=len(rows),rows=rows,
      scores=scored,by_family=by_fam,strongest_equal_byte_fair=baseline,
      candidate_gain=gain,retrieval_ablation_gain=ablation,
      per_family_nondegradation=family_safe,frozen_gate_met=accepted,
      verdict=("TRAIN_ONLY_CHAIN_VALUE_SUPPORTED" if accepted else
               "TRAIN_ONLY_CHAIN_VALUE_NEGATIVE"),
      independent_F3=False,original_executed=False,
      accepted_ref_mutation=False,paid_api_calls=0)
if __name__=="__main__":print(json.dumps(run(),sort_keys=True,indent=2))

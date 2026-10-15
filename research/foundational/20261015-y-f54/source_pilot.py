"""Y-F54: learned global relation-state memory + public-only offline reference.

The model learns from FIT-only labeled full trajectories which compressed
relation-state candidates support potential future questions. At diagnostic
time the policy sees only each public incoming relation and its current
bounded memory. The future question is revealed after the memory is frozen.
This is synthetic science, NOT a native 576-byte residency demonstration.
"""
from __future__ import annotations
import importlib.util,json,math,random,sys
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location("y53_f52_lossless_codec",
                                         HERE.parent/"20261015-y-f52"/"source_pilot.py")
codec=importlib.util.module_from_spec(sp);sys.modules[sp.name]=codec;sp.loader.exec_module(codec)
FIT=range(591000,591016)
DIAG=range(591100,591116)
FIT_FAM=(1060,1061,1062,1063)
DIAG_FAM=(1064,1065,1066,1067)
RESERVED=range(592000,592016)
CAP=12
EVENTS=72
DIMS=12
ARMS=("learned_global_relation_state","F53_frozen_learned_chunker",
      "fixed_public_triple_chunks","fixed_public_pair_chunks",
      "public_connected_component_chunks","public_DAG_path_compression",
      "raw_degree_and_FIFO","public_hash","private_future_question_oracle_unfair")
fsp=importlib.util.spec_from_file_location("y54_frozen_f53_control",HERE.parent/"20261015-y-f53"/"source_pilot.py")
prev=importlib.util.module_from_spec(fsp);sys.modules[fsp.name]=prev;fsp.loader.exec_module(prev)

def source(seed,fam):
    if not ((seed in FIT and fam in FIT_FAM) or
            (seed in DIAG and fam in DIAG_FAM)):
        raise ValueError("unregistered FIT/DIAG, forbidden original or mixed family")
    rng=random.Random(seed*23167+fam*2903+54077)
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
    # Distinct public tag channel is exactly balanced 50% for every role
    # chain edge and distractor. Tags are never kept in compact records.
    core=[e for p in paths for e in p["edges"]]
    noise=[e for motif in motifs for e in motif]
    assert len(core)==32 and len(noise)==40
    core_bits=[1]*16+[0]*16;noise_bits=[1]*20+[0]*20
    rng.shuffle(core_bits);rng.shuffle(noise_bits)
    label={e:b for e,b in zip(core,core_bits)}
    label.update({e:b for e,b in zip(noise,noise_bits)})
    assert len(label)==72
    public_tags=tuple(label[e] for e in public)
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
    return tuple(public),future,tuple(paths),tuple(motifs),public_tags

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
    # Global, query-agnostic summaries from ONLY the currently retained
    # compact graph, not evicted history or private source-class labels.
    base=codec.features(rec,memory,index)
    a,b,codes=rec
    distinct=len({c//2 for c in codes})/4
    inverse=sum(c&1 for c in codes)/6
    degrees=Counter()
    adjacency={}
    for x,y,ops in memory:
        degrees[x]+=1;degrees[y]+=1
        adjacency.setdefault(x,set()).add(y)
        adjacency.setdefault(y,set()).add(x)
    visited={a};queue=[a]
    while queue:
        at=queue.pop()
        for v in adjacency.get(at,()):
            if v not in visited:visited.add(v);queue.append(v)
    component=min(1,len(visited)/14)
    local_degree=min(1,(degrees[a]+degrees[b])/12)
    leaf_fraction=sum(v==1 for v in degrees.values())/max(1,len(degrees))
    return (*base,distinct,inverse,component,local_degree,leaf_fraction)

def sigmoid(z):
    return 1/(1+math.exp(-max(-15,min(15,z))))
def evaluate(rec,memory,index,mode,w):
    v=features(rec,memory,index)
    if mode=="learned_global_relation_state":
        return sigmoid(sum(x*y for x,y in zip(w,v)))
    if mode=="fixed_public_pair_chunks":
        return min(len(rec[2]),2)*4+.01*v[2]+.00001*index
    if mode=="fixed_public_triple_chunks":
        return min(len(rec[2]),3)*4+.01*v[2]+.00001*index
    if mode=="public_connected_component_chunks":
        return 4*v[6]+v[2]+.25*v[1]
    if mode=="public_DAG_path_compression":
        return 3*v[1]+v[7]+v[6]
    if mode=="raw_degree_and_FIFO":return 4*v[2]+v[6]
    if mode=="raw_FIFO":return index/71
    if mode=="public_hash":return codec.hash_value(rec)
    raise ValueError("unregistered public memory method")

def retain(events,mode,w):
    memory=[]
    for i,e in enumerate(events):
        new=codec.edge_record(e)
        may_merge=mode not in ("raw_degree_and_FIFO","raw_FIFO","public_hash")
        if may_merge:
            proposals=codec.candidates(memory,new)
            if mode=="fixed_public_pair_chunks":
                proposals=[p for p in proposals if len(p[1][2])<=2]
            if mode=="fixed_public_triple_chunks":
                proposals=[p for p in proposals if len(p[1][2])<=3]
            if mode=="public_DAG_path_compression":
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
        events,future,paths,motifs,tags=source(seed,fam)
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
    for epoch in range(9):
        for feats,label in data:
            p=sigmoid(sum(x*y for x,y in zip(weights,feats)))
            factor=2. if label else 1.
            for j in range(DIMS):
                weights[j]-=.015*(factor*(p-label)*feats[j]+.0005*weights[j])
    # Retain bounded 8-bit weights for a compact scientific pilot.
    quant=[max(-127,min(127,int(round(w*24)))) for w in weights]
    return tuple(v/24 for v in quant),len(data),quant

def public_offline_reference(events):
    # Noncompetitive, query-blind FULL-PUBLIC graph reference. It sees all
    # 72 public source edges after stream completion (not online 144B).
    # Bounded 6000 public candidate expansions; not a theorem or an oracle.
    adjacency={}
    for a,r,b in events:
        adjacency.setdefault(a,[]).append((b,2*r))
        adjacency.setdefault(b,[]).append((a,2*r+1))
    candidates=[];steps=0
    for begin in sorted(adjacency):
        frontier=[(begin,())]
        for depth in range(1,7):
            next_level=[]
            for node,codes in frontier:
                for end,op in adjacency.get(node,()):
                    steps+=1
                    if steps>6000:break
                    new=codes+(op,)
                    candidates.append((begin,end,new))
                    if depth<6:next_level.append((end,new))
                if steps>6000:break
            if steps>6000:break
            frontier=sorted(next_level,key=lambda z:(z[0],z[1]))[:150]
        if steps>6000:break
    out=[];seen=set()
    for candidate in sorted(candidates,key=lambda v:(-len(v[2]),v[0],v[1],v[2])):
        if candidate not in seen:
            seen.add(candidate);out.append(candidate)
            if len(out)==12:break
    assert all(codec.unpack(codec.pack(*r))==r for r in out)
    return tuple(out),steps

def run():
    assert not set(FIT)&set(DIAG) and not set(FIT_FAM)&set(DIAG_FAM)
    assert not set(DIAG)&set(RESERVED)
    weights,nfit,packed=train()
    f53weights,_,f53packed=prev.train()
    rows=[];reference_work=0;reference_correct=0
    for seed in DIAG:
      for family in DIAG_FAM:
        public,future,paths,motifs,tags=source(seed,family)
        assert len(public)==72 and len(tags)==72
        core={edge for path in paths for edge in path["edges"]}
        assert sum(tag for edge,tag in zip(public,tags) if edge in core)==16
        assert sum(tag for edge,tag in zip(public,tags) if edge not in core)==20
        answers={};receipts={}
        for arm in ARMS[:-1]:
            if arm=="F53_frozen_learned_chunker":
                # Immutable historical policy on new source, not re-fitted.
                stored=prev.retain(public,"learned_future_value_consolidation",f53weights)
            else:stored=retain(public,arm,weights)
            answers[arm]=int(codec.solve(stored,future)==future["answer"])
            receipts[arm]=[codec.pack(*r).hex() for r in stored]
        learned=[codec.unpack(bytes.fromhex(x)) for x in receipts[ARMS[0]]]
        ablated=int(codec.solve([r for r in learned if len(r[2])==1],future)==future["answer"])
        original=next(path for path in paths if path["start"]==future["start"])
        oracle=[codec.edge_record(e) for e in original["edges"][:len(future["ops"])]]
        answers[ARMS[-1]]=int(codec.solve(oracle,future)==future["answer"])
        offline,expansions=public_offline_reference(public)
        ref_correct=int(codec.solve(offline,future)==future["answer"])
        reference_work+=expansions;reference_correct+=ref_correct
        rows.append(dict(seed=seed,family=family,
          public_events=[list(e) for e in public],public_tags=list(tags),
          question=dict(start=future["start"],ops=[list(x) for x in future["ops"]],
                        answer=future["answer"]),
          receipts=receipts,answers=answers,
          retrieval_without_composed_chunks=ablated,
          bounded_offline_public_reference_correct=ref_correct,
          bounded_offline_public_reference_expansions=expansions))
    correct={arm:sum(row["answers"][arm] for row in rows) for arm in ARMS}
    scored={a:dict(correct=correct[a],total=len(rows),accuracy=correct[a]/len(rows)) for a in ARMS}
    by_family={str(f):{a:sum(row["answers"][a] for row in rows if row["family"]==f)
                        for a in ARMS} for f in DIAG_FAM}
    fair=ARMS[1:-1];best=max(fair,key=lambda a:correct[a])
    gain=(correct[ARMS[0]]-correct[best])/len(rows)
    ablation=(correct[ARMS[0]]-sum(row["retrieval_without_composed_chunks"] for row in rows))/len(rows)
    no_reg=all(by_family[str(f)][ARMS[0]]>=max(by_family[str(f)][a] for a in fair) for f in DIAG_FAM)
    qualified=gain>=.05 and ablation>0 and no_reg
    return dict(schema="yggdrasil.f54.global-public-memory.trainonly.v1",
      stage="TRAIN_ONLY_NEW_GLOBAL_QUERY_BLIND_MEMORY_NOT_ORIGINAL",
      fit_seeds=[FIT.start,FIT.stop],fit_families=list(FIT_FAM),
      diagnostic_seeds=[DIAG.start,DIAG.stop],diagnostic_families=list(DIAG_FAM),
      original_seeds_NOT_RESERVED=[RESERVED.start,RESERVED.stop],
      train_examples=nfit,learned_weight_int8=list(packed),
      F53_frozen_learned_weight_int8=list(f53packed),
      max_records=CAP,record_bytes=12,serialized_payload_budget_bytes=144,
      public_tag_core_rate=.5,public_tag_distractor_rate=.5,
      future_question_hidden_until_retention_complete=True,
      cases=len(rows),rows=rows,scores=scored,by_family=by_family,
      strongest_equal_byte_fair=best,candidate_gain=gain,
      retrieval_ablation_gain=ablation,per_family_nondegradation=no_reg,
      bounded_offline_public_reference_correct=reference_correct,
      bounded_offline_public_reference_expansions=reference_work,
      reference_extra_work_noncompetitive=True,
      frozen_gate_met=qualified,
      verdict=("TRAIN_ONLY_GLOBAL_MEMORY_SUPPORTED" if qualified else
               "TRAIN_ONLY_GLOBAL_MEMORY_NEGATIVE"),
      physically_measured_native_total_576B=False,
      independent_F3=False,original_executed=False,accepted_ref_mutation=False,
      paid_api_calls=0)

if __name__=="__main__":print(json.dumps(run(),sort_keys=True,indent=2))

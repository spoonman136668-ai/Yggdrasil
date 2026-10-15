"""Y-F52: tag-balanced topology stress for learned online retention.

Synthetic TRAIN-only science: at every ingest decision only 12 retained edges
and the incoming public edge are available. Neither a future query nor core
membership is exposed to the diagnostic retention policy. FIT labels are
used only in a separate training optimizer.
"""
from __future__ import annotations
import json,math,random
FIT=range(571000,571016)
DIAG=range(571100,571116)
FIT_FAM=(1020,1021,1022,1023)
DIAG_FAM=(1024,1025,1026,1027)
RESERVED=range(572000,572016)
EVENTS=64
CAPACITY=12
F_DIM=8
ARMS=("learned_bridge_retention","learned_topology_retention","public_connected_component",
      "public_degree_adjacency","public_tag_only","FIFO_last12",
      "public_frequency","public_hash","private_future_question_oracle_unfair")
ROLES=(
 ((0,1),(1,1),(2,-1),(3,1)),((3,-1),(1,1),(0,-1),(2,1)),
 ((1,1),(2,-1),(3,1),(0,1)),((2,1),(3,-1),(1,1),(0,-1)),
 ((0,-1),(2,1),(1,-1),(3,1)),((3,1),(0,1),(2,-1),(1,1)),
 ((1,-1),(3,-1),(0,1),(2,1)),((2,-1),(0,-1),(3,1),(1,1)))
def source(seed,family):
    train=seed in FIT and family in FIT_FAM
    diagnostic=seed in DIAG and family in DIAG_FAM
    if not (train or diagnostic):
        raise ValueError("unregistered source; originals and mixed folds denied")
    rng=random.Random(seed*13093+family*7531+51031)
    used=set()
    def unique():
        while True:
            z=rng.randrange(200,200000)
            if z not in used:used.add(z);return z
    raw_core=[];paths=[]
    for p in range(4):
        chain=ROLES[(family-1020+p)%8]
        at=unique();start=at;selected=[]
        for role,direction in chain:
            end=unique()
            u,v=(at,end) if direction==1 else (end,at)
            edge=(u,role,v);raw_core.append(edge);selected.append(edge);at=end
        paths.append(dict(start=start,chain=chain,answer=at,edges=tuple(selected)))
    raw_distractors=[]
    if train:
        for p in range(24):
            a,b,c=unique(),unique(),unique()
            raw_distractors.extend(((a,rng.randrange(4),b),(b,rng.randrange(4),c)))
    else:
        # Heldout distractors have novel closed 3-cycles and short chains.
        for p in range(12):
            a,b,c=unique(),unique(),unique()
            raw_distractors.extend(((a,rng.randrange(4),b),
                                    (a,rng.randrange(4),c),
                                    (a,rng.randrange(4),unique())))
        for p in range(6):
            a,b,c=unique(),unique(),unique()
            raw_distractors.extend(((a,rng.randrange(4),b),(b,rng.randrange(4),c)))
    assert len(raw_core)==16 and len(raw_distractors)==48
    # Balanced, independently shuffled Bernoulli labels: exactly 8/16
    # true core tags and exactly 24/48 distracting tags in EVERY stream.
    core_tags=[1]*8+[0]*8;distractor_tags=[1]*24+[0]*24
    rng.shuffle(core_tags);rng.shuffle(distractor_tags)
    events=[(*edge,t) for edge,t in zip(raw_core,core_tags)]
    events.extend((*edge,t) for edge,t in zip(raw_distractors,distractor_tags))
    rng.shuffle(events)
    # An independent index is privately drawn after the public event stream.
    selected=paths[rng.randrange(4)]
    assert len(events)==EVENTS
    return tuple(events),selected,tuple(paths)

def public_features(edge,pool,idx):
    # All component/degree features are computed only from current <=13
    # publicly retained candidates; no history of evicted edges is kept.
    u,role,v,tag=edge
    nodes={}
    adjacency={}
    for e in pool:
        a,r,b,t=e
        nodes[a]=nodes.get(a,0)+1
        nodes[b]=nodes.get(b,0)+1
        adjacency.setdefault(a,set()).add(b)
        adjacency.setdefault(b,set()).add(a)
    deg=(nodes.get(u,0)+nodes.get(v,0)-2)/8
    seen={u};queue=[u]
    while queue:
        q=queue.pop()
        for x in adjacency.get(q,()):
            if x not in seen:seen.add(x);queue.append(x)
    component=len(seen)/14
    roles={e[1] for e in pool if
           (e[0]==u or e[2]==u or e[0]==v or e[2]==v)}
    joins=sum(1 for a,r,b,t in pool if (a,r,b,t)!=edge and
              ((b==u and r!=role) or (a==v and r!=role)))
    return (1.,float(tag),deg,component,len(roles)/4,idx/63.,
            float(nodes.get(u,0)>1 and nodes.get(v,0)>1),
            min(8,joins)/8.)

def public_hash(edge,index):
    u,r,v,t=edge
    return random.Random(u*3319+v*53+r*7793+index*97+5151).random()

def scored(edge,pool,index,method,weights):
    feat=public_features(edge,pool,index)
    if method=="learned_bridge_retention":
        return sum(x*w for x,w in zip(feat,weights))
    if method=="learned_topology_retention":
        return sum(x*w for x,w in zip(feat[:-1],weights[:-1]))
    if method=="public_connected_component":
        return feat[3]*4+feat[2]*.5+feat[4]*.1
    if method=="public_degree_adjacency":
        return feat[2]*4+feat[6]*.5
    if method=="public_tag_only":return feat[1]
    if method=="FIFO_last12":return index/63
    if method=="public_frequency":return feat[4]+feat[2]
    if method=="public_hash":return public_hash(edge,index)
    raise ValueError("unregistered public retention control")

def held_after_ingestion(events,method,weights,collect=False):
    memory=[];training=[]
    for t,e in enumerate(events):
        candidates=memory+[(t,e)]
        public=[edge for index,edge in candidates]
        if collect:
            training.append(public_features(e,public,t))
        sorted_candidates=sorted(
          candidates,key=lambda z:(scored(z[1],public,z[0],method,weights),z[0]),
          reverse=True)
        memory=sorted_candidates[:CAPACITY]
        assert len(memory)<=CAPACITY
    assert len(memory)==CAPACITY
    return tuple(sorted(z[0] for z in memory)),training

def train():
    data=[]
    for seed in FIT:
      for family in FIT_FAM:
        events,chosen,paths=source(seed,family)
        _,feats=held_after_ingestion(events,"public_degree_adjacency",[0.]*F_DIM,collect=True)
        relevant={e for path in paths for e in path["edges"]}
        for i,(event,feat) in enumerate(zip(events,feats)):
            data.append((feat,int(event[:3] in relevant)))
    weights=[0.]*F_DIM
    for epoch in range(24):
        for features,y in data:
            z=sum(w*f for w,f in zip(weights,features))
            pred=1/(1+math.exp(-max(-15,min(15,z))))
            factor=3 if y else 1
            for k in range(F_DIM):
                weights[k]-=.025*(factor*(pred-y)*features[k]+.0002*weights[k])
    return weights,len(data)

def solve(edges,path):
    at=path["start"]
    for role,d in path["chain"]:
        matches=[e for e in edges if e[1]==role and
                 (e[0] if d==1 else e[2])==at]
        if len(matches)!=1:return None
        edge=matches[0]
        at=edge[2] if d==1 else edge[0]
    return at

def run():
    assert not set(FIT)&set(DIAG) and not set(FIT_FAM)&set(DIAG_FAM)
    assert not set(DIAG)&set(RESERVED)
    weights,nfit=train()
    rows=[]
    total_positive_core=total_positive_distractor=0
    for seed in DIAG:
      for family in DIAG_FAM:
        events,question,paths=source(seed,family)
        core={e for path in paths for e in path["edges"]}
        total_positive_core+=sum(e[3] for e in events if e[:3] in core)
        total_positive_distractor+=sum(e[3] for e in events if e[:3] not in core)
        results={};receipts={}
        for arm in ARMS[:-1]:
            indices,_=held_after_ingestion(events,arm,weights)
            memory=[events[i] for i in indices]
            results[arm]=int(solve(memory,question)==question["answer"])
            receipts[arm]=indices
        results["private_future_question_oracle_unfair"]=int(
             solve(question["edges"],question)==question["answer"])
        rows.append(dict(seed=seed,family=family,question=dict(
          start=question["start"],chain=[list(x) for x in question["chain"]],
          answer=question["answer"]),public_events=[list(x) for x in events],
          results=results,retained_indices={a:list(v) for a,v in receipts.items()}))
    scores={a:dict(correct=sum(r["results"][a] for r in rows),total=len(rows))
            for a in ARMS}
    for s in scores.values():s["accuracy"]=s["correct"]/s["total"]
    by_fam={str(f):{a:sum(r["results"][a] for r in rows if r["family"]==f)
                    for a in ARMS} for f in DIAG_FAM}
    fair=ARMS[1:-1]
    best=max(fair,key=lambda a:scores[a]["accuracy"])
    gain=scores["learned_bridge_retention"]["accuracy"]-scores[best]["accuracy"]
    no_reg=all(by_fam[str(f)]["learned_bridge_retention"]>=
           max(by_fam[str(f)][a] for a in fair) for f in DIAG_FAM)
    qualified=gain>=.05 and no_reg
    return dict(schema="yggdrasil.f52.bridge-aware-neutral-tags.trainonly.v1",
      stage="TRAIN_ONLY_UNSEEN_DISTRACTOR_GRAPH_TOPOLOGY_NOT_ORIGINAL",
      fit_seeds=[FIT.start,FIT.stop],fit_families=list(FIT_FAM),
      diagnostic_seeds=[DIAG.start,DIAG.stop],diagnostic_families=list(DIAG_FAM),
      original_seeds_NOT_RESERVED=[RESERVED.start,RESERVED.stop],
      events_per_stream=EVENTS,memory_cap_edges=CAPACITY,
      future_question_hidden_until_retention_complete=True,
      tag_core_rate=total_positive_core/(16*len(rows)),
      tag_distractor_rate=total_positive_distractor/(48*len(rows)),
      train_examples=nfit,weights=weights,cases=len(rows),rows=rows,
      scores=scores,by_family=by_fam,strongest_fair_control=best,
      candidate_gain=gain,per_family_nondegradation=no_reg,
      frozen_gate_met=qualified,verdict=("TRAIN_ONLY_STRUCTURAL_MEMORY_SUPPORTED"
        if qualified else "TRAIN_ONLY_STRUCTURAL_MEMORY_NEGATIVE"),
      source_independent_F3=False,original_executed=False,
      native_576_bytes_residency_qualified=False,accepted_ref_mutation=False,
      paid_api_calls=0)

if __name__=="__main__":print(json.dumps(run(),sort_keys=True,indent=2))

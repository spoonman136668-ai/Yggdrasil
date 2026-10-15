"""Y-F50: learned online retention of relational facts before future task known.

One pass over a 64-edge stream, at most 12 retained edges. Trainable policy
fits only on FIT examples labeled by future-question *distribution*, never
receives future question or source-private core labels during diagnostic
retention. Independent synthetic TRAIN-only study, no F3/native residency.
"""
from __future__ import annotations
import json,math,random
FIT=range(511000,511016)
DIAG=range(511100,511116)
FIT_FAM=(820,821,822,823)
DIAG_FAM=(824,825,826,827)
RESERVED=range(512000,512016)
MEMORY=12
EVENTS=64
FEATURES=6
ARMS=("learned_retention","public_frequency_priority","public_tag_only",
      "FIFO_last12","public_hash_reservoir","private_future_query_oracle_unfair")
PATTERNS=(
 ((0,1),(1,1),(2,-1)),
 ((1,-1),(3,1),(0,1)),
 ((2,1),(0,-1),(1,-1)),
 ((3,-1),(2,1),(3,1)),
 ((1,1),(2,-1),(0,-1)),
 ((0,-1),(3,-1),(1,1)),
 ((2,-1),(1,1),(3,-1)),
 ((3,1),(0,1),(2,1)),
)
def source(seed,family):
    if not ((seed in FIT and family in FIT_FAM) or
            (seed in DIAG and family in DIAG_FAM)):
        raise ValueError("registered FIT/DIAG only, originals prohibited")
    rng=random.Random(seed*23717+family*7993+50053)
    used=set()
    def node():
        while True:
            v=rng.randrange(100,100000)
            if v not in used:used.add(v);return v
    events=[];paths=[]
    for group in range(4):
        seq=PATTERNS[(family-820+group)%8]
        cur=node();start=cur;truth_edges=[]
        for role,direction in seq:
            end=node()
            # Actual stored physical edge is directed, inverse traversal is allowed.
            u,v=(cur,end) if direction==1 else (end,cur)
            tag=int(rng.random()<.86)
            triple=(u,role,v,tag)
            events.append(triple);truth_edges.append(triple)
            cur=end
        paths.append(dict(start=start,chain=seq,answer=cur,edges=tuple(truth_edges)))
    for i in range(EVENTS-12):
        u=node();v=node()
        role=rng.randrange(4)
        tag=int(rng.random()<.17)
        events.append((u,role,v,tag))
    rng.shuffle(events)
    # The future query is chosen ONLY after the entire source stream exists.
    # This value is intentionally not provided to any retention method.
    chosen=rng.randrange(4)
    return tuple(events),paths[chosen],tuple(paths)

def features(event,seen_nodes,index):
    u,role,v,tag=event
    # All features computed at the time this observation arrives.
    return (1.,float(tag),min(seen_nodes.get(u,0),3)/3,
            min(seen_nodes.get(v,0),3)/3,
            index/(EVENTS-1),int(role in (1,3)))
def hash_score(event,index):
    u,r,v,tag=event
    return random.Random(u*91813+v*317+r*19+index*7+50011).random()

def per_event_features(events):
    seen={}
    out=[]
    for idx,e in enumerate(events):
        out.append(features(e,seen,idx))
        seen[e[0]]=seen.get(e[0],0)+1
        seen[e[2]]=seen.get(e[2],0)+1
    return out

def train():
    data=[]
    for seed in FIT:
      for family in FIT_FAM:
        events,query,paths=source(seed,family)
        potentially_valuable=set(e for p in paths for e in p["edges"])
        feats=per_event_features(events)
        assert len(events)==EVENTS
        for e,f in zip(events,feats):
            y=1 if e in potentially_valuable else 0
            data.append((f,y))
    weights=[0.]*FEATURES
    # Regularized, class-balanced online logistic regression.
    for epoch in range(22):
        for f,y in data:
            z=sum(a*b for a,b in zip(weights,f))
            p=1/(1+math.exp(-max(-15,min(15,z))))
            weight=4. if y else 1.
            for k in range(FEATURES):
                weights[k]-=.025*(weight*(p-y)*f[k]+.0003*weights[k])
    return weights,len(data)

def retained(events,method,weights):
    # Policies see public events only: no source-private graph, answer or query.
    if method not in ARMS[:-1]:raise ValueError("invalid public memory selector")
    seen={};held=[]
    for index,e in enumerate(events):
        f=features(e,seen,index)
        if method=="learned_retention":score=sum(a*b for a,b in zip(weights,f))
        elif method=="public_frequency_priority":
            score=2*f[2]+2*f[3]+.0001*f[4]
        elif method=="public_tag_only":score=f[1]+.0001*f[4]
        elif method=="FIFO_last12":score=index
        else:score=hash_score(e,index)
        held.append((score,index,e))
        held.sort(key=lambda pair:(-pair[0],-pair[1]))
        if len(held)>MEMORY:held.pop()
        seen[e[0]]=seen.get(e[0],0)+1
        seen[e[2]]=seen.get(e[2],0)+1
    assert len(held)==MEMORY
    return [e for _,_,e in held]

def solve(held,query):
    # A task-specific cognition consumer, not a hindsight memory selector.
    at=query["start"]
    for role,direction in query["chain"]:
        choices=[e for e in held if e[1]==role and (e[0] if direction==1 else e[2])==at]
        if len(choices)!=1:return None
        e=choices[0];at=e[2] if direction==1 else e[0]
    return at

def run():
    assert not set(FIT)&set(DIAG) and not set(DIAG)&set(RESERVED)
    assert not set(FIT_FAM)&set(DIAG_FAM)
    weights,nfit=train()
    rows=[]
    for seed in DIAG:
      for family in DIAG_FAM:
        events,query,all_paths=source(seed,family)
        results={};receipts={}
        for method in ARMS[:-1]:
            kept=retained(events,method,weights)
            results[method]=int(solve(kept,query)==query["answer"])
            receipts[method]=[events.index(e) for e in kept]
        # Evaluator hindsight is an explicitly unfair ceiling; no public policy sees query.
        ceiling=list(query["edges"])
        results["private_future_query_oracle_unfair"]=int(solve(ceiling,query)==query["answer"])
        rows.append(dict(seed=seed,family=family,truth_answer=query["answer"],
          future_query=dict(start=query["start"],chain=[list(e) for e in query["chain"]]),
          results=results,retained_event_indices=receipts,
          public_events=[list(e) for e in events]))
    scores={a:dict(correct=sum(r["results"][a] for r in rows),total=len(rows)) for a in ARMS}
    for s in scores.values():s["accuracy"]=s["correct"]/s["total"]
    by_fam={str(f):{a:sum(r["results"][a] for r in rows if r["family"]==f)
                    for a in ARMS} for f in DIAG_FAM}
    fair=ARMS[1:-1]
    strongest=max(fair,key=lambda a:scores[a]["accuracy"])
    gain=scores["learned_retention"]["accuracy"]-scores[strongest]["accuracy"]
    nonreg=all(by_fam[str(f)]["learned_retention"]>=max(by_fam[str(f)][a] for a in fair)
               for f in DIAG_FAM)
    passed=gain>=.05 and nonreg
    return dict(schema="yggdrasil.f50.learned-online-retention.trainonly.v1",
      stage="DISJOINT_TRAIN_ONLY_MEMORY_NO_PRIMARY_ORIGINAL",
      fit_seeds=[FIT.start,FIT.stop],fit_families=list(FIT_FAM),
      diagnostic_seeds=[DIAG.start,DIAG.stop],diagnostic_families=list(DIAG_FAM),
      proposed_original_seeds_NOT_RESERVED=[RESERVED.start,RESERVED.stop],
      events_per_stream=EVENTS,memory_capacity_edges=MEMORY,
      future_question_hidden_until_retention_complete=True,
      training_examples=nfit,weights=weights,
      cases=len(rows),scores=scores,by_family=by_fam,
      strongest_fair_control=strongest,candidate_gain=gain,
      per_family_nondegradation=nonreg,frozen_criterion_met=passed,
      verdict="TRAIN_ONLY_LEARNED_MEMORY_SUPPORTED" if passed else
              "TRAIN_ONLY_LEARNED_MEMORY_NEGATIVE",
      rows=rows,source_independent_F3=False,original_executed=False,
      native_576_bytes_residency_qualified=False,accepted_ref_mutation=False,paid_api_calls=0)

if __name__=="__main__":print(json.dumps(run(),indent=2,sort_keys=True))

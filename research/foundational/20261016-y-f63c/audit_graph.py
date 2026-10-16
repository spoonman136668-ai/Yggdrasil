"""F63C generator-independent public-graph/topology auditor.

Never imports source or labels; accepts only supplied public graph and
post-retention question for offline audit. No registered source dispatch.
"""
from __future__ import annotations
from collections import defaultdict,Counter
def verify(public,question):
    assert len(public)==72 and len(set(map(tuple,public)))==72
    assert all(len(edge)==3 and 0<=edge[1]<4 and
               0<=edge[0]<2**32 and 0<=edge[2]<2**32 and edge[0]!=edge[2]
               for edge in public)
    neighbor=defaultdict(set);degrees=Counter()
    for a,r,b in public:
        neighbor[a].add(b);neighbor[b].add(a)
        degrees[a]+=1;degrees[b]+=1
    visited=set();components=[]
    for root in neighbor:
        if root in visited:continue
        queue=[root];seen={root}
        while queue:
            node=queue.pop()
            for other in neighbor[node]:
                if other not in seen:seen.add(other);queue.append(other)
        visited.update(seen)
        edges=sum(int(a in seen and b in seen) for a,_,b in public)
        components.append((len(seen),edges))
    sizes=Counter(components)
    assert sizes==Counter({(18,17):2,(4,3):6,(3,2):10}),("INVALID_BRAID_STRUCTURE",dict(sizes))
    states={question["start"]}
    for role,direction in question["ops"]:
        assert 0<=role<=3 and direction in (-1,1)
        nxt=set()
        for a,r,b in public:
            if r!=role:continue
            src,dst=(a,b) if direction==1 else (b,a)
            if src in states:nxt.add(dst)
        states=nxt
    assert states=={question["answer"]},"AMBIGUOUS_OR_UNGROUNDED_QUESTION"
    assert len(question["ops"]) in (4,6)
    return dict(public_edges=72,components=dict((str(k),v) for k,v in sizes.items()),
         public_answer_unique=True,question_hops=len(question["ops"]),
         max_public_degree=max(degrees.values()),registered_source_used=False)

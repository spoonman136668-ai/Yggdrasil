"""Independent F63A public-graph structure audit. No source import or FIT use."""
from collections import Counter
def verify(public,question):
    assert len(public)==72 and len(set(public))==72
    assert all(len(e)==3 and 0<=e[1]<=3 and e[0]!=e[2] for e in public)
    incident=Counter()
    for a,_,b in public:
        incident[a]+=1;incident[b]+=1
    hubs=[node for node,degree in incident.items() if degree>=4]
    assert len(hubs)==1,("EXPECTED_ONE_SHARED_HUB",hubs)
    hub=hubs[0]
    assert incident[hub]>=12,("MISSING_BRAID_HUB",incident[hub])
    states={question["start"]}
    for role,direction in question["ops"]:
        nxt=set()
        for a,r,b in public:
            if r!=role:continue
            src,dst=(a,b) if direction==1 else (b,a)
            if src in states:nxt.add(dst)
        states=nxt
    assert states=={question["answer"]},("AMBIGUOUS_PUBLIC_QUESTION",states)
    assert len(question["ops"])==4
    return dict(schema="f63a.public-graph-independent-audit.v1",edges=len(public),
                shared_hub_degree=incident[hub],public_question_unique=True,
                fit_or_heldout_access=False)

"""F63C independent four-corridor braided public graph source, engineering-only.

NEVER dispatch registered FIT/validation/DIAG/original here. Public role-edge
stream; future question returned only to offline scientific evaluator.
"""
from __future__ import annotations
import json,random,sys

REGISTERED=(range(801000,801016),range(801100,801116),range(802000,802016))
def public_witness(public,question):
    states={question["start"]}
    for role,direction in question["ops"]:
        nxt=set()
        for a,r,b in public:
            if r==role:
                src,dst=(a,b) if direction==1 else (b,a)
                if src in states:nxt.add(dst)
        states=nxt
    return states

def _create(seed,family,attempt):
    rng=random.Random(seed*33017+family*61169+attempt*9739+63063)
    used=set()
    def fresh():
        while True:
            a=rng.randrange(1000,1500000000)
            if a not in used:used.add(a);return a
    paths=[]
    for k in range(4):
        nodes=tuple(fresh() for _ in range(9))
        roles=[];edges=[]
        for j in range(8):
            role=rng.choice([r for r in range(4) if not roles or r!=roles[-1][0]])
            direction=1 if rng.randrange(2)==0 else -1
            a,b=nodes[j:j+2]
            edges.append((a,role,b) if direction==1 else (b,role,a))
            roles.append((role,direction))
        paths.append((nodes,tuple(roles),tuple(edges)))
    links=[]
    for left,right in ((0,1),(2,3)):
        a=paths[left][0][4];b=paths[right][0][4]
        # Prevent a crosslink from sharing the same outgoing step role
        # at either hub. All role conditions are public structural ones.
        forbidden={paths[left][1][4][0],paths[right][1][4][0]}
        valid=[r for r in range(4) if r not in forbidden]
        role=rng.choice(valid)
        forward=bool(rng.randrange(2))
        links.append(((a,role,b) if forward else (b,role,a),
                      (role,1 if forward else -1),left,right))
    noise=[]
    for n in range(6):
        ns=[fresh() for _ in range(4)]
        for i in range(3):
            a,b=ns[i:i+2]
            if rng.randrange(2):a,b=b,a
            noise.append((a,rng.randrange(4),b))
    for n in range(10):
        ns=[fresh() for _ in range(3)]
        for i in range(2):
            a,b=ns[i:i+2]
            if rng.randrange(2):a,b=b,a
            noise.append((a,rng.randrange(4),b))
    assert len(noise)==38
    order=list(range(4));rng.shuffle(order)
    regime="clustered_with_braided_hubs" if family%2==0 else "two_phase_braided_joins"
    if family%2==0:
        stream=[]
        for rank,k in enumerate(order):
            stream.extend(paths[k][2]);stream.extend(noise[3*rank:3*rank+3])
        stream.extend([x[0] for x in links]);stream.extend(noise[12:])
    else:
        stream=[]
        for rank,k in enumerate(order):
            stream.extend(paths[k][2][:4]);stream.extend(noise[2*rank:2*rank+2])
        stream.extend([x[0] for x in links])
        for rank,k in enumerate(order):
            stream.extend(paths[k][2][4:]);stream.extend(noise[8+2*rank:8+2*rank+2])
        stream.extend(noise[16:])
    assert len(stream)==72 and len(set(stream))==72
    kind="crosslink_reach_6_steps" if (seed+2*family)%4==0 else "within_component_4_steps"
    if kind=="crosslink_reach_6_steps":
        which=rng.randrange(2)
        link,bridge,left,right=links[which]
        nodes,ops,_=paths[left]
        target_nodes,target_ops,_=paths[right]
        q=dict(start=nodes[0],ops=ops[:4]+(bridge,)+target_ops[4:5],
               answer=target_nodes[5])
    else:
        selected=paths[rng.randrange(4)]
        q=dict(start=selected[0][0],ops=selected[1][:4],answer=selected[0][4])
    return tuple(stream),q,dict(regime=regime,question_type=kind,attempt=attempt)
def source(seed,family):
    if seed>=0 or family not in (-2,-1):
        raise ValueError("REGISTERED_F63C_SOURCE_DENIED")
    for attempt in range(8):
        public,q,meta=_create(seed,family,attempt)
        if public_witness(public,q)=={q["answer"]}:
            return public,q,meta
    raise AssertionError("SOURCE_UNIQUE_PUBLIC_QUESTION_FAILED_EIGHT_ATTEMPTS")
def synthetic_smoke():
    rows=[]
    for i in range(24):
        seed=-401-i;family=(-2,-1)[i%2]
        public,q,meta=source(seed,family)
        assert len(public)==72 and len(set(public))==72
        assert public_witness(public,q)=={q["answer"]}
        rows.append(dict(seed=seed,kind=meta["question_type"],regime=meta["regime"],retry=meta["attempt"]))
    assert len({r["kind"] for r in rows})==2
    assert len({r["regime"] for r in rows})==2
    return dict(schema="yggdrasil.f63c.synthetic-source-smoke.v1",
        cases=len(rows),rows=rows,registered_fit_executed=False,
        validation_executed=False,original_executed=False)
if __name__=="__main__":
    assert sys.argv[1:]==["--synthetic-only"]
    print(json.dumps(synthetic_smoke(),sort_keys=True))

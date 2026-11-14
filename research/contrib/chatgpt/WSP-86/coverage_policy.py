"""Source-blind WSP86 B(6,3) complete triple coverage for physical paid actions."""
from __future__ import annotations

ACTIONS=tuple(range(6))
TRIPLES=216
STAGE_A=144
STAGE_B=240

def _cycle():
    k,n=6,3
    a=[0]*(k*n+1)
    out=[]
    def db(t,p):
        if t>n:
            if n%p==0:
                out.extend(a[1:p+1])
            return
        a[t]=a[t-p]
        db(t+1,p)
        for j in range(a[t-p]+1,k):
            a[t]=j
            db(t+1,t)
    db(1,1)
    if len(out)!=TRIPLES:
        raise AssertionError("invalid de Bruijn cycle")
    return tuple(out)

CYCLE=_cycle()

def stage_b_actions(paid_stage_a_actions):
    """Plan 240 charged actions, including one complete 216-triple cycle."""
    hist=paid_stage_a_actions
    if (type(hist) not in (tuple,list) or len(hist)!=STAGE_A
            or any(type(a) is not int or a not in ACTIONS for a in hist)):
        raise PermissionError("requires exactly 144 paid public StageA actions")
    tail=tuple(hist[-2:])
    pivot=next((i for i in range(TRIPLES)
                if (CYCLE[i],CYCLE[(i+1)%TRIPLES])==tail),None)
    if pivot is None:
        raise AssertionError("missing de Bruijn prefix")
    result=tuple(CYCLE[(pivot+2+j)%TRIPLES] for j in range(STAGE_B))
    if full_triple_coverage(tail+result[:TRIPLES])!=TRIPLES:
        raise AssertionError("guaranteed 216 triple coverage failed")
    return result

def full_triple_coverage(paid_action_history):
    hist=paid_action_history
    if (type(hist) not in (tuple,list) or any(
            type(a) is not int or a not in ACTIONS for a in hist)):
        raise ValueError("invalid public paid action history")
    return len({tuple(hist[i:i+3]) for i in range(max(0,len(hist)-2))})

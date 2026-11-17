"""WSP146 source-blind, hypothesis-specific paid intervention selector.
Never import source or scoring. Parent WSP145 learner and policy are immutable.
"""
from collections import defaultdict
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

def _parent():
    path=Path(__file__).resolve().parents[1]/'WSP-145'/'selector.py'
    spec=spec_from_file_location('_wsp146_pinned_parent_selector',path)
    mod=module_from_spec(spec)
    sys.modules[spec.name]=mod
    spec.loader.exec_module(mod)
    return mod

P145=_parent()
H=P145.H
FIXED=P145.FIXED
WARM=P145.WARM
MASKS=P145.MASKS
LOW=tuple(sorted(m for d in (0,1,2) for m in H.LEVELS[d]))
HIGH=H.LEVELS[5]
POLICIES=frozenset(('fixed','random','baseline_adaptive','falsifier'))
MAX_CHALLENGERS_PER_HIGH=128

def _key(prefix,law,x):
    return sha256((prefix+str(law)+'|'+str(x)).encode()).digest()

def _law(law):
    P145._law(law)

def fixed_schedule():
    return P145.fixed_schedule()

def random_schedule(law):
    return P145.random_schedule(law)

def parent_adaptive_schedule(law,observe):
    return P145.adaptive_schedule(law,observe)

def _low_residual_programs(rows, high):
    """Exact forced fifth-degree term + at most 3 low-degree XOR terms.
    Only observed rows enter the signature equations, never truth/future x.
    Overflow is a visible uncertainty event, NOT truncated confident evidence.
    """
    xs=tuple(x for x,y in rows)
    target=sum(y<<i for i,(x,y) in enumerate(rows))
    residual=target^H.signature(high,xs)
    sig={m:H.signature(m,xs) for m in LOW}
    inv=defaultdict(list)
    for m in LOW:inv[sig[m]].append(m)
    matches=[]
    if residual==0: return ((high,),),False
    for m in LOW:
        if sig[m]==residual:
            matches.append((high,m))
            if len(matches)>MAX_CHALLENGERS_PER_HIGH:return (),True
    if matches:return tuple(matches),False
    for i,a in enumerate(LOW):
        for b in LOW[i+1:]:
            if (sig[a]^sig[b])==residual:
                matches.append((high,a,b))
                if len(matches)>MAX_CHALLENGERS_PER_HIGH:return (),True
    if matches:return tuple(matches),False
    for i,a in enumerate(LOW):
        for j in range(i+1,len(LOW)):
            b=LOW[j]
            for c in inv.get(residual^sig[a]^sig[b],()):
                if c<=b:continue
                matches.append((high,a,b,c))
                if len(matches)>MAX_CHALLENGERS_PER_HIGH:return (),True
    return tuple(matches),False

def challenger_hypotheses(rows):
    P145.validate_rows(rows)
    result=[]
    overflow=False
    for high in HIGH:
        fits,over=_low_residual_programs(rows,high)
        overflow|=over
        result.extend(fits)
    return tuple(result) if not overflow else (),overflow

def _vote(program,x):
    value=0
    for mask in program:value^=int((x&mask)==mask)
    return value

def choose_next(rows,law):
    _law(law)
    rows=P145.validate_rows(rows)
    if len(rows)>=32:raise ValueError('WSP146_ACTION_BUDGET_EXHAUSTED')
    challengers,overflow=challenger_hypotheses(rows)
    stages=P145._stage_candidates(rows)
    if not challengers or overflow or not stages:
        return P145.choose_next(rows,law)
    incumbent=stages[0]
    paid={x for x,y in rows}
    def rank(x):
        votes={_vote(p,x) for p in incumbent}
        if len(votes)!=1:return (0.0,0,0,_key('WSP146|TIE|',law,x),x)
        incumbent_value=next(iter(votes))
        disagreement=sum(_vote(p,x)!=incumbent_value for p in challengers)/len(challengers)
        return (-disagreement,-P145.structural_split(rows,x),
                -sum((x&m)==m for m in HIGH),
                _key('WSP146|TIE|',law,x),x)
    candidates=[x for x in range(64) if x not in paid]
    best=min(candidates,key=rank)
    if rank(best)[0]==0.0:
        return P145.choose_next(rows,law)
    return best

def falsifier_schedule(law,observe):
    _law(law)
    if not callable(observe):raise ValueError('WSP146_BAD_OBSERVER')
    rows=[]
    for x in WARM:
        y=observe(x)
        if type(y) is not int or y not in (0,1):raise ValueError('WSP146_BAD_CHARGED_EFFECT')
        rows.append((x,y))
    for _ in range(12):
        x=choose_next(rows,law)
        y=observe(x)
        if type(y) is not int or y not in (0,1):raise ValueError('WSP146_BAD_CHARGED_EFFECT')
        rows.append((x,y))
    return tuple(rows)

def hidden_future_questions(law,actions_by_policy,predictions_by_policy):
    _law(law)
    if (type(actions_by_policy) is not dict or set(actions_by_policy)!=POLICIES
        or type(predictions_by_policy) is not dict or set(predictions_by_policy)!=POLICIES):
        raise ValueError('WSP146_OWNER_SEAL_INCOMPLETE')
    paid=set()
    for name in POLICIES:
        xs=tuple(actions_by_policy[name])
        preds=predictions_by_policy[name]
        if (len(xs)!=32 or len(set(xs))!=32
            or any(type(x) is not int or not 0<=x<64 for x in xs)
            or xs[:20]!=WARM or type(preds) is not dict
            or set(preds)!=set(range(64))
            or any(y is not None and (type(y) is not int or y not in (0,1)) for y in preds.values())):
            raise ValueError('WSP146_UNSEALED_POLICY_OR_PREDICTIONS')
        paid.update(xs)
    unseen=set(range(64))-paid
    if len(unseen)<8:raise AssertionError('WSP146_HIDDEN_HELD_UNION_TOO_LARGE')
    return tuple(sorted(unseen,key=lambda x:(_key('WSP146|HELD|',law,x),x))[:8])

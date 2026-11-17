"""WSP146 exact source-free high-order counterhypothesis confidence gate.

Receives ONLY 32 charged typed public (x,effect) observations. Produces a
full 64-output vector without future-query coordinates or source truth.
No new predictions and no label flips: only justified abstentions.
"""
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
from time import process_time_ns,perf_counter_ns
import sys
from hashlib import sha256

def _pin_h():
    spec=spec_from_file_location('_wsp146_h',Path(__file__).resolve().parents[1]/'WSP-143'/'concepts.py')
    mod=module_from_spec(spec)
    sys.modules[spec.name]=mod
    spec.loader.exec_module(mod)
    return mod
H=_pin_h()
FIVE_MASKS=tuple(H.LEVELS[5])
LOW_FEATURES=tuple(sorted(m for depth in range(5) for m in H.LEVELS[depth]))
assert FIVE_MASKS==(31,47,55,59,61,62)
assert len(LOW_FEATURES)==57

def _check(rows):
    if (type(rows) not in (tuple,list) or len(rows)!=32
        or len({x for x,y in rows})!=32
        or any(type(x) is not int or not 0<=x<64 or type(y) is not int
               or y not in (0,1) for x,y in rows)):
        raise ValueError('WSP146_BAD_CHARGED_TYPED_EFFECTS')
    return tuple(rows)

def original(state):
    return tuple(H.predict(state,x) for x in range(64))

def depth_only(state,base):
    return (tuple(None for x in range(64)) if state['level'] in (3,4)
            else tuple(base))

def counterhypotheses(rows):
    rows=_check(rows)
    xs=tuple(x for x,y in rows)
    target=sum(y<<i for i,(x,y) in enumerate(rows))
    signs=tuple(H.signature(m,xs) for m in LOW_FEATURES)
    alternatives=[]
    overflow=False
    for hi in FIVE_MASKS:
        rem=target^H.signature(hi,xs)
        exact=H._solve(LOW_FEATURES,signs,rem)
        if exact['terms'] is None or exact['terms']>3 or exact['count']==0:
            continue
        if exact['overflow']:
            overflow=True
            continue
        for terms in exact['fits']:
            if len(terms)>3:raise AssertionError('WSP146_HIGH_ORDER_TERMS_OVER_LIMIT')
            hypothesis=(hi,)+tuple(terms)
            if any((sum(int((x&mask)==mask) for mask in hypothesis)&1)!=y
                   for x,y in rows):
                raise AssertionError('WSP146_NONEXACT_COUNTERHYPOTHESIS')
            alternatives.append(hypothesis)
    return tuple(alternatives),overflow

def challenge(rows,state=None):
    rows=_check(rows)
    canonical=H.fit(rows)
    if state is None:state=canonical
    elif state!=canonical:raise ValueError('WSP146_FOREIGN_OR_NONCANONICAL_STATE')
    base=original(state)
    if state['level'] not in (3,4):
        return {'original':base,'challenged':base,'depth_only':depth_only(state,base),
                'alternatives':0,'overflow':False}
    competitors,overflow=counterhypotheses(rows)
    out=[]
    for x,value in enumerate(base):
        if value is None or overflow:
            out.append(None)
        elif any((sum(int((x&mask)==mask) for mask in prog)&1)!=value
                 for prog in competitors):
            out.append(None)
        else:
            out.append(value)
    return {'original':base,'challenged':tuple(out),
            'depth_only':depth_only(state,base),
            'alternatives':len(competitors),'overflow':overflow}

def measured_challenge(rows):
    c=process_time_ns();w=perf_counter_ns()
    value=challenge(rows)
    value['cpu_s']=round((process_time_ns()-c)/1e9,6)
    value['wall_s']=round((perf_counter_ns()-w)/1e9,6)
    return value

def hidden_future_questions(law_id,actions_by_policy,predictions_by_policy):
    """Source-blind independent held-coordinate audit after full prediction seals.

    Same WSP146 namespace as source owner, not legacy WSP145. This function
    is NOT callable by the acquisition policy and consumes zero source effects.
    """
    if type(law_id) is not int or law_id<0:
        raise ValueError('WSP146_BAD_PUBLIC_LAW_ID')
    names={'fixed','random','adaptive'}
    if (type(actions_by_policy) is not dict or set(actions_by_policy)!=names
        or type(predictions_by_policy) is not dict or set(predictions_by_policy)!=names):
        raise ValueError('WSP146_OWNER_SEALS_MISSING')
    observed=set()
    warm=None
    for name in ('fixed','random','adaptive'):
        inputs=tuple(actions_by_policy[name])
        preds=predictions_by_policy[name]
        if (len(inputs)!=32 or len(set(inputs))!=32
            or any(type(x) is not int or not 0<=x<64 for x in inputs)
            or type(preds) is not dict or set(preds)!=set(range(64))
            or any(v is not None and (type(v) is not int or v not in (0,1))
                   for v in preds.values())):
            raise ValueError('WSP146_UNSEALED_FULL_PREDICTIONS_OR_ACTIONS')
        prefix=inputs[:20]
        if warm is None:warm=prefix
        elif prefix!=warm:raise ValueError('WSP146_UNMATCHED_WARM_OBSERVATIONS')
        observed.update(inputs)
    unseen=set(range(64))-observed
    if len(unseen)<8:raise AssertionError('WSP146_HELD_UNION_TOO_LARGE')
    return tuple(sorted(unseen,key=lambda x:(
        sha256(('WSP146|HELD|'+str(law_id)+'|'+str(x)).encode()).digest(),x))[:8])

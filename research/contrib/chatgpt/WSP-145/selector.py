"""WSP145 source-free policy; no private future question, truth or evaluator access."""
from collections import defaultdict
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

def _pin():
    spec=spec_from_file_location('_wsp145_pinned_h',Path(__file__).resolve().parents[1]/'WSP-143'/'concepts.py')
    mod=module_from_spec(spec)
    sys.modules[spec.name]=mod
    spec.loader.exec_module(mod)
    return mod
H=_pin()
MASKS=tuple(sorted(m for d in range(6) for m in H.LEVELS[d]))
FIXED=tuple(sorted(range(64),key=lambda x:(sha256(('WSP135|ACTIONS|'+str(x)).encode()).digest(),x))[:32])
WARM=FIXED[:20]
WARM_COUNT=20
FINAL_COUNT=32
HELD_COUNT=8

def _key(prefix,law,x):
    return sha256((prefix+str(law)+'|'+str(x)).encode()).digest()

def _law(law):
    if type(law) is not int or law<0:raise ValueError('WSP145_BAD_PUBLIC_LAW_ID')

def validate_rows(rows):
    if (type(rows) not in (list,tuple) or not 20<=len(rows)<=32
        or len({x for x,y in rows})!=len(rows)
        or any(type(x) is not int or not 0<=x<64 or type(y) is not int or y not in (0,1) for x,y in rows)
        or tuple(x for x,y in rows[:20])!=WARM):
        raise ValueError('WSP145_UNQUALIFIED_CHARGED_ROWS')
    return tuple(rows)

def fixed_schedule():return FIXED

def random_schedule(law):
    _law(law)
    tail=tuple(sorted((x for x in range(64) if x not in WARM),
       key=lambda x:(_key('WSP145|RANDOM|',law,x),x))[:12])
    return WARM+tail

def _stage_candidates(rows):
    xs=tuple(x for x,y in rows)
    target=sum(y<<i for i,(x,y) in enumerate(rows))
    stages=[]
    for depth in (2,3,4,5):
        features=tuple(sorted(m for d in range(depth+1) for m in H.LEVELS[d]))
        result=H._solve(features,tuple(H.signature(m,xs) for m in features),target)
        if result['count'] and not result['overflow'] and result['fits']:
            stages.append(result['fits'])
    return tuple(stages)

def _program_value(program,x):
    return sum((x&m)==m for m in program)&1

def _uncertainty(stages,x):
    if not stages:return 0.0
    p=sum(sum(_program_value(prog,x) for prog in progs)/len(progs) for progs in stages)/len(stages)
    return p*(1-p)

def structural_split(rows,x):
    if type(x) is not int or not 0<=x<64:raise ValueError('WSP145_BAD_ACTION')
    xs=tuple(a for a,y in rows)
    groups=defaultdict(lambda:[0,0])
    for mask in MASKS:
        groups[H.signature(mask,xs)][int((x&mask)==mask)]+=1
    return sum(a*b for a,b in groups.values())

def choose_next(rows,law):
    _law(law)
    rows=validate_rows(rows)
    if len(rows)>=32:raise ValueError('WSP145_ACTION_BUDGET_EXHAUSTED')
    stages=_stage_candidates(rows)
    seen={x for x,y in rows}
    return min((x for x in range(64) if x not in seen),
        key=lambda x:(-_uncertainty(stages,x),-structural_split(rows,x),
                      _key('WSP145|TIE|',law,x),x))

def adaptive_schedule(law,observe):
    """Outcome-dependent sequential charges, exactly 20 warm +12 active."""
    _law(law)
    if not callable(observe):raise ValueError('WSP145_BAD_OBSERVER')
    rows=[]
    for x in WARM:
        y=observe(x)
        if type(y) is not int or y not in (0,1):raise ValueError('WSP145_BAD_CHARGED_EFFECT')
        rows.append((x,y))
    for i in range(12):
        x=choose_next(rows,law)
        y=observe(x)
        if type(y) is not int or y not in (0,1):raise ValueError('WSP145_BAD_CHARGED_EFFECT')
        rows.append((x,y))
    return tuple(rows)

def hidden_future_questions(law,actions_by_policy,predictions_by_policy):
    """Owner-only after three complete action vectors and 64-output seals."""
    _law(law)
    names={'fixed','random','adaptive'}
    if (type(actions_by_policy) is not dict or set(actions_by_policy)!=names
        or type(predictions_by_policy) is not dict or set(predictions_by_policy)!=names):
        raise ValueError('WSP145_OWNER_SEAL_INCOMPLETE')
    paid=set()
    for name in names:
        xs=tuple(actions_by_policy[name])
        preds=predictions_by_policy[name]
        if (len(xs)!=32 or len(set(xs))!=32
            or any(type(x) is not int or not 0<=x<64 for x in xs)
            or xs[:20]!=WARM or type(preds) is not dict
            or set(preds)!=set(range(64))
            or any(y is not None and (type(y) is not int or y not in (0,1)) for y in preds.values())):
            raise ValueError('WSP145_UNSEALED_POLICY_OR_PREDICTIONS')
        paid.update(xs)
    unseen=set(range(64))-paid
    if len(unseen)<8:raise AssertionError('WSP145_HIDDEN_HELD_IMPOSSIBLE')
    return tuple(sorted(unseen,key=lambda x:(_key('WSP145|HELD|',law,x),x))[:8])

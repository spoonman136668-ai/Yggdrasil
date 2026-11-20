"""Evaluator-only synthetic source; never import into learner.py."""
import hashlib

FAMILIES=('cubic_action','cubic_coupling','paired_nonlin','switching_cubic',
          'unchanged','unidentifiable_fourth','out_of_degree_four')
PILOT=794001
SEEDS=(794011,794033,794057,794089)
COUNTS={'old_fit':64,'new_fit':128,'valid':32,'held_shared':32,'held_policy':32,'return_old':64}
OLD_IDS=('old.x0','old.x1','old.x2','old.x3','old.action_1','old.action_2')
NEW_IDS=('new.x0','new.x1','new.x2','new.x3','new.action_1','new.action_2')

def entropy(seed,family,phase,index,tag,action=0):
    v=f'nci-novel04/{seed}/{family}/{phase}/{index}/{tag}/{action}'.encode('ascii')
    return int.from_bytes(hashlib.sha256(v).digest()[:8],'big')

def inputs(seed,family,phase,index):
    x=tuple(entropy(seed,family,phase,index,'x'+str(j))%2 for j in range(4))
    if family=='unidentifiable_fourth' and phase not in ('old_fit','return_old'):
        x=(*x[:3],0)
    return x

def truth(family,phase,x,a1,s2=None,a2=None):
    x0,x1,x2,x3=x
    if phase in ('old_fit','return_old') or family=='unchanged':
        return (x0^a1) if s2 is None else (x1^a2)
    if family=='cubic_action':
        return (x0&x3&a1)^x2 if s2 is None else (x3&s2&a2)^x1
    if family=='cubic_coupling':
        return (x0&x1&x3)^(x2&a1) if s2 is None else (x2&x3&a2)^(x0&s2)
    if family=='paired_nonlin':
        return (x0&x3)^(x1&a1) if s2 is None else (x3&s2)^(x2&a2)
    if family=='switching_cubic':
        return (x3&x2&a1)^(x0&x1) if s2 is None else (x3&x1&s2)^(x0&a2)
    if family=='unidentifiable_fourth':
        return (x3&x1&a1)^x0 if s2 is None else (x3&s2&a2)^x1
    if family=='out_of_degree_four':
        return (x0&x1&x2&x3)^a1 if s2 is None else (x0&x1&x2&x3)^a2
    raise ValueError('UNKNOWN_SOURCE_FAMILY')

def reveal(seed,family,phase,index,stage,x,a1,s2=None,a2=None):
    # Prevent future a2 from affecting stage-one noise or transition.
    effect=truth(family,phase,x,a1,s2,a2)
    action=a1 if stage=='t' else a2
    flip=entropy(seed,family,phase,index,'noise_'+stage,action)%10000<600
    return effect^int(flip)

def balanced(seed,family,phase,index,stage):
    return entropy(seed,family,phase,index,'a_'+stage)&1

def witness(seed,family,phase,index,stage):
    return hashlib.sha256(f'nci-novel04/receipt/{seed}/{family}/{phase}/{index}/{stage}'.encode('ascii')).hexdigest()

def ids(phase):
    return OLD_IDS if phase in ('old_fit','return_old') else NEW_IDS

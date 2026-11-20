"""NCI-NOVEL-02 evaluator-only synthetic source. Learners MUST NOT import this."""
import hashlib

FAMILIES=('novel_toggle','novel_guard','novel_cross','novel_parity4',
          'unchanged','irrelevant_x3','unidentifiable_x3','outside_grammar')
SEEDS=(592113,592127,592139,592157)
PILOT_SEED=592101
SIZES={'old_fit':64,'new_fit':96,'valid':32,'held_shared':32,'held_policy':32,'old_return':64}
OLD_IDS=('old.x0','old.x1','old.x2','old.x3','old.action_1','old.action_2')
NEW_IDS=('new.x0','new.x1','new.x2','new.x3','new.action_1','new.action_2')


def rand(seed,family,phase,index,tag,action=0):
    msg=f'nci-novel02|{seed}|{family}|{phase}|{index}|{tag}|{action}'.encode('ascii')
    return int.from_bytes(hashlib.sha256(msg).digest()[:8],'big')


def inputs(seed,family,phase,index):
    x=tuple(rand(seed,family,phase,index,'x'+str(j))&1 for j in range(4))
    if family=='unidentifiable_x3' and phase not in ('old_fit','old_return'):
        return (*x[:3],0)
    return x


def truth(family,phase,x,a1,s2=None,a2=None):
    x0,x1,x2,x3=x
    if phase in ('old_fit','old_return') or family in ('unchanged','irrelevant_x3'):
        return x0 ^ a1 if s2 is None else x1 ^ s2 ^ a2
    if family=='novel_toggle':
        return x3 ^ a1 if s2 is None else x3 ^ s2 ^ a2
    if family=='novel_guard':
        return x0 ^ (x3&a1) if s2 is None else (x3&s2) ^ a2
    if family=='novel_cross':
        return (x3|x1) ^ a1 if s2 is None else (x3&s2)^a2
    if family=='novel_parity4':
        return x3 ^ x0 ^ x1 ^ a1 if s2 is None else x3 ^ x1 ^ s2 ^ a2
    if family=='unidentifiable_x3':
        return x3 ^ x0 ^ a1 if s2 is None else x3 ^ x1 ^ s2 ^ a2
    if family=='outside_grammar':
        return (x3&x0)^(x1&a1) if s2 is None else (x3&s2)^(x2&a2)
    raise ValueError('UNKNOWN_SOURCE_FAMILY')


def consequence(seed,family,phase,index,stage,x,a1,s2=None,a2=None):
    effect=truth(family,phase,x,a1,s2,a2)
    action=a1 if stage=='t' else a2
    flip=rand(seed,family,phase,index,'noise_'+stage,action)%10000<600
    return effect ^ int(flip)


def action(seed,family,phase,index,stage):
    return rand(seed,family,phase,index,'action_'+stage)&1


def witness(seed,family,phase,index,stage):
    key=f'nci-novel02/witness/{seed}/{family}/{phase}/{index}/{stage}'
    return hashlib.sha256(key.encode('ascii')).hexdigest()


def identity(phase):
    return OLD_IDS if phase in ('old_fit','old_return') else NEW_IDS

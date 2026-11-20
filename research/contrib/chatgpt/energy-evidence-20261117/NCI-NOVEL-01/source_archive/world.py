"""Evaluator ONLY. Never imported from learner core.py. All identities/rights synthetic."""
from __future__ import annotations
import hashlib

OLD_NAMES=('old.x','old.y','old.z','old.act1','old.act2')
NEW_NAMES=('new.x','new.y','new.z','new.act1','new.act2')
FAMILIES=('disjoint_xor','disjoint_and','disjoint_or','disjoint_mixed','unchanged_a','unchanged_b','equiv_unidentified','out_of_grammar')
PHASES=('old_fit','new_fit','valid','held_new','return_old')


def entropy_bit(seed,family,phase,index,tag,action=0):
    b=f'{seed}|{family}|{phase}|{index}|{tag}|{action}'.encode('ascii')
    return int.from_bytes(hashlib.sha256(b).digest()[:8],'big')


def source_inputs(seed,family,phase,index):
    p=entropy_bit(seed,family,phase,index,'p')&1
    q=entropy_bit(seed,family,phase,index,'q')&1
    r=0 if family=='equiv_unidentified' else entropy_bit(seed,family,phase,index,'r')&1
    return p,q,r


def private_law(family,phase,p,q,r,a1,s2=None,a2=None):
    """Private evaluator truth; return deterministic effect bit, not a learner label."""
    old=phase in ('old_fit','return_old')
    if old or family.startswith('unchanged'):
        return p^a1 if s2 is None else q^s2^a2
    if s2 is None:
        if family=='disjoint_xor':return p^q^a1
        if family=='disjoint_and':return (p&q)^a1
        if family=='disjoint_or':return (p|q)^a1
        if family=='disjoint_mixed':return (p^q)&a1
        if family=='equiv_unidentified':return p^a1^(r&1)
        if family=='out_of_grammar':return p^q^a1^r
        raise ValueError('unexpected family')
    if family=='disjoint_xor':return (q&s2)^a2
    if family=='disjoint_and':return (q|s2)^a2
    if family=='disjoint_or':return (q^s2)&a2
    if family=='disjoint_mixed':return q^(s2|a2)
    if family=='equiv_unidentified':return q^s2^a2^(r&1)
    if family=='out_of_grammar':return q^s2^a2^r
    raise ValueError('unexpected family')


def observed_outcome(seed,family,phase,index,stage,action,bit):
    noisy=entropy_bit(seed,family,phase,index,'noise-'+stage,action)%1000<60
    return bit^int(noisy)


def planned_action(seed,family,phase,index,stage):
    return entropy_bit(seed,family,phase,index,'public-random-'+stage)&1


def event_id(seed,family,phase,index,stage):
    return hashlib.sha256(f'nci-novel01|{seed}|{family}|{phase}|{index}|{stage}'.encode()).hexdigest()


def world_step(seed,family,phase,index,p,q,r,a1,a2=None,s2=None):
    if a2 is None:
        truth=private_law(family,phase,p,q,r,a1)
        return observed_outcome(seed,family,phase,index,'t',a1,truth)
    truth=private_law(family,phase,p,q,r,a1,s2,a2)
    return observed_outcome(seed,family,phase,index,'y',a2,truth)


def IDs(phase):
    return OLD_NAMES if phase in ('old_fit','return_old') else NEW_NAMES

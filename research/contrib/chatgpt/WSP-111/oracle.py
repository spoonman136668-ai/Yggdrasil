"""Evaluator-owned hidden WSP111 causal effect categories.

A model may read only the first 3000 group effects returned by training_feedback.
Never import this module from native.py, controls.py or fixtures. Original test
group effect oracle is read only AFTER all 22000 heldout predictions are sealed.
The relation categories have no supplied semantic names or predetermined IDs.
"""
from __future__ import annotations

from hashlib import sha256
from world import source_types_for_group,N_SUPPORT,N_GROUPS

def _hash(*items:object)->bytes:
    return sha256("|".join(map(str,items)).encode("ascii")).digest()

_MOTIF_ORDER=tuple(sorted(range(16),
    key=lambda kind:(_hash("WSP111","CLASS","v1",kind),kind)))
_CLASS_BY_MOTIF={kind:rank%4 for rank,kind in enumerate(_MOTIF_ORDER)}
_SIGNATURES=(1,2,4,7)
_SIGNATURE_ORDER=tuple(sorted(_SIGNATURES,
    key=lambda code:(_hash("WSP111","SIGNATURE","v1",code),code)))
_SIGNATURE_BY_CLASS={i:code for i,code in enumerate(_SIGNATURE_ORDER)}

def hidden_signature(group:int)->int:
    """Stable mechanism signature, not the noisy observed action consequence."""
    if type(group) is not int or not 0<=group<N_GROUPS:
        raise ValueError("unregistered WSP111 world")
    a,b,_=source_types_for_group(group)
    return _SIGNATURE_BY_CLASS[_CLASS_BY_MOTIF[a*4+b-4]]

def _flip(namespace:str,group:int,bit:int)->bool:
    return int.from_bytes(_hash("WSP111",namespace,"v1",group,bit),"big")%64==0

def effect_one(group:int)->int:
    """Observed first intervention: 3 sensor channels, no class label exposed."""
    value=hidden_signature(group)
    for bit in range(3):
        if _flip("NOISE1",group,bit):
            value ^= (1<<bit)
    return value

def effect_two(group:int)->int:
    """Observed second intervention, composed from latent relation and third edge."""
    _,_,third=source_types_for_group(group)
    value=_hash("WSP111","SECOND","v1",hidden_signature(group),third-10)[0]%4
    for bit in range(2):
        if _flip("NOISE2",group,bit):
            value ^= (1<<bit)
    return value

def training_feedback()->tuple[tuple[int,int,int],...]:
    """Only labels authorized to leave the evaluator before sealing."""
    return tuple((g,effect_one(g),effect_two(g)) for g in range(N_SUPPORT))

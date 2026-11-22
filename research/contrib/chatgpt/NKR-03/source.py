"""Fresh, public synthetic causal sources frozen as NKR-03 DEV only.

These deterministic laws are visible/fabricated. They are NOT protected
scientific heldout-world data and do NOT authorize real knowledge ingestion.
"""
from __future__ import annotations

import hashlib

TRAIN=(0,1,2,4,8)
AUDIT=(3,5,6,9,10,12)
UNAUDITED=(7,11,13,14,15)
PAIR_TERMS=((0,1),(0,2),(0,3),(1,2),(1,3),(2,3))
TRIPLE_TERMS=((0,1,2),(0,1,3),(0,2,3),(1,2,3))
FAMILIES=("quadratic","cubic")
SHARD_ID="NKR03|fresh|20261115"

def law(slot,context,action,family):
    if (type(slot) is not int or not 0<=slot<16 or
        type(context) is not int or not 0<=context<16 or
        type(action) is not int or action not in (0,1) or
        family not in FAMILIES):
        raise ValueError("NKR03_SOURCE_OUT_OF_SCOPE")
    h=hashlib.sha256(f"{SHARD_ID}|{family}|{slot}".encode("ascii")).digest()
    base=((context & (h[0]&15)).bit_count()&1)^(h[1]&1)^action
    terms=PAIR_TERMS if family=="quadratic" else TRIPLE_TERMS
    term=terms[h[2]%len(terms)]
    return int(base^int(all((context>>bit)&1 for bit in term)))

"""Y-F33: strictly evaluator-only recomputation of source information.

This module receives evaluator-only latent data AFTER policy actions and cannot
be imported by the sensor-selection policy. Two distinct formulas recompute
conditional information and out-of-fold logloss on TRAIN-only examples.
It is an independent algorithmic cross-check, not independently held F3 custody.
"""
from __future__ import annotations
import math
from collections import Counter,defaultdict

def mi(rows, conditioned):
    """Sum p(mode, sign | public_orientation) log2 likelihood ratio."""
    groups=defaultdict(list)
    for mode,sign,orientation in rows:
        groups[orientation if conditioned else 0].append((int(mode),int(sign)))
    ans=0.0
    for samples in groups.values():
        n=len(samples)
        modes=Counter(m for m,s in samples)
        signs=Counter(s for m,s in samples)
        pairs=Counter(samples)
        partial=0.
        for (m,s),c in pairs.items():
            partial+=(c/n)*math.log2(c*n/(modes[m]*signs[s]))
        ans+=len(samples)/len(rows)*partial
    return ans

def information_gain(rows):
    """Two-fold predictive difference, computed without outside model weights."""
    def cost(ref, val, conditional):
        counts=Counter()
        for m,s,p in ref:
            counts[(p,s,m)]+=1
            counts[(p,s,None)]+=1
            counts[(p,None,m)]+=1
            counts[(p,None,None)]+=1
        err=0.
        for m,s,p in val:
            if conditional:
                prob=(counts[(p,s,m)]+1)/(counts[(p,s,None)]+2)
            else:
                prob=(counts[(p,None,m)]+1)/(counts[(p,None,None)]+2)
            err-=math.log(prob)
        return err/len(val)
    first=rows[::2];second=rows[1::2]
    return (cost(first,second,False)-cost(first,second,True)+
            cost(second,first,False)-cost(second,first,True))/2

def independently_audit(data):
    rows=data["evaluator_only_private_mode_information"]
    assert rows and all(len(v)==3 for v in rows)
    return {
        "pooled_mutual_information_bits":mi(rows,False),
        "conditional_mutual_information_bits":mi(rows,True),
        "heldout_conditional_logloss_gain_nats":information_gain(rows),
        "evaluator_private_records":len(rows),
        "policy_not_given_mode":True,
        "source_custody_independent_of_repository":False,
    }

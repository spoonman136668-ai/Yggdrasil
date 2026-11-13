"""WSP72 source-blind gating of dreamed labels before direct neural weight edits.

No physics source import, oracle labels, hidden roles or heldout queries.
Two distinct numerical neural teachers receive only the SAME 96 charged
Phase-A observations. The independent teacher is a random-neuron WSP70
model, not an independent source-of-truth. Validation uses ALREADY charged
Phase-B facts. The selection controls share the same number of proposed
teacher labels / real teacher features / physical Phase-B actions.

A real durable neural student and its input/output parameters are inherited
unchanged from WSP71; this changes *which* synthetic predictions are
written into its readout, never the learner/snapshot/threshold or physics.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
from random import Random
import sys

_BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(_BASE/"WSP-71"))
from consolidate import (
    DREAM_MAX, DurableNeuralWeights, visible_dreams, distinct_charged_A
)


def _seeded(seed,domain):
    return Random(int.from_bytes(sha256(
        f"WSP72|{domain}|{seed}".encode("ascii")).digest(),"big"))


def select_committee_rehearsal(primary,secondary,phase_a,phase_b,seed):
    """Choose one trustworthy-looking subset with equal-k random control.

    The only 'validation' labels used are physical B observations, charged
    before rehearsal. All proposed and accepted teacher labels are
    hypothetical, not free source interactions. Never use withheld physics.
    """
    if type(seed) is not int or len(phase_a)!=96 or len(phase_b)!=96:
        raise ValueError("unqualified physical ledger/budget")
    candidates,queries=visible_dreams(primary,phase_a,seed)
    if len(candidates)>DREAM_MAX:
        raise ValueError("teacher proposed too many pseudo observations")
    b_experience={}
    for s,a,y in phase_b:
        key=(s,a)
        if key in b_experience and b_experience[key]!=y:
            raise ValueError("physically contradictory Phase B labels")
        b_experience[key]=y
    charged_A=distinct_charged_A(phase_a,seed)
    kcap=min(DREAM_MAX,len(charged_A))
    agreed=[]
    secondary_disagreed=0
    charged_B_contradictions=0
    secondary_queries=0
    for s,a,primary_y in candidates:
        secondary_queries+=1
        alt=secondary.predict(s,a)
        if alt is None or alt!=primary_y:
            secondary_disagreed+=1
            continue
        if (s,a) in b_experience and b_experience[(s,a)]!=primary_y:
            charged_B_contradictions+=1
            continue
        agreed.append((s,a,primary_y))
    k=min(kcap,len(agreed))
    selected=tuple(agreed[:k])
    # Same primary proposal set, same k, same generated labels: only
    # committee+physical-contradiction SELECTION distinguishes treatment.
    other=_seeded(seed,"equal-k-unfiltered")
    equal_k=tuple(other.sample(list(candidates),k)) if k else tuple()
    b_rng=_seeded(seed,"matched-B-duplicates")
    b_repeats=tuple(phase_b[b_rng.randrange(len(phase_b))]
                    for _ in range(k))
    true_a=tuple(charged_A[:k])
    scrambled=tuple((s,(a+1)%4,y) for s,a,y in selected)
    return {
        "k":k,"candidate":selected,"unfiltered":equal_k,
        "true_A":true_a,"B_repeat":b_repeats,
        "scrambled":scrambled,
        "all_primary_proposals":tuple(candidates),
        "candidate_proposals_agreed":len(agreed),
        "secondary_disagreement_count":secondary_disagreed,
        "charged_B_contradiction_count":charged_B_contradictions,
        "primary_queries":queries,
        "secondary_queries":secondary_queries,
        "distinct_charged_A":len(charged_A),
        "distinct_charged_B":len(b_experience)
    }

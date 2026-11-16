"""CUE-02 read-only finite-domain causal-memory evidence auditor.

No world identity, source provenance, private law, accepted native weights or
protected outcomes are accessible to this module. Even matching all 32 binary
public do(context,action) outcomes does NOT authenticate a source or guarantee
the dynamics beyond this specific observational interface.
"""
from __future__ import annotations

import hashlib

from yggdrasil.native_cumulative_action_bank import NativeCumulativeActionBank
from yggdrasil.native_intervention_repair import features
from yggdrasil.public_causal_cells import PublicCausalCells

ALL_PUBLIC_PROBES = tuple((x,a) for x in range(16) for a in (0,1))
MAX_PUBLIC_PROBES = len(ALL_PUBLIC_PROBES)
BUDGET_SWEEP = (32,24,16,12,8)


def probe_order(policy):
    """Policy-specific probe order, independent of any world identity."""
    if policy == "dense":
        return tuple(sorted(ALL_PUBLIC_PROBES,
                            key=lambda p:(-p[0].bit_count(),-p[0],-p[1])))
    if policy == "lex":
        return ALL_PUBLIC_PROBES
    if policy == "hash":
        return tuple(sorted(ALL_PUBLIC_PROBES,
                    key=lambda p:(hashlib.sha256(
                        f"CUE02|public-probe|{p[0]}|{p[1]}".encode("ascii")
                    ).digest(),p)))
    raise ValueError("CUE02_UNKNOWN_POLICY")


def _observations(public_cues):
    if type(public_cues) not in (tuple,list) or len(public_cues)>MAX_PUBLIC_PROBES:
        raise ValueError("CUE02_PUBLIC_PROBE_BUDGET")
    seen=set()
    out=[]
    for item in public_cues:
        if type(item) not in (tuple,list) or len(item)!=3:
            raise ValueError("CUE02_PUBLIC_CUE_SHAPE")
        x,a,y=item
        features(x,a)
        if type(y) is not int or y not in (0,1):
            raise ValueError("CUE02_PUBLIC_OUTCOME_INVALID")
        if (x,a) in seen:
            raise ValueError("CUE02_DUPLICATE_PUBLIC_PROBE")
        seen.add((x,a));out.append((x,a,y))
    return tuple(out)


def _native_prediction(bank,slot,x,a):
    if type(slot) is not int or not 0<=slot<16:
        raise ValueError("CUE02_INVALID_NATIVE_MEMORY_SLOT")
    active=PublicCausalCells.ACTIVE_SLOTS
    result=bank.predict(slot if slot<active else slot-active,
                        x,a,retained=slot>=active)
    bit=result["public_outcome"]
    if bit is not None and (type(bit) is not int or bit not in (0,1)):
        raise ValueError("CUE02_INVALID_STORED_PUBLIC_PREDICTION")
    return bit


def audit(bank, public_cues):
    """An observation-compatible hypothesis, NEVER a source identity proof.

    For a complete-domain observational match, every one of the 32 public
    context/action pairs must have been actually observed exactly once.
    A source with the *same* 32 outputs remains indistinguishable and is NOT
    identified. No result causes automatic model activation, acceptance or
    scientific promotion.
    """
    if not isinstance(bank,NativeCumulativeActionBank):
        raise ValueError("CUE02_NATIVE_BANK_REQUIRED")
    cues=_observations(public_cues)
    matches=[]
    for slot in bank.stored_slots:
        if all(_native_prediction(bank,slot,x,a) == truth and
               _native_prediction(bank,slot,x,a) is not None
               for x,a,truth in cues):
            matches.append(slot)
    full=len(cues)==MAX_PUBLIC_PROBES
    if len(bank.stored_slots)==0:
        classification="NO_STORED_RELATIONS_ABSTAIN"
    elif not matches:
        classification="FALSIFIED_ALL_STORED_RELATIONS"
    elif full and len(matches)==1:
        classification="COMPLETE_DOMAIN_OBSERVATIONAL_EQUIVALENCE_NOT_AUTHENTICITY"
    elif full:
        classification="COMPLETE_DOMAIN_STILL_AMBIGUOUS_ABSTAIN"
    elif len(matches)==1:
        classification="PROVISIONAL_MATCH_UNSAFE_UNCERTIFIED"
    else:
        classification="AMBIGUOUS_OR_INCOMPLETE_ABSTAIN"
    return {
       "classification":classification,
       "compatible_slots":matches,
       "candidate_slot":matches[0] if len(matches)==1 else None,
       "public_observations":len(cues),
       "domain_actions":MAX_PUBLIC_PROBES,
       "full_domain_observed":full,
       "observational_equivalence_only":full and len(matches)==1,
       "source_identity_authenticated":False,
       "native_accepted":False,
       "scientific_pass":False,
       "safe_to_activate_accepted_model":False,
       "write_to_accepted_model":False,
    }

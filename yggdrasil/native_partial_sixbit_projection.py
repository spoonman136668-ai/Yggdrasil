"""WSP-156: strictly local projection of partial six-bit do evidence.

Engineering fixtures ONLY. An unobserved nuisance counterpart is *not* a
certificate of invariance, and a preexisting numerical prediction is not
source-certified evidence. All native learning uses unchanged NKR-04.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import json

from yggdrasil.native_evidence_compiler import (
    SCHEMA as NATIVE_SCHEMA, canonical_json, digest, stage_native_bundle
)
from yggdrasil.native_relation_memory import NativeRelationMemory
from yggdrasil.native_sixbit_projection import (
    _ascii, _mask, _unique, SOURCE_MODE, SOURCE_KIND, LICENSE
)

SCHEMA="yggdrasil.wsp156.partial-do-projection.v1"
RECEIPT_SCHEMA="yggdrasil.wsp156.partial-projection-candidate.v1"
MAX_INPUT_BYTES=32768
DOC_KEYS=frozenset(("schema","source_id","source_mode","source_kind",
                    "license","slot","action_bit","nuisance_bit","records"))

@dataclass(frozen=True)
class PartialNativeCandidate:
    """Provisional source-local certificate plus unchanged native checkpoint."""
    checkpoint:bytes
    verified_actions:tuple[int|None,...]
    receipt:dict

    def choose_certified(self,context:int)->int|None:
        """Answer only from *this source's* two fully witnessed action pairs."""
        if type(context) is not int or not 0<=context<16:
            raise ValueError("WSP156_CONTEXT_INVALID")
        return self.verified_actions[context]

def _parse(raw,expected_sha256):
    if type(raw) is not bytes or not 0<len(raw)<=MAX_INPUT_BYTES:
        raise ValueError("WSP156_SOURCE_BYTES_INVALID")
    if (type(expected_sha256) is not str or len(expected_sha256)!=64
            or any(ch not in "0123456789abcdef" for ch in expected_sha256)
            or not hmac.compare_digest(digest(raw),expected_sha256)):
        raise ValueError("WSP156_SOURCE_PIN_MISMATCH")
    try:
        doc=json.loads(raw.decode("ascii"),object_pairs_hook=_unique)
    except (ValueError, UnicodeError) as exc:
        raise ValueError("WSP156_SOURCE_DOCUMENT_INVALID") from exc
    if type(doc) is not dict or set(doc)!=DOC_KEYS:
        raise ValueError("WSP156_SOURCE_SCHEMA_INVALID")
    if (doc["schema"]!=SCHEMA or doc["source_mode"]!=SOURCE_MODE
            or doc["source_kind"]!=SOURCE_KIND or doc["license"]!=LICENSE):
        raise PermissionError("WSP156_UNQUALIFIED_SOURCE_DENIED")
    if not _ascii(doc["source_id"]):
        raise ValueError("WSP156_SOURCE_ID_INVALID")
    if raw!=canonical_json(doc):
        raise ValueError("WSP156_NONCANONICAL_SOURCE")
    slot,action_bit,nuisance_bit=(doc[k] for k in ("slot","action_bit","nuisance_bit"))
    if (type(slot) is not int or not 0<=slot<NativeRelationMemory.ADDRESSES
            or type(action_bit) is not int or not 0<=action_bit<6
            or type(nuisance_bit) is not int or not 0<=nuisance_bit<6
            or action_bit==nuisance_bit):
        raise ValueError("WSP156_PROJECTION_ROLE_INVALID")
    rows=doc["records"]
    if type(rows) is not list or not 1<=len(rows)<=64:
        raise ValueError("WSP156_PAID_EFFECT_COUNT_INVALID")
    seen_refs=set()
    by_mask={}
    prev=-1
    for row in rows:
        if (type(row) is not list or len(row)!=4
                or type(row[0]) is not int or not prev<row[0]<64
                or type(row[1]) is not int or row[1] not in (0,1)
                or row[2]!="observed_do" or not _ascii(row[3])
                or row[3] in seen_refs):
            raise ValueError("WSP156_ACTION_PROVENANCE_INVALID")
        prev=row[0]
        seen_refs.add(row[3])
        by_mask[row[0]]=(row[1],row[3])
    return doc,by_mask

def stage_partial_sixbit_bundle(raw,expected_source_sha256,*,prior_checkpoint=None):
    """Compile only *locally paired* nuisance-invariant do consequences.

    The 16-context certified action readout must NOT be replaced by native
    raw predict/fallback on an unsupported context. The checkpoint alone is
    not a source-ownership or global invariance certificate.
    """
    doc,by_mask=_parse(raw,expected_source_sha256)
    bit_a,bit_n=doc["action_bit"],doc["nuisance_bit"]
    context_bits=tuple(i for i in range(6) if i not in (bit_a,bit_n))
    slot=doc["slot"]
    rows=[]
    witnesses=[]
    incomplete=0
    absent=0
    certified={}
    for context in range(16):
        for action in (0,1):
            low=_mask(context,action,0,context_bits,bit_a,bit_n)
            high=_mask(context,action,1,context_bits,bit_a,bit_n)
            a,b=by_mask.get(low),by_mask.get(high)
            if a is None or b is None:
                if a is None and b is None:
                    absent+=1
                else:
                    incomplete+=1
                continue
            if a[0]!=b[0]:
                # Refuse all writes, not merely this bad native coordinate.
                raise ValueError("WSP156_WITNESSED_NUISANCE_CONTRADICTION")
            proof=[slot,context,action,[low,a[0],a[1]],[high,b[0],b[1]]]
            witnesses.append(proof)
            ref="wsp156:"+hashlib.sha256(
                canonical_json([doc["source_id"],proof])).hexdigest()
            rows.append([slot,context,action,a[0],ref])
            certified[context,action]=a[0]
    native_raw=canonical_json({
        "schema":NATIVE_SCHEMA,"source_id":doc["source_id"],
        "source_mode":SOURCE_MODE,"source_kind":SOURCE_KIND,
        "license":LICENSE,"records":rows
    })
    # The existing compiler handles prior checkpoint integrity, atomic
    # conflict rejection and native capacity. No native internals mutated.
    compiled=stage_native_bundle(native_raw,digest(native_raw),
                                 prior_checkpoint=prior_checkpoint)
    restored=NativeRelationMemory.restore(compiled.checkpoint)
    local=slot if slot<7 else slot-7
    verified_actions=[]
    witnessed_both=0
    for context in range(16):
        if (context,0) not in certified or (context,1) not in certified:
            verified_actions.append(None)
            continue
        witnessed_both+=1
        own_pair=(certified[context,0],certified[context,1])
        if restored.observed_action_pair(local,context,retained=slot>=7)!=own_pair:
            raise AssertionError("WSP156_NATIVE_COLD_READBACK_DIFFERENCE")
        # Both actions equally good: no evidence-based preference.
        verified_actions.append(
            0 if own_pair[0]>own_pair[1] else
            1 if own_pair[1]>own_pair[0] else None)
    receipt={
        "schema":RECEIPT_SCHEMA,
        "source_authenticity":"UNVERIFIED_EXACT_BYTES_ONLY",
        "source_sha256":expected_source_sha256,
        "projection_bits":{"action":bit_a,"nuisance":bit_n,"context":context_bits},
        "slot":slot,
        "charged_do_effects":len(by_mask),
        "certified_native_observations":len(rows),
        "single_nuisance_observations":incomplete,
        "unobserved_native_coordinates":absent,
        "both_actions_witnessed_contexts":witnessed_both,
        "verified_non_tied_actions":sum(x is not None for x in verified_actions),
        "verified_action_contexts":tuple(i for i,x in enumerate(verified_actions)
                                          if x is not None),
        "witness_proof_sha256":digest(canonical_json(witnesses)),
        "native_source_sha256":digest(native_raw),
        "candidate_checkpoint_sha256":digest(compiled.checkpoint),
        "candidate_checkpoint_bytes":len(compiled.checkpoint),
        "native_receipt":compiled.receipt,
        "science_pass":False,
        "source_first_use":False,
        "native_admission":False,
        "accepted_main_mutated":False
    }
    return PartialNativeCandidate(compiled.checkpoint,tuple(verified_actions),
                                  receipt)

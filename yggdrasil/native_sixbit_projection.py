"""WSP-155: source-free six-bit do-evidence projection into EXISTING NKR-04.

This is an exact witnessed adapter, not a new causal learner or weight store.
Only 64 complete, source-free development observations can justify discarding
one of six intervention bits. Arbitrary truncation is refused.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from yggdrasil.native_evidence_compiler import (
    SCHEMA as NATIVE_SCHEMA, canonical_json, digest, stage_native_bundle
)
from yggdrasil.native_relation_memory import NativeRelationMemory

SCHEMA="yggdrasil.wsp155.sixbit-do-projection.v1"
RECEIPT_SCHEMA="yggdrasil.wsp155.projection-candidate.v1"
MAX_INPUT_BYTES=32768
KEYS=frozenset(("schema","source_id","source_mode","source_kind",
                "license","slot","action_bit","nuisance_bit","records"))
SOURCE_MODE="engineering_fixture_only"
SOURCE_KIND="observed_public_intervention"
LICENSE="synthetic-fixture"

@dataclass(frozen=True)
class ProjectedNativeWeights:
    checkpoint:bytes
    receipt:dict

def _unique(pairs):
    result={}
    for key,val in pairs:
        if key in result:
            raise ValueError("WSP155_DUPLICATE_JSON_KEY")
        result[key]=val
    return result

def _ascii(value,limit=96):
    return (type(value) is str and 1<=len(value)<=limit and value.isascii()
            and all(33<=ord(x)<=126 for x in value))

def _doc(raw,expected_source_sha256):
    if type(raw) is not bytes or not 0<len(raw)<=MAX_INPUT_BYTES:
        raise ValueError("WSP155_INPUT_BYTES_INVALID")
    if (type(expected_source_sha256) is not str
            or len(expected_source_sha256)!=64
            or any(c not in "0123456789abcdef" for c in expected_source_sha256)
            or digest(raw)!=expected_source_sha256):
        raise ValueError("WSP155_SOURCE_PIN_MISMATCH")
    try:
        doc=json.loads(raw.decode("ascii"),object_pairs_hook=_unique)
    except (ValueError, UnicodeError) as exc:
        raise ValueError("WSP155_DOCUMENT_INVALID") from exc
    if type(doc) is not dict or set(doc)!=KEYS:
        raise ValueError("WSP155_SCHEMA_INVALID")
    if (doc["schema"]!=SCHEMA or doc["source_mode"]!=SOURCE_MODE
            or doc["source_kind"]!=SOURCE_KIND or doc["license"]!=LICENSE):
        raise PermissionError("WSP155_UNQUALIFIED_SOURCE")
    if not _ascii(doc["source_id"]):
        raise ValueError("WSP155_SOURCE_ID_INVALID")
    if raw!=canonical_json(doc):
        raise ValueError("WSP155_NONCANONICAL_SOURCE")
    slot=doc["slot"]
    action=doc["action_bit"]
    nuisance=doc["nuisance_bit"]
    if (type(slot) is not int or not 0<=slot<NativeRelationMemory.ADDRESSES
            or type(action) is not int or not 0<=action<6
            or type(nuisance) is not int or not 0<=nuisance<6
            or action==nuisance):
        raise ValueError("WSP155_PROJECTION_ROLE_INVALID")
    rows=doc["records"]
    if type(rows) is not list or len(rows)!=64:
        raise ValueError("WSP155_COMPLETE_SIXBIT_WITNESSES_REQUIRED")
    refs=set()
    by_mask={}
    for i,row in enumerate(rows):
        if (type(row) is not list or len(row)!=4
                or type(row[0]) is not int or row[0]!=i
                or type(row[1]) is not int or row[1] not in (0,1)
                or row[2]!="observed_do"
                or not _ascii(row[3]) or row[3] in refs):
            raise ValueError("WSP155_UNQUALIFIED_OR_REPEATED_ACTION")
        refs.add(row[3])
        by_mask[i]=(row[1],row[3])
    return doc,by_mask

def _mask(context,action,nuisance,context_bits,action_bit,nuisance_bit):
    mask=(action<<action_bit)|(nuisance<<nuisance_bit)
    for i,pos in enumerate(context_bits):
        mask|=((context>>i)&1)<<pos
    return mask

def stage_sixbit_do_bundle(raw,expected_source_sha256,*,prior_checkpoint=None):
    """Project only after 64 independent do witnesses certify invariance.

    Caller must independently authenticate REAL sources before any acceptance.
    Current source grammar admits engineering fixtures only.
    """
    doc,by_mask=_doc(raw,expected_source_sha256)
    action_bit=doc["action_bit"]
    nuisance_bit=doc["nuisance_bit"]
    slot=doc["slot"]
    context_bits=tuple(x for x in range(6) if x not in (action_bit,nuisance_bit))
    assert len(context_bits)==4
    native_rows=[]
    witnesses=[]
    for context in range(16):
        for action in (0,1):
            low=_mask(context,action,0,context_bits,action_bit,nuisance_bit)
            high=_mask(context,action,1,context_bits,action_bit,nuisance_bit)
            first=by_mask[low]
            second=by_mask[high]
            if first[0]!=second[0]:
                raise ValueError("WSP155_NUISANCE_DEPENDENCE_UNREPRESENTABLE")
            proof=[slot,context,action,[low,first[0],first[1]],
                   [high,second[0],second[1]]]
            witnesses.append(proof)
            ref="wsp155:"+hashlib.sha256(canonical_json(
                [doc["source_id"],proof])).hexdigest()
            native_rows.append([slot,context,action,first[0],ref])
    native_source=canonical_json({
        "schema":NATIVE_SCHEMA,"source_id":doc["source_id"],
        "source_mode":SOURCE_MODE,"source_kind":SOURCE_KIND,
        "license":LICENSE,"records":native_rows})
    native=stage_native_bundle(native_source,digest(native_source),
                               prior_checkpoint=prior_checkpoint)
    restored=NativeRelationMemory.restore(native.checkpoint)
    for context in range(16):
        pair=restored.observed_action_pair(
            slot if slot<7 else slot-7,context,retained=slot>=7)
        if pair!=tuple(native_rows[context*2+a][3] for a in (0,1)):
            raise AssertionError("WSP155_NATIVE_COLD_READBACK_MISMATCH")
    receipt={
        "schema":RECEIPT_SCHEMA,
        "source_authenticity":"UNVERIFIED_EXACT_BYTES_ONLY",
        "source_sha256":expected_source_sha256,
        "projection_bits":{"action":action_bit,"nuisance":nuisance_bit,
                           "context":context_bits},
        "slot":slot,"charged_do_witnesses":64,
        "invariance_comparisons":32,"native_observations":32,
        "native_bundle_sha256":digest(native_source),
        "witness_proof_sha256":digest(canonical_json(witnesses)),
        "candidate_checkpoint_sha256":digest(native.checkpoint),
        "native_receipt":native.receipt,
        "source_first_use":False,"scientific_pass":False,
        "native_admission":False,"accepted_main_mutated":False,
    }
    return ProjectedNativeWeights(native.checkpoint,receipt)

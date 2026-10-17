"""Y-F101: inspectable native-memory path witnesses and deletion/role interventions.

SOURCE-ONLY engineering. Does not choose memories, infer future answers, learn,
run protected source cohorts, or modify the original F99/F100/F62 mechanisms.
No external controller or credentials. Prereg frozen at ceda4afb6cbdd7....
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PREREG_BLOB = "ba93493da66e7659f3b75c49875b2eb7927d6a16"
F100_BLOB = "14066ad4f36e09e77134e7d5e192fcacf94b5810"
F99_BLOB = "5de08fe74eb74dd917a7559cc3a8755185aac823"
F62_BLOB = "7ed72deca5584d7c0b6562d74456fa7d4bee6712"
MAX_STATES = 150_000
MAX_SIGNATURES = 250_000
MAX_RECORDS = 12
MAX_BYTES = 144
MAX_HOPS = 6

class AttributionBoundExceeded(RuntimeError):
    """Fail closed; no partial decision-witness is ever admissible."""


def blob(path):
    data = Path(path).read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() +
                        b"\0" + data).hexdigest()


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, file)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def frozen_sources():
    if blob(HERE / "prereg.json") != PREREG_BLOB:
        raise AssertionError("F101_PREREGISTRATION_DRIFT")
    if blob(ROOT / "20261017-y-f100" / "presto.py") != F100_BLOB:
        raise AssertionError("F101_F100_PARENT_DRIFT")
    if blob(ROOT / "20261016-y-f99" / "causal_closure.py") != F99_BLOB:
        raise AssertionError("F101_F99_PARENT_DRIFT")
    if blob(ROOT / "20261015-y-f62" / "source_pilot.py") != F62_BLOB:
        raise AssertionError("F101_NATIVE_F62_PARENT_DRIFT")
    f100 = module("yf101_frozen_f100", ROOT/"20261017-y-f100"/"presto.py")
    f99 = f100.frozen_sources()
    native = module("yf101_frozen_f62", ROOT/"20261015-y-f62"/"source_pilot.py")
    return f99, native


def check_memory(memory):
    if type(memory) not in (tuple, list) or len(memory) > MAX_RECORDS:
        raise ValueError("F101_MEMORY_CAP_OR_TYPE")
    result = []
    for r in memory:
        if (type(r) not in (tuple, list) or len(r) != 3 or
            type(r[0]) is not int or type(r[1]) is not int or
            r[0] == r[1] or type(r[2]) not in (tuple,list) or
            not 1 <= len(r[2]) <= 6 or
            any(type(x) is not int or x < 0 or x > 7 for x in r[2])):
            raise ValueError("F101_MALFORMED_NATIVE_RECORD")
        result.append((r[0], r[1], tuple(r[2])))
    if 12 * len(result) > MAX_BYTES:
        raise AssertionError("F101_PACKED_MEMORY_OVER_BUDGET")
    return tuple(result)


def check_signature(signature):
    if (type(signature) not in (tuple, list) or len(signature) != 3 or
        type(signature[0]) is not int or type(signature[2]) is not int or
        type(signature[1]) not in (tuple, list) or
        not 1 <= len(signature[1]) <= MAX_HOPS or
        any(type(code) is not int or not 0 <= code <= 7
            for code in signature[1])):
        raise ValueError("F101_SIGNED_ROLE_SIGNATURE_SHAPE")
    return (signature[0], tuple(signature[1]), signature[2])


def oriented(memory, f99):
    arcs = {}
    for idx, (u,v,codes) in enumerate(memory):
        arcs.setdefault(u, []).append((idx,0,u,v,codes))
        arcs.setdefault(v, []).append((idx,1,v,u,f99.signed_reverse(codes)))
    return {k:tuple(sorted(a, key=lambda x:(x[0],x[1]))) for k,a in arcs.items()}


def witness(memory, signature, f99, max_states=MAX_STATES):
    """Lex-first native-record witness, exact codes, not fictitious inner nodes."""
    if type(max_states) is not int or max_states < 1:
        raise ValueError("F101_WITNESS_BUDGET_INVALID")
    mem = check_memory(memory)
    start, required, target = check_signature(signature)
    edges = oriented(mem, f99)
    visited = 0
    denied = set()

    def walk(node, consumed):
        nonlocal visited
        visited += 1
        if visited > max_states:
            raise AttributionBoundExceeded("F101_WITNESS_STATE_BOUND")
        if consumed == len(required):
            return () if node == target else None
        key = (node, consumed)
        if key in denied:
            return None
        for idx, direction, u, v, codes in edges.get(node, ()):
            n = len(codes)
            if consumed+n > len(required) or required[consumed:consumed+n] != codes:
                continue
            continuation = walk(v,consumed+n)
            if continuation is not None:
                return ((idx,direction,u,v,codes),)+continuation
        denied.add(key)
        return None

    path = walk(start,0)
    return path,visited


def memory_digest(memory):
    # Canonical structural byte receipt, NOT a Git/codec native packing claim.
    mem = check_memory(memory)
    return hashlib.sha256(json.dumps(mem,separators=(",",":")).encode()).hexdigest()


def role_shift(record):
    u,v,codes = record
    return (u,v,tuple(((x+2)%8) for x in codes))


def explain(memory, signature, f99, max_states=MAX_STATES):
    """Offline exact structural attribution with genuine recomputed ablations.

    Return source provenance, direct witness and real deletion/role effects.
    Computing a deletion is not equivalent to predicting online future value.
    """
    mem=check_memory(memory)
    sig=check_signature(signature)
    original=f99.closure(mem,max_hops=6,max_signatures=MAX_SIGNATURES)
    present=sig in original
    path,search_states=witness(mem,sig,f99,max_states=max_states)
    if present != (path is not None):
        raise AssertionError("F101_TRACE_NOT_EQUIVALENT_TO_FROZEN_CLOSURE")
    if path is not None:
        assert path[0][2]==sig[0] and path[-1][3]==sig[2]
        if tuple(c for p in path for c in p[4])!=sig[1]:
            raise AssertionError("F101_PATH_ROLE_ORDER_FABRICATED")
        if any(path[i][3]!=path[i+1][2] for i in range(len(path)-1)):
            raise AssertionError("F101_PATH_ENDPOINT_JOIN_FABRICATED")
    effects=[]
    if present:
        for i,record in enumerate(mem):
            without=mem[:i]+mem[i+1:]
            removal_preserves=sig in f99.closure(without,max_hops=6,
                                                  max_signatures=MAX_SIGNATURES)
            altered=mem[:i]+(role_shift(record),)+mem[i+1:]
            changed_role_preserves=sig in f99.closure(altered,max_hops=6,
                                                      max_signatures=MAX_SIGNATURES)
            effects.append(dict(
                native_record_index=i,source=record[0],target=record[1],
                signed_role_codes=list(record[2]),
                present_in_lex_first_witness=any(part[0]==i for part in path),
                necessary_under_single_record_deletion=not removal_preserves,
                survived_single_record_deletion=removal_preserves,
                survived_single_record_role_shift=changed_role_preserves,
                role_shifted_signed_codes=list(role_shift(record)[2])))
    return dict(
       schema="yggdrasil.f101.native-structural-memory-attribution.v1",
       status="STRUCTURAL_PATH_FOUND" if present else "NO_NATIVE_PATH",
       signature=dict(source=sig[0],signed_roles=list(sig[1]),target=sig[2]),
       retained_record_count=len(mem),retained_native_bytes=12*len(mem),
       memory_structural_sha256=memory_digest(mem),
       present_in_frozen_f99_closure=present,
       search_states_visited=search_states,
       exact_lex_first_witness=[
           dict(record_index=i,orientation="stored" if d==0 else "signed_inverse",
                from_node=u,to_node=v,signed_role_codes=list(codes))
           for i,d,u,v,codes in (path if path is not None else ())
       ],
       single_record_interventions=effects,
       total_necessary_records=sum(x["necessary_under_single_record_deletion"]
                                   for x in effects),
       result_scope="OFFLINE_NATIVE_MEMORY_STRUCTURE_NOT_BEHAVIORAL_CAUSAL_ACCURACY",
       any_question_answer_or_future_event_accessed=False,
       learned_parameter_changes=0,original_sci_first_use=False,
       independent_scientific_acceptance=False,
       accepted_ref_mutation=False,external_controller_access=False)


def native_smoke_receipt():
    """Unregistered negative-seed public stream; NO F62 FIT/DIAG/ORIGINAL read."""
    f99,native=frozen_sources()
    pack=native.codec()
    memories=[]
    for seed,family in ((-71,-2),(-72,-1)):
        tagged,question,_paths,regime=native._construct(seed,family)
        public=tuple(x[:3] for x in tagged)
        mem=()
        for event in public:
            mem=native._f60_step(mem,event,pack)
        native._valid_memory(mem,pack)
        candidates=sorted(f99.closure(mem,max_hops=6,max_signatures=MAX_SIGNATURES),
                          key=lambda x:(len(x[1]),x))
        chosen=candidates[:2]+candidates[-2:] if len(candidates)>=4 else candidates
        outputs=[explain(mem,sig,f99) for sig in chosen]
        if not all(x["present_in_frozen_f99_closure"] and
                   x["exact_lex_first_witness"] for x in outputs):
            raise AssertionError("F101_NATIVE_SOURCE_WITNESS_NOT_GROUNDED")
        memories.append(dict(seed=seed,source_family=family,regime=regime,
                             events=len(public),native_records=len(mem),
                             native_bytes=len(mem)*12,
                             witnessed_signatures=outputs))
    return dict(
        schema="yggdrasil.f101.source-only-native-memory-smoke.v1",
        frozen_f100_blob=F100_BLOB,frozen_f99_blob=F99_BLOB,
        frozen_f62_blob=F62_BLOB,
        source_only_nonfirstuse=True,
        no_online_policy_or_learning=True,
        no_protected_f62_sources=True,
        receipts=memories,
        scientific_acceptance=False)


def main():
    data=native_smoke_receipt()
    print(json.dumps(data,sort_keys=True,separators=(",",":")))

if __name__=="__main__":
    main()

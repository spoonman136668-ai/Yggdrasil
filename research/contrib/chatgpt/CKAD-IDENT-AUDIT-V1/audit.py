"""Read-only structural identifiability audit of already sealed CKAD-SHARED-V2.

This is retrospective evidence inspection. It NEVER imports a source generator,
trains any model, reads held truth, or performs an original/fabricated action.
A broader program class contains degree-1/2/3 action conjunctions; a zero-error
fit is a compatibility statement, not evidence that the program is true.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from yggdrasil.native_hypothesis_portfolio import canonical,digest
from yggdrasil.native_shared_operator_memory import NativeSharedOperatorMemory

ARCHIVE="research/contrib/chatgpt/CKAD-SHARED-V2/native-shared-checkpoint.json"
RESULT="research/contrib/chatgpt/CKAD-SHARED-V2/result.json"
PIN_CHECKPOINT_BLOB="57ccfdeecb63859b7f3232ec40d8a2739e3839af"
PIN_RESULT_BLOB="ae4935481c4b85a9f52bc8194ee83b651ed96d73"
OLD_SOURCE_SHA="cd9d52d86882326e6f0ecbb04979141dc6a2d893"
SUITE_CLASS="RETROSPECTIVE_SOURCE_FREE_IDENTIFIABILITY_AUDIT"
SLOTS=64
EXPANDED_GATES=tuple(g for g in range(1,32) if g.bit_count() in (1,2,3))
EXPRESSION_COUNT=64*len(EXPANDED_GATES)*2

def require(condition,reason):
    if not condition:
        raise ValueError("CKAD_IDENT_AUDIT_"+reason)

def pin_blob(path,expected):
    path=ROOT/path
    proc=subprocess.run(["git","-C",str(ROOT),"hash-object",str(path)],
                        text=True,capture_output=True,check=True,timeout=15)
    require(proc.stdout.strip()==expected,"GIT_BLOB_CUSTODY_"+path.name)
    return path.read_bytes()

def held_input_masks():
    raw=lambda m:hashlib.sha256(("ckad-shared-v2:held:"+str(m)).encode("ascii")).digest()
    masks=sorted(range(64),key=raw)
    held=tuple(sorted(masks[:32]))
    require(len(held)==32,"HELD_MASKS")
    return held

def public_program(mask,linear,gate,bias):
    """Independent arithmetic, never imports source_truth or a V2 actor."""
    return (((mask&linear).bit_count()&1)
            ^int((mask&32)!=0 and (mask&gate)==gate)^bias)

def expanded_candidates(witnesses):
    """Explicit 25-gate family; no outcome oracle, only sealed witnesses."""
    require(type(witnesses) in (list,tuple) and len(set(m for m,_ in witnesses))==len(witnesses),
            "WITNESSES")
    matches=[]
    minimum=99
    minimum_count=0
    for gate in EXPANDED_GATES:
        for linear in range(64):
            for bias in (0,1):
                differences=sum(public_program(mask,linear,gate,bias)!=y
                                for mask,y in witnesses)
                if differences==0:
                    matches.append((linear,gate,bias))
                if differences<minimum:
                    minimum=differences
                    minimum_count=1
                elif differences==minimum:
                    minimum_count+=1
    return matches,minimum,minimum_count

def consensus_at(programs,mask):
    """A structural certificate conditional on the admitted broader class."""
    require(type(mask) is int and 0<=mask<64,"MASK")
    if not programs:
        return None
    first=public_program(mask,*programs[0])
    return first if all(public_program(mask,*p)==first for p in programs) else None

def input_only_proposals(programs,allowed,source_slot,limit=4):
    """Potential distinguishing experiments only: no outcomes or calls."""
    require(type(allowed) in (tuple,list) and len(set(allowed))==len(allowed)
            and 0<=limit<=4,"PROPOSAL_SCOPE")
    pending=set(allowed)
    chosen=[]
    summary=[]
    while pending and len(chosen)<limit and programs:
        def value(mask):
            ones=sum(public_program(mask,*p)==1 for p in programs)
            balance=min(ones,len(programs)-ones)
            tiebreak=hashlib.sha256(
                ("ckad-ident-audit-v1:proposal:"+str(source_slot)+":"+str(mask))
                .encode("ascii")).digest()
            return (-balance,tiebreak,mask)
        best=min(pending,key=value)
        pending.remove(best)
        chosen.append(best)
        ones=sum(public_program(best,*p)==1 for p in programs)
        summary.append({"mask":best,"candidate_votes_zero":len(programs)-ones,
                        "candidate_votes_one":ones,
                        "potential_split":min(ones,len(programs)-ones)})
    return {"masks":chosen,"input_only":True,"source_effects_performed":0,
            "hypothetical_nonexecuted":True,
            "mask_sha256":digest(canonical(chosen)),"splits":summary}

def load_anchored():
    raw=pin_blob(ARCHIVE,PIN_CHECKPOINT_BLOB)
    previous=pin_blob(RESULT,PIN_RESULT_BLOB)
    bundle=json.loads(raw)
    scored=json.loads(previous)
    require(type(bundle) is dict and
            set(bundle)=={"schema","native_ascii","checkpoint_sha256",
                          "all_world_vector_sha256","fit_global_gate_mask"},
            "ARCHIVE_KEYS")
    cp=bundle["native_ascii"].encode("ascii")
    require(digest(cp)==bundle["checkpoint_sha256"],"COLD_PIN")
    model=NativeSharedOperatorMemory.restore(cp,bundle["checkpoint_sha256"])
    require(model._frozen and model.fit_worlds==16 and
            model.global_gate_support==bundle["fit_global_gate_mask"],
            "LEARNED_MEMORY")
    require(digest(canonical([model.vector(i) for i in range(64)]))==
            bundle["all_world_vector_sha256"],"COLD_READOUT")
    require(scored["worlds_total"]==64 and len(scored["cases"])==48
            and scored["original_source_actions"]==0 and
            scored["classification"]=="SHARED_OPERATOR_DEV_NO_GO",
            "PRIOR_RESULT_STATUS")
    return model,cp,scored

def witness_rows(model,slot):
    state,seen,ones,n=model._local._state(slot)
    rows=[(m,int(bool(ones&(1<<m)))) for m in range(64)
          if seen&(1<<m)]
    require(len(rows)==n and n in (8,16) and
            all(y in (0,1) for _,y in rows),"SEALED_ROWS")
    return rows

def audit():
    model,immutable,previous=load_anchored()
    held=held_input_masks()
    held_digest=digest(canonical(held))
    original_by_slot={x["slot"]:x for x in previous["cases"]}
    require(set(original_by_slot)==set(range(16,64)),"SLOT_INDEX")
    report=[]
    for slot in range(64):
        regime="FIT" if slot<16 else original_by_slot[slot]["regime"]
        rows=witness_rows(model,slot)
        seen={m for m,_ in rows}
        candidates,minimum,multiplicity=expanded_candidates(rows)
        require(len(candidates)<=EXPRESSION_COUNT and
                (minimum==0)==bool(candidates),"CANDIDATE_ACCOUNTING")
        not_seen=tuple(m for m in range(64) if m not in seen)
        consensus=[consensus_at(candidates,m) for m in not_seen]
        certificates=sum(y is not None for y in consensus)
        ambiguous=len(not_seen)-certificates if candidates else 0
        unsupported=len(not_seen) if not candidates else 0
        selected=tuple(m for m in held if m not in seen)
        if slot>=16:
            require(len(selected)==32 and
                    original_by_slot[slot]["held_input_sha256"]==held_digest,
                    "HELD_SOURCE_PIN")
            original_vec=model.vector(slot)
            require(digest(canonical([original_vec[m] for m in held]))==
                    original_by_slot[slot]["metrics"]["shared"]["answers_sha256"],
                    "READOUT_SOURCE_PIN")
            held_certified=sum(consensus_at(candidates,m) is not None for m in held)
            originally_answered=sum(original_vec[m] is not None for m in held)
            not_certified=sum(original_vec[m] is not None and
                        consensus_at(candidates,m) is None for m in held)
            require(held_certified<=len(held) and
                    originally_answered==(
                        original_by_slot[slot]["metrics"]["shared"]["correct"]+
                        original_by_slot[slot]["metrics"]["shared"]["wrong"]),
                    "SOURCE_ANSWER_ACCOUNTING")
            for m in held:
                broad=consensus_at(candidates,m)
                if broad is not None and original_vec[m] is not None:
                    require(broad==original_vec[m],"CERTIFIED_SOURCE_DISAGREEMENT")
            pool=tuple(m for m in range(64) if m not in held and m not in seen)
            require(len(pool)==24 and not set(pool)&seen
                    and not set(pool)&set(held),"PROPOSAL_POOL")
            proposals=input_only_proposals(candidates,pool,slot)
            wrong=original_by_slot[slot]["metrics"]["shared"]["wrong"]
            require(0<=wrong<=originally_answered,"FROZEN_WRONG")
        else:
            held_certified=0;originally_answered=0;not_certified=0;wrong=0
            proposals={"masks":[],"input_only":True,"source_effects_performed":0,
                       "hypothetical_nonexecuted":True,
                       "mask_sha256":digest(canonical([])),"splits":[]}
        report.append({
            "slot":slot,"regime":regime,"source_observations":len(rows),
            "source_witness_sha256":digest(canonical(rows)),
            "v2_admitted_programs":model.count(slot,True),
            "broadened_gate_count":len(EXPANDED_GATES),
            "broadened_programs_exactly_consistent":len(candidates),
            "minimum_label_mismatches":minimum,
            "minimum_mismatch_candidate_count":multiplicity,
            "unobserved_inputs":len(not_seen),
            "broad_unseen_unanimous":certificates,
            "broad_unseen_ambiguous":ambiguous,
            "broad_unseen_unsupported":unsupported,
            "held_mask_count":len(selected),
            "held_broad_unanimous":held_certified,
            "original_held_answered":originally_answered,
            "original_held_answered_not_broadly_certified":not_certified,
            "original_reported_wrong":wrong,
            "input_only_proposals":proposals})
    require(model.checkpoint()==immutable,"ORIGINAL_STATE_MUTATED")
    groups={}
    for group in ("FIT","TRANSFER","SHIFT","CORRUPT"):
        chosen=[c for c in report if c["regime"]==group]
        def total(field):return sum(c[field] for c in chosen)
        hist={}
        for c in chosen:
            k=str(c["minimum_label_mismatches"])
            hist[k]=hist.get(k,0)+1
        groups[group]={
            "worlds":len(chosen),
            "v2_singleton_worlds":sum(c["v2_admitted_programs"]==1 for c in chosen),
            "expanded_multiple_worlds":sum(c["broadened_programs_exactly_consistent"]>1 for c in chosen),
            "expanded_inconsistent_worlds":sum(c["broadened_programs_exactly_consistent"]==0 for c in chosen),
            "expanded_exact_candidate_total":total("broadened_programs_exactly_consistent"),
            "minimum_observed_mismatches_histogram":hist,
            "unseen_input_consensus":total("broad_unseen_unanimous"),
            "unseen_input_ambiguous":total("broad_unseen_ambiguous"),
            "unseen_input_unsupported":total("broad_unseen_unsupported"),
            "held_unanimous":total("held_broad_unanimous"),
            "held_original_answered":total("original_held_answered"),
            "held_original_answered_not_certified":total("original_held_answered_not_broadly_certified"),
            "original_wrong_answers":total("original_reported_wrong"),
            "hypothetical_proposals":sum(len(c["input_only_proposals"]["masks"])
                                         for c in chosen)}
    require(sum(g["worlds"] for g in groups.values())==SLOTS,"WORLD_TOTAL")
    require(all(x["source_effects_performed"]==0 for c in report
                for x in (c["input_only_proposals"],)),"NEW_SOURCE_ACTION")
    return {
        "schema":"ckad.identifiability.audit.v1.result",
        "classification":SUITE_CLASS,
        "scientific_pass":False,"accepted_native":False,
        "new_original_source_actions":0,"new_synthetic_source_actions":0,
        "held_outcome_reads":0,"new_model_training_calls":0,
        "source_commit":OLD_SOURCE_SHA,"source_checkpoint_git_blob":PIN_CHECKPOINT_BLOB,
        "source_result_git_blob":PIN_RESULT_BLOB,
        "source_checkpoint_sha256":digest(immutable),
        "family_terms":len(EXPANDED_GATES),
        "expanded_program_count":EXPRESSION_COUNT,
        "grouped":groups,"cases":report}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--expected-sha256")
    args=p.parse_args()
    result=audit()
    stable=digest(canonical(result))
    if args.expected_sha256:
        require(stable==args.expected_sha256,"CROSS_PLATFORM_DRIFT")
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_bytes(canonical({"result":result,"stable_sha256":stable}))
    print("CKAD_IDENT_V1_STABLE_SHA256="+stable,flush=True)
    print("CKAD_IDENT_V1_SUMMARY="+canonical(result["grouped"]).decode("ascii"),flush=True)

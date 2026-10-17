"""Y-F107 signed-source equivariance and teacher-contrast attribution.

Four transformations of EXACTLY the same fresh synthetic graph & question.
Native F60 receives only arrived public edges; ALL answer paths and signed
causal-credit targets are used only in the offline source diagnostic.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
PREREG_BLOB="41526d27e90f28efeba387d5513d64d6c075726b"
F106_BLOB="3b49cd349413c641a900e935f92270dbd3441f34"
F105_BLOB="f78cae2150b48b4c7ffb1274f80392a563bd64ce"
F104_BLOB="dd1f7bb2fd7288b5933f7a23085196c8a62e17b8"
F102_BLOB="8686390483c1e367c5cc1016a865a15c926b8376"
PARENT="84523755408d2685dca525950a1cc7718e13052b"
PERM=(2,0,3,1)
MODES=("raw","role_only","edge_direction_only","both")
SOURCE=((-20001,-111,0),(-20101,-112,8))
CHECKPOINTS=(11,23,35,47,59,71)
SCHEMA="yggdrasil.f107.signed-source-equivariance-public.v1"

class Invalid(ValueError): pass
def need(ok,reason):
    if not ok:raise Invalid("F107_"+reason)
def gitblob(path):
    b=Path(path).read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

def load():
    need(gitblob(HERE/"prereg.json")==PREREG_BLOB
         and gitblob(ROOT/"20261017-y-f106"/"identifiability.py")==F106_BLOB
         and gitblob(ROOT/"20261017-y-f105"/"relational_credit.py")==F105_BLOB
         and gitblob(ROOT/"20261017-y-f104"/"causal_credit.py")==F104_BLOB
         and gitblob(ROOT/"20261017-y-f102"/"delayed_credit.py")==F102_BLOB,
         "PARENT_SOURCE_OR_PRECODE_PREREG_DRIFT")
    protocol=json.loads((HERE/"prereg.json").read_text())
    need(protocol["schema"]==
         "yggdrasil.f107.signed-role-credit-equivariance-prereg.v1"
         and protocol["parent"]["exact_f106_head"]==PARENT
         and protocol["source"]["frozen_role_permutation"]==list(PERM)
         and protocol["source"]["arms"]==list(MODES)
         and all(protocol["authority"].values()),
         "FROZEN_PROTOCOL_IDENTITY_CHANGED")
    spec=importlib.util.spec_from_file_location(
         "yf107_pinned_f106",ROOT/"20261017-y-f106"/"identifiability.py")
    f106=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=f106
    spec.loader.exec_module(f106)
    _,f105,f104,parent,f102,native=f106.load()
    return protocol,f106,f105,f104,parent,f102,native

def role(r):
    need(type(r) is int and 0<=r<4,"ROLE_INVALID")
    return PERM[r]

def signed_role(code,mode):
    need(type(code) is int and 0<=code<=7 and mode in MODES,
         "SIGNED_ROLE_INVALID")
    ren=mode in ("role_only","both")
    inv=mode in ("edge_direction_only","both")
    return 2*(role(code//2) if ren else code//2) + ((code%2)^int(inv))

def transform(stream,question,mode):
    """Invert stored edge direction and query traversal direction jointly.

    Use one immutable raw public graph; preserve node IDs, order and question.
    No source answer or source seed is an online action input.
    """
    need(mode in MODES and len(stream)==72,"BAD_TRANSFORM")
    ren=mode in ("role_only","both")
    inv=mode in ("edge_direction_only","both")
    out=[]
    for u,r,v in stream:
        code=role(r) if ren else r
        out.append((v,code,u) if inv else (u,code,v))
    q=dict(start=question["start"],answer=question["answer"],
           ops=tuple((role(r) if ren else r, -direction if inv else direction)
                     for r,direction in question["ops"]))
    need(len(set(out))==72,"EDGE_SOURCE_COLLISION")
    return tuple(out),q

def paired_world(f102,native,seed,family,namespace):
    need(seed<0 and family<0 and 0<=namespace<16,
         "NOT_NEW_UNREGISTERED_PAIR")
    stream,q,identity=f102.episode(native,seed,family,"raw",namespace)
    return tuple((mode,*transform(stream,q,mode))
                 for mode in MODES),identity

def arcs(f99,mem):
    return frozenset((u,tuple(codes),v)
                     for u,items in f99.native_arcs(mem).items()
                     for v,codes in items)

def compare_native_arcs(f99,raw,changed,mode):
    desired=frozenset((u,tuple(signed_role(c,mode) for c in codes),v)
                      for u,codes,v in arcs(f99,raw))
    observed=arcs(f99,changed)
    return dict(exact_arc_equivariant=desired==observed,
                raw_arc_count=len(desired),changed_arc_count=len(observed),
                missing_expected_signed_arcs=len(desired-observed),
                extra_unexpected_signed_arcs=len(observed-desired))

def source_path_contract(f104,raw_q,raw_nodes,raw_codes,stream,q,mode):
    nodes,codes=f104.source_path(stream,q)
    need(nodes==raw_nodes and codes==
         tuple(signed_role(c,mode) for c in raw_codes),
         "ANSWER_PATH_NOT_BIJECTIVE_UNDER_MODE_"+mode)
    need(nodes[0]==raw_q["start"] and nodes[-1]==raw_q["answer"]
         and len(codes) in (4,6,8),"SOURCE_ANSWER_OR_HOPS_INVALID")
    return nodes,codes

def signs(values,baseline):
    return tuple(1 if v>baseline else (-1 if v<baseline else 0)
                 for v in values)

def native_trace(f105,f104,native,pack,stream,spans):
    memory=()
    receipts=[]
    for t,event in enumerate(stream):
        # These real F62 actions and fixed F60 transitions are future-blind.
        legal=native.actions(memory,event,t,pack)
        fixed=native._f60_step(memory,event,pack)
        need(sum(x[3]==fixed for x in legal)==1,"NATIVE_F60_NOT_IN_ACTION_SPACE")
        if t in CHECKPOINTS:
            previous=tuple(memory)
            idx=next(i for i,a in enumerate(legal) if a[3]==fixed)
            direct=[f104.structural_retained_score(a[3],spans,native)
                    for a in legal]
            suffix=stream[t+1:min(72,t+9)]
            delayed=[f104.structural_retained_score(
                     native._finish_fixed(a[3],suffix,pack),spans,native)
                     for a in legal]
            direct_labels=signs(direct,direct[idx])
            delayed_labels=signs(delayed,delayed[idx])
            direct_count=Counter(direct_labels)
            delayed_count=Counter(delayed_labels)
            receipts.append(dict(
                checkpoint=t,legal_actions=len(legal),
                prefix_mem_records=len(previous),
                prefix_memory_sha256=hashlib.sha256(
                    b"".join(pack.pack(*record) for record in previous)).hexdigest(),
                fixed_next_sha256=hashlib.sha256(
                    b"".join(pack.pack(*record) for record in fixed)).hexdigest(),
                eight_event_suffix_length=len(suffix),
                source_native_bytes=len(fixed)*12,
                positive_direct=direct_count[1],negative_direct=direct_count[-1],
                neutral_direct=direct_count[0],
                positive_eight_event=delayed_count[1],
                negative_eight_event=delayed_count[-1],
                neutral_eight_event=delayed_count[0],
                direct_scores=direct,delayed_scores=delayed,
                direct_labels=direct_labels,delayed_labels=delayed_labels,
                nonneutral_direct_lost_after_suffix=sum(
                    a!=0 and b==0 for a,b in zip(direct_labels,delayed_labels)),
                nonneutral_direct_created_after_suffix=sum(
                    a==0 and b!=0 for a,b in zip(direct_labels,delayed_labels)),
                changed_credit_sign_by_suffix=sum(
                    a!=b for a,b in zip(direct_labels,delayed_labels)),
                direct_teacher_future_path_only_offline=True,
                online_memory_action_no_query_seen=True))
        memory=fixed
        native._valid_memory(memory,pack)
    need(len(receipts)==6 and len(memory)<=12,
         "SOURCE_PREFIX_OR_NATIVE_BUDGET_INVALID")
    return tuple(memory),tuple(receipts)

def summary(rows,key):
    return dict(
      positive=sum(x["positive_"+key] for x in rows),
      negative=sum(x["negative_"+key] for x in rows),
      neutral=sum(x["neutral_"+key] for x in rows),
      action_labels=sum(x["legal_actions"] for x in rows))

def analyze_pair(f104,f105,f102,native,f99,pack,seed,family,namespace):
    pair,original_id=paired_world(f102,native,seed,family,namespace)
    raw_stream,raw_q=pair[0][1:]
    raw_nodes,raw_codes=f104.source_path(raw_stream,raw_q)
    mode_results={}
    raw_memory=None
    for mode,stream,q in pair:
        nodes,codes=source_path_contract(f104,raw_q,raw_nodes,raw_codes,
                                         stream,q,mode)
        spans=f104.subpaths(nodes,codes)
        mem,receipts=native_trace(f105,f104,native,pack,stream,spans)
        if mode=="raw":raw_memory=mem
        mode_results[mode]=dict(
            source_sha256=hashlib.sha256(json.dumps(
                [stream,q["start"],q["ops"],q["answer"]],
                sort_keys=True).encode()).hexdigest(),
            source_answer_path_preserved=True,
            path_hops=len(codes),
            source_signed_codes=list(codes),
            native_final_memory_records=len(mem),
            native_final_memory_sha256=hashlib.sha256(
                b"".join(pack.pack(*record) for record in mem)).hexdigest(),
            final_structural_credit=f104.structural_retained_score(
                mem,spans,native),
            direct=summary(receipts,"direct"),
            eight_event=summary(receipts,"eight_event"),
            vanished_direct_credit=sum(
                x["nonneutral_direct_lost_after_suffix"] for x in receipts),
            created_delayed_credit=sum(
                x["nonneutral_direct_created_after_suffix"] for x in receipts),
            signed_native_equivariance=None if mode=="raw" else
                 compare_native_arcs(f99,raw_memory,mem,mode),
            checkpoints=receipts)
    need(raw_memory is not None and len(mode_results)==4,
         "MISSING_PAIRED_MODE")
    return dict(seed_OFFLINE_ONLY=seed,original_graph_sha256=original_id,
                same_identity_mode_pair=True,
                source_family_OFFLINE_ONLY=family,
                question_answer_never_online=True,
                path_hops=len(raw_codes),modes=mode_results)

def evaluate(head):
    need(type(head) is str and len(head)==40 and
         all(c in "0123456789abcdef" for c in head),
         "GIT_HEAD_REQUIRED")
    protocol,f106,f105,f104,parent,f102,native=load()
    cfg,f101,f99,_=f102.source_modules()
    pack=native.codec()
    all_pairs=[]
    blocks=[]
    for g,(first,family,namespace) in enumerate(SOURCE):
        pairs=[analyze_pair(f104,f105,f102,native,f99,pack,
                   first-i,family,namespace+i) for i in range(8)]
        all_pairs.extend(pairs)
        blocks.append(dict(name=protocol["source"][
            "new_paired_negative_seed_cases"][g]["name"],
            cases=len(pairs),paired_results=pairs))
    ids=[p["original_graph_sha256"] for p in all_pairs]
    need(len(ids)==16 and len(set(ids))==16,"DUPLICATE_SOURCE_IDENTITY")
    overall={}
    for mode in MODES:
        reports=[p["modes"][mode] for p in all_pairs]
        overall[mode]=dict(
            paired_episodes=len(reports),
            direct=dict(positive=sum(r["direct"]["positive"] for r in reports),
                negative=sum(r["direct"]["negative"] for r in reports),
                neutral=sum(r["direct"]["neutral"] for r in reports)),
            eight_event=dict(
                positive=sum(r["eight_event"]["positive"] for r in reports),
                negative=sum(r["eight_event"]["negative"] for r in reports),
                neutral=sum(r["eight_event"]["neutral"] for r in reports)),
            direct_credit_vanished_with_eight_event_suffix=sum(
                r["vanished_direct_credit"] for r in reports),
            direct_credit_created_by_eight_event_suffix=sum(
                r["created_delayed_credit"] for r in reports),
            total_final_f60_structural_credit=sum(
                r["final_structural_credit"] for r in reports),
            exact_native_f60_arc_equivariant_cases=(
                None if mode=="raw" else sum(
                  r["signed_native_equivariance"]["exact_arc_equivariant"]
                  for r in reports)))
    return dict(
        schema=SCHEMA,exact_head=head,
        frozen_F106_source_head=PARENT,
        frozen_F106_git_blob=F106_BLOB,
        first_prereg_git_blob=PREREG_BLOB,
        source_kind="PUBLIC_SYNTHETIC_FROZEN_PAIRED_DIAG_NOT_PROTECTED",
        raw_base_cases=16, paired_mode_cases=64,
        native_online_events_per_case=72,
        native_max_retained_bytes=144,
        checked_source_path_bijective_for_all_modes=True,
        same_underlying_graph_for_each_mode=True,
        no_F102_F106_consumed_diagnostics_reused=True,
        no_F62_protected_FIT_DIAG_ORIGINAL=True,
        all_future_query_and_label_access_offline_only=True,
        no_new_online_policy_or_fitted_parameters=True,
        blocks=blocks,summary_by_mode=overall,
        teacher_collapse_modes=[
          mode for mode in MODES if overall[mode]["eight_event"]["positive"]+
                 overall[mode]["eight_event"]["negative"]==0],
        source_information_loss=False,
        source_only_not_real_independent_scientific_firstuse=True,
        scientific_acceptance=False,
        accepted_ref_mutations=0,
        no_optimizer_promotion=True,
        Codex_used=False,CKB_connected=False,
        MindPalace_written=False)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-ref",required=True)
    args=parser.parse_args()
    print(json.dumps(evaluate(args.source_ref),sort_keys=True,separators=(",",":")))
if __name__=="__main__":
    main()

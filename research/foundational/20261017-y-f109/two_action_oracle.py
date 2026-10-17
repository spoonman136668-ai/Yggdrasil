"""Y-F109: frozen two-decision future-answer native memory oracle, NOT an online learner.

Prereg frozen before executable code at 8c932a2638dadb10cb5b9fc4fce5e460c3a1a067.
Native F62 policy runs source-only. Full future and true target are used ONLY
in diagnostic counterfactual branches; all base online transitions are blind.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
FREEZE="dd0fe76e9a833283102ef67366f09d9cea1d84d1"
F108_BLOB="07aae5b5717a7b02af1b09eb0df686fb1dc89cd5"
PARENT="1831f380a0987fd70f6806a4e4581280c181a956"
SOURCE=((-22001,-131,0,"S109-A"),(-22101,-132,6,"S109-B"))
MODES=("raw","reverse_arrival")
CHECKPOINTS=(11,23,35,47,59)
OFFSETS=(1,8)
SCHEMA="yggdrasil.f109.two-native-intervention-oracle-public.v1"

class Invalid(ValueError):pass
def require(flag,label):
    if not flag:raise Invalid("F109_"+label)
def gitblob(path):
    data=Path(path).read_bytes()
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\x00"+data).hexdigest()

def load():
    require(gitblob(HERE/"prereg.json")==FREEZE and
            gitblob(ROOT/"20261017-y-f108"/"oracle.py")==F108_BLOB,
            "PREREG_OR_F108_SOURCE_CHANGED")
    cfg=json.loads((HERE/"prereg.json").read_text())
    require(cfg["schema"]=="yggdrasil.f109.paired-native-action-oracle-prereg.v1"
            and cfg["parent"]["exact_f108_head"]==PARENT
            and cfg["source"]["second_intervention_offsets"]==list(OFFSETS)
            and cfg["source"]["checkpoint_events"]==list(CHECKPOINTS)
            and all(cfg["authority"].values()),"PRECODE_PROTOCOL_CHANGED")
    spec=importlib.util.spec_from_file_location(
        "y_f109_pinned_f108",ROOT/"20261017-y-f108"/"oracle.py")
    f108=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=f108
    spec.loader.exec_module(f108)
    _,f107,f104,f102,native=f108.load()
    return cfg,f108,f104,f102,native

def hash_memory(f108,pack,mem):
    return f108.digest(mem,pack)

def fixed_prefixes(native,pack,stream):
    state=()
    prefixes=[]
    for edge in stream:
        prefixes.append(state)
        state=native._f60_step(state,edge,pack)
    require(len(prefixes)==72 and len(state)<=12,"BAD_F60_SOURCE")
    return tuple(prefixes),state

def eval_world(f108,native,pack,stream,q,source_id,mode):
    require(mode in MODES and len(stream)==72,"SOURCE_EVENT_SHAPE")
    prefixes,terminal=fixed_prefixes(native,pack,stream)
    baseline_ok=int(pack.solve(terminal,q)==q["answer"])
    windows=[]
    for t in CHECKPOINTS:
        fixed,first_states=f108.candidate_states(
             native,pack,prefixes[t],stream[t],t,12)
        require(fixed==prefixes[t+1],"PREFIX_ACTION_F60_DRIFT")
        initial=[]
        for ix,(first_j,after) in enumerate(first_states):
            resolved=f108.finish(native,pack,after,stream[t+1:],12)
            initial.append(int(pack.solve(resolved,q)==q["answer"]))
        first_baseline_idx=next(i for i,(_,v) in enumerate(first_states)
                                if v==fixed)
        require(initial[first_baseline_idx]==baseline_ok,
                "INITIAL_BASELINE_TERMINAL_DRIFT")
        for offset in OFFSETS:
            u=t+offset
            require(u<72,"SECOND_INDEX_OVERFLOW")
            all_options=[]
            independent_second=[]
            # The second choice is conditioned on the first choice's actual
            # F60-reached memory; there is no synthesized shortcut action.
            for first_i,(first_j,first_state) in enumerate(first_states):
                second_before=f108.finish(native,pack,first_state,
                                         stream[t+1:u],12)
                second_fixed,second_states=f108.candidate_states(
                    native,pack,second_before,stream[u],u,12)
                second_fixed_i=next(i for i,(_,m) in enumerate(second_states)
                                    if m==second_fixed)
                for second_i,(second_j,after_second) in enumerate(second_states):
                    result=f108.finish(native,pack,after_second,
                                       stream[u+1:],12)
                    success=int(pack.solve(result,q)==q["answer"])
                    first_changed=(first_i!=first_baseline_idx)
                    second_changed=(second_i!=second_fixed_i)
                    all_options.append(dict(
                        first_native_action_index=first_j,
                        second_native_action_index=second_j,
                        first_altered=first_changed,
                        second_altered=second_changed,
                        final_correct=success,
                        final_native_memory_sha256=hash_memory(
                            f108,pack,result),
                        final_native_records=len(result)))
                    if not first_changed and second_changed:
                        independent_second.append(success)
                    if (not first_changed and not second_changed):
                        require(success==baseline_ok,
                                "TWO_POINT_F60_PARITY_BROKEN")
            first_rescue=not baseline_ok and any(
               outcome for i,outcome in enumerate(initial)
               if i!=first_baseline_idx)
            second_rescue=not baseline_ok and any(independent_second)
            pair_rescue=not baseline_ok and any(
               c["final_correct"] for c in all_options)
            coordination=not baseline_ok and not first_rescue and not second_rescue and any(
               c["final_correct"] and c["first_altered"] and c["second_altered"]
               for c in all_options)
            windows.append(dict(
                t=t,second_t=u,offset=offset,
                source_native_144B_original_F60=True,
                fixed_terminal_correct=baseline_ok,
                first_native_states=len(first_states),
                exact_legal_pair_outcomes=all_options,
                legal_pair_count=len(all_options),
                single_action_at_first_rescue=bool(first_rescue),
                single_action_at_second_rescue=bool(second_rescue),
                either_single_action_rescue=bool(first_rescue or second_rescue),
                two_action_any_rescue=bool(pair_rescue),
                strictly_coordinated_two_action_synergy=bool(coordination),
                F60_native_prefix_memory_sha256=hash_memory(
                    f108,pack,prefixes[t]),
                no_answer_or_future_access_in_online_controller=True))
    require(len(windows)==len(CHECKPOINTS)*len(OFFSETS),
            "MISSING_WINDOWS")
    return dict(source_sha256=source_id,arrival_mode=mode,
                full_native_F60_terminal_correct=baseline_ok,
                full_native_F60_final_sha256=hash_memory(
                    f108,pack,terminal),
                windows=windows)

def aggregate(worlds):
    rows=[w for x in worlds for w in x["windows"]]
    return dict(worlds=len(worlds),windows=len(rows),
       real_F60_correct=sum(w["full_native_F60_terminal_correct"]
                            for w in worlds),
       native_two_action_combinations=sum(w["legal_pair_count"] for w in rows),
       first_point_rescues=sum(w["single_action_at_first_rescue"] for w in rows),
       second_point_rescues=sum(w["single_action_at_second_rescue"] for w in rows),
       any_single_rescues=sum(w["either_single_action_rescue"] for w in rows),
       any_two_action_rescues=sum(w["two_action_any_rescue"] for w in rows),
       strict_two_action_synergies=sum(
           w["strictly_coordinated_two_action_synergy"] for w in rows))

def evaluate(head):
    require(type(head) is str and len(head)==40 and
            all(ch in "0123456789abcdef" for ch in head),
            "EXACT_HEAD_REQUIRED")
    cfg,f108,f104,f102,native=load()
    pack=native.codec()
    blocks=[]
    all_ids=[]
    for family,(first,group,ns,label) in enumerate(SOURCE):
        worlds=[]
        for i in range(6):
            seed=first-i
            source,q,identity=f102.episode(native,seed,group,"raw",ns+i)
            other=tuple(reversed(source))
            full=f104.source_path(source,q)
            reverse_full=f104.source_path(other,q)
            require(full==reverse_full,"FULL_PUBLIC_SOURCE_PATH_CHANGED")
            all_ids.append(identity)
            for mode,stream in (("raw",source),("reverse_arrival",other)):
                worlds.append(eval_world(f108,native,pack,
                                          stream,q,identity,mode))
        require(len(worlds)==12,"MISSING_FAMILY_WORLDS")
        blocks.append(dict(name=label,worlds=worlds,summary=aggregate(worlds)))
    require(len(set(all_ids))==12,"DUPLICATE_SOURCE_GRAPH_IDENTITIES")
    all_worlds=[w for block in blocks for w in block["worlds"]]
    totals=aggregate(all_worlds)
    require(totals["worlds"]==24 and totals["windows"]==240,
            "PRECOMMITTED_WORLD_OR_WINDOW_MISSING")
    return dict(schema=SCHEMA,head=head,
       frozen_F108_exact_sha=PARENT,
       precode_frozen_git_blob=FREEZE,
       f108_exact_source_git_blob=F108_BLOB,
       source="PUBLIC_SYNTHETIC_NEW_NEGATIVE_NATIVE_F62_GRAPHS_ONLY",
       base_graphs=12,paired_arrival_worlds=24,
       frozen_first_checkpoints=list(CHECKPOINTS),
       frozen_second_offsets=list(OFFSETS),
       original_native_record_limit=12,native_record_bytes=12,
       source_public_answer_path_verified_across_arrival_modes=True,
       source_only_undeployable_future_answer_oracle=True,
       no_protected_original_or_prior_GUARD_DIAG_reuse=True,
       no_new_learned_or_controller_policy=True,
       blocks=blocks,totals=totals,
       disposition=("LIMITED_TWO_ACTION_FEASIBILITY_SOURCE_ONLY"
           if totals["strict_two_action_synergies"]>0
           else "NO_TWO_ACTION_SYNERGY_OBSERVED_SOURCE_ONLY"),
       no_independently_accepted_scientific_firstuse=True,
       no_generalization_or_superiority_claim=True,
       accepted_refs_mutated=0,optimizer_promoted=False,
       CKB_connected=False,Codex_used=False,MindPalace_written=False)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-ref",required=True)
    args=parser.parse_args()
    print(json.dumps(evaluate(args.source_ref),sort_keys=True,separators=(",",":")))
if __name__=="__main__":main()

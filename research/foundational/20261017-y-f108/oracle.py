"""Y-F108: exact native fixed controller, capacity stress and future-answer oracle.

Research instrument ONLY. This does not fit a model, expose queries online, use
scientific first-use sources or mutate external controllers. F108 prereg was
frozen at Git commit 190d7fa6ab623416c4738026588cbed7856ff781.
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
FREEZE="6d1a6d922645a840e155c5b0550667ecbf3f63d2"
F107_BLOB="3e39984754c87e702ed48030862f2237a6bd120e"
F104_BLOB="dd1f7bb2fd7288b5933f7a23085196c8a62e17b8"
F102_BLOB="8686390483c1e367c5cc1016a865a15c926b8376"
PARENT_HEAD="135137f7b2ee013dc0e1b2b80b18507d9f6229e6"
FAMILIES=((-21001,-121,0,"rolling_interleaved_hubs"),
          (-21101,-122,6,"delayed_public_joins"))
MODES=("raw","reverse_arrival")
CAPS=(4,8,12)
CHECKPOINTS=(11,23,35,47,59,71)
SCHEMA="yggdrasil.f108.native-memory-capacity-oracle-public.v1"

class BadSource(ValueError):pass
def require(ok,reason):
    if not ok:raise BadSource("F108_"+reason)
def gitblob(path):
    data=Path(path).read_bytes()
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()

def load():
    require(gitblob(HERE/"prereg.json")==FREEZE and
            gitblob(ROOT/"20261017-y-f107"/"signed_role_diagnosis.py")==F107_BLOB
            and gitblob(ROOT/"20261017-y-f104"/"causal_credit.py")==F104_BLOB
            and gitblob(ROOT/"20261017-y-f102"/"delayed_credit.py")==F102_BLOB,
            "PRECODE_SOURCE_OR_PARENT_DRIFT")
    data=json.loads((HERE/"prereg.json").read_text())
    require(data["schema"]==
        "yggdrasil.f108.frozen-native-capacity-information-oracle.v1" and
        data["parent"]["exact_f107_head"]==PARENT_HEAD and
        data["source"]["capacities"]==list(CAPS) and
        data["source"]["modes"]==list(MODES) and
        all(data["authority"].values()),"FROZEN_PLAN_CHANGED")
    spec=importlib.util.spec_from_file_location("f108_frozen_f107",
        ROOT/"20261017-y-f107"/"signed_role_diagnosis.py")
    f107=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=f107
    spec.loader.exec_module(f107)
    _,f106,f105,f104,parent,f102,native=f107.load()
    return data,f107,f104,f102,native

def pair(f102,native,seed,family,namespace,regime):
    require(seed<0 and family<0 and 0<=namespace<12,
            "UNREGISTERED_SOURCE_REQUIRED")
    stream,q,identity=f102.episode(native,seed,family,"raw",namespace)
    need_regime="rolling_interleaved_hubs" if family%2 else "delayed_public_joins"
    require(need_regime==regime and len(stream)==72,
            "NATIVE_F62_FAMILY_OR_EVENT_DRIFT")
    return (("raw",stream,q),("reverse_arrival",tuple(reversed(stream)),q)),identity

def trim(mem,cap):
    require(type(cap) is int and cap in CAPS and len(mem)<=12,
            "NATIVE_CAP_NOT_AUTHORIZED")
    # This is an explicit TAIL-TRUNCATION STRESS ADAPTER after every F60
    # step, not the unchanged F60 itself except when cap=12.
    return tuple(mem[-cap:])

def step(native,pack,mem,event,cap):
    out=native._f60_step(mem,event,pack)
    return trim(out,cap)

def finish(native,pack,mem,suffix,cap):
    cur=tuple(mem)
    for event in suffix:
        cur=step(native,pack,cur,event,cap)
    return cur

def digest(mem,pack):
    return hashlib.sha256(b"".join(pack.pack(*row) for row in mem)).hexdigest()

def candidate_states(native,pack,memory,event,t,cap):
    native._valid_memory(memory,pack)
    raw=native.actions(memory,event,t,pack)
    baseline=step(native,pack,memory,event,cap)
    states=[]
    seen=set()
    for j,a in enumerate(raw):
        after=trim(a[3],cap)
        native._valid_memory(after,pack)
        if after not in seen:
            seen.add(after)
            states.append((j,after))
    require(sum(after==baseline for _,after in states)==1,
            "F60_ADAPTED_CHOICE_MISSING_FROM_NATIVE_ACTIONS")
    return baseline,tuple(states)

def path_public(f104,stream,q):
    nodes,codes=f104.source_path(stream,q)
    require(nodes[0]==q["start"] and nodes[-1]==q["answer"]
       and len(codes) in (4,6,8),"FULL_SOURCE_ANSWER_PATH_MISSING")
    return nodes,codes,f104.subpaths(nodes,codes)

def analyze_episode(f104,f102,native,pack,stream,q,cap,mode,source_id):
    # Verify full public source oracle before any limited-memory decisions.
    nodes,codes,spans=path_public(f104,stream,q)
    memory=()
    checkpoints=[]
    for t,event in enumerate(stream):
        if t in CHECKPOINTS:
            baseline,states=candidate_states(native,pack,memory,event,t,cap)
            future=stream[t+1:]
            short=future[:8]
            # True answer oracle: unavailable to online fixed F60. Every
            # candidate uses SAME cap-adapted suffix. Not a new learned policy.
            terminal=[]
            structural=[]
            current=[]
            for j,after in states:
                final=finish(native,pack,after,future,cap)
                shortmem=finish(native,pack,after,short,cap)
                terminal.append(dict(
                  native_action_index=j,
                  native_after_records=len(after),
                  native_after_sha256=digest(after,pack),
                  final_after_sha256=digest(final,pack),
                  true_terminal_correct=int(pack.solve(final,q)==q["answer"]),
                  eight_event_structural_potential=f104.structural_retained_score(
                      shortmem,spans,native)))
            fixed_index=next(i for i,(_,s) in enumerate(states) if s==baseline)
            fixed=terminal[fixed_index]
            baseline_correct=fixed["true_terminal_correct"]
            baseline_potential=fixed["eight_event_structural_potential"]
            for item in terminal:
                item["eight_event_structural_positive_relative_to_fixed"]=(
                    item["eight_event_structural_potential"]>baseline_potential)
                item["terminal_rescue_relative_to_fixed"]=(
                    item["true_terminal_correct"]>baseline_correct)
            any_structural=any(x["eight_event_structural_positive_relative_to_fixed"]
                               for x in terminal)
            any_rescue=any(x["terminal_rescue_relative_to_fixed"]
                           for x in terminal)
            # Classification compares existentially available improvement on
            # the same checkpoint, not learned choices or a combined policy.
            checkpoints.append(dict(
                t=t,source_native_memory_before_sha256=digest(memory,pack),
                source_native_memory_records=len(memory),
                fixed_next_memory_sha256=digest(baseline,pack),
                legal_native_action_states=len(states),
                original_native_legal_actions=len(native.actions(memory,event,t,pack)),
                source_native_cap_records=cap,
                original_F60_at_cap_12=(cap==12),
                cap_stress_post_event_tail_truncation=(cap<12),
                fixed_action_index_in_deduplicated_states=fixed_index,
                fixed_eventual_correct=baseline_correct,
                some_legal_one_action_answer_rescue=any_rescue,
                some_legal_one_action_positive_eight_step_proxy=any_structural,
                proxy_true_positive=int(any_structural and any_rescue),
                proxy_false_positive=int(any_structural and not any_rescue),
                proxy_missed_rescue=int(not any_structural and any_rescue),
                proxy_true_negative=int(not any_structural and not any_rescue),
                candidate_outcomes=terminal,
                fixed_source_path_full_public_only_offline=True,
                online_fixed_controller_receives_only_prefix=True))
        memory=step(native,pack,memory,event,cap)
        native._valid_memory(memory,pack)
    require(len(checkpoints)==len(CHECKPOINTS) and len(memory)<=cap,
            "CHECKPOINT_COUNT_OR_MEMORY_LIMIT")
    final_correct=int(pack.solve(memory,q)==q["answer"])
    # F60 parity for original 12-record regime; truncated stress arms are
    # explicitly NOT a faithful implementation of the original native F60.
    if cap==12:
        baseline=()
        for event in stream:
            baseline=native._f60_step(baseline,event,pack)
        require(baseline==memory,"FROZEN_F60_REAL_NATIVE_DRIFT")
    return dict(mode=mode,capacity_records=cap,
        capacity_bytes=12*cap,native_persistent_bytes=len(memory)*12,
        endpoint_answer_available_in_full_public_graph=True,
        source_path_hops=len(codes),
        fixed_terminal_correct=final_correct,
        final_memory_sha256=digest(memory,pack),
        source_sha256=source_id,
        checkpoints=checkpoints)

def summarize(cases):
    points=[p for c in cases for p in c["checkpoints"]]
    return dict(world_count=len(cases),checkpoint_count=len(points),
        fixed_terminal_correct=sum(c["fixed_terminal_correct"] for c in cases),
        baseline_incorrect_checkpoints=sum(not p["fixed_eventual_correct"]
                                           for p in points),
        true_one_action_rescue_available=sum(
            p["some_legal_one_action_answer_rescue"] for p in points),
        eight_event_proxy_positive_available=sum(
            p["some_legal_one_action_positive_eight_step_proxy"] for p in points),
        proxy_true_positive=sum(p["proxy_true_positive"] for p in points),
        proxy_false_positive=sum(p["proxy_false_positive"] for p in points),
        proxy_missed_rescue=sum(p["proxy_missed_rescue"] for p in points),
        proxy_true_negative=sum(p["proxy_true_negative"] for p in points),
        evaluated_native_action_states=sum(
            p["legal_native_action_states"] for p in points))

def evaluate(head):
    require(type(head) is str and len(head)==40
            and all(c in "0123456789abcdef" for c in head),
            "SOURCE_COMMIT_REQUIRED")
    protocol,f107,f104,f102,native=load()
    pack=native.codec()
    blocks=[]
    all_ids=[]
    for group,(first,family,namespace,regime) in enumerate(FAMILIES):
        worlds=[]
        for offset in range(6):
            seed=first-offset
            pairs,identity=pair(f102,native,seed,family,namespace+offset,regime)
            all_ids.append(identity)
            raw_nodes,raw_codes,_=path_public(f104,pairs[0][1],pairs[0][2])
            rev_nodes,rev_codes,_=path_public(f104,pairs[1][1],pairs[1][2])
            require((raw_nodes,raw_codes)==(rev_nodes,rev_codes),
                    "SOURCE_REVERSE_ARRIVAL_CHANGED_TRUE_ANSWER")
            for mode,stream,q in pairs:
                for cap in CAPS:
                    outcome=analyze_episode(
                        f104,f102,native,pack,stream,q,cap,mode,identity)
                    worlds.append(outcome)
        blocks.append(dict(name=protocol["source"][
            "two_independent_negative_seed_families"][group]["label"],
            native_generator_regime=regime,
            distinct_original_graphs=6,
            evaluated_worlds=len(worlds),
            outcomes=worlds,
            summary_by_mode_capacity={
              mode:{str(cap):summarize([c for c in worlds
                        if c["mode"]==mode and c["capacity_records"]==cap])
                    for cap in CAPS}
              for mode in MODES}))
    require(len(set(all_ids))==12 and
            sum(len(b["outcomes"]) for b in blocks)==72,
            "PAIRED_SOURCE_IDENTITIES_OR_WORLD_COUNTS")
    # NOTE 12 base graphs × 2 arrival modes × 3 budgets = 72 worlds;
    # each contains six audits: 432 fully replayed native checkpoints.
    counts=summarize([c for b in blocks for c in b["outcomes"]])
    require(counts["checkpoint_count"]==432,
            "ALL_PRECOMMITTED_CHECKPOINTS_NOT_EVALUATED")
    return dict(schema=SCHEMA,exact_head=head,parent_F107_head=PARENT_HEAD,
        frozen_F107_git_blob=F107_BLOB,precode_prereg_git_blob=FREEZE,
        source_kind="PUBLIC_SYNTHETIC_F62_NATIVE_NEGATIVE_SEEDS_ONLY",
        source_base_graphs=12,source_paired_modes=2,
        memory_cap_stress_levels=list(CAPS),world_count=72,
        complete_native_action_checkpoint_count=432,
        same_full_public_source_answer_for_both_arrival_orders=True,
        no_prior_guards_or_protected_source_accessed=True,
        fixed_policy_true_native_F60_only_at_cap12=True,
        reduced_capacity_uses_explicit_tail_truncation_adapter=True,
        no_training_or_new_online_model=True,
        future_question_and_true_answer_offline_only=True,
        full_results=blocks,pooled=counts,
        no_generalization_or_scientific_gain_claim=True,
        no_original_firstuse=True,independent_scientific_acceptance=False,
        Codex_used=False,CKB_connected=False,
        MindPalace_written=False,optimizer_promoted=False,
        accepted_ref_mutations=0)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-ref",required=True)
    args=parser.parse_args()
    print(json.dumps(evaluate(args.source_ref),sort_keys=True,separators=(",",":")))
if __name__=="__main__":main()

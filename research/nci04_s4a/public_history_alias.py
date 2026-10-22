"""NCI-04 S4A — independent original Pycolab public-history alias feasibility.

Source reproduction and information acquisition ONLY. No new Yggdrasil
learner or communication model is trained, no hidden source game state is
read, no privileged velocity, player identity, reward or teacher target
enters the source-blind actor. All masks originate from Pycolab's
unmodified native ObservationCharacterRepainter.

A public-history alias is not proof of causal-memory trainability:
native public action/current masked image may match across naturally
reached prior histories and next original public board may differ.
This diagnostic requires exactly reproducible original source action
trajectories before classifying any such observation ambiguity, then
retrospectively asks how far back public action/image histories differ.
"""
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import random
import sys
import time

from research.mr34d.admit_pycolab import exact_source,public_bytes, SOURCE_SHA

CONTRACT=Path(__file__).with_name("frozen_protocol.json")
SCHEMA="yggdrasil.nci04.s4a.authentic-independent-public-history-alias.dev.v1"
SEEDS=(1103,1109,1117,1123)
STREAMS=(0,1,2,3)
WINDOWS=(1,2,4,8)
LIMIT=32


def protocol():
    obj=json.loads(CONTRACT.read_text(encoding="utf-8"))
    if (obj["schema"]!=SCHEMA or
        obj["exact_parent_independent_source_candidate_sha"]!=
            "a2464da8d3a8a9bb28dcd3a37638c5309dc63247" or
        obj["original_pycolab_git_sha"]!=SOURCE_SHA or
        obj["fresh_development_source_reset_seeds"]!=list(SEEDS) or
        obj["four_source_blind_stream_ids"]!=list(STREAMS) or
        obj["history_depths_for_alias"]!=list(WINDOWS) or
        obj["source_native_max_original_actions_per_episode"]!=LIMIT or
        obj["no_new_Ygg_45_coefficient_model_changes"] is not True or
        obj["no_independent_scientific_first_use"] is not True):
        raise ValueError("NCI04_S4A_FROZEN_INDEPENDENT_SOURCE_DRIFT")
    return obj


def episode(apprehend,rendering,seed,stream):
    # Source original pycolab model itself uses Python RNG seeded before
    # game creation; private initial ball velocity never leaves source.
    random.seed(seed)
    game=apprehend.make_game()
    observer=rendering.ObservationCharacterRepainter(
        apprehend.REPAINT_MAPPING)
    public_obs,_unused_reward,_unused_discount=game.its_showtime()
    before=public_bytes(public_obs,observer)
    policy=random.Random(1000003*seed+337+10007*stream)
    events=[]
    entire=sha256()
    for tick in range(LIMIT):
        action=policy.randrange(2)
        next_obs,_unseen_reward,discount=game.play(action)
        after=public_bytes(next_obs,observer)
        if len(before)!=70 or len(after)!=70 or action not in (0,1):
            raise ValueError("NCI04_S4A_UNAUTHENTIC_NATIVE_PUBLIC_MASK")
        entire.update(before)
        entire.update(bytes([action]))
        entire.update(after)
        entire.update(bytes([1 if discount==0.0 else 0]))
        events.append({
            "public_before":before,
            "announced_native_action":action,
            "public_after":after,
            "prior_action_image_digest":sha256(
                b"".join(
                    t["public_before"]+
                    bytes([t["announced_native_action"]])
                    for t in events)
            ).hexdigest(),
        })
        before=after
        if discount==0.0:
            break
    if not events:
        raise ValueError("NCI04_S4A_ZERO_REAL_NATIVE_STEPS")
    return events,{
        "source_reset_seed":seed,"policy_stream":stream,
        "native_actions":len(events),
        "initial_original_public_frame_sha256":
            sha256(events[0]["public_before"]).hexdigest(),
        "source_native_action_consequence_sha256":entire.hexdigest(),
        "natural_episode_terminated":len(events)<LIMIT,
    }


def history_context(events,index,depth):
    if index<depth:
        return None
    return tuple((e["public_before"],e["announced_native_action"])
                 for e in events[index-depth:index])


def classify(worlds):
    groups=defaultdict(list)
    for (seed,stream),events in worlds.items():
        for j,event in enumerate(events):
            key=(seed,event["public_before"],event["announced_native_action"])
            groups[key].append((seed,stream,j,event))
    counts={
        "same_entire_current_public_and_action_cross_stream_groups":0,
        "native_strict_different_next_public_pairs":0,
        "qualified_different_previous_public_policy_histories":0,
        "matching_recent_public_history_but_different_native_next_pairs":0,
        "same_prefix_different_public_next_source_reproducibility_warning":0,
    }
    differences={str(k):{"compared_with_sufficient_history":0,
                         "distinct_public_history":0} for k in WINDOWS}
    clusters=set()
    examples=[]
    for members in groups.values():
        if len({z[1] for z in members})<2:
            continue
        counts[
            "same_entire_current_public_and_action_cross_stream_groups"]+=1
        for i,a in enumerate(members):
            for b in members[i+1:]:
                if a[1]==b[1]:
                    continue
                if a[3]["public_after"]==b[3]["public_after"]:
                    continue
                counts["native_strict_different_next_public_pairs"]+=1
                histories_a=worlds[(a[0],a[1])]
                histories_b=worlds[(b[0],b[1])]
                kdiffs=[]
                for k in WINDOWS:
                    x=history_context(histories_a,a[2],k)
                    y=history_context(histories_b,b[2],k)
                    if x is not None and y is not None:
                        differences[str(k)][
                            "compared_with_sufficient_history"]+=1
                        if x!=y:
                            differences[str(k)]["distinct_public_history"]+=1
                            kdiffs.append(k)
                if kdiffs:
                    clusters.add(a[0])
                    counts[
                        "qualified_different_previous_public_policy_histories"]+=1
                else:
                    if a[2] and b[2] and histories_a[:a[2]]==histories_b[:b[2]]:
                        counts[
                            "same_prefix_different_public_next_source_reproducibility_warning"]+=1
                    else:
                        counts[
                            "matching_recent_public_history_but_different_native_next_pairs"]+=1
                if len(examples)<6:
                    examples.append({
                        "native_seed":a[0],
                        "different_uninterrupted_public_policy_streams":[a[1],b[1]],
                        "authentic_original_native_indices":[a[2],b[2]],
                        "identical_original_public_masked_frame_sha256":
                            sha256(a[3]["public_before"]).hexdigest(),
                        "original_announced_action":a[3]["announced_native_action"],
                        "different_next_original_public_hashes":[
                            sha256(a[3]["public_after"]).hexdigest(),
                            sha256(b[3]["public_after"]).hexdigest()],
                        "prior_public_history_windows_differing":kdiffs,
                    })
    return {
        "original_public_histories_counted":counts,
        "source_seed_clusters_with_history_resolvable_alias":
            sorted(clusters),
        "retrospective_public_history_window_differences":differences,
        "public_alias_examples_evaluator_only":examples
    }


def main(source):
    p=protocol()
    root=exact_source(source)
    sys.path.insert(0,str(root))
    from pycolab.examples import apprehend
    from pycolab import rendering
    if apprehend.REPAINT_MAPPING!={"b":"X","P":"X"}:
        raise ValueError("NCI04_S4A_ORIGINAL_PUBLIC_OBSERVATION_DRIFT")
    start=time.process_time_ns()
    runs=[]
    witnesses=[]
    for repeat in (0,1):
        observations={}
        receipts=[]
        for seed in SEEDS:
            for stream in STREAMS:
                ev,rec=episode(apprehend,rendering,seed,stream)
                observations[(seed,stream)]=ev
                receipts.append(rec)
        runs.append((observations,receipts))
        witnesses.append([
            (x["source_reset_seed"],x["policy_stream"],
             x["native_actions"],x["source_native_action_consequence_sha256"],
             x["initial_original_public_frame_sha256"],
             x["natural_episode_terminated"])
            for x in receipts])
    if witnesses[0]!=witnesses[1]:
        raise ValueError("NCI04_S4A_PYCOLAB_SAME_OS_NATIVE_REPLAY_DRIFT")
    if any(len(r)!=16 for _,r in runs):
        raise ValueError("NCI04_S4A_SOURCE_EPISODE_COHORT_DRIFT")
    report=classify(runs[0][0])
    check=report["original_public_histories_counted"]
    source_ready=(
        check["same_prefix_different_public_next_source_reproducibility_warning"]==0)
    enough=(
        check["qualified_different_previous_public_policy_histories"]>=8
        and len(report["source_seed_clusters_with_history_resolvable_alias"])>=4)
    digest=sha256(json.dumps(witnesses[0],sort_keys=True,
                             separators=(",",":")).encode()).hexdigest()
    exact_source(root)
    print("NCI04_S4A_ORIGINAL_INDEPENDENT_PUBLIC_ALIAS="+json.dumps({
        "original_independently_authored_upstream_source_sha":SOURCE_SHA,
        "frozen_protocol_sha256":sha256(CONTRACT.read_bytes()).hexdigest(),
        "source_native_uninterrupted_episodes_per_repeat":16,
        "repeated_original_native_source_episode_receipts":runs[0][1],
        "strict_within_OS_public_action_source_replay":True,
        "source_original_event_digest_for_cross_OS_comparison":digest,
        "native_public_original_masked_board_bytes":70,
        "original_source_announced_actions":2,
        "retrospective_history_identifiability":report,
        "precommitted_sufficient_natural_history_contrasts":enough,
        "no_same_prefix_explained_by_original_source_instability":source_ready,
        "MR34D_independently_cross_OS_admitted_source":"SEPARATE_PREREQUISITE",
        "original_public_actor_read_private_game_state":False,
        "original_native_source_world_private_velocity_read":False,
        "source_reward_or_game_object_roles_to_actor_or_model":False,
        "no_native_learned_state_training":True,
        "original_Yggdrasil_45_parameters_unchanged":True,
        "full_process_CPU_ns_one_worker_diagnostic":
            time.process_time_ns()-start,
        "two_full_episode_trace_copies_evaluator_only":True,
        "original_source_memory_CPU_RSS_wire_parity":"NOT_QUALIFIED",
        "unfamiliar_source_family_learned_transfer":"NOT_TESTED",
        "protected_scientific_first_use":False,
        "G29_atlas":"BLOCKED",
        "scientific_admission":"NO_GO"
    },sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.nci04_s4a.public_history_alias SOURCE")
    main(sys.argv[1])

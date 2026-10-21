"""MR27A: audit whether the ENTIRE current MR15 learner input is aliased.

MR25B found authentic original native histories with the same full current
public image and action, matched actual pose and inventory, but different
original world and next eight-bit observations. That did NOT establish
that the existing prior eight change bits were also identical. If prior
bits distinguish the pairs, no beyond-current-input memory is necessary
for these PARTICULAR sampled development witnesses.

Replay only the ALREADY CONSUMED MR25B public-only original trajectories.
All authentic source action choices, original native events and source
history SHA must match the previously published receipt. No new seeds,
new policies, hidden-world staging, semantic labels, model training,
learned parameters or protected scientific source consumption.

The auditor reads previously captured source-private world/pose solely
to classify pairs; it cannot feed them to the actor. Retrospective
prefix-window differences do NOT prove transferable predictive signal.
"""
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import sys

from research.mr15.public_view_delta import SOURCE_COMMIT
from research.mr25b.natural_twin_audit import (
    source_contract, native_trajectory, matched_natural_aliases
)

PROTOCOL=Path(__file__).with_name("frozen_protocol.json")
SCHEMA="yggdrasil.mr27a.original-current-input-sufficiency.dev.v1"


def protocol_verified(original_source):
    cfg=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    if (cfg["schema"]!=SCHEMA or
        cfg["original_source_sha"]!=SOURCE_COMMIT or
        cfg["exact_parent_pr376"]!=
            "5a2dec826bf283ab180b17113b86d95e42a22f2e" or
        cfg["previous_verified_native_episodes"]!=48 or
        cfg["previous_verified_native_actions"]!=10029 or
        cfg["previous_verified_strict_matched_world_contrast_classes"]!=3 or
        cfg["source_reset_seeds"]!=[223,227,229,233,239,241] or
        cfg["public_only_policy_stream_ids"]!=[0,1,2,3] or
        cfg["max_original_steps"]!=256 or
        cfg["history_windows_in_native_actions"]!=[1,2,4,8] or
        cfg["model_trained"] is not False or
        cfg["no_new_development_source_cohorts"] is not True):
        raise ValueError("MR27A_UNAUTHORIZED_ORIGINAL_PROTOCOL_DRIFT")
    prior,root=source_contract(original_source)
    if (prior["development_reset_seeds"]!=cfg["source_reset_seeds"] or
        prior["uninterrupted_action_stream_ids"]!=cfg[
            "public_only_policy_stream_ids"] or
        prior["max_native_original_steps_per_stream"]!=cfg["max_original_steps"]):
        raise ValueError("MR27A_MR25B_PREDECESSOR_CUSTODY_DRIFT")
    return cfg,root


def enriched_original_trajectory(factory,family,seed,stream,cap,windows):
    # ORIGINAL MR25B native_trajectory owns all env resets/actions/steps.
    rows,receipt=native_trajectory(factory,family,seed,stream,cap)
    prior=(0,)*8
    for i,r in enumerate(rows):
        if r["step"]!=i or len(r["next_bits"])!=8 or (
            i==0 and r["history_before"]!=sha256().hexdigest()):
            raise ValueError("MR27A_ORIGINAL_PRIOR_NATIVE_SEQUENCE_DRIFT")
        r["original_model_prior_bits"]=prior
        # Audit-only histories of events that strictly PRECEDE current
        # action. Never supplied to actor or a learning predictor.
        for k in windows:
            events=rows[max(0,i-k):i]
            source=json.dumps([
                [x["action"],sha256(x["before_public"]).hexdigest(),
                 sha256(x["next_public"]).hexdigest()]
                for x in events
            ],sort_keys=True,separators=(",",":")).encode()
            r[f"prior_{k}_native_public_event_window_digest"]=sha256(
                source).hexdigest()
        prior=r["next_bits"]
    return rows,receipt


def strict_audit(rows,windows):
    buckets=defaultdict(list)
    for row in rows:
        buckets[(row["family"],row["seed"],
                 row["before_public"],row["action"])].append(row)
    out={
        "natural_strict_hidden_world_contrast_equivalence_classes":0,
        "strict_real_source_pair_comparisons":0,
        "strong_witness_pairs_differing_current_MR15_prior_bits":0,
        "strong_witness_pairs_identical_entire_current_MR15_input":0,
        "strict_world_classes_with_identical_current_MR15_input":0,
        "history_window_differentiation_for_identical_current_input":{
            str(k):0 for k in windows
        },
        "strict_source_witnesses":[],
        "predeclared_pair_comparison_bound_exhausted":0
    }
    for key,members in buckets.items():
        if len({r["stream"] for r in members})<2:
            continue
        contains_strict=False
        contains_identical_input_strict=False
        checks=0
        for i,a in enumerate(members):
            for b in members[i+1:]:
                if a["stream"]==b["stream"] or a[
                    "history_before"]==b["history_before"]:
                    continue
                if checks>=20000:
                    out["predeclared_pair_comparison_bound_exhausted"]+=1
                    break
                checks+=1
                # Exact current public bytes already equal within bucket.
                strict=(
                    a["before_pose"]==b["before_pose"] and
                    a["before_dir"]==b["before_dir"] and
                    a["before_carried"]==b["before_carried"] and
                    a["before_world"]!=b["before_world"] and
                    a["next_bits"]!=b["next_bits"])
                if not strict:
                    continue
                contains_strict=True
                out["strict_real_source_pair_comparisons"]+=1
                same_bits=(a["original_model_prior_bits"]==
                           b["original_model_prior_bits"])
                if same_bits:
                    contains_identical_input_strict=True
                    out[
                        "strong_witness_pairs_identical_entire_current_MR15_input"
                    ]+=1
                    differing={
                        str(k):(
                          a[f"prior_{k}_native_public_event_window_digest"]!=
                          b[f"prior_{k}_native_public_event_window_digest"])
                        for k in windows
                    }
                    for name,exists in differing.items():
                        out[
                          "history_window_differentiation_for_identical_current_input"
                        ][name]+=int(exists)
                else:
                    differing=None
                    out[
                        "strong_witness_pairs_differing_current_MR15_prior_bits"
                    ]+=1
                if len(out["strict_source_witnesses"])<12:
                    out["strict_source_witnesses"].append({
                        "original_family":a["family"],
                        "same_original_seed":a["seed"],
                        "same_full_current_public_sha256":sha256(
                            a["before_public"]).hexdigest(),
                        "native_action":a["action"],
                        "natural_streams":[a["stream"],b["stream"]],
                        "native_source_steps":[a["step"],b["step"]],
                        "same_current_MR15_prior_eight_bits":same_bits,
                        "preaction_bits":[
                            list(a["original_model_prior_bits"]),
                            list(b["original_model_prior_bits"])],
                        "next_native_source_MR15_targets":[
                            list(a["next_bits"]),list(b["next_bits"])],
                        "prior_public_history_window_differences_only_if_current_input_identical":differing,
                        "evaluator_only_original_world_grid_differs":True,
                        "evaluator_only_original_pose_and_inventory_identical":True,
                        "privileged_world_did_not_select_original_actions":True
                    })
            if checks>=20000:
                break
        out[
            "natural_strict_hidden_world_contrast_equivalence_classes"
        ]+=int(contains_strict)
        out[
            "strict_world_classes_with_identical_current_MR15_input"
        ]+=int(contains_identical_input_strict)
    return out


def main(original_source):
    cfg,original=protocol_verified(original_source)
    sys.path.insert(0,str(original))
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv
    source_types=[
        ("DoorKeyEnv(size=8)",lambda:DoorKeyEnv(size=8,render_mode=None)),
        ("EmptyEnv(size=8)",lambda:EmptyEnv(size=8,render_mode=None))
    ]
    allrows=[]
    receipts=[]
    for family,make in source_types:
        for seed in cfg["source_reset_seeds"]:
            for stream in cfg["public_only_policy_stream_ids"]:
                rows,receipt=enriched_original_trajectory(
                    make,family,seed,stream,cfg["max_original_steps"],
                    cfg["history_windows_in_native_actions"])
                allrows.extend(rows)
                receipts.append(receipt)
    # Receipt contract must exactly match the published original MR25B
    # independent Windows/Linux development source custody.
    observed_sha=sha256(json.dumps([
        [r["family"],r["seed"],r["stream"],r["step"],r["action"],
         sha256(r["before_public"]).hexdigest(),
         sha256(r["next_public"]).hexdigest(),list(r["next_bits"])]
        for r in allrows
    ],sort_keys=True,separators=(",",":")).encode()).hexdigest()
    if (observed_sha!=cfg["previous_development_source_receipt_sha256"] or
        len(receipts)!=cfg["previous_verified_native_episodes"] or
        len(allrows)!=cfg["previous_verified_native_actions"]):
        raise ValueError("MR27A_PRIOR_PUBLISHED_REAL_SOURCE_CUSTODY_MISMATCH")
    baseline=matched_natural_aliases(allrows)
    if (baseline[
        "buckets_with_same_pose_inventory_different_world_and_next_bits"
        ]!=cfg["previous_verified_strict_matched_world_contrast_classes"] or
        baseline["pair_groups_truncated_at_frozen_limit"]):
        raise ValueError("MR27A_MR25B_ORIGINAL_STRICT_WITNESSES_NOT_PRESERVED")
    audit=strict_audit(allrows,cfg["history_windows_in_native_actions"])
    if audit[
        "natural_strict_hidden_world_contrast_equivalence_classes"
    ]!=cfg["previous_verified_strict_matched_world_contrast_classes"]:
        raise ValueError("MR27A_STRICT_SUBCLASS_NOT_REPRODUCIBLE")
    print("MR27A_NATURAL_ORIGINAL_CURRENT_INPUT_SUFFICIENCY="+json.dumps({
        "original_farama_source_commit":SOURCE_COMMIT,
        "frozen_protocol_sha256":sha256(PROTOCOL.read_bytes()).hexdigest(),
        "previous_MR25B_native_source_replay_sha256":observed_sha,
        "same_original_source_episodes":len(receipts),
        "same_original_source_native_actions":len(allrows),
        "original_MR25B_baseline_strict_classes":baseline[
            "buckets_with_same_pose_inventory_different_world_and_next_bits"],
        "original_source_MR15_input_history_necessity":audit,
        "at_least_one_strict_pair_indistinguishable_from_entire_current_MR15_input":
            audit["strict_world_classes_with_identical_current_MR15_input"]>0,
        "positive_current_input_alias_is_not_proof_older_public_history_predicts":True,
        "no_hidden_source_world_or_pair_labels_passed_to_actor":True,
        "only_previously_consumed_original_development_histories":True,
        "new_source_training_events_consumed":0,
        "native_original_trainable_coefficients_unchanged":45,
        "learner_or_comparator_trained":False,
        "original_model_retained_MR15_sidecar_bytes":32,
        "all_in_CPU_peak_RSS_wire":"NOT_QUALIFIED",
        "G29_source_atlas":"NOT_QUALIFIED",
        "independent_scientific_first_use":False,
        "scientific_admission":"NO_GO"
    },sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.mr27a.probe_original_input_sufficiency ORIGINAL")
    main(sys.argv[1])

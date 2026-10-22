"""MR33: retrospective, prequential public intervention-change identifiability.

This read-only development audit reuses EXACT native histories from the
qualified original MR32A source protocol, without inventing actions,
staging poses, training Yggdrasil, or consuming new evaluation cohorts.

A source action is called camera-stationary here ONLY when its ORIGINAL
MiniGrid action identifier is pickup=3, drop=4 or toggle=5. Those
actions do not themselves translate/rotate the agent's camera; they do
not ensure that the source world is unchanged, nor label the hidden
cause. Full 7x7x3 current/next public image byte inequality is the
actual public target. Brier is valid for the model's pre-action changed
probability; 4p(1-p) is an uncertainty ranking, NOT that probability.

Every reported forecast is made from strictly PREVIOUS genuine native
actions, with global action-only, bounded exact public-context and
bounded existing MR15 24-byte sampled-view conventional predictors.
This audit does NOT use source-private world labels and does NOT prove
causal effect, real-world alignment, or self-organized cognition.
"""
from collections import OrderedDict, defaultdict
from hashlib import sha256
import json
import math
from pathlib import Path
import sys

import numpy as np

from research.mr15.public_view_delta import SOURCE_COMMIT, public_raw_view
from research.mr32a.original_native_cost import worker
from research.mr32a.isolated_worker import load_contract

CONTRACT=Path(__file__).with_name("frozen_protocol.json")
SCHEMA="yggdrasil.mr33.original-public-stationary-intervention-signal.v1"
MODES=("novelty","contrast")
STATIONARY=(3,4,5)
CAPACITY=128


def protocol_verified():
    p=json.loads(CONTRACT.read_text(encoding="utf-8"))
    if (p["schema"]!=SCHEMA or
        p["base_exact_source_sha"]!="a7a26e1480c7499f83491c54a9efa58f3d27451c" or
        p["original_farama_sha"]!=SOURCE_COMMIT or
        p["mr32a_previously_consumed_episodes"]!=96 or
        p["mr32a_original_native_development_digest"]!=
            "cb12b87859c478fa1213bb0dbed3ec201f2ceff13b0de7ba988dc3a54747e729" or
        p["predeclared_stationary_intervention_actions"]!=[3,4,5] or
        p["predeclared_motion_actions_excluded_from_primary"]!=[0,1,2] or
        p["source_first_use"] is not False or
        p["new_exploration_policy"] is not False or
        p["trained_native_yggdrasil_coefficients_changed"]!=0):
        raise ValueError("MR33_FROZEN_SOURCE_PROTOCOL_DRIFT")
    original=load_contract()
    if (original["development_door_seeds"]!=
            p["existing_source_reset_seeds_only"]["DoorKey"] or
        original["development_empty_seeds"]!=
            p["existing_source_reset_seeds_only"]["Empty"]):
        raise ValueError("MR33_ORIGINAL_MR32A_SOURCE_SEED_DRIFT")
    return p


class BoundedPublicActionCounts:
    """Action-conditioned public forecast with exactly 128 cached keys.

    Both exact-full and sampled-key models use the same cached-state
    structure, action outcomes, sequential updates, and global shrinkage.
    """
    def __init__(self):
        self.seen=OrderedDict()
        self.trials=[0]*6
        self.changes=[0]*6

    def forecast(self,key,action):
        if not isinstance(key,bytes) or len(key)!=32 or action not in range(6):
            raise ValueError("MR33_PUBLIC_FORECAST_INPUT_INVALID")
        global_p=(self.changes[action]+1)/(self.trials[action]+2)
        counts=self.seen.get(key)
        if counts is None:
            return global_p,global_p
        n,c=counts[action]
        return global_p,(c+2*global_p)/(n+2)

    def observe(self,key,action,changed):
        if key not in self.seen:
            if len(self.seen)==CAPACITY:
                self.seen.popitem(last=False)
            self.seen[key]=[[0,0] for _ in range(6)]
        bucket=self.seen[key][action]
        bucket[0]+=1
        bucket[1]+=int(changed)
        self.trials[action]+=1
        self.changes[action]+=int(changed)


class OriginalMR31AmbiguityShadow:
    """Only preaction ambiguity from prior source-public observations.

    Reflects the MR31 fixed FIFO packing and historical observed-change
    counts, but CANNOT choose an action or influence the original actor.
    """
    def __init__(self):
        self.cache=OrderedDict()

    def preaction(self,before,action):
        key=sha256(before).digest()
        if key not in self.cache:
            if len(self.cache)==CAPACITY:
                self.cache.popitem(last=False)
            self.cache[key]=[[0,0] for _ in range(6)]
        trials,changes=self.cache[key][action]
        if changes>trials:
            raise ValueError("MR33_ORIGINAL_CHANGED_ATTEMPTS_DRIFT")
        p=(changes+1)/(trials+2)
        return 4*p*(1-p)

    def observe(self,before,action,after):
        key=sha256(before).digest()
        nxt=sha256(after).digest()
        bucket=self.cache[key][action]
        bucket[0]+=1
        if nxt not in self.cache:
            if len(self.cache)==CAPACITY:
                self.cache.popitem(last=False)
            self.cache[nxt]=[[0,0] for _ in range(6)]
        if key in self.cache and nxt!=key:
            bucket[1]+=1


def per_episode(rows):
    """Prequential eval from consecutive original full source-public frames."""
    if not rows:
        raise ValueError("MR33_EMPTY_PREVIOUSLY_CONSUMED_EPISODE")
    counts_full=BoundedPublicActionCounts()
    counts_sample=BoundedPublicActionCounts()
    shadow=OriginalMR31AmbiguityShadow()
    scored=[]
    for index,record in enumerate(rows):
        if record["step"]!=index or len(record["public"])!=147:
            raise ValueError("MR33_NATIVE_SOURCE_ORDER_OR_IMAGE_DRIFT")
        if index+1==len(rows):
            continue # MR32A saved BEFORE-frame only; terminal next unseen.
        following=rows[index+1]
        if following["step"]!=index+1:
            raise ValueError("MR33_ORIGINAL_NATIVE_FRAME_NOT_CONTIGUOUS")
        before=record["public"]
        after=following["public"]
        action=record["action"]
        if action not in range(6):
            raise ValueError("MR33_ORIGINAL_SOURCE_ACTION_INVALID")
        changed=int(before!=after)
        full=sha256(before).digest()
        image=np.frombuffer(before,dtype=np.uint8).reshape((7,7,3))
        sampled=bytes(public_raw_view(image))
        if len(sampled)!=24:
            raise ValueError("MR33_ORIGINAL_MR15_PUBLIC_SOURCE_NOT_24_BYTES")
        sampled_key=sha256(sampled).digest()
        global_p,full_p=counts_full.forecast(full,action)
        second_global,sampled_p=counts_sample.forecast(sampled_key,action)
        if global_p!=second_global:
            raise ValueError("MR33_GLOBAL_ACTION_CONTROL_DATA_DRIFT")
        ambiguity=shadow.preaction(before,action)
        if action in STATIONARY:
            scored.append({
                "mode":record["mode"],"family":record["family"],
                "seed":record["seed"],"action":action,
                "changed":changed,"p_global":global_p,
                "p_full":full_p,"p_mr15":sampled_p,
                "uncertainty":ambiguity,
                "loss_global":(global_p-changed)**2,
                "loss_full":(full_p-changed)**2,
                "loss_mr15":(sampled_p-changed)**2
            })
        # Update histories only AFTER original native observed next frame.
        counts_full.observe(full,action,changed)
        counts_sample.observe(sampled_key,action,changed)
        shadow.observe(before,action,after)
    return scored


def aggregate(samples):
    if not samples:
        return {"native_stationary_actions_scored":0,
                "reason":"NO_STATIONARY_PUBLIC_INTERVENTIONS"}
    n=len(samples)
    result={
        "native_stationary_actions_scored":n,
        "actual_source_public_change_rate":
            sum(x["changed"] for x in samples)/n,
        "preaction_brier_lower_better":{
            kind:sum(x["loss_"+kind] for x in samples)/n
            for kind in ("global","full","mr15")},
        "original_MR31_ambiguity_mean_prior_when_next_changed":
            (sum(x["uncertainty"] for x in samples if x["changed"])/sum(
                x["changed"] for x in samples)) if any(x["changed"]
                    for x in samples) else None,
        "original_MR31_ambiguity_mean_prior_when_next_unchanged":
            (sum(x["uncertainty"] for x in samples if not x["changed"])/sum(
                1-x["changed"] for x in samples)) if any(
                    not x["changed"] for x in samples) else None,
        "full_public_beats_both_controls":
            all(sum(x["loss_full"] for x in samples)<
                sum(x["loss_"+k] for x in samples)
                for k in ("global","mr15")),
        "full_public_beats_action_only":
            sum(x["loss_full"] for x in samples)<
            sum(x["loss_global"] for x in samples),
    }
    return result


def main(original):
    p=protocol_verified()
    import tempfile
    reports={}
    all_samples=[]
    receipts=[]
    with tempfile.TemporaryDirectory(prefix="mr33-previous-dev-") as folder:
        for mode in MODES:
            rows,original_receipts,report=worker(original,mode,folder)
            reports[mode]=report
            receipts.extend(original_receipts)
            groups=defaultdict(list)
            for r in rows:
                groups[(r["family"],r["seed"],r["stream"])].append(r)
            if len(groups)!=48:
                raise ValueError("MR33_ORIGINAL_CONSUMED_POLICY_EPISODE_COUNT")
            for _,entries in groups.items():
                all_samples+=per_episode(entries)
    if len(receipts)!=96:
        raise ValueError("MR33_PREVIOUS_ORIGINAL_SOURCE_EPISODES_DRIFT")
    previous_digest=sha256(json.dumps([
        [mode,reports[mode]["native_source_history_sha256"]]
        for mode in MODES],sort_keys=True,
        separators=(",",":")).encode()).hexdigest()
    if previous_digest!=p["mr32a_original_native_development_digest"]:
        raise ValueError("MR33_PREVIOUS_PUBLISHED_NATIVE_MR32A_RECEIPT_MISMATCH")

    by_policy={}
    for mode in MODES:
        by_policy[mode]={}
        for family in ("DoorKeyEnv(size=8)","EmptyEnv(size=8)"):
            selected=[s for s in all_samples
                      if s["mode"]==mode and s["family"]==family]
            report=aggregate(selected)
            per_seed={}
            for seed in sorted(set(s["seed"] for s in selected)):
                ss=[s for s in selected if s["seed"]==seed]
                if ss:
                    per_seed[str(seed)]={
                        "native_public_intervention_events":len(ss),
                        "full_minus_global_brier":
                            (sum(s["loss_full"]-s["loss_global"] for s in ss)/
                             len(ss)),
                        "full_minus_sampled_brier":
                            (sum(s["loss_full"]-s["loss_mr15"] for s in ss)/
                             len(ss))
                    }
            report["original_source_independent_seed_cluster_comparisons"]={
                "seed_clusters_scored":len(per_seed),
                "full_public_beats_global_seed_clusters":sum(
                    a["full_minus_global_brier"]<0 for a in per_seed.values()),
                "full_public_beats_sampled_seed_clusters":sum(
                    a["full_minus_sampled_brier"]<0 for a in per_seed.values()),
                "seed_stratified_development_receipts":per_seed,
            }
            by_policy[mode][family]=report
    go=all(
        by_policy[mode][family]["full_public_beats_both_controls"]
        for mode in MODES for family in by_policy[mode]
    )
    print("MR33_ORIGINAL_NATIVE_PUBLIC_INTERVENTION_SIGNAL="+json.dumps({
        "source_exact_sha":SOURCE_COMMIT,
        "protocol_sha256":sha256(CONTRACT.read_bytes()).hexdigest(),
        "previous_consumed_source_event_digest":previous_digest,
        "authentic_native_episodes_replayed":len(receipts),
        "authentic_native_stationary_intervention_events_scored":
            len(all_samples),
        "strict_public_camera_stationary_actions":[3,4,5],
        "retrospective_online_public_change_prediction_by_policy_and_family":
            by_policy,
        "precommitted_full_view_predictive_signal_go":go,
        "uncertainty_is_not_public_change_probability":True,
        "original_candidate_policies_unmodified":True,
        "private_original_source_state_consulted_by_predictor":False,
        "original_model_45_coefficients_unchanged":True,
        "new_native_learning_mechanism_trained":False,
        "protected_scientific_first_use_consumed":False,
        "score_is_public_observational_prediction_not_causal_identification":
            True,
        "source_worker_resource_cost_new_original_process_replay":
            "NOT_A_NEW_INDEPENDENT_RESOURCE_COMPARISON",
        "G29_semantic_atlas":"BLOCKED",
        "scientific_admission":"NO_GO"
    },sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.mr33.public_intervention ORIGINAL")
    main(sys.argv[1])

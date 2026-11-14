"""ST1 authentic ORIGINAL native action/outcome DEV comparison on CONSUMED S2 seeds.

No protected first-use, no new original source law, no tuning frozen ST1.
The identical original Farama source actor is action-blind to all policies.
Independent upstream source and published S1/S2 training code are reused.
This experiment is developmental falsification, NOT SCIENTIFIC_PASS.
"""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from research.mr15.public_view_delta import SOURCE_COMMIT, PublicViewLocalDelta, public_raw_view
from research.mr26.public_novelty import BoundedPublicNoveltyExplorer
from research.mr27.natural_memory import source_guard
from research.nci04_s1.original_native_messages import models_new, native_episode, loss
from research.nci04_s1.local_messages import LocalPredictiveMessages45
from research.nci04_st1.adaptive_topology import NativeAdaptiveTopology45

CONTRACT = Path(__file__).with_name("frozen_dev_comparison.json")
CONTRACT_GIT_BLOB = "6edcd39c117d6bbfdafa3286535e1fdf0706b2d1"
PREREG_ANCESTOR = "71b8ac443a7c9460ee16ef751e6aa54e8bb62883"
MODEL_PARENT = "46d270da66084c6371fc52772ab6bd3c2f332a71"
NAMES = ("adaptive", "ring", "dev_selected_per_cell", "fixed0", "fixed1",
         "fixed2", "fixed3", "sham", "no_neighbor", "no_state",
         "recurrent45", "memoryless45", "count_unmatched")
N = 8


def source_preflight(upstream):
    p = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if (p.get("schema") !=
          "yggdrasil.nci04.st1.frozen-original-native-development-comparison.v1"
        or p.get("status") !=
          "FROZEN_BEFORE_NATIVE_COMPARISON_SOURCE_OR_OUTCOMES"
        or p.get("base_st1_sha") != MODEL_PARENT
        or p.get("original_independent_farama_git_sha") != SOURCE_COMMIT
        or p.get("source_training_previously_consumed") !=
          [263,269,271,277,281,283,293,307]
        or p.get("topology_adaptation_previously_consumed") !=
          [827,829,839]
        or p.get("evaluation_previously_consumed") !=
          [853,857,859]
        or p.get("source_per_episode_action_cap") != 256
        or p.get("reserved_first_use_opened") is not False
        or p.get("additional_learner_weights") != 0):
        raise ValueError("ST1_DEV_FROZEN_CONTRACT_DRIFT")
    for gitargs, expect in (
        (["rev-parse", "HEAD:research/nci04_st1/frozen_dev_comparison.json"],
         CONTRACT_GIT_BLOB),):
        got = subprocess.check_output(["git"] + gitargs, text=True).strip()
        if got != expect:
            raise ValueError("ST1_DEV_PREREG_BLOB_DRIFT")
    if subprocess.run(["git", "merge-base", "--is-ancestor",
                       PREREG_ANCESTOR, "HEAD"], check=False).returncode:
        raise ValueError("ST1_DEV_PREREG_ANCESTRY_MISSING")
    original = source_guard(upstream)
    return p, original


def original_episode(make, family, seed, model, training, score_store,
                     selected, baseline, controls):
    """One original source trajectory; predictions precede the real step."""
    env = make()
    actor = BoundedPublicNoveltyExplorer(seed)
    sensor = PublicViewLocalDelta()
    ring = LocalPredictiveMessages45.restore(baseline)
    ring.reset_episode()
    model.reset_episode()
    recurrent = None
    if controls is not None:
        from research.mr18.native_public_learning import Recurrent45
        recurrent = Recurrent45.restore(controls["recurrent"])
        recurrent.reset_episode()
    total = {k:0.0 for k in NAMES if not training}
    digest = sha256()
    steps = 0
    preaction_cpu = 0
    native_adaptation_cpu = 0
    other_models_cpu = 0
    try:
        obs, _ = env.reset(seed=seed)
        sensor.prime(obs["image"])
        for t in range(256):
            raw = public_raw_view(obs["image"])
            bits = tuple(sensor.bits)
            action = actor.choose(obs["image"])
            start = time.process_time_ns()
            adaptive = model.predict(raw, bits, action)
            candidate = model._predictions(raw, bits, action, True)
            preaction_cpu += time.process_time_ns() - start
            start = time.process_time_ns()
            base_ring = ring.predict(raw, bits, action)
            if model.choices == [0]*N and adaptive != base_ring:
                raise ValueError("ST1_DEV_DEFAULT_GRAPH_NOT_S1_EQUIVALENT")
            preds = None
            if not training:
                preds = {
                    "adaptive":adaptive, "ring":base_ring,
                    "dev_selected_per_cell":[candidate[i][selected[i]]
                                             for i in range(N)],
                    "sham":[candidate[i][(3*i+1)%4] for i in range(N)],
                    "no_neighbor":ring.predict(raw,bits,action,
                                               drop_neighbors=True),
                    "no_state":ring.predict(raw,bits,action,drop_state=True),
                    "recurrent45":recurrent.predict(raw,bits,action),
                    "memoryless45":controls["memoryless"].predict(raw,bits,action),
                    "count_unmatched":controls["count"].predict(raw,bits,action),
                }
                for q in range(4):
                    preds["fixed"+str(q)] = [candidate[i][q] for i in range(N)]
                if set(preds) != set(NAMES):
                    raise ValueError("ST1_DEV_CONTROL_INCOMPLETE")
            other_models_cpu += time.process_time_ns() - start
            before_image = obs["image"].tobytes()
            next_obs, _reward, terminated, truncated, _info = env.step(action)
            event = sensor.observe_after_native_step(action,next_obs["image"])
            next_raw = public_raw_view(next_obs["image"])
            target = event["observed_next_local_bits"]
            if (event["source_commit"] != SOURCE_COMMIT
                or event["observed_action"] != action
                or event["prior_local_bits"] != list(bits)
                or target != [int(raw[3*i:3*i+3]!=next_raw[3*i:3*i+3])
                              for i in range(N)]):
                raise ValueError("ST1_DEV_REAL_SOURCE_ACTION_OUTCOME_DRIFT")
            if training:
                for i in range(N):
                    for q in range(4):
                        delta = target[i] - candidate[i][q]
                        score_store[i][q] += delta * delta
            else:
                for key in NAMES:
                    total[key] += loss(preds[key],target)
            start = time.process_time_ns()
            returned = model.observe(raw,bits,action,target,train=training)
            native_adaptation_cpu += time.process_time_ns()-start
            if returned != adaptive:
                raise ValueError("ST1_DEV_POST_OUTCOME_PREDICTION_LEAK")
            check = ring.observe(raw,bits,action,target,train=False)
            if check != base_ring or model.native.state != ring.state:
                raise ValueError("ST1_DEV_ORIGINAL_STATE_PATH_DIVERGENCE")
            if recurrent is not None:
                recurrent.advance_public_history(raw)
            if t == 11:
                state = model.snapshot()
                model = NativeAdaptiveTopology45.restore(state)
                if model.snapshot() != state:
                    raise ValueError("ST1_DEV_COLD_RESTART_MISMATCH")
            actor.observe_original_next_public_image(action,next_obs["image"])
            actor.validate()
            digest.update(bytes((action,*bits,*target)))
            digest.update(sha256(before_image).digest())
            digest.update(sha256(next_obs["image"].tobytes()).digest())
            obs = next_obs
            steps += 1
            if terminated or truncated:
                break
        if not steps:
            raise ValueError("ST1_DEV_ZERO_NATIVE_SOURCE_ACTIONS")
        return model, {
            "family":family,"seed":seed,
            "phase":"previously_consumed_adaptation" if training else
                    "previously_consumed_held_development",
            "original_native_steps":steps,
            "source_public_actions_outcomes_sha256":digest.hexdigest(),
            "preaction_brier":({k:total[k]/steps for k in NAMES}
                               if not training else None),
            "preaction_adaptive_and_candidate_cpu_ns":preaction_cpu,
            "structural_state_update_cpu_ns":native_adaptation_cpu,
            "other_controls_cpu_ns_shared_process":other_models_cpu,
            "source_private_state_supplied_to_model":False,
            "genuine_native_source_steps":True,
        }
    finally:
        env.close()


def process_peak_rss():
    if os.name == "nt":
        import psutil
        return int(psutil.Process().memory_info().peak_wset)
    import resource
    # On Linux ru_maxrss is KiB; never infer portable parity from raw units.
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)*1024


def run(upstream, output):
    start = time.process_time_ns()
    protocol, root = source_preflight(upstream)
    sys.path.insert(0,str(root))
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv
    factories = (
        ("DoorKeyEnv(size=8)",lambda:DoorKeyEnv(size=8,render_mode=None)),
        ("EmptyEnv(size=8)",lambda:EmptyEnv(size=8,render_mode=None)),
    )
    original = models_new()
    native_training = []
    for family,make in factories:
        for seed in protocol["source_training_previously_consumed"]:
            native_training.append(native_episode(
                make,family,seed,True,original,{"native_restart_checks":0}))
    frozen_s1 = original["s1_messages"].snapshot()
    trained_core = original["s1_messages"].runtime.core.snapshot()
    frozen_conv = {
        "recurrent":original["conventional_recurrent"].snapshot(),
        "memoryless":original["conventional_memoryless"],
        "count":original["public_count_unmatched"],
    }
    conv_weights = [
        [r[:] for r in original["conventional_recurrent"].local],
        original["conventional_recurrent"].shared[:],
        original["conventional_memoryless"].snapshot(),
        original["public_count_unmatched"].snapshot(),
    ]
    family_receipts = {}
    source_digests = {}
    for family,make in factories:
        st1 = NativeAdaptiveTopology45(frozen_s1)
        scores = [[0.0]*4 for _ in range(N)]
        adapt_receipts = []
        for seed in protocol["topology_adaptation_previously_consumed"]:
            st1, rec = original_episode(
                make,family,seed,st1,True,scores,None,frozen_s1,None)
            adapt_receipts.append(rec)
        chosen_fixed = tuple(min(range(4),key=lambda q:(scores[i][q],q))
                             for i in range(N))
        if st1.native.runtime.core.snapshot()!=trained_core:
            raise ValueError("ST1_DEV_NEURAL_WEIGHTS_MUTATED_DURING_ADAPT")
        structural = (st1.choices[:],[row[:] for row in st1.losses],
                      st1.switches[:],st1.window_seen,st1.total_windows)
        mid = st1.snapshot()
        st1 = NativeAdaptiveTopology45.restore(mid)
        if st1.snapshot()!=mid:
            raise ValueError("ST1_DEV_ADAPTED_GRAPH_COLD_PERSISTENCE")
        held = []
        for seed in protocol["evaluation_previously_consumed"]:
            st1, rec = original_episode(
                make,family,seed,st1,False,scores,chosen_fixed,frozen_s1,
                frozen_conv)
            held.append(rec)
        if (structural!=(st1.choices[:],[row[:] for row in st1.losses],
                         st1.switches[:],st1.window_seen,st1.total_windows)
            or st1.native.runtime.core.snapshot()!=trained_core):
            raise ValueError("ST1_DEV_HELDOUT_WEIGHT_OR_GRAPH_UPDATE")
        n = sum(x["original_native_steps"] for x in held)
        aggregate = {key:sum(x["original_native_steps"]*
                             x["preaction_brier"][key] for x in held)/n
                     for key in NAMES}
        seeds_better = sum(
            x["preaction_brier"]["adaptive"]<
            x["preaction_brier"]["dev_selected_per_cell"] for x in held)
        outcome = {
            "adaptation":adapt_receipts,
            "held_development":held,
            "held_original_source_actions":n,
            "preaction_brier_lower_better":aggregate,
            "per_cell_adaptation_selected_fixed_controls":list(chosen_fixed),
            "structural_choices_after_adaptation":st1.choices[:],
            "structural_switches_per_cell":st1.switches[:],
            "total_structural_switches":sum(st1.switches),
            "held_seed_clusters_better_than_trained_fixed":seeds_better,
            "native_45_coefficients_frozen":True,
            "original_training_checkpoint_bytes":len(frozen_s1.encode()),
            "adapted_structural_checkpoint_bytes":len(mid.encode()),
            "held_structural_checkpoint_bytes":len(st1.snapshot().encode()),
            "extra_candidate_training_read_budget_per_event":64,
            "active_inference_neighbor_scalar_reads_per_event":16,
            "dev_pass_necessary":{
                "real_consequence_triggered_structural_switch":
                    sum(st1.switches)>0,
                "beats_original_ring_by_0_0001":
                    aggregate["adaptive"]+0.0001<aggregate["ring"],
                "beats_strong_dev_trained_fixed_by_0_0001":
                    aggregate["adaptive"]+0.0001<
                    aggregate["dev_selected_per_cell"],
                "beats_strong_trained_fixed_on_at_least_two_of_three_held_seeds":
                    seeds_better>=2,
                "no_worse_than_original_trained_recurrent":
                    aggregate["adaptive"]<=aggregate["recurrent45"]
            },
        }
        family_receipts[family]=outcome
        source_digests[family]=sha256(
            "".join(x["source_public_actions_outcomes_sha256"]
                    for x in adapt_receipts+held).encode("ascii")
            ).hexdigest()
    if (original["s1_messages"].runtime.core.snapshot()!=trained_core
        or conv_weights!=[
            [r[:] for r in original["conventional_recurrent"].local],
            original["conventional_recurrent"].shared[:],
            original["conventional_memoryless"].snapshot(),
            original["public_count_unmatched"].snapshot()
        ]):
        raise ValueError("ST1_DEV_PRETRAINED_SOURCE_CONTROLS_DRIFT")
    dev_pass = all(all(x for x in value["dev_pass_necessary"].values())
                   for value in family_receipts.values())
    out = {
        "schema":"yggdrasil.nci04.st1.consumed-native-dev-result.v1",
        "source_original_git_sha":SOURCE_COMMIT,
        "frozen_protocol_git_blob":CONTRACT_GIT_BLOB,
        "st1_initial_model_sha":MODEL_PARENT,
        "native_training_original_episodes":native_training,
        "native_training_source_digest":sha256(
            "".join(x["source_original_public_history_sha256"]
                    for x in native_training).encode("ascii")).hexdigest(),
        "frozen_native_45_weights_sha256":sha256(
            trained_core.encode("utf-8")).hexdigest(),
        "original_dev_source_digests":source_digests,
        "family_results":family_receipts,
        "worker_full_cpu_ns_including_original_source_and_all_controls":
            time.process_time_ns()-start,
        "worker_peak_rss_bytes_shared_process":process_peak_rss(),
        "fresh_original_world_seeds":0,
        "protected_scientific_first_use":False,
        "full_isolated_equal_compute_or_memory_parity":False,
        "independent_unfamiliar_causal_law_transfer":False,
        "scientific_admission":"NOT_QUALIFIED",
        "development_disposition":"DEV_SIGNAL_NOT_SCIENCE" if dev_pass
                                  else "NO_GO",
        "post_result_learner_tuning":False,
    }
    content=json.dumps(out,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n"
    output.write_text(content,encoding="utf-8")
    print("ST1_NATIVE_DEV_AUTHENTIC_RESULT="+content.strip())
    print("ST1_NATIVE_DEV_DISPOSITION="+out["development_disposition"])
    return out


if __name__ == "__main__":
    cmd=argparse.ArgumentParser()
    cmd.add_argument("original_source")
    cmd.add_argument("--output",type=Path,required=True)
    args=cmd.parse_args()
    run(args.original_source,args.output)

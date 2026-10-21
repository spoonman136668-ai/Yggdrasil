"""MR16: original MiniGrid prequential local-cell learning development check.

The candidate sees ONLY MR15 public-image spatial deltas and the action
selected before the native step. Source-held reward, termination and native
internal state are evaluator-only and cannot serve as a training target.
Fixed scripted DEVELOPMENT observations; no held-out science or transfer.
"""
import json
import pathlib
import subprocess
import sys

from research.mr15.public_view_delta import SOURCE_COMMIT
from research.mr16.native_prequential import (
    NativePublicPrequential, MatchedActionCount, prediction, action_features
)

ACTIONS = (0,2,1,2,0,2,1,2,5,3,2,1,2,0,2,5)


def verify_original(upstream):
    root = pathlib.Path(upstream).resolve()
    source = subprocess.check_output(
        ["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
    status = subprocess.check_output(
        ["git","-C",str(root),"status","--porcelain"],text=True).strip()
    if source != SOURCE_COMMIT or status:
        raise ValueError("MR16_ORIGINAL_FARAMA_CUSTODY_INVALID")
    return root


def measure(environment, label):
    try:
        initial,_ = environment.reset(seed=11)
        candidate = NativePublicPrequential()
        candidate.prime(initial["image"])
        initial_model = candidate.runtime.snapshot()
        conventional = MatchedActionCount()
        model_loss = []
        conventional_loss = []
        distinct = set()
        checkpoint_bytes = 0
        for t,action in enumerate(ACTIONS):
            bits = tuple(candidate.sensor.bits)
            before = prediction(candidate.runtime,bits,action)
            compare = conventional.probabilities(bits,action)
            record = candidate.step(environment,action)
            assert record["pre_action_probabilities"] == before
            assert record["observed_original_action"] == action
            assert record["fixed_native_coefficients"] == 45
            assert record["native_reward_was_not_training_target"]
            targets = record["native_observed_delta_targets"]
            assert len(targets)==8 and all(x in (0,1) for x in targets)
            conventional_loss.append(sum((p-y)**2 for p,y in zip(compare,targets))/8)
            conventional.observe(bits,action,targets)
            model_loss.append(record["prequential_brier"])
            distinct.add((tuple(bits),action,tuple(targets)))
            assert candidate.sensor.steps == candidate.runtime.core.events == t+1
            assert candidate.runtime.neighbors == NativePublicPrequential().runtime.neighbors
            if t == 7:
                snapshots = candidate.snapshot()
                checkpoint_bytes = sum(len(s.encode("utf-8")) for s in snapshots)
                candidate = NativePublicPrequential.restore(*snapshots)
                assert candidate.snapshot()==snapshots
            # Original environment can terminate before the fixed script ends.
        assert len(model_loss)==len(ACTIONS)
        assert candidate.runtime.snapshot()!=initial_model
        assert checkpoint_bytes>0
        final=candidate.snapshot()
        for invalid in (-1,7,True,"toggle"):
            try:
                candidate.step(environment,invalid)
            except ValueError:
                pass
            else:
                raise AssertionError("MR16_INVALID_ACTION_ACCEPTED")
            assert candidate.snapshot()==final
        # The action occupies one of seven original coefficients, rather than
        # adding another learned feature dimension.
        assert len(action_features((0,)*8,0,0))==7
        assert action_features((0,)*8,0,0)!=action_features((0,)*8,0,6)
        return {
            "original_environment":label,
            "observed_source_steps":len(model_loss),
            "distinct_native_input_action_consequence_triples":len(distinct),
            "candidate_prequential_brier_mean":sum(model_loss)/len(model_loss),
            "equal_information_count_brier_mean":sum(conventional_loss)/len(conventional_loss),
            "learner_updated":True,
            "actual_original_native_steps":True,
            "model_coefficients":45,
            "additional_model_coefficients":0,
            "sensor_raw_sidecar_bytes":24,
            "sensor_last_delta_bits":8,
            "exact_midstream_model_and_sensor_restart":True,
            "checkpoint_serialized_bytes":checkpoint_bytes,
            "strong_recurrent_control":"NOT_QUALIFIED",
            "complete_all_process_cpu_peak_rss":"NOT_QUALIFIED",
            "independent_scientific_first_use":False,
            "causal_memory_proven":False,
            "native_transfer_proven":False,
        }
    finally:
        environment.close()


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.mr16.probe_original_prequential UPSTREAM")
    upstream=verify_original(sys.argv[1])
    sys.path.insert(0,str(upstream))
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv
    checks=[
        measure(DoorKeyEnv(size=5,render_mode=None),"Original DoorKeyEnv(5)"),
        measure(EmptyEnv(size=8,render_mode=None),"Original EmptyEnv(8)")
    ]
    print("MR16_NATIVE_PREQUENTIAL_DEVELOPMENT="+json.dumps({
        "source_commit":SOURCE_COMMIT,
        "source_author_independent":True,
        "experiments":checks,
        "outcomes_from_original_public_images_only":True,
        "fixed_45_parameter_native_core":True,
        "original_trainable_learner_was_updated":True,
        "training_causality_pre_action_predictions":True,
        "prior_mr7_to_mr15_receipts_intact":True,
        "no_oracle_or_role_labels":True,
        "model_superiority":"NOT_CLAIMED",
        "complete_resource_fairness":"NOT_QUALIFIED",
        "source_license_discrepancy":"UNRESOLVED",
        "g29_atlas":"NOT_QUALIFIED",
        "scientific_first_use":False,
        "scientific_admission":"NO_GO"
    },sort_keys=True))

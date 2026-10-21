"""MR18 native Farama prequential comparison; consumed dev source ONLY.

MR18 contrastive credit, a same-45-weight conventional raw-byte learner,
the original MR17 coarse local learner, and a fully trained raw-byte exact
conditional count all predict prior to ORIGINAL env.step and receive identical
original PUBLIC observation consequences only afterwards.

Frozen protocol: research/mr18/frozen_protocol.json (committed first).
No reward/map/mission/hidden role, model-provided target, new task or holdout.
"""
import json
import pathlib
import subprocess
import sys
import time

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"research"/"mr15"))
from research.mr15.public_view_delta import PublicViewLocalDelta,SOURCE_COMMIT
from research.mr16.native_local_online import brier
from research.mr17.contrastive_local import LocalContrastLearner
from research.mr18.public_byte_learning import (
    PublicByteLocalLearner,RawPublicConditionalCount,raw_cell_features
)

def exact_original_source(root):
    root=pathlib.Path(root).resolve()
    head=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
    clean=subprocess.check_output(["git","-C",str(root),"status","--porcelain"],text=True).strip()
    if head!=SOURCE_COMMIT or clean:
        raise ValueError("MR18_EXTERNAL_SOURCE_IDENTITY_DRIFT")
    return root

def main(upstream):
    original=exact_original_source(upstream)
    sys.path.insert(0,str(original))
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv

    protocol=json.loads((ROOT/"research"/"mr18"/"frozen_protocol.json").read_text())
    assert protocol["schema"]=="nci04.mr18.frozen-native-public-byte-credit.v1"
    assert protocol["original_farama_commit"]==SOURCE_COMMIT
    actions=protocol["original_action_sequence"]
    assert len(actions)==16
    contrast=PublicByteLocalLearner(contrast=True)
    plain=PublicByteLocalLearner(contrast=False)
    mr17=LocalContrastLearner()
    count=RawPublicConditionalCount()
    all_original_public_dev_events=[]
    environments=[]
    cpu_start=time.process_time_ns()
    wall_start=time.perf_counter_ns()

    for label,env in (
        ("Original DoorKeyEnv(size=5)",DoorKeyEnv(size=5,render_mode=None)),
        ("Original EmptyEnv(size=8)",EmptyEnv(size=8,render_mode=None))
    ):
        try:
            first,_=env.reset(seed=11)
            sensor=PublicViewLocalDelta()
            sensor.prime(first["image"])
            previous_image=first["image"].copy()
            losses={n:[] for n in ("mr18_contrast","conventional_45_byte",
                                   "mr17_coarse","raw_conditional_count")}
            for step,action in enumerate(actions):
                prior=tuple(sensor.bits)
                frozen_image=previous_image.copy()
                # Never read next outcome/terminal/reward before forecasting.
                forecasts={
                    "mr18_contrast":contrast.predict(prior,action,frozen_image),
                    "conventional_45_byte":plain.predict(prior,action,frozen_image),
                    "mr17_coarse":mr17.predict(prior,action),
                    "raw_conditional_count":count.predict(prior,action,frozen_image),
                }
                old_contrast=contrast.snapshot()
                next_obs,_,done,stopped,_=env.step(action)
                event=sensor.observe_after_native_step(action,next_obs["image"])
                targets=tuple(event["observed_next_local_bits"])
                if (tuple(event["prior_local_bits"])!=prior or
                    event["observed_action"]!=action or
                    event["privileged_world_fields_consumed"]!=0):
                    raise ValueError("MR18_PREOUTCOME_IDENTITY_FAILED")
                for name,pred in forecasts.items():
                    losses[name].append(brier(pred,targets))
                # All 4 train after this exact original source event.
                contrast.observe(prior,action,frozen_image,targets)
                plain.observe(prior,action,frozen_image,targets)
                mr17.observe_after_original_step(prior,action,targets)
                count.observe(prior,action,frozen_image,targets)
                all_original_public_dev_events.append((prior,action,frozen_image,targets))
                previous_image=next_obs["image"].copy()
                if contrast.snapshot()==old_contrast:
                    raise ValueError("MR18_CAUSAL_LEARNER_INERT")
                if step==7:
                    a,b,c,d=contrast.snapshot(),plain.snapshot(),mr17.snapshot(),sensor.snapshot()
                    contrast=PublicByteLocalLearner.restore(a,contrast=True)
                    plain=PublicByteLocalLearner.restore(b,contrast=False)
                    mr17=LocalContrastLearner.restore(c)
                    sensor=PublicViewLocalDelta.restore(d)
                    if (contrast.snapshot()!=a or plain.snapshot()!=b or
                        mr17.snapshot()!=c or sensor.snapshot()!=d):
                        raise ValueError("MR18_LOCAL_COLD_RESTART_DRIFT")
                if done or stopped:
                    break
            environments.append({
                "original_native_environment":label,
                "actual_source_step_count":len(losses["mr18_contrast"]),
                "strictly_prequential_brier":{
                    k:sum(values)/len(values) for k,values in losses.items()},
                "predeclared_known_development_only":True,
            })
        finally:
            env.close()

    frozen=contrast.snapshot()
    plain_frozen=plain.snapshot()
    if len(all_original_public_dev_events)!=32:
        raise ValueError("MR18_NATIVE_EVENT_COUNT_DRIFT")
    if contrast.rt.core.events!=32 or plain.rt.core.events!=32:
        raise ValueError("MR18_TRAINING_EVENT_DRIFT")
    if sum(map(len,contrast.rt.core.genome))+sum(map(len,contrast.rt.core.roles))!=45:
        raise ValueError("MR18_45_WEIGHT_BUDGET_DRIFT")
    if sum(map(len,plain.rt.core.genome))+sum(map(len,plain.rt.core.roles))!=45:
        raise ValueError("MR18_MATCHED_CONTROL_45_WEIGHT_BUDGET_DRIFT")

    def retrospective_loss(model):
        return sum(brier(model.predict(prior,a,im),future)
                   for prior,a,im,future in all_original_public_dev_events)/32
    trained_dev=retrospective_loss(contrast)
    all_erased=PublicByteLocalLearner.restore(frozen,contrast=True)
    for i in range(8):
        all_erased.rt.core.roles[i]=[0.]*3
    erased_dev=retrospective_loss(all_erased)
    by_cell=[]
    for cell in range(8):
        ablated=contrast.ablate_cell(cell)
        dist=[]
        change=[]
        for prior,a,im,future in all_original_public_dev_events:
            p=contrast.predict(prior,a,im)[cell]
            q=ablated.predict(prior,a,im)[cell]
            dist.append(abs(p-q))
            change.append((q-future[cell])**2-(p-future[cell])**2)
        by_cell.append({"cell":cell,"mean_abs_prediction_change":sum(dist)/len(dist),
                        "dev_trained_role_erasure_loss_delta":sum(change)/len(change)})
    if contrast.snapshot()!=frozen or plain.snapshot()!=plain_frozen:
        raise ValueError("MR18_ABLATION_MUTATED_NATIVE_MODEL")

    try:
        contrast.observe([0]*8,7,all_original_public_dev_events[0][2],[0]*8)
    except ValueError:
        pass
    else:
        raise ValueError("MR18_INVALID_ACTION_DID_NOT_FAIL")
    if contrast.snapshot()!=frozen:
        raise ValueError("MR18_INVALID_ACTION_MUTATED_STATE")
    snapshot_bytes=len(frozen.encode())
    print("MR18_NATIVE_PUBLIC_BYTE_CAUSAL_CREDIT="+json.dumps({
        "exact_external_source_commit":SOURCE_COMMIT,
        "precommitted_source_protocol":"research/mr18/frozen_protocol.json",
        "original_native_environment_results":environments,
        "original_native_development_observations":len(all_original_public_dev_events),
        "trained_model_weights_mr18":45,
        "trained_model_weights_conventional":45,
        "extra_trainable_weights":0,
        "frozen_visible_input":"8 previous public-image delta bits, original action and original 8x3 public raw bytes",
        "privileged_world_or_object_role_labels":False,
        "strong_raw_conditional_control_same_public_information":True,
        "mr17_coarse_uses_less_public_information":True,
        "retrospective_train_dev_brier":trained_dev,
        "retrospective_train_dev_brier_roles_reset":erased_dev,
        "retrospective_train_dev_role_necessity_delta":erased_dev-trained_dev,
        "individual_private_role_dev_ablations":by_cell,
        "native_model_cold_restart":True,
        "native_candidate_serialized_state_bytes":snapshot_bytes,
        "untrained_MR15_sensor_sidecar_bytes":32,
        "dev_evaluator_replay_public_images_bytes":32*7*7*3,
        "raw_conditional_count_table_entries":len(count.counts),
        "parent_only_cpu_ns":time.process_time_ns()-cpu_start,
        "parent_only_wall_ns":time.perf_counter_ns()-wall_start,
        "full_process_tree_cpu_peak_rss":"NOT_QUALIFIED",
        "independent_scientific_first_use":False,
        "genuinely_unseen_transfer":"NOT_TESTED",
        "recovery_of_lost_local_function":"NOT_TESTED",
        "native_source_license":"UNRESOLVED",
        "g29_exact_source_final_acceptance":"BLOCKED",
        "scientific_admission":"NO_GO"
    },sort_keys=True))

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.mr18.run_original ORIGINAL_UPSTREAM")
    main(sys.argv[1])

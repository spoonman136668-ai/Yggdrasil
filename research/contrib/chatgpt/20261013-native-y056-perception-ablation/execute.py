"""Y056: original DG1A Torch NCA training with spatial perception ablation."""
import hashlib
import json
import math
import torch

from yggdrasil.nca import NCAConfig, NeuralCellularAutomaton, make_seed_state
from yggdrasil.target import TargetSpec, make_target, target_identity
from yggdrasil.training import TrainingConfig, train, evaluate_growth_and_recovery

SEEDS=(340,341,342,343)
ARMS=("FULL_NATIVE_PERCEPTION","IDENTITY_ONLY_PERCEPTION")
SPEC=TargetSpec(kind="disk",radius=2,rgba=(.15,.75,.30,1.0))


def sha_params(model):
    digest=hashlib.sha256()
    for name,param in sorted(model.named_parameters()):
        digest.update(name.encode())
        digest.update(bytes(param.detach().contiguous().view(torch.uint8).flatten().tolist()))
    return digest.hexdigest()


def run_one(seed,arm):
    torch.manual_seed(seed)
    model=NeuralCellularAutomaton(NCAConfig(
        state_channels=6,hidden_channels=12,fire_rate=1.0,
        alive_channel=3,alive_threshold=0.1,max_steps=12)).cpu()
    initial=sha_params(model)
    before=model.perception_kernels.detach().clone()
    if arm=="IDENTITY_ONLY_PERCEPTION":
        with torch.no_grad():
            model.perception_kernels[1:].zero_()
    assert torch.equal(model.perception_kernels[0],before[0])
    spatial_disabled=bool(torch.count_nonzero(model.perception_kernels[1:])==0)
    if arm=="FULL_NATIVE_PERCEPTION":
        assert torch.equal(model.perception_kernels,before) and not spatial_disabled
    else:
        assert spatial_disabled
    start=make_seed_state(batch_size=1,channels=6,height=9,width=9,alive_channel=3)
    target=make_target(batch_size=1,channels=6,height=9,width=9,spec=SPEC)
    cfg=TrainingConfig(
        variant="growth_only",iterations=32,learning_rate=.001,
        steps_min=4,steps_max=6,batch_size=2,pool_size=8,
        damage_probability=.5,damage_height_fraction=.35,
        damage_width_fraction=.35,damage_min_active_cells=4,
        gradient_clip_norm=1.0,hidden_state_l2_weight=.00001,
        loss_mode="global_mse",visible_channels=4,record_every=8,seed=seed)
    summary=train(model=model,seed_state=start,target=target,config=cfg)
    native_eval=evaluate_growth_and_recovery(
        model=model,seed_state=start,target=target,
        growth_steps=8,recovery_steps=8,seed=seed+1000,
        lesion_height_fraction=.4,lesion_width_fraction=.4,visible_channels=4)
    if not all(math.isfinite(native_eval[x]) for x in
               ("pre_error","post_damage_error","final_recovery_error")):
        raise ValueError("nonfinite native evaluation")
    return {
        "seed":seed,"cohort":"development" if seed<342 else "heldout",
        "arm":arm,"initial_genome_sha256":initial,
        "final_genome_sha256":sha_params(model),
        "parameters":model.parameter_count(),
        "perception_identity_preserved":bool(torch.equal(model.perception_kernels[0],before[0])),
        "spatial_channels_disabled":spatial_disabled,
        "training":{"iterations":summary.iterations,
                    "initial_recorded_loss":summary.initial_recorded_loss,
                    "final_recorded_loss":summary.final_recorded_loss,
                    "minimum_recorded_loss":summary.minimum_recorded_loss},
        "recovery":native_eval,
    }


def run():
    torch.set_num_threads(1)
    rows=[run_one(seed,arm) for seed in SEEDS for arm in ARMS]
    by={(r["seed"],r["arm"]):r for r in rows}
    structural=all(
        by[seed,ARMS[0]]["initial_genome_sha256"]==
        by[seed,ARMS[1]]["initial_genome_sha256"]
        and by[seed,ARMS[0]]["parameters"]==by[seed,ARMS[1]]["parameters"]
        and by[seed,ARMS[0]]["recovery"]["resources"]["genome_parameters"]==
        by[seed,ARMS[1]]["recovery"]["resources"]["genome_parameters"]
        and by[seed,ARMS[0]]["perception_identity_preserved"]
        and by[seed,ARMS[1]]["perception_identity_preserved"]
        and not by[seed,ARMS[0]]["spatial_channels_disabled"]
        and by[seed,ARMS[1]]["spatial_channels_disabled"]
        for seed in SEEDS)
    heldout={}
    effective=True
    for seed in (342,343):
        native=by[seed,"FULL_NATIVE_PERCEPTION"]["recovery"]
        ablated=by[seed,"IDENTITY_ONLY_PERCEPTION"]["recovery"]
        difference=ablated["pre_error"]-native["pre_error"]
        heldout[str(seed)]={
            "native_pre_error":native["pre_error"],
            "ablated_pre_error":ablated["pre_error"],
            "native_formation_gain":difference,
            "native_recovery_fraction":native["recovery_fraction"],
            "ablated_recovery_fraction":ablated["recovery_fraction"],
        }
        effective &= difference>=.002
    classification=("STRUCTURAL_INVALID" if not structural else
                    "SPATIAL_PERCEPTION_BENEFIT" if effective else "NO_BENEFIT")
    return {"schema":"yggdrasil.y056-native-perception-ablation.v1",
            "classification":classification,
            "source_parent":"878464cf84833d06a1ac7e45988bfb79608547dc",
            "torch_version":torch.__version__,
            "seeds":list(SEEDS),"target_sha256":target_identity(SPEC,height=9,width=9),
            "structural_controls_pass":structural,
            "heldout":heldout,"rows":rows,"model_calls":0,
            "claim_limit":"Four small trained native NCA initializations, one morphology disk task, targeted nontrainable Sobel perception ablation; no language/general intelligence."}


if __name__=="__main__":
    original=run()
    print(json.dumps(original,sort_keys=True,indent=2))

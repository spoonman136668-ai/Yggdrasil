"""Y055: pilot true native DG1A training and damaged-phenotype recovery."""
import hashlib
import json
import math
import torch

from yggdrasil.nca import NCAConfig, NeuralCellularAutomaton, make_seed_state
from yggdrasil.target import TargetSpec, make_target, target_identity
from yggdrasil.training import TrainingConfig, train, evaluate_growth_and_recovery

SEEDS=(330,331,332,333)
ARMS=("GROWTH_ONLY","REGEN_TRAIN")
TARGET=TargetSpec(kind="disk",radius=2,rgba=(.15,.75,.30,1.0))


def genome_hash(model):
    h=hashlib.sha256()
    for name,param in sorted(model.named_parameters()):
        h.update(name.encode())
        h.update(bytes(param.detach().cpu().contiguous().view(torch.uint8).flatten().tolist()))
    return h.hexdigest()


def run_one(seed,arm):
    torch.manual_seed(seed)
    model=NeuralCellularAutomaton(NCAConfig(
        state_channels=6,hidden_channels=12,fire_rate=1.0,
        alive_channel=3,alive_threshold=.1,max_steps=12)).cpu()
    first=genome_hash(model)
    start=make_seed_state(batch_size=1,channels=6,height=9,width=9,alive_channel=3)
    target=make_target(batch_size=1,channels=6,height=9,width=9,spec=TARGET)
    config=TrainingConfig(
        variant="growth_only" if arm=="GROWTH_ONLY" else "regeneration",
        iterations=24,learning_rate=.001,steps_min=4,steps_max=6,
        batch_size=2,pool_size=8,damage_probability=.5,
        damage_height_fraction=.35,damage_width_fraction=.35,
        damage_min_active_cells=4,gradient_clip_norm=1.0,
        hidden_state_l2_weight=.00001,loss_mode="global_mse",
        visible_channels=4,record_every=6,seed=seed)
    summary=train(model=model,seed_state=start,target=target,config=config)
    final=genome_hash(model)
    evaluation=evaluate_growth_and_recovery(
        model=model,seed_state=start,target=target,
        growth_steps=8,recovery_steps=8,seed=seed+1000,
        lesion_height_fraction=.4,lesion_width_fraction=.4,visible_channels=4)
    assert model.parameter_count()==model.parameter_count()
    assert math.isfinite(evaluation["pre_error"])
    assert math.isfinite(evaluation["post_damage_error"])
    assert math.isfinite(evaluation["final_recovery_error"])
    return {"seed":seed,"cohort":"development" if seed<332 else "heldout",
            "arm":arm,"initial_genome_sha256":first,"final_genome_sha256":final,
            "genome_parameters":model.parameter_count(),
            "training":{"iterations":summary.iterations,
                        "initial_recorded_loss":summary.initial_recorded_loss,
                        "final_recorded_loss":summary.final_recorded_loss,
                        "minimum_recorded_loss":summary.minimum_recorded_loss,
                        "history":summary.to_dict()["history"]},
            "recovery":evaluation}


def run():
    torch.set_num_threads(1)
    rows=[run_one(seed,arm) for seed in SEEDS for arm in ARMS]
    by={(r["seed"],r["arm"]):r for r in rows}
    matched=all(
        by[seed,ARMS[0]]["initial_genome_sha256"]==
        by[seed,ARMS[1]]["initial_genome_sha256"]
        and by[seed,ARMS[0]]["genome_parameters"]==
        by[seed,ARMS[1]]["genome_parameters"]
        for seed in SEEDS)
    records={}
    insufficient=False
    qualified_gain=True
    for seed in (332,333):
        grow=by[seed,"GROWTH_ONLY"]["recovery"]
        regen=by[seed,"REGEN_TRAIN"]["recovery"]
        ga,ra=grow["recovery_fraction"],regen["recovery_fraction"]
        valid=(grow["damage_effect"]>0 and regen["damage_effect"]>0
               and ga is not None and ra is not None
               and math.isfinite(ga) and math.isfinite(ra))
        insufficient|=not valid
        if not valid or ra-ga<.05:qualified_gain=False
        records[str(seed)]={
            "valid_damage_effect":valid,
            "growth_recovery_fraction":ga,
            "regeneration_recovery_fraction":ra,
            "paired_regen_minus_growth":ra-ga if valid else None,
        }
    if not matched:
        outcome="NO_GAIN"
    elif insufficient:
        outcome="INSUFFICIENT_DAMAGE"
    elif qualified_gain:
        outcome="NATIVE_REGENERATION_GAIN"
    else:
        outcome="NO_GAIN"
    return {"schema":"yggdrasil.y055-native-trained-recovery.v1",
            "classification":outcome,
            "source_parent":"878464cf84833d06a1ac7e45988bfb79608547dc",
            "torch_version":torch.__version__,
            "seed_list":list(SEEDS),"target_sha256":target_identity(TARGET,height=9,width=9),
            "paired_initial_genome_identity":matched,
            "heldout":records,"rows":rows,"model_calls":0,
            "claim_limit":"Four short separately trained native NCAs on one synthetic target; two seeds heldout only by initialization, no unseen tasks or standalone cognition."}


if __name__=="__main__":
    original=run()
    print(json.dumps(original,sort_keys=True,indent=2))

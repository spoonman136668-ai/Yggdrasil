"""Y053: mechanistic locality of actual Yggdrasil NeuralCellularAutomaton, not learning."""
import hashlib
import json
import math

import torch

from yggdrasil.nca import NCAConfig, NeuralCellularAutomaton
from yggdrasil.resources import snapshot_resources

SEEDS = tuple(range(300, 308))
STEPS = (1, 2, 3, 4)
SIDE = 13
CENTER = SIDE // 2
CHANNELS = 6
EPSILON = 1e-7


def create(seed):
    torch.manual_seed(seed)
    config = NCAConfig(
        state_channels=CHANNELS, hidden_channels=12, fire_rate=1.0,
        alive_channel=3, alive_threshold=0.1, max_steps=8)
    model = NeuralCellularAutomaton(config).cpu().eval()
    with torch.no_grad():
        torch.nn.init.normal_(model.update_net[-1].weight, mean=0.0, std=0.03)
    return model


def original_state():
    state = torch.zeros((1, CHANNELS, SIDE, SIDE), dtype=torch.float32)
    state[:, 3, :, :] = 1.0  # all grid cells alive, no death boundary confound
    state[:, 0, :, :] = 0.5
    state[:, 4, :, :] = 0.25
    return state


def model_identity(model):
    digest = hashlib.sha256()
    for name, param in sorted(model.named_parameters()):
        digest.update(name.encode())
        digest.update(param.detach().cpu().contiguous().numpy().tobytes())
    return digest.hexdigest()


def run():
    torch.set_num_threads(1)
    grids = torch.meshgrid(torch.arange(SIDE), torch.arange(SIDE), indexing="ij")
    distance = torch.maximum((grids[0]-CENTER).abs(), (grids[1]-CENTER).abs())
    rows = []
    signatures = {}
    source_ok = True
    outside_violation = False
    missing_first_signal = False
    for seed in SEEDS:
        model = create(seed)
        signatures[str(seed)] = model_identity(model)
        unaltered = original_state()
        perturbed = unaltered.clone()
        perturbed[0, 4, CENTER, CENTER] += 0.5
        snap_before = snapshot_resources(model=model, state=unaltered, active_cells=SIDE*SIDE)
        snap_perturbed = snapshot_resources(model=model, state=perturbed, active_cells=SIDE*SIDE)
        assert snap_before == snap_perturbed
        assert snap_before.genome_parameters == model.parameter_count()
        assert snap_before.active_cells == SIDE*SIDE
        assert snap_before.resident_state_bytes == SIDE*SIDE*CHANNELS*4
        with torch.no_grad():
            for steps in STEPS:
                left = model.run(unaltered, steps)
                right = model.run(perturbed, steps)
                finite = bool(torch.isfinite(left).all() and torch.isfinite(right).all())
                source_ok = source_ok and finite
                difference = (left-right).abs().amax(dim=1)[0]
                outside = distance > steps
                inside = distance <= steps
                far = difference[outside]
                near = difference[inside]
                far_max = float(far.max()) if far.numel() else 0.0
                near_max = float(near.max()) if near.numel() else 0.0
                far_count = int((far > EPSILON).sum().item())
                near_count = int((near > EPSILON).sum().item())
                outside_violation = outside_violation or far_count > 0
                missing_first_signal = missing_first_signal or (
                    steps == 1 and near_count == 0)
                # Alive occupancy and byte footprint are unchanged by a local
                # perturbation under these fixed all-alive positive-alpha states.
                count_a = int((left[0, 3] > model.config.alive_threshold).sum())
                count_b = int((right[0, 3] > model.config.alive_threshold).sum())
                source_ok = source_ok and count_a == count_b == SIDE*SIDE
                snap_left = snapshot_resources(model=model, state=left, active_cells=count_a)
                snap_right = snapshot_resources(model=model, state=right, active_cells=count_b)
                source_ok = source_ok and (snap_left == snap_right == snap_before)
                rows.append({
                    "seed":seed,"steps":steps,"inside_radius_changed_cells":near_count,
                    "outside_radius_changed_cells":far_count,
                    "max_difference_inside":near_max,"max_difference_outside":far_max,
                    "alive_cells_reference":count_a,"alive_cells_intervention":count_b,
                    "resident_bytes_each":snap_before.resident_state_bytes,
                    "parameter_count":snap_before.genome_parameters,
                    "finite":finite,
                })
    distinct = len(set(signatures.values())) == len(SEEDS)
    if not distinct:
        result = "STRUCTURAL_NEGATIVE"
    elif not source_ok or outside_violation:
        result = "STRUCTURAL_NEGATIVE"
    elif missing_first_signal:
        result = "NO_SIGNAL"
    else:
        result = "NATIVE_CAUSAL_LOCALITY_ONLY"
    return {
        "schema":"yggdrasil.y053-native-nca-causal-cone.v1",
        "classification":result,
        "source_parent":"878464cf84833d06a1ac7e45988bfb79608547dc",
        "native_module":"yggdrasil.nca.NeuralCellularAutomaton",
        "torch_version":torch.__version__,
        "seeds":list(SEEDS),"step_counts":list(STEPS),
        "source_genome_sha256":signatures,"genomes_distinct":distinct,
        "source_invariants_pass":source_ok,"outside_causal_cone_violation":outside_violation,
        "no_first_step_signal":missing_first_signal,
        "comparison_count":len(rows),"rows":rows,"model_calls":0,
        "claim_limit":"Untrained experimentally nonzero NCA update weights; a structural locality audit, not learned regeneration/cognition.",
    }


if __name__ == "__main__":
    original = run()
    print(json.dumps(original, sort_keys=True, indent=2))

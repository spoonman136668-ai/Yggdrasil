"""Train the native model and the four retained heads on one shared receipt."""
from argparse import ArgumentParser
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import time

from growth_preflight import BASE, LEGACY, COHORT, SEED, ACTIONS, expect_value_error
from shadow_preflight import MANIFEST, checked_bytes, require
from yggdrasil.native_causal_amalgam import NativeCausalAmalgam
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import EXPERIENCE_SOURCE

HERE = Path(__file__).resolve()


def parent_material(native_path, donor_path):
    manifest = json.loads(MANIFEST.read_bytes())
    native_pin = manifest["native_artifacts_sha256"][native_path.name]
    native = checked_bytes(native_path, native_pin)
    donor = json.loads(checked_bytes(donor_path, manifest["specialist_artifacts_sha256"][donor_path.name]))
    return {"native_parent":native, "native_pin":native_pin,
            "donor_parent":donor["state_ascii"].encode("ascii"), "donor_pin":donor["state_sha256"]}


def admit(system, identifier, views, row):
    return system.observe_experience(identifier, views, row, source_sha256=EXPERIENCE_SOURCE,
                                     packet_sha256=digest(canonical([identifier, views, row])))


def run(native_path, donor_path, checkpoint_out=None):
    started = time.monotonic()
    material = parent_material(native_path, donor_path)
    system = NativeCausalAmalgam.activate(material["native_parent"], material["native_pin"],
                                        material["donor_parent"], material["donor_pin"])
    initial = system.checkpoint()
    fixture = BASE.make_episode(cohort=COHORT, seed=SEED, index=0, family="invariant", regime=0)
    views = BASE.public_views(fixture)
    row = LEGACY.fixed_rollout(fixture, ACTIONS)
    identifier = LEGACY.event_id(COHORT, SEED, 0, "engineering")
    p = system.specialist_forecasts(views, ACTIONS[0])
    q = system.specialist_forecasts(views, ACTIONS[0], row["s2"], ACTIONS[1])
    require(all(0 <= x <= 1 for x in (*p, *q)), "SHADOW_FORECASTS")
    require(system.checkpoint() == initial, "SHADOW_FORECAST_MUTATION")
    updated = admit(system, identifier, views, row)
    raw = updated.checkpoint()
    require(system.checkpoint() == initial and raw != initial, "JOINT_UPDATE_ATOMICITY")
    require(admit(updated, identifier, views, row) is updated, "JOINT_DUPLICATE_REPLAY")
    expect_value_error(lambda: admit(updated, identifier, views, {**row, "y":1-row["y"]}),
                       "EPISODE_CONFLICTING_REPLAY")
    require(updated.checkpoint() == raw, "JOINT_CONFLICT_MUTATION")
    step_deltas = [after.steps-before.steps for before, after in zip(system._heads, updated._heads, strict=True)]
    require(all(delta == 3 for delta in step_deltas), "JOINT_SOURCE_HEAD_UPDATES")
    require(updated.plan(views[0]) == updated.native.experience_context_plan(views[0]),
            "NATIVE_PLANNER")
    growth = json.loads(HERE.with_name("growth-result.json").read_bytes())
    require(digest(updated.native.checkpoint()) == growth["fixture_descendant_sha256"],
            "JOINT_NATIVE_DESCENDANT")
    with TemporaryDirectory(prefix="amalgam-joint-restore-") as directory:
        path = Path(directory)/"state.json"
        path.write_bytes(raw)
        child = subprocess.check_output([sys.executable, "-B", str(HERE),
            str(native_path.resolve()), str(donor_path.resolve()), "--cold", str(path), digest(raw)],
            timeout=180, text=True).strip()
        require(child == digest(raw), "JOINT_FRESH_PROCESS")

    forged = json.loads(raw)
    forged["action_heads"][0]["encoder_bias"][0] += .05
    corrupt = canonical(forged)
    expect_value_error(lambda: NativeCausalAmalgam.restore(corrupt, digest(corrupt), **material),
                       "JEPA3_SOURCE_BIAS_PARITY")
    if checkpoint_out is not None:
        checkpoint_out.write_bytes(raw)
    return {"joint_engineering_preflight":"PASS", "head_gradient_steps":step_deltas,
            "native_checkpoint_sha256":digest(updated.native.checkpoint()),
            "joint_checkpoint_sha256":digest(raw), "native_episodes":1025,
            "additional_shared_witnesses":1, "synthetic_engineering_actions":2,
            "held_worlds_scored":0, "predictions_select_actions":False,
            "forged_head_rejected":True, "cold_replay_exact":True,
            "wall_seconds":time.monotonic()-started}


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("native", type=Path)
    parser.add_argument("donor", type=Path)
    parser.add_argument("--cold", nargs=2)
    parser.add_argument("--checkpoint-out", type=Path)
    args = parser.parse_args()
    if args.cold:
        path, expected = args.cold
        learner = NativeCausalAmalgam.restore(Path(path).read_bytes(), expected,
                                             **parent_material(args.native, args.donor))
        print(digest(learner.checkpoint()))
    else:
        print(json.dumps(run(args.native, args.donor, args.checkpoint_out), indent=2, sort_keys=True))

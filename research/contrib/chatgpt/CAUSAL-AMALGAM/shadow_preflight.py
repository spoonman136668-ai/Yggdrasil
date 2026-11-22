"""Probe the native planner and already-trained JEPA heads on one public history.

Use the pinned CKAD26 and JEPA2-03 development archives. The probe enumerates
public input shapes without observing consequences or scoring a world.
"""
from argparse import ArgumentParser
from hashlib import sha256
from itertools import product
import json
from math import isfinite
from pathlib import Path
import time

from yggdrasil.native_cumulative_learner import NativeCumulativeLearner, _two_stage_plan
from yggdrasil.native_jepa_temporal import NativeTemporalMultiLearner

ROOT = Path(__file__).resolve().parents[4]
MANIFEST = Path(__file__).with_name("sources.json")


def require(condition, label):
    if not condition:
        raise RuntimeError(label)


def checked_bytes(path, expected):
    raw = path.read_bytes()
    require(sha256(raw).hexdigest() == expected, f"PIN_MISMATCH_{path.name}")
    return raw


def specialist_forecasts(experts, views, actions, native_history):
    """Every head reads the same supplied public inputs; none selects an action."""
    if len(actions) == 1:
        direct, temporal = experts.base.transition, experts.transition
    else:
        direct, temporal = experts.base.reward, experts.reward
    results = (direct.probability(views, *actions),
               temporal.probability(views, actions, native_history))
    require(all(isfinite(p) and 0 <= p <= 1 for p in results), "SPECIALIST_PROBABILITY")
    return results


def verify_pair(native, donor):
    experience = native._episode_reader()
    # The trained temporal head interprets public coordinate zero as aligned.
    # Require native evidence selection and donor evidence to agree on it.
    require(experience.info()["projection"] == 0, "NATIVE_COORDINATE")
    require(donor.base.native.info()["projection"] == 0, "DONOR_COORDINATE")
    history = experience._ledger[-8:]
    require(len(history) == 8 and all(e[1][0][0] == e[1][1][0] for e in history),
            "PUBLIC_HISTORY_ALIGNMENT")
    before_native, before_donor = native.checkpoint(), donor.checkpoint()

    def forecast(view, alternate, *actions):
        specialist_forecasts(donor, (view, alternate), actions, history)
        return native.experience_context_forecast(view, *actions)

    calls = 0
    for context, nuisance1, nuisance2 in product((0, 1), repeat=3):
        view, alternate = (context, nuisance1), (context, nuisance2)
        plan = _two_stage_plan(
            lambda first: forecast(view, alternate, first),
            lambda first, state, second: forecast(view, alternate, first, state, second),
        )
        require(plan == native.experience_context_plan(view), "NATIVE_PLANNER_FALLBACK")
        calls += 10  # Two transition and eight terminal inputs in the existing planner.
    require(native.checkpoint() == before_native, "READ_ONLY_NATIVE")
    require(donor.checkpoint() == before_donor, "READ_ONLY_SPECIALISTS")
    return calls


def run(native_directory, specialist_directory):
    manifest = json.loads(MANIFEST.read_bytes())
    started = time.monotonic()
    for path, expected in manifest["specialist_source_sha256"].items():
        checked_bytes(ROOT / path, expected)
    donors = {}
    for name, pin in manifest["specialist_artifacts_sha256"].items():
        package = json.loads(checked_bytes(specialist_directory / name, pin))
        raw = package["state_ascii"].encode("ascii")
        donor = NativeTemporalMultiLearner.restore(raw, package["state_sha256"])
        require(donor.checkpoint() == raw, "DONOR_COLD_BYTES")
        donors[name] = donor
    pairings = []
    for name, pin in manifest["native_artifacts_sha256"].items():
        raw = checked_bytes(native_directory / name, pin)
        native = NativeCumulativeLearner.restore(raw, pin)
        require(native.checkpoint() == raw, "NATIVE_COLD_BYTES")
        for donor_name, donor in donors.items():
            pairings.append({"native": name, "specialists": donor_name,
                             "public_inputs": verify_pair(native, donor)})
    return {"engineering_preflight": "PASS", "pairings": pairings,
            "source_actions": 0, "consequence_updates": 0, "held_worlds_scored": 0,
            "qualifies_runtime_specialist_selection": False,
            "scientific_pass": False, "deployment": "NONE",
            "wall_seconds": time.monotonic() - started}


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("native_directory", type=Path)
    parser.add_argument("specialist_directory", type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.native_directory, args.specialist_directory), indent=2, sort_keys=True))

"""Real native-class read-only ZERO-probe on already-consumed CKAD22 checkpoints.

Inputs MUST be the original pinned historical Actions ZIP; no source actors,
new training/witnesses, accepted checkpoint writes, source first-use, or rollout.
"""
from fractions import Fraction
from hashlib import sha1, sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json
import sys

from yggdrasil.native_cumulative_learner import NativeCumulativeLearner

ROOT = Path(__file__).resolve().parents[4]
PATH = Path(__file__).with_name("ckad22_exact_intermediate.py")
SPEC = spec_from_file_location("ckad22_exact_intermediate_zero_probe", PATH)
REC = module_from_spec(SPEC)
SPEC.loader.exec_module(REC)
SCHEMA = "ckad22.historical-native-cold-zero-probe.v1"
BLOBS = {
    "yggdrasil/native_cumulative_learner.py": "1bdeaa4277fc9b34bbf7c0f36c6d0a4cc00e1ca4",
    "yggdrasil/native_episode_experience.py": "5a18b00a4c4131526e71f51d63dfd9eb9471c81e",
    "research/contrib/chatgpt/CAUSAL-AMALGAM/ckad22_exact_intermediate.py":
        "f5868744ec6c59e874d0cd480eb1582740d6ac4f",
}
HISTORICAL = {
    101: "c98c3aca9388b8f1fa96f057955aceb1a460410641c3b87892501ce563bfb3c4",
    202: "6a91dfed5eaebaf5766e400ff05c9c323f95b66cf77f0d2dab683668d60af42e",
    303: "708334d15e385fb02513c5b9b701b400681a04086037d8209725637f38c066fb",
}
FROZEN_FIRST = {101: (0, 0), 202: (0, 0), 303: (0, 1)}
PRIOR = (Fraction(7, 96),) * 12 + (Fraction(1, 8),)


def git_blob(raw):
    return sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def verify_sources(root=ROOT):
    for path, expected in BLOBS.items():
        if git_blob((Path(root) / path).read_bytes()) != expected:
            raise ValueError("COLD_SOURCE_BLOB_DRIFT:" + path)


def ratio(value):
    if type(value) is not Fraction:
        raise ValueError("COLD_EXACT_FRACTION")
    if not 0 <= value <= 1:
        raise ValueError("COLD_PROBABILITY_BOUNDS")
    return [value.numerator, value.denominator]


def check_prior(reader):
    if (len(reader._ledger) != 384 or reader._context_start != 384
            or reader._context_novel is not True
            or len(reader._context_models) != 13 or reader._context_weights != PRIOR):
        raise ValueError("COLD_ZERO_PROBE_PRIOR_OR_CONTEXT")
    for index, (start, stop, _digest, _model) in enumerate(reader._context_models[:12]):
        if (start, stop) != (index * 32, (index + 1) * 32):
            raise ValueError("COLD_OLD_BLOCK_RANGE")
    if reader._context_models[-1][:2] != (384, 384):
        raise ValueError("COLD_NOVEL_BLOCK_RANGE")


def mixture(reader, view, first, state=None, second=None):
    """Independent rational expression over SAME native members, NOT a novel control."""
    if (state is None) != (second is None):
        raise ValueError("COLD_TWO_STAGE_HISTORY")
    check_prior(reader)
    weights = PRIOR
    if state is not None:
        preds = tuple(m.forecast(view, first) for _a, _b, _c, m in reader._context_models)
        masses = tuple(w * (p if state else 1-p) for w, p in zip(weights, preds))
        total = sum(masses, Fraction(0))
        if total <= 0:
            raise ValueError("COLD_CONDITIONING_ZERO_MASS")
        weights = tuple(w / total for w in masses)
    preds = tuple(m.forecast(view, first, state, second)
                  for _a, _b, _c, m in reader._context_models)
    return sum((w * p for w, p in zip(weights, preds)), Fraction(0))


def plan_from_mixture(reader, view):
    values, second_arms = [], []
    for first in (0, 1):
        p = mixture(reader, view, first)
        returns, actions = [], []
        for state in (0, 1):
            possibilities = [mixture(reader, view, first, state, second)
                             for second in (0, 1)]
            action = int(possibilities[1] > possibilities[0])
            returns.append(possibilities[action])
            actions.append(action)
        values.append((1-p) * returns[0] + p * returns[1])
        second_arms.append(tuple(actions))
    return {"first_values": tuple((v.numerator, v.denominator) for v in values),
            "first_action": int(values[1] > values[0]),
            "second_actions": tuple(second_arms)}


def readout(model, seed):
    reader = model._episode_reader()
    check_prior(reader)
    results = []
    for s1 in (0, 1):
        alternatives = []
        for n in (0, 1):
            view = (s1, n)
            predictions = []
            for first in (0, 1):
                p = model.experience_context_forecast(view, first)
                if p != mixture(reader, view, first):
                    raise ValueError("COLD_TRANSITION_SOURCE_PARITY")
                predictions.append(ratio(p))
                for state in (0, 1):
                    for second in (0, 1):
                        q = model.experience_context_forecast(view, first, state, second)
                        if q != mixture(reader, view, first, state, second):
                            raise ValueError("COLD_TERMINAL_SOURCE_PARITY")
                        predictions.append(ratio(q))
            if len(predictions) != 10:
                raise ValueError("COLD_FORECAST_CELL_COUNT")
            plan = model.experience_context_plan(view)
            if plan != plan_from_mixture(reader, view):
                raise ValueError("COLD_PLANNER_SOURCE_PARITY")
            explore = [model.experience_context_explore(view)]
            explore += [model.experience_context_explore(view, first, state)
                        for first in (0, 1) for state in (0, 1)]
            if len(explore) != 5 or any(a not in (0, 1) for a in explore):
                raise ValueError("COLD_EXPLORATION_SHAPE")
            alternatives.append((predictions, plan, explore))
        if alternatives[0] != alternatives[1]:
            raise ValueError("COLD_NUISANCE_ALIASED_FORECAST")
        predictions, plan, explore = alternatives[0]
        results.append({"s1": s1, "forecasts": predictions,
                        "planner_first": plan["first_action"],
                        "planner_first_values": [list(x) for x in plan["first_values"]],
                        "planner_second": [list(x) for x in plan["second_actions"]],
                        "explorer_actions": explore})
    if tuple(row["planner_first"] for row in results) != FROZEN_FIRST[seed]:
        raise ValueError("COLD_FROZEN_ACTUAL_PLAN_FALSIFIED")
    return results


def audit(ckad22_zip):
    verify_sources()
    receipts = []
    with REC.open_pinned(ckad22_zip, REC.CKAD22_SHA) as z:
        report = REC.load_report(z)
        if report.get("scientific_pass") is not False or report.get("accepted_native") is not False:
            raise ValueError("COLD_ARCHIVE_SCIENCE_FENCE")
        for row in sorted(report["seeds"], key=lambda x: x["seed"]):
            seed = row["seed"]
            if seed not in HISTORICAL or len(row["sessions"]) != 4:
                raise ValueError("COLD_ORIGINAL_SEED_OR_SESSION")
            evidence = row["sessions"][1]["states"]["novel_active"]
            if evidence["checkpoint_sha256"] != HISTORICAL[seed]:
                raise ValueError("COLD_FROZEN_INTERMEDIATE_PIN")
            final_raw = z.read(row["final_checkpoint_name"])
            if sha256(final_raw).hexdigest() != row["final_checkpoint_sha256"]:
                raise ValueError("COLD_FINAL_MEMBER_HASH")
            raw = REC.reconstruct(json.loads(final_raw), evidence, 384)
            if sha256(raw).hexdigest() != HISTORICAL[seed]:
                raise ValueError("COLD_RECONSTRUCTION_HASH")
            model = NativeCumulativeLearner.restore(raw, HISTORICAL[seed])
            if model.checkpoint() != raw:
                raise ValueError("COLD_NATIVE_PARENT_ROUNDTRIP")
            oldinfo = model._episode_reader().info()
            if (oldinfo["count"] != 384
                    or oldinfo["context"]["context_start"] != 352
                    or oldinfo["state_sha256"] != evidence["experience"]["state_sha256"]):
                raise ValueError("COLD_PARENT_CONTEXT_MISMATCH")
            fresh = model.begin_experience_context(novel=True)
            check_prior(fresh._episode_reader())
            if model.checkpoint() != raw:
                raise ValueError("COLD_PARENT_MUTATED")
            observations = readout(fresh, seed)
            fresh_raw = fresh.checkpoint()
            fresh_pin = sha256(fresh_raw).hexdigest()
            restarted = NativeCumulativeLearner.restore(fresh_raw, fresh_pin)
            if (restarted.checkpoint() != fresh_raw
                    or restarted._episode_reader().info() != fresh._episode_reader().info()
                    or readout(restarted, seed) != observations):
                raise ValueError("COLD_RESTART_CHANGED_NATIVE_READOUT")
            if model.checkpoint() != raw:
                raise ValueError("COLD_READOUT_MUTATED_PARENT")
            receipts.append({"seed": seed, "original_384_sha256": HISTORICAL[seed],
                             "native_zero_probe_sha256": fresh_pin,
                             "retained_witnesses": 384, "end_b_context_start": 352,
                             "new_context_start": 384, "prior_old": [7, 96],
                             "prior_novel": [1, 8], "cold_restore_equal": True,
                             "source_model_actions": 0, "public_readouts": observations})
    if [r["seed"] for r in receipts] != [101, 202, 303]:
        raise ValueError("COLD_ALL_ORIGINAL_SEEDS_REQUIRED")
    return {"schema": SCHEMA, "results": receipts,
            "historical_original_zip_sha256": REC.CKAD22_SHA,
            "original_world_source_actions": 0, "new_observations": 0,
            "canonical_checkpoint_writes": 0, "scientific_gain_verified": False,
            "source_first_use": False, "deployment": "NONE"}


def main(argv=None):
    args = sys.argv[1:] if argv is None else list(argv)
    if len(args) != 1:
        raise SystemExit("usage: python ckad22_native_zero_probe.py ckad22-original.zip")
    print(json.dumps(audit(args[0]), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

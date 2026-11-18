"""YGG-JEPA2-02: independently verify frozen source/score and trained states."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_jepa2_multilearner import NativeMultiLearner

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "CKAD-37"
CONTROLS = ("beta_full", "beta_window24", "beta_window48", "beta_discount95")
PHASES = ("stable_A", "early_B", "late_B", "early_return_A", "late_return_A")
ARMS = ("mixed", "jepa", "mispaired", "native_stream", "native_global",
        *CONTROLS, "sham")


def check(value, name):
    if not value:
        raise RuntimeError("YGG_JEPA2_02_AUDIT_" + name)


def verify(directory):
    result = json.loads((directory / "result.json").read_bytes())
    check(result["schema"] == "yggdrasil.jepa2-02.actual-native-source-development.v1"
          and result["prereg_first_sha"] == "f00d39793bff2091b7c74c05192a873725e675c2"
          and result["source_parent"] == "60634ab8c46b13039e021f28f8fa70bb6b69db96"
          and result["science_pass"] is False
          and result["accepted_native"] is False
          and result["deployment"] == "NONE"
          and result["source_first_use"] is False, "RESULT_CONTRACT")
    seen = []
    for seed in (14071, 14072):
        source = json.loads((SOURCE / f"pilot-{seed}.json").read_bytes())["case"]
        model = next(r for r in result["seeds"] if r["seed"] == seed)
        states = json.loads((directory / f"seed-{seed}-states.json").read_bytes())
        trace = json.loads((directory / f"seed-{seed}-trace.json").read_bytes())
        original = source["original_episode_receipts"]
        check(len(original) == len(trace) == model["source_original_episode_count"]
              and len(states) == 2, "SOURCE_LENGTH")
        check(set(r["seed"] for r in result["seeds"]) == {14071, 14072},
              "REPLICA_SEEDS")
        keypairs = set()
        for o, t in zip(original, trace):
            check((o["world"], o["index"], o["source_id"], o["phase"]) ==
                  (t["world"], t["index"], t["source_id"], t["phase"]),
                  "SOURCE_ORDER_OR_HELD_LABEL")
            keypairs.add((t["world"], t["source_id"]))
            for arm in ARMS[3:]:
                check(abs(t["scores"][arm] - o["prequential_brier"][arm]) < 1e-11,
                      "INDEPENDENT_ORIGINAL_CONTROL_SCORE")
        check(len(keypairs) == len(trace), "DUPLICATE_WITNESS")
        for phase in PHASES + ("pooled_late",):
            rows = [t for t in trace if t["phase"] == phase] if phase != "pooled_late" else [
                t for t in trace if t["phase"] in ("late_B", "late_return_A")
            ]
            check(bool(rows), "PHASE_EMPTY")
            for arm in ARMS:
                expected = sum(t["scores"][arm] for t in rows) / len(rows)
                got = model["metrics"][phase][arm]
                check(got["episodes"] == len(rows) and
                      abs(got["brier"] - expected) <= 1e-12, "SCORE_ARITHMETIC")
        pooled = model["metrics"]["pooled_late"]
        strong = min(pooled[a]["brier"] for a in CONTROLS)
        check(abs(model["strongest_control_brier"] - strong) <= 1e-12,
              "STRONGEST_COMPARATOR")
        early, late = model["metrics"]["early_B"], model["metrics"]["late_return_A"]
        b = pooled["mixed"]["brier"]
        checks = {
            "vs_native": b <= pooled["native_stream"]["brier"] - 0.005,
            "vs_conventional": b <= strong - 0.010,
            "early_shift_nonregression":
                early["mixed"]["brier"] <= early["native_stream"]["brier"] + 0.010,
            "old_world_return_nonregression":
                late["mixed"]["brier"] <= late["native_stream"]["brier"] + 0.010,
            "true_pairing_signal":
                pooled["jepa"]["brier"] <= pooled["mispaired"]["brier"] - 0.010,
        }
        check(checks == model["predicates"] and
              model["development_go"] == all(checks.values())
              and model["science_pass"] is False, "FROZEN_GATES")
        for index, state in enumerate(states):
            check(index == state["world"] == model["worlds"][index]["world"],
                  "WORLD_STATE_ID")
            raw = state["multi_learner_ascii"].encode("ascii")
            check(digest(raw) == state["multi_learner_sha256"] ==
                  model["worlds"][index]["multi_learner_sha256"], "LEARNER_SHA")
            restored = NativeMultiLearner.restore(raw, digest(raw))
            orig_sha = source["worlds"][index]["final_state_sha256"]
            check(state["native_original_sha256"] == orig_sha ==
                  digest(restored.native.checkpoint()) ==
                  model["worlds"][index]["native_replayed_sha256"],
                  "NATIVE_SOURCE_BYTE_CUSTODY")
            check(restored.native.info()["count"] == source["worlds"][index]["episodes"],
                  "NATIVE_EVENT_COUNT")
        seen.append(model["development_go"])
    check(result["development_go"] == all(seen), "GLOBAL_DEVELOPMENT_GATE")
    print("YGG_JEPA2_02_SOURCE_TRAINING_AUDIT_PASS"
          " DEVELOPMENT_GO=" + str(result["development_go"])
          + " SCIENCE_NOT_PASS", flush=True)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    verify(args.directory)


if __name__ == "__main__":
    main()


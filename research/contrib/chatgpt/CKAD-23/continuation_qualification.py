"""Post-training engineering check; no frozen evaluation scores are recomputed.

Uses six new synthetic episodes in a separate qualification cohort. These
temporary descendants are never promoted or included in the primary results.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner, EXPERIENCE_SOURCE
spec = importlib.util.spec_from_file_location("ckad23_continuation_source", HERE.parent / "CKAD-20" / "synthetic_world.py")
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)

def advance(model, seed, index):
    cohort = "ckad23-cold-continuation-qualification"
    episode = source.make_episode(cohort=cohort, seed=seed + 21000,
                                  index=index, family="invariant", regime=0)
    views = source.public_views(episode)
    plan = model.experience_context_plan(views[0])
    row = source.rollout(episode, lambda _: plan["first_action"],
                         lambda _, first, state: plan["second_actions"][first][state])
    identifier = digest(canonical([cohort, EXPERIENCE_SOURCE, seed, index]))
    return model.observe_experience(identifier, views, row,
        source_sha256=EXPERIENCE_SOURCE,
        packet_sha256=digest(canonical([identifier, views, row])))

def child(seed, checkpoint, expected_pin, output):
    raw = checkpoint.read_bytes()
    model = NativeCumulativeLearner.restore(raw, expected_pin)
    assert model.checkpoint() == raw
    first = advance(model, seed, 0).checkpoint()
    resumed = NativeCumulativeLearner.restore(first, digest(first))
    final = advance(resumed, seed, 1).consolidate_experience().checkpoint()
    assert NativeCumulativeLearner.restore(final, digest(final)).checkpoint() == final
    output.write_bytes(final)

def qualify():
    result = json.loads((HERE / "campaign-result.json").read_bytes())
    reports = []
    for case in result["seeds"]:
        seed = case["seed"]
        path = HERE / case["final_checkpoint_name"]
        raw = path.read_bytes()
        assert digest(raw) == case["final_checkpoint_sha256"]
        model = NativeCumulativeLearner.restore(raw, case["final_checkpoint_sha256"])
        direct = advance(advance(model, seed, 0), seed, 1).checkpoint()
        with tempfile.TemporaryDirectory(prefix="ckad23-cold-") as directory:
            output = Path(directory) / "continued.json"
            subprocess.check_call([sys.executable, "-B", str(Path(__file__).resolve()),
                "--child", str(seed), str(path), case["final_checkpoint_sha256"], str(output)], cwd=ROOT)
            assert output.read_bytes() == direct
        previous, continued = json.loads(raw), json.loads(direct)
        before = json.loads(previous.pop("experience_ascii"))
        after = json.loads(continued.pop("experience_ascii"))
        assert previous == continued
        assert len(before["episodes"]) == 640 and len(after["episodes"]) == 642
        assert after["episodes"][:640] == before["episodes"]
        assert after["stream_start"] == before["stream_start"] == 448
        assert path.read_bytes() == raw
        reports.append({"seed": seed, "parent_sha256": digest(raw),
                        "continued_sha256": digest(direct), "witnesses": 642})
    return {"classification": "COLD_CONTINUED_TRAINING_VERIFIED",
            "qualification_only_unique_synthetic_episodes": 6,
            "qualification_only_unique_synthetic_actions": 12,
            "primary_results_changed": False, "saved_primary_states_changed": False,
            "scientific_pass": False, "seeds": reports}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--child", nargs=4)
    args = parser.parse_args()
    if args.child:
        seed, checkpoint, pin, output = args.child
        child(int(seed), Path(checkpoint), pin, Path(output))
    else:
        print(json.dumps(qualify(), sort_keys=True))

"""Check the staged trial's reported gate decisions and cold checkpoint custody."""

from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from time import monotonic

from selection_trial import restore
from staged_retention import admit

HERE = Path(__file__).resolve().parent
CONTROLS = ("pinned", "fit_full", "fit_trailing", "fit_change_point")


def check(checkpoints, override, result_directory):
    started = monotonic()
    plan_raw = override.read_bytes()
    plan = json.loads(plan_raw)
    protocol = json.loads((HERE / plan["checkpoint_contract"]).read_bytes())
    result = json.loads((result_directory / "result.json").read_bytes())
    if result["protocol_sha256"] != sha256(plan_raw).hexdigest():
        raise ValueError("Frozen protocol does not match scored result")
    if result["parent_ckpt_sha256"] != protocol["joint_sha256"]:
        raise ValueError("Starting checkpoint pin mismatch")
    anchor = restore(checkpoints, protocol)
    history = anchor.native._episode_reader()._ledger
    if [case["seed"] for case in result["replicas"]] != plan["seeds"]:
        raise ValueError("Unexpected replica roster")
    old_limit = Fraction(plan["max_brier_drift"])
    gain = Fraction(plan["min_novel_gain"])
    new_limit = Fraction(plan["max_new_loss_vs_unguarded"])
    validated = []
    primary_checks = []
    for case in result["replicas"]:
        source = result_directory / f"seed-{case['seed']}"
        work = source / "native-joint.json"
        trace_bytes = (source / "trace.json").read_bytes()
        trail = json.loads(trace_bytes)
        if sha256(trace_bytes).hexdigest() != case["trace_sha256"]:
            raise ValueError("Scored trace digest mismatch")
        if work.is_file():
            trained = restore(checkpoints, protocol, work.resolve(), case["full_joint_sha256"])
        else:
            reconstructed = anchor
            for entry in trail:
                views = tuple(tuple(view) for view in entry["views"])
                reconstructed = admit(reconstructed, entry["id"], views, entry["row"])
            with TemporaryDirectory(prefix="amalgam-staged-audit-") as directory:
                recovered = Path(directory) / "native-joint.json"
                recovered.write_bytes(reconstructed.checkpoint())
                trained = restore(checkpoints, protocol, recovered, case["full_joint_sha256"])
        cold = trained.native._episode_reader()._ledger
        if cold[:len(history)] != history or len(cold) - len(history) != len(trail):
            raise ValueError("Original native history failed cold replay")
        action_count = 0
        accepted = 0
        decisions = case["decisions"]
        for index, (phase, step) in enumerate(zip(plan["phases"], decisions, strict=True), 1):
            action_count += phase["n"] * 2
            if (step["stage"], step["name"]) != (index, phase["name"]):
                raise ValueError("Phase drift")
            if all(step["gates"].values()):
                accepted = index
            if step["selected_stage"] != accepted:
                raise ValueError("Guard selected an inadmissible stage")
            if phase["name"] == "return":
                continue
            new = step["new_report"]
            old = step["old_report"]
            mean = lambda name: sum(Fraction(str(value)) for value in new[name])/2
            historical_ok = all(Fraction(str(a))-Fraction(str(b)) <= old_limit
                                for a,b in zip(old["guarded"], old["pinned"], strict=True))
            primary_checks.append(historical_ok and
                                  min(mean(name) for name in CONTROLS)-mean("guarded") >= gain
                                  and mean("guarded")-mean("unguarded") <= new_limit)
        if case["selected_stage"] != accepted or case["training_actions"] != action_count:
            raise ValueError("Guard or action summary drift")
        if accepted == 0 and case["selected_joint_sha256"] != protocol["joint_sha256"]:
            raise ValueError("Readout with no admissible stages must retain the anchor")
        expected = tuple((e["id"], tuple(tuple(v) for v in e["views"]),
                          *(e["row"][k] for k in ("x1","s2","x2","y"))) for e in trail)
        if cold[len(history):] != expected:
            raise ValueError("Joint state contains different witnesses than the scored trial")
        new_steps = [b.steps-a.steps for a,b in zip(anchor._heads,trained._heads,strict=True)]
        if new_steps != [3*len(trail)] * 4 or new_steps != case["head_steps"]:
            raise ValueError("Specialist continuation counts failed cold replay")
        validated.append(dict(seed=case["seed"], joint_sha256=case["full_joint_sha256"],
                              witnesses=len(cold), gradient_steps=new_steps))
    if ("DEV_GO" if all(primary_checks) else "DEV_NO_GO") != result["development"]:
        raise ValueError("Independent classification mismatch")
    return dict(cold_replay=validated, protected_first_use=False, source_actions=0,
                exact_report_classification=True, wall_seconds=monotonic()-started)


if __name__ == "__main__":
    checkpoint_directory, manifest_path, result_directory = map(Path, sys.argv[1:])
    print(json.dumps(check(checkpoint_directory, manifest_path, result_directory),
                     indent=2, sort_keys=True))

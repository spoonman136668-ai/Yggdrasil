"""Exercise CKAD25 evidence guards without training or learner imports."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import time

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ckad25_negative_reference", HERE / "independent_audit.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def verify(root=HERE):
    start = time.monotonic()
    result = json.loads((root / "campaign-result.json").read_bytes())
    mutations = [
        ("gate", "CKAD25_INDEPENDENT_FROZEN_METRICS_GATES",
         lambda r:r["development_gates"].__setitem__("whole_curve_vs_original",
                  not r["development_gates"]["whole_curve_vs_original"])),
        ("comparator", "CKAD25_INDEPENDENT_HELD_101_0_original_active",
         lambda r:r["seeds"][0]["stream"][0]["evaluation"]["original_active"].__setitem__(
             "reward_sum", r["seeds"][0]["stream"][0]["evaluation"]["original_active"]["reward_sum"]+1)),
        ("monitor", "CKAD25_INDEPENDENT_MONITOR_TRACE",
         lambda r:r["seeds"][0]["stream"][0]["monitors"]["uniform_random"].__setitem__("score",[2,1])),
        ("checkpoint", "CKAD25_INDEPENDENT_CHECKPOINT_REPLAY_101_0",
         lambda r:r["seeds"][0]["stream"][0].__setitem__("checkpoint_sha256","0"*64)),
        ("capacity", "CKAD25_INDEPENDENT_CAPACITY_PROBE",
         lambda r:r["seeds"][0]["capacity_probe"].__setitem__("admitted", True)),
        ("parent", "CKAD25_INDEPENDENT_PARENT_PIN",
         lambda r:r["seeds"][0].__setitem__("parent_checkpoint_sha256","0"*64)),
    ]
    rejected = {}
    for name, expected, mutate in mutations:
        changed = copy.deepcopy(result)
        mutate(changed)
        changed["stable_sha256"] = audit.sha(audit.canonical(audit.stable(changed)))
        try:
            if name == "gate":
                audit.verify_gates(changed)
            elif name == "capacity":
                case = changed["seeds"][0]
                raw = (root / case["final_checkpoint_name"]).read_bytes()
                ledger = json.loads(json.loads(raw)["experience_ascii"])["episodes"]
                audit.verify_capacity(case,ledger,audit.sha(raw))
            else:
                with tempfile.TemporaryDirectory(prefix="ckad25-negative-") as temporary:
                    directory = Path(temporary)
                    (directory / "campaign-result.json").write_text(json.dumps(changed),encoding="ascii")
                    for checkpoint in root.glob("seed-*-capacity-native.json"):
                        (directory / checkpoint.name).write_bytes(checkpoint.read_bytes())
                    audit.audit(directory)
        except RuntimeError as exc:
            if str(exc) != expected:
                raise AssertionError(f"{name}: expected {expected}; received {exc}") from exc
            rejected[name] = expected
        else:
            raise AssertionError("Altered CKAD25 evidence accepted: "+name)
    return {"negative_controls":"PASS", "rejections":rejected,
            "semantic_hash_recomputed":True, "native_imports":0,
            "new_primary_observations":0, "wall_seconds":time.monotonic()-start}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory",nargs="?",type=Path,default=HERE)
    args = parser.parse_args()
    print(json.dumps(verify(args.directory),sort_keys=True))

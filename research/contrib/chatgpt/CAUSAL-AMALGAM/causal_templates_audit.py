"""Independently verify exact cold custody and Brier scores from frozen public traces."""

from collections import Counter
from fractions import Fraction
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from time import monotonic

from selection_trial import restore
from staged_retention import admit
from yggdrasil.native_context_basis import canonical, digest

HERE = Path(__file__).resolve().parent
SCALE = 1_000_000


def replay(checkpoints, manifest_path, outputs):
    wall = monotonic()
    protocol = json.loads((HERE/"selection_protocol_dev.json").read_bytes())
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    result = json.loads((outputs/"result.json").read_bytes())
    if result["protocol_sha256"] != digest(manifest_bytes) or result["input_sha256"] != protocol["joint_sha256"]:
        raise ValueError("Template source and starting checkpoint custody mismatch")
    anchor = restore(checkpoints, protocol)
    old = anchor.native._episode_reader()._ledger
    verified = []
    for replica, expected_seed in zip(result["replicas"],manifest["seeds"],strict=True):
        seed = replica["seed"]
        if seed != expected_seed:
            raise ValueError("Unexpected replica seed or order")
        root = outputs/f"seed-{seed}"
        trace = (root/"trace.json").read_bytes()
        if digest(trace) != replica["checkpoints"]["trace_sha256"]:
            raise ValueError("Witness trace hash mismatch")
        events = json.loads(trace)
        counts = Counter(row["stage"] for row in events)
        if counts != dict(enumerate(phase["count"] for phase in manifest["phases"])):
            raise ValueError("Frozen stage witness-count mismatch")
        for stage, (phase, scores) in enumerate(zip(manifest["phases"],replica["scores"],strict=True)):
            visible = [row for row in events if row["stage"] == stage]
            scored = visible[manifest["warmup"]:]
            if scores["n"] != len(scored) or scores["phase"] != phase["name"]:
                raise ValueError("Frozen reporting window changed")
            for arm, recorded in scores["squared_errors"].items():
                value = sum((r["forecasts"][arm] - SCALE*r["row"]["s2"])**2 for r in scored)
                if value != recorded:
                    raise ValueError("Independent Brier numerator mismatch")
            errors = scores["squared_errors"]
            if phase["name"] == "paired_new":
                baseline = min(v for k,v in errors.items() if k != "native_structure")
                accepted = Fraction(baseline-errors["native_structure"],len(scored)*SCALE**2) >= Fraction(manifest["gain"])
            else:
                baseline = (errors["pinned"] if phase["name"] == "familiar" else
                            min(errors[k] for k in ("live","change_point","fitted_structure")))
                accepted = Fraction(errors["native_structure"]-baseline,len(scored)*SCALE**2) <= Fraction(manifest["old_and_unsupported_loss"])
            if accepted != result["gates"][f"{seed}:{phase['name']}"]["pass_gate"]:
                raise ValueError("Frozen gate mismatch")
        checkpoint = root/"joint.json"
        pin = replica["checkpoints"]["final_sha256"]
        if checkpoint.is_file():
            cold = restore(checkpoints,protocol,checkpoint.resolve(),pin)
        else:
            live = anchor
            for e in events:
                live = admit(live,e["identifier"],tuple(tuple(v) for v in e["views"]),e["row"])
            with TemporaryDirectory(prefix="amalgam-template-audit-") as scratch:
                checkpoint = Path(scratch)/"recovered.json"
                checkpoint.write_bytes(live.checkpoint())
                cold = restore(checkpoints,protocol,checkpoint,pin)
        witnessed = cold.native._episode_reader()._ledger
        suffix = tuple((e["identifier"],tuple(tuple(v) for v in e["views"]),
                        *(e["row"][k] for k in ("x1","s2","x2","y"))) for e in events)
        if witnessed != old+suffix or replica["head_steps"] != [3*len(events)]*4:
            raise ValueError("Model history or specialist continuation mismatch")
        verified.append(dict(seed=seed,retained=len(old),total_witnesses=len(witnessed),joint_sha256=pin))
    return dict(models=verified, exact_cold=True, new_source_actions=0, wall_seconds=monotonic()-wall)


if __name__ == "__main__":
    print(json.dumps(replay(*map(Path,sys.argv[1:])),indent=2,sort_keys=True))

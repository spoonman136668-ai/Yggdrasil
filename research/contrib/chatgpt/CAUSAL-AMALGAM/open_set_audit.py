"""Recompute scored open-set losses and reconstruct the exact recorded descendants."""

from fractions import Fraction
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from time import monotonic

from selection_trial import restore
from staged_retention import admit
from yggdrasil.native_context_basis import digest

HERE = Path(__file__).resolve().parent
SCALE = 1_000_000


def audit(checkpoints, plan_path, evidence):
    wall = monotonic()
    raw_plan = plan_path.read_bytes()
    plan = json.loads(raw_plan)
    protocol = json.loads((HERE / plan["checkpoint_contract"]).read_bytes())
    result = json.loads((evidence/"result.json").read_bytes())
    if result["protocol_sha256"] != digest(raw_plan) or result["input_sha256"] != protocol["joint_sha256"]:
        raise ValueError("Recorded provenance does not match frozen input")
    base = restore(checkpoints,protocol)
    prefix = base.native._episode_reader()._ledger
    accepted = []
    checks = []
    for seed, replica in zip(plan["seeds"],result["replicas"],strict=True):
        if seed != replica["seed"]:
            raise ValueError("Recorded seeds changed")
        directory = evidence/f"seed-{seed}"
        raw = (directory/"trace.json").read_bytes()
        if digest(raw) != replica["checkpoints"]["trace_sha256"]:
            raise ValueError("Scored trace hash mismatch")
        events = json.loads(raw)
        if replica["actions"] != 2*len(events):
            raise ValueError("Invalid intervention accounting")
        for stage_index,(phase,score) in enumerate(zip(plan["phases"],replica["scores"],strict=True)):
            phase_rows = [r for r in events if r["stage"] == stage_index]
            scored = phase_rows[plan["warmup"]:]
            if (len(phase_rows) != phase["count"] or len(scored) != score["n"] or
                    phase["name"] != score["phase"]):
                raise ValueError("Stage reporting window changed")
            points = {arm:sum((p["forecasts"][arm]-p["row"]["s2"]*SCALE)**2 for p in scored)
                      for arm in score["squared_errors"]}
            if points != score["squared_errors"]:
                raise ValueError("Recomputed loss numerator does not match")
            trial = points["candidate"]
            if phase["name"] == "paired_new":
                strongest = min(v for name,v in points.items() if name != "candidate")
                go = Fraction(strongest-trial,len(scored)*SCALE**2) >= Fraction(plan["gain"])
            else:
                strongest = (points["pinned"] if phase["name"]=="familiar" else
                             min(points[k] for k in ("native_live","fitted_gate","history_change_point")))
                go = Fraction(trial-strongest,len(scored)*SCALE**2) <= Fraction(plan["old_and_unsupported_loss"])
            if result["gates"][f"{seed}:{phase['name']}"]["pass_gate"] != go:
                raise ValueError("Independent gate decisions differ")
            accepted.append(go)
        path = directory/"joint.json"
        pin = replica["checkpoints"]["final_sha256"]
        if path.is_file():
            restored = restore(checkpoints,protocol,path.resolve(),pin)
        else:
            model = base
            for row in events:
                model = admit(model,row["identifier"],tuple(tuple(v) for v in row["views"]),row["row"])
            with TemporaryDirectory(prefix="amalgam-open-set-audit-") as scratch:
                checkpoint = Path(scratch)/"restored.json"
                checkpoint.write_bytes(model.checkpoint())
                restored = restore(checkpoints,protocol,checkpoint,pin)
        replay = restored.native._episode_reader()._ledger
        recorded = tuple((r["identifier"],tuple(tuple(v) for v in r["views"]),
                          *(r["row"][key] for key in ("x1","s2","x2","y"))) for r in events)
        if replay != prefix+recorded or [b.steps-a.steps for a,b in zip(base._heads,restored._heads,strict=True)] != [3*len(events)]*4:
            raise ValueError("Cold state fails append-only witness or head continuation")
        checks.append(dict(seed=seed,final_sha256=pin,count=len(replay)))
    if result["development"] != ("DEV_GO" if all(accepted) else "DEV_NO_GO"):
        raise ValueError("Final disposition mismatch")
    return dict(exact_audit=True,cold_descendants=checks,new_source_actions=0,wall_seconds=monotonic()-wall)


if __name__=="__main__":
    print(json.dumps(audit(*map(Path,sys.argv[1:])),indent=2,sort_keys=True))

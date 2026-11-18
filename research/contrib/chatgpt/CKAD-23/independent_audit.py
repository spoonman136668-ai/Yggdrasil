"""Independent final SHA audit of CKAD23 immutable action-consequence evidence.

Recomputes all frozen development gates from committed per-seed source receipts.
Reopens every final checkpoint from disk and verifies exact native restoration.
Never executes additional source episodes or changes the learned model.
"""
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT))
if hasattr(sys,"set_int_max_str_digits"):sys.set_int_max_str_digits(0)
import audit
from yggdrasil.native_context_basis import digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner


def run():
    frozen=json.loads((HERE/"result.json").read_bytes())
    secondary=json.loads((HERE/"replication-windows.json").read_bytes())
    audits=[json.loads((HERE/f"seed-{n}-source-proof.json").read_bytes())
            for n in audit.SEEDS]
    windows=[json.loads((HERE/f"seed-{n}-windows-proof.json").read_bytes())
             for n in audit.SEEDS]
    rebuilt=audit.aggregate(audits)
    replicated=audit.aggregate(windows)
    audit.need(rebuilt==replicated==frozen==secondary,
               "SOURCE_RECOMPUTATION")
    audit.need(rebuilt["scientific_pass"] is False and
               rebuilt["accepted_native"] is False and
               rebuilt["deployment"]=="NONE","SCIENTIFIC_FENCE")
    checkpoints=[]
    for seed in audit.SEEDS:
        row=next(a["seeds"][0] for a in audits if a["seeds"][0]["seed"]==seed)
        path=HERE/f"seed-{seed}-stream-native.json"
        raw=path.read_bytes()
        sha=digest(raw)
        audit.need(sha==row["final_checkpoint_sha256"] and
                   len(raw)==row["final_checkpoint_bytes"],"BYTES_CUSTODY")
        native=NativeCumulativeLearner.restore(raw,sha)
        audit.need(native.checkpoint()==raw,"COLD_RESTORE_PARITY")
        info=native.info()["episode_experience"]
        audit.need(info["count"]==640 and
                   info["stream"]["stream_start"]==448 and
                   info["stream"]["detections"]==row["detected_boundaries"],
                   "LEARNED_CONTEXT_RETENTION")
        legacy=json.loads(raw)
        experience=json.loads(legacy["experience_ascii"])
        audit.need(experience["schema"]==
                   "yggdrasil.ckad.native-episode-experience.v4" and
                   experience["stream_start"]==448 and
                   len({event[0] for event in experience["episodes"]})==640,
                   "CHECKPOINT_SCHEMA_AND_IDENTITIES")
        checkpoints.append({"seed":seed,"sha256":sha,"bytes":len(raw),
                            "detections":len(row["detected_boundaries"])})
    return {
      "independent_audit":"PASS",
      "source":"CKAD23_SYNTHETIC_UNSIGNALED_CONTEXT",
      "classification":frozen["classification"],
      "stable_sha256":frozen["stable_sha256"],
      "frozen_gates":frozen["development_gates"],
      "checkpoint_custody":checkpoints,
      "scientific_pass":False,"accepted_native":False,"deployment":"NONE",
    }

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True))

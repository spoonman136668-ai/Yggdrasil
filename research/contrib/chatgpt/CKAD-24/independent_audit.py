"""CKAD24 evidence-only source rerender and cold-state proof.

Read six preserved gzip sources and six exact model checkpoints. Independently
recompute frozen gates and compare original 448-source history, all 192
appended witnesses, cold-replay bytes, stream history and evidence counts.
"""
import gzip
from itertools import product
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
PARENT=HERE.parent/"CKAD-22"
sys.path.insert(0,str(ROOT))
if hasattr(sys,"set_int_max_str_digits"):sys.set_int_max_str_digits(0)
import audit
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner


def need(ok,reason):
    if not ok:raise ValueError("CKAD24_INDEPENDENT_"+reason)


def exact_gzip(path):
    data=path.read_bytes()
    need(len(data)>=20 and data[:3]==b"\x1f\x8b\x08","GZIP_TYPE")
    need(data[4:8]==b"\x00"*4,"DETERMINISTIC_GZIP_TIMESTAMP")
    return gzip.decompress(data)


def run():
    cases=[]
    custody=[]
    protocol,original=audit.source_protocol()
    for schedule,seed in product(audit.SCHEDULES,audit.SEEDS):
        stem=f"{schedule}-{seed}"
        source=exact_gzip(HERE/f"{stem}-source-proof.json.gz")
        checkpoint=exact_gzip(HERE/f"{stem}-native.json.gz")
        case=json.loads(source)
        diagnostic=audit.validate_case(case,protocol,original)
        trained=case["seed_result"]
        sha=audit.sha(checkpoint)
        need(sha==trained["final_checkpoint_sha256"] and
             len(checkpoint)==trained["final_checkpoint_bytes"],
             "CHECKPOINT_BYTE_PIN")
        root=json.loads(checkpoint)
        episode=json.loads(root["experience_ascii"])
        need(len(episode["episodes"])==640 and
             len({v[0] for v in episode["episodes"]})==640,
             "UNIQUE_EVIDENCE_COUNT")
        original_raw=(PARENT/f"seed-{seed}-expanded-native.json").read_bytes()
        need(audit.sha(original_raw)==trained["parent_checkpoint_sha256"],
             "QUALIFIED_PARENT_CHECKPOINT")
        before=json.loads(original_raw)
        old=json.loads(before["experience_ascii"])["episodes"]
        need(len(old)==448 and episode["episodes"][:448]==old,
             "NO_HISTORY_PREFIX_LOSS")
        need({k:v for k,v in root.items() if k!="experience_ascii"}==
             {k:v for k,v in before.items() if k!="experience_ascii"},
             "LEGACY_SUBSTRATE_IMMUTABLE")
        need(all(v[0] not in {r[0] for r in old}
                 for v in episode["episodes"][448:]),
             "NEW_UNIQUE_SOURCE_WITNESSES")
        restored=NativeCumulativeLearner.restore(checkpoint,sha)
        need(restored.checkpoint()==checkpoint,"EXACT_COLD_CONTINUATION")
        info=restored.info()["episode_experience"]
        need(info["count"]==640 and info["stream"]["stream_start"]==448 and
             info["stream"]["detections"]==trained["active_detections"],
             "DETECTED_CAUSAL_EVENT_PINS")
        need(audit.classify(info["stream"]["detections"])==diagnostic,
             "INDEPENDENT_BOUNDARY_CLASSIFICATION")
        cases.append(case)
        custody.append({
          "schedule":schedule,"seed":seed,
          "checkpoint_sha256":sha,
          "checkpoint_bytes":len(checkpoint),
          "restored_equal":True,
          "prefix_witnesses":448,
          "appended_witnesses":192,
          "detector_alarms":len(trained["active_detections"]),
        })
    sealed=audit.aggregate(cases)
    recorded=json.loads((HERE/"result.json").read_bytes())
    need(sealed==recorded,"AGGREGATE_NOT_REPRODUCIBLE")
    need(sealed["scientific_pass"] is False and
         sealed["accepted_native"] is False and sealed["deployment"]=="NONE",
         "PROMOTION_BARRIER")
    return {
       "audit":"PASS","classification":sealed["classification"],
       "stable_sha256":sealed["stable_sha256"],
       "frozen_gates":sealed["frozen_gates"],
       "native_checkpoint_proofs":custody,
       "scientific_pass":False,"accepted_native":False,"deployment":"NONE",
    }


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True))

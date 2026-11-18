"""CKAD28 source-free independent cold-custody and frozen metric replay.

Rehydrate six source proofs and 18 complete native models, compare every
public action consequence to the witnessed ledger, preserve original 448
prefix, independently re-evaluate all frozen gates without using a new
source episode or training data, and reject any scientific promotion.
"""
from itertools import product
from pathlib import Path
import gzip
import json
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
CK22=HERE.parent/"CKAD-22"
sys.path.insert(0,str(ROOT))
if hasattr(sys,"set_int_max_str_digits"):sys.set_int_max_str_digits(0)
import audit
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner


def require(ok,reason):
    if not ok:raise ValueError("CKAD28_INDEPENDENT_"+reason)


def unpack(name):
    z=(HERE/name).read_bytes()
    require(z[:3]==b"\x1f\x8b\x08" and z[4:8]==b"\0\0\0\0",
            "LOSSLESS_DETERMINISTIC_GZIP")
    return gzip.decompress(z)


def run():
    report=json.loads((HERE/"result.json").read_bytes())
    provenance=json.loads((HERE/"provenance.json").read_bytes())
    p=audit.campaign.source_protocol()
    cases=[]
    witness_custody=[]
    for scenario,seed in product(audit.SCENARIOS,audit.SEEDS):
        prefix=f"{scenario}-{seed}"
        proof=json.loads(unpack(prefix+"-source-proof.json.gz"))
        audit.verify_case(proof,p)
        original=(CK22/f"seed-{seed}-expanded-native.json").read_bytes()
        require(audit.digest(original)==proof["parent_checkpoint_sha256"],
                "PINNED_SOURCE_448")
        base=json.loads(original)
        old=json.loads(base["experience_ascii"])["episodes"]
        require(len(old)==448,"EXACT_ORIGINAL_LENGTH")
        for arm in audit.ARMS:
            raw=unpack(f"{prefix}-{arm}-native.json.gz")
            sha=audit.digest(raw)
            receipt=proof["custody"][arm]
            require(sha==receipt["checkpoint_sha256"] and
                    len(raw)==receipt["checkpoint_bytes"],
                    "NATIVE_SOURCE_SHA256")
            state=json.loads(raw)
            ledger=json.loads(state["experience_ascii"])
            episodes=ledger["episodes"]
            require(len(episodes)==576 and episodes[:448]==old and
                    len({x[0] for x in episodes})==576,
                    "CUMULATIVE_WITNESS_PREFIX")
            require({k:v for k,v in state.items() if k!="experience_ascii"}==
                    {k:v for k,v in base.items() if k!="experience_ascii"},
                    "UNRELATED_NATIVE_MUTATION")
            require(ledger["schema"]=="yggdrasil.ckad.native-episode-experience.v4"
                    and ledger["stream_start"]==448,"UNSIGNALED_NATIVE_MODEL")
            for native,public in zip(episodes[448:],proof["source_receipts"][arm]):
                require(native[0]==public["event_id"] and
                        native[1]==public["views"] and
                        native[2:]==[
                            public["first_action"],public["next_state"],
                            public["second_action"],public["reward"]],
                        "ACTUAL_INTERVENTION_RECEIPT")
            cold=NativeCumulativeLearner.restore(raw,sha)
            require(cold.checkpoint()==raw and
                    cold.info()["episode_experience"]["count"]==576,
                    "EXACT_COLD_RESTORE")
            witness_custody.append({
                "scenario":scenario,"seed":seed,"arm":arm,
                "sha256":sha,"source_prefix":448,
                "new_public_episodes":128,
                "restored":True
            })
        cases.append(proof)
    replay=audit.metrics(cases)
    require(replay==report and
            provenance["result_stable_sha256"]==report["stable_sha256"] and
            provenance["exact_cross_os_model_and_result_parity"] is True and
            len(provenance["cold_model_checkpoints"])==18,
            "INDEPENDENT_FINAL_GATES")
    require(report["scientific_pass"] is False and
            report["accepted_native"] is False and
            report["deployment"]=="NONE","SCIENTIFIC_NONPROMOTION")
    return {
        "audit":"PASS","classification":report["classification"],
        "frozen_gates":report["frozen_gates"],
        "stable_sha256":report["stable_sha256"],
        "cold_native_custody":witness_custody,
        "scientific_pass":False,"accepted_native":False,"deployment":"NONE",
    }


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True))

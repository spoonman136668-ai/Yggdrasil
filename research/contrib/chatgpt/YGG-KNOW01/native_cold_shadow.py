"""KNOW06: real archived native component cold-restore + source-pinned factual shadow.

Read-only engineering check. This is NOT canonical owner custody, four-head
Amalgam restoration, semantic causal grounding, or scientific gain.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import time
from pathlib import Path
from knowledge_capacity_audit import inventory
from typed_readout_bridge import TypedFactualReadoutBridge
from explicit_view_projection import ExplicitPublicViewProjection, make_fixture_manifest

JOINT_SHA = "576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8"
NATIVE_SHA = "5720151e18b52f7219763027c2ad9c7c37476e099b4334e42417615adb7f959d"
IMAGE_SHA = "6dd87ba5bbf5fd7ecaffa6d48f674e34ce2a7cc7fa748ec7698d2c0a4cdae3d1"
NFACTS = 21_343_681

def digest(data):
    return hashlib.sha256(data).hexdigest()

def require(ok, msg):
    if not ok:
        raise ValueError("YGG_KNOW06_" + msg)

def valid_nested(raw, joint_sha=JOINT_SHA, native_sha=NATIVE_SHA):
    require(type(raw) is bytes and 0 < len(raw) <= 32*1024*1024
            and digest(raw) == joint_sha, "JOINT_EXTERNAL_SHA")
    try:
        def unique(pairs):
            out = {}
            for key, value in pairs:
                require(key not in out, "DUPLICATE_KEY")
                out[key] = value
            return out
        doc = json.loads(raw.decode("ascii"), object_pairs_hook=unique)
        norm = lambda d: json.dumps(d,sort_keys=True,separators=(",",":"),
                                    ensure_ascii=True,allow_nan=False).encode("ascii")
        require(type(doc) is dict and norm(doc) == raw
                and set(doc) == {"schema", "native_ascii", "native_parent_sha256",
                    "specialist_parent_sha256", "action_heads", "temporal_heads"}
                and doc["schema"] == "yggdrasil.ckad.native-causal-amalgam.v1"
                and type(doc["action_heads"]) is list
                and len(doc["action_heads"]) == 2
                and type(doc["temporal_heads"]) is list
                and len(doc["temporal_heads"]) == 2, "JOINT_CONTRACT")
        native = doc["native_ascii"].encode("ascii")
        require(digest(native) == native_sha, "NATIVE_EXTERNAL_SHA")
        ndoc = json.loads(native.decode("ascii"), object_pairs_hook=unique)
        require(type(ndoc) is dict and norm(ndoc) == native
                and ndoc.get("schema") == "yggdrasil.ckad.native-cumulative-learner.v5"
                and ndoc.get("source_mode") == "engineering_fixture_only"
                and ndoc.get("accepted_native") is False
                and ndoc.get("scientific_pass") is False, "NATIVE_RESEARCH_ONLY")
    except (UnicodeError, TypeError, KeyError, ValueError, OverflowError) as exc:
        if isinstance(exc, ValueError) and str(exc).startswith("YGG_KNOW06_"):
            raise
        raise ValueError("YGG_KNOW06_BAD_JSON") from exc
    return native

class FrozenNative:
    __slots__ = ("_joint", "_native", "_learned")
    def __init__(self, joint, native, learned):
        require(digest(joint) == JOINT_SHA and digest(native) == NATIVE_SHA,
                "FIXED_ARCHIVE")
        require(learned.checkpoint() == native, "COLD_READBACK")
        self._joint, self._native, self._learned = joint, native, learned
    def checkpoint(self):
        require(self._learned.checkpoint() == self._native, "MUTATED_NATIVE")
        return self._joint
    def plan(self, view):
        self.checkpoint()
        prediction = self._learned.experience_context_plan(view)
        self.checkpoint()
        return prediction

def prove(installed_session, joint_path):
    from yggdrasil.native_cumulative_learner import NativeCumulativeLearner
    from yggdrasil.native_cumulative_facts import CumulativeNativeFacts
    from yggdrasil.native_knowledge_activation import (
        PINNED_ROWS, PINNED_PACKED_SHA, open_installed_session)
    start = time.monotonic()
    path = Path(joint_path)
    require(path.is_file() and not path.is_symlink() and
            0 < path.stat().st_size <= 32*1024*1024, "JOINT_PATH")
    raw = path.read_bytes()
    report = inventory(raw, JOINT_SHA)
    require(report["native_checkpoint_sha256"] == NATIVE_SHA
            and report["retained_native_public_witnesses"] == 1025
            and report["trained_specialist_count"] == 4, "PINNED_ARCHIVE_STATE")
    native = valid_nested(raw)
    learned = NativeCumulativeLearner.restore(native, NATIVE_SHA)
    require(learned.checkpoint() == native, "REAL_NATIVE_RESTORE")
    shadow = FrozenNative(raw, native, learned)
    with open_installed_session(installed_session) as base:
        require(PINNED_ROWS == NFACTS and PINNED_PACKED_SHA == IMAGE_SHA
                and len(base._weights) == NFACTS, "HISTORICAL_IMAGE")
        first, last = tuple(base._weights.row_at(0)), tuple(base._weights.row_at(NFACTS-1))
        require(first != last and base.fact(*first)["witnessed"]
                and base.fact(*last)["witnessed"], "HISTORICAL_FACTS")
        facts = CumulativeNativeFacts(base)
        facts_raw = facts.checkpoint()
        bridge = TypedFactualReadoutBridge(
            shadow, facts, native_checkpoint_sha256=JOINT_SHA,
            facts_checkpoint_sha256=digest(facts_raw))
        rows = sorted([[list(first), [[0,0],[0,1]]],
                       [list(last), [[1,1],[1,0]]]], key=lambda item:item[0])
        bundle, expected = make_fixture_manifest(
            JOINT_SHA, facts.checkpoint_sha256, rows)
        proposal = ExplicitPublicViewProjection(bridge, bundle, expected)
        probes = {}
        for view in ((0,0),(0,1),(1,0),(1,1)):
            forecast = shadow.plan(view)
            require(shadow.plan(view) == forecast, "NATIVE_NONDETERMINISTIC")
            probes[str(view)] = digest(repr(forecast).encode("ascii"))
        for triple, view in ((first,(0,0)),(last,(1,1))):
            result = proposal.shadow_plan(*triple)
            require(result["classification"] == "SYNTHETIC_VIEW_PROPOSAL_ONLY"
                    and result["source_fact_kind"] == "HISTORICAL_STORED_QPQ"
                    and result["native_plan_called"] is True
                    and result["shadow_plan"] == shadow.plan(view)
                    and result["native_training_performed"] is False
                    and result["causal_observation_admitted"] is False,
                    "NO_KNOWLEDGE_CAUSAL_GAIN")
        unknown = proposal.shadow_plan(0xffffffff,0xffffffff,0xffffffff)
        require(unknown["classification"] == "ABSTAIN_UNKNOWN_FACT"
                and unknown["native_plan_called"] is False, "UNKNOWN_ABSTENTION")
        for operation in (proposal.observe_experience, proposal.stage):
            try:
                operation()
            except PermissionError:
                pass
            else:
                raise ValueError("YGG_KNOW06_WRITE_INTERFACE")
        require(shadow.checkpoint() == raw and learned.checkpoint() == native
                and facts.checkpoint() == facts_raw
                and base.fact(*first)["witnessed"] and base.fact(*last)["witnessed"],
                "STATE_OR_HISTORY_DRIFT")
        return {"schema":"yggdrasil.know06.real-native-cold-shadow.v1",
                "classification":"EXPERIMENTAL_ENGINEERING_ONLY",
                "historical_facts":NFACTS,"archived_joint_sha256":JOINT_SHA,
                "cold_restored_native_sha256":NATIVE_SHA,"native_cold_restore":True,
                "specialist_heads_cold_restored":False,
                "native_witnesses":1025,"historical_facts_proposed":2,
                "native_planner_views":4,"shadow_equals_native_control":True,
                "planner_readout_digests":probes,"unknown_abstains":True,
                "native_and_fact_checkpoints_unchanged":True,
                "new_real_facts":0,"new_training":0,"real_causal_grounding":False,
                "scientific_pass":False,"owner_canonical_model":"UNVERIFIED",
                "deployment":"NONE","elapsed_seconds_no_source_fetch":round(time.monotonic()-start,6)}
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--installed-session",type=Path,required=True)
    p.add_argument("--joint-checkpoint",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a = p.parse_args()
    receipt=prove(a.installed_session,a.joint_checkpoint)
    a.output.write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("KNOW06_NATIVE_COLD_SHADOW_PASS "+json.dumps({
        "native_sha":NATIVE_SHA,"n_facts":NFACTS,"science_pass":False},sort_keys=True))
if __name__=="__main__":
    main()

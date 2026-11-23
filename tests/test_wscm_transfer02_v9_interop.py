"""Source-free v7/v9 interoperability: exact pinned sources, no scored trial.

Requires native episode source at v9 Git blob 5a77232c..., sparse source at
1fda97c..., and read-only research wrapper at a29be47f.... Tests execute
on a reconstructed local overlay of two pinned Git source trees.
"""
import json
import unittest

from yggdrasil.native_episode_experience import NativeEpisodeExperience, SPARSE_FIXTURE_SCHEMA
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_sparse_operator_evidence import RECEIPT_SCHEMA as SPARSE_RECEIPT_SCHEMA, SOURCE_MODE as SPARSE_SOURCE_MODE
from yggdrasil.native_external_action_identity import RECEIPT_SCHEMA as EXTERNAL_RECEIPT_SCHEMA, SOURCE_MODE as EXTERNAL_SOURCE_MODE
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "research" / "contrib" / "chatgpt" / "WSCM-TRANSFER-02"))
from unrestricted_safe_readout_dev import propose_unrestricted_safe_composition as safe

STATES = ((0,0),(0,1),(1,0),(1,1))
FIRST = (0,1,1,0)
SECOND = (0,0,1,1)


def add_external(native, action, sig, source_start=1, limit=4):
    for i, view in enumerate(STATES[:limit]):
        req = {"public_view": list(view), "external_action_id": action}
        raw = canonical({"schema": EXTERNAL_RECEIPT_SCHEMA,
                         "source_mode": EXTERNAL_SOURCE_MODE,
                         "source_id": f"{source_start+i:064x}",
                         **req, "outcome": sig[i]})
        native = native.observe_external_fixture(req, raw, digest(raw))
    return native


def add_sparse(native, serial=1):
    req = {"public_view": [0,0,0,0], "external_action_id": 55551}
    raw = canonical({"schema": SPARSE_RECEIPT_SCHEMA,
                     "source_mode": SPARSE_SOURCE_MODE,
                     "source_id": f"{serial:064x}", **req, "outcome": 0})
    return native.observe_sparse_fixture(req, raw, digest(raw))


def trace(serial, state):
    x,y = state
    bit=FIRST[2*x+y]
    middle=(y,bit)
    return {"source_id": f"{serial:064x}", "public_view": [x,y],
            "first_outcome": bit, "second_public_view": list(middle),
            "second_outcome": SECOND[2*middle[0]+middle[1]]}


def readout(native):
    return safe(native, 1301, 22007,
                (trace(700, (0,1)),trace(701,(1,0))), [1,1])


class V9Interoperability(unittest.TestCase):
    def setUp(self):
        self.initial=NativeEpisodeExperience()
        both=add_external(self.initial,1301,FIRST,1)
        self.both=add_external(both,22007,SECOND,10)

    def test_v7_then_v9_readout_and_cold_restore(self):
        original=readout(self.both)
        staged=add_sparse(self.both)
        self.assertEqual(json.loads(staged.checkpoint())["schema"], SPARSE_FIXTURE_SCHEMA)
        self.assertEqual(readout(staged),original)
        cold=NativeEpisodeExperience.restore(staged.checkpoint(),digest(staged.checkpoint()))
        self.assertEqual(readout(cold),original)
        self.assertEqual(cold.checkpoint(),staged.checkpoint())
        self.assertEqual(original["status"],"ABSTAIN")
        self.assertEqual(original["reason"],"UNRESTRICTED_MAPPING_AMBIGUOUS")
        self.assertEqual(original["possible_next_bits"],[0,1])

    def test_v9_then_v7_reverse_order_cold_and_consolidation(self):
        sparse=add_sparse(self.initial)
        plus=add_external(sparse,1301,FIRST,100)
        plus=add_external(plus,22007,SECOND,110)
        self.assertEqual(readout(plus),readout(self.both))
        raw=plus.checkpoint()
        cold=NativeEpisodeExperience.restore(raw,digest(raw))
        self.assertEqual(cold.consolidate().checkpoint(),raw)
        self.assertEqual(readout(cold),readout(self.both))
        self.assertEqual(cold.observed_external_fixture_value((1,1),1301),FIRST[3])

    def test_readout_is_pure_and_does_not_change_native_binary_forecast(self):
        staged=add_sparse(self.both)
        raw=staged.checkpoint()
        native_forecast=staged.forecast((0,0),0)
        baseline_hash=staged.info()["state_sha256"]
        result=readout(staged)
        self.assertEqual(staged.checkpoint(),raw)
        self.assertEqual(staged.forecast((0,0),0),native_forecast)
        self.assertEqual(staged.info()["state_sha256"],baseline_hash)
        for flag in ("action_authorized","scientific_gain_verified",
                     "structural_chain_authenticated", "native_state_updated"):
            self.assertFalse(result[flag])
        self.assertEqual(result["source_mode"],"engineering_fixture_only")

    def test_sparse_fixture_is_independent_and_non_authoritative(self):
        staged=add_sparse(self.both)
        raw=staged.checkpoint()
        info=staged.info()
        self.assertEqual(info["sparse_fixture_count"],1)
        self.assertEqual(info["external_action_fixture_count"],8)
        value=staged.sparse_fixture_forecast([0,0,0,0],55551)
        self.assertFalse(value["action_authorized"])
        self.assertFalse(value["scientific_gain_verified"])
        self.assertEqual(staged.checkpoint(),raw)

    def test_renamed_external_action_abstains_despite_sparse_fixture(self):
        staged=add_sparse(self.both)
        partial=add_external(staged,90017,SECOND,1000,3)
        self.assertIsNone(partial.observed_external_fixture_value((0,0),90017))
        result=safe(partial,1301,90017,
                    (trace(700,(0,1)),trace(701,(1,0))),[1,1])
        self.assertEqual(result["status"],"ABSTAIN")
        self.assertEqual(result["reason"],"PRIMITIVE_NOT_FULLY_WITNESSED")
        self.assertEqual(partial.info()["sparse_fixture_count"],1)

    def test_hidden_phase_rejected_after_both_envelopes(self):
        staged=add_sparse(self.both)
        raw=staged.checkpoint()
        request={"public_view":[0,0],"external_action_id":1301}
        forged=canonical({"schema":EXTERNAL_RECEIPT_SCHEMA,
                          "source_mode":EXTERNAL_SOURCE_MODE,
                          "source_id":"f"*64,**request,"outcome":0,"phase":"hidden"})
        with self.assertRaises(ValueError):
            staged.observe_external_fixture(request,forged,digest(forged))
        self.assertEqual(staged.checkpoint(),raw)

if __name__=="__main__":
    unittest.main()

"""CUE-01 frozen tests for source-blind retrieval from native causal memory."""
from __future__ import annotations

import importlib.util
import inspect
import json
from pathlib import Path
import subprocess
import sys
import unittest

from yggdrasil.native_action_cue_router import (
    ALL_ACTIONS, MAX_PUBLIC_CUES, propose, select,
)
from yggdrasil.native_cumulative_action_bank import NativeCumulativeActionBank
from yggdrasil.native_intervention_repair import digest
from yggdrasil.public_causal_cells import PublicCausalCells

ROOT=Path(__file__).resolve().parents[1]
DEV=ROOT/"research/contrib/chatgpt/CUE-01/dev.py"
sp=importlib.util.spec_from_file_location("cue01_test_reused_source",DEV)
d=importlib.util.module_from_spec(sp)
sp.loader.exec_module(d)


class CueRetrievalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank,cls.separate,cls.data_sha=d.build_bank()

    def test_exact_native_16slot_capacity_and_12_reusable(self):
        self.assertEqual(self.bank.stored_slots,tuple(range(12)))
        self.assertLessEqual(self.bank.checkpoint_bytes,262144)
        self.assertEqual(PublicCausalCells.ACTIVE_SLOTS,7)

    def test_no_exposed_target_identity_in_router_interface(self):
        self.assertEqual(tuple(inspect.signature(select).parameters),("bank","public_cues"))
        self.assertEqual(tuple(inspect.signature(propose).parameters),("bank","public_cues"))
        with open(inspect.getsourcefile(select),encoding="utf-8") as fd:
            native=fd.read()
        self.assertNotIn("import study",native)
        self.assertNotIn("import world",native)
        self.assertNotIn("true_step",native)
        self.assertNotIn("world_id",native)
        self.assertNotIn("env.intervene",native)

    def test_ambiguous_empty_cues_cannot_select_a_task(self):
        v=select(self.bank,[])
        self.assertEqual(v["classification"],"AMBIGUOUS_MEMORY_ABSTAIN")
        self.assertIsNone(v["provisional_slot"])
        self.assertEqual(len(v["remaining_slots"]),12)
        self.assertFalse(v["learned_task_identity_verified"])

    def test_empty_bank_does_not_hallucinate_relations(self):
        v=select(NativeCumulativeActionBank(),[])
        self.assertEqual(v["classification"],"NO_STORED_RELATIONSHIPS_ABSTAIN")
        p=propose(NativeCumulativeActionBank(),[])
        self.assertEqual(p["classification"],"NO_MORE_SAFE_PROBES")

    def test_strict_probe_count(self):
        with self.assertRaisesRegex(ValueError,"CUE01_PUBLIC_CUE_BUDGET"):
            select(self.bank,[[i,0,0] for i in range(9)])
        self.assertEqual(MAX_PUBLIC_CUES,8)

    def test_duplicate_action_feedback_denied(self):
        with self.assertRaisesRegex(ValueError,"CUE01_REPLAYED_ACTION_CUE"):
            select(self.bank,[(0,0,0),(0,0,1)])

    def test_untyped_and_hidden_cues_denied(self):
        for invalid in [[(0,0,True)],[(0,0,2)],[(True,0,0)],
                        [(0,True,0)],[(16,0,0)],[(0,3,0)],
                        [(0,0,0,"hidden")],["world-3"],
                        [{"context":0,"world_id":3}]]:
            with self.assertRaises(ValueError):select(self.bank,invalid)

    def test_no_source_or_task_information_entered_into_proposal(self):
        proposal=propose(self.bank,[])
        self.assertEqual(proposal["classification"],"PUBLIC_PROBE_PROPOSED_NOT_EXECUTED")
        self.assertIn(proposal["context"],range(16))
        self.assertIn(proposal["action"],(0,1))
        self.assertNotIn("world_id",proposal)
        self.assertNotIn("true_slot",proposal)
        self.assertFalse(proposal["native_accepted"])

    def test_proposal_is_deterministic_and_read_only(self):
        raw=self.bank.checkpoint()
        self.assertEqual(propose(self.bank,[]),propose(self.bank,[]))
        self.assertEqual(self.bank.checkpoint(),raw)

    def test_cold_restored_bank_same_public_action_choice(self):
        restored=NativeCumulativeActionBank.restore(
            self.bank.checkpoint(),self.bank.checkpoint_sha256)
        self.assertEqual(select(self.bank,[]),select(restored,[]))
        self.assertEqual(propose(self.bank,[]),propose(restored,[]))

    def test_provisional_never_accepts_or_authenticates_a_source(self):
        decision=select(self.bank,[])
        for forbidden in ("native_accepted","scientific_pass",
                          "write_to_accepted_model","learned_task_identity_verified"):
            self.assertIs(decision[forbidden],False)
        self.assertEqual(decision["source_authenticity"],
                         "UNVERIFIED_PUBLIC_OBSERVATION_CLAIM")

    def test_wrong_cues_cannot_install_or_repair_native_memory(self):
        raw=self.bank.checkpoint()
        select(self.bank,[(0,0,1)])
        propose(self.bank,[(0,0,1)])
        self.assertEqual(self.bank.checkpoint(),raw)

    def test_source_provenance_does_not_gain_authenticity_from_sha(self):
        self.assertRegex(self.data_sha,r"^[0-9a-f]{64}$")
        self.assertFalse(select(self.bank,[])["native_accepted"])

    def test_independent_exact_symbolic_reference_sees_identical_candidates(self):
        first=propose(self.bank,[])
        x,a=first["context"],first["action"]
        outcome=d.study.ComputationalEnvironment(0).intervene(x,a)
        cues=[(x,a,outcome)]
        native=select(self.bank,cues)
        symbolic, candidates=d.symbolic_decide(self.separate,cues)
        self.assertIsNone(symbolic)
        self.assertEqual(native["remaining_slots"],list(candidates))

    def test_protected_first_use_always_denied(self):
        p=subprocess.run([sys.executable,str(DEV),"--primary"],
                         capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0)
        self.assertIn("CUE01 SCIENTIFIC FIRST USE DISARMED",p.stderr)

    def test_all_32_public_actions_well_typed_and_unique(self):
        self.assertEqual(len(ALL_ACTIONS),32)
        self.assertEqual(len(set(ALL_ACTIONS)),32)
        self.assertEqual(ALL_ACTIONS[0],(0,0))
        self.assertEqual(ALL_ACTIONS[-1],(15,1))

    def test_frozen_development_known_worlds_strong_controls_and_unknowns(self):
        v=d.run()
        self.assertEqual(v["known_worlds"],12)
        self.assertEqual(v["negative_out_of_family_worlds"],4)
        self.assertEqual(v["max_paid_public_probes_per_episode"],8)
        self.assertEqual(v["policies"]["active"],v["policies"]["strong_symbolic"])
        self.assertEqual(v["policies"]["active"]["wrong"],0)
        self.assertTrue(v["native_memory_unchanged"])
        self.assertEqual(v["scientific_first_use_consumed"],0)
        self.assertFalse(v["accepted_native_changed"])

if __name__=="__main__":
    unittest.main()

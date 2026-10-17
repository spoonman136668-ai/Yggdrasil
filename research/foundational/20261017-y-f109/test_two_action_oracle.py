"""Y-F109: frozen native two-action study with actual one-action controls."""
import importlib.util
import inspect
import sys
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("yf109_two_action_test",
    HERE/"two_action_oracle.py")
m=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=m
spec.loader.exec_module(m)

class F109NativeContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg,cls.f108,cls.f104,cls.f102,cls.native=m.load()
        cls.pack=cls.native.codec()
        cls.source,cls.q,cls.id=cls.f102.episode(
            cls.native,-22001,-131,"raw",0)

    def test_frozen_protocol_and_unmodified_parent(self):
        self.assertEqual(m.gitblob(HERE/"prereg.json"),m.FREEZE)
        self.assertEqual(m.gitblob(HERE.parent/"20261017-y-f108"/"oracle.py"),
                         m.F108_BLOB)
        self.assertEqual(m.CHECKPOINTS,(11,23,35,47,59))
        self.assertEqual(m.OFFSETS,(1,8))

    def test_future_query_absent_from_native_online_implementation(self):
        self.assertEqual(tuple(inspect.signature(m.fixed_prefixes).parameters),
                         ("native","pack","stream"))
        self.assertEqual(tuple(inspect.signature(
            self.native._f60_step).parameters),("memory","event","packing"))
        self.assertEqual(tuple(inspect.signature(
            self.f108.candidate_states).parameters),
            ("native","pack","memory","event","t","cap"))

    def test_two_arrival_orders_same_answer_and_path(self):
        self.assertEqual(len(self.source),72)
        self.assertEqual(
            self.f104.source_path(self.source,self.q),
            self.f104.source_path(tuple(reversed(self.source)),self.q))
        with self.assertRaises(ValueError):
            self.native.source(-22001,-131)

    def test_frozen_F60_prefix_and_final_match_direct(self):
        pref,terminal=m.fixed_prefixes(self.native,self.pack,self.source)
        self.assertEqual(len(pref),72)
        mem=()
        for i,event in enumerate(self.source):
            self.assertEqual(pref[i],mem)
            mem=self.native._f60_step(mem,event,self.pack)
        self.assertEqual(mem,terminal)
        self.assertLessEqual(len(mem)*12,144)

    def test_one_new_world_honest_two_action_counterfactuals(self):
        world=m.eval_world(self.f108,self.native,self.pack,
                          self.source,self.q,self.id,"raw")
        self.assertEqual(len(world["windows"]),10)
        for w in world["windows"]:
            self.assertEqual(w["second_t"]-w["t"],w["offset"])
            self.assertIn(w["offset"],(1,8))
            self.assertGreaterEqual(w["first_native_states"],1)
            self.assertEqual(len(w["exact_legal_pair_outcomes"]),
                             w["legal_pair_count"])
            self.assertGreater(w["legal_pair_count"],0)
            self.assertTrue(w["source_native_144B_original_F60"])
            self.assertTrue(w["no_answer_or_future_access_in_online_controller"])
            for o in w["exact_legal_pair_outcomes"]:
                self.assertIn(o["final_correct"],(0,1))
                self.assertLessEqual(o["final_native_records"],12)
                self.assertEqual(len(o["final_native_memory_sha256"]),64)
            if w["strictly_coordinated_two_action_synergy"]:
                self.assertTrue(w["two_action_any_rescue"])
                self.assertFalse(w["either_single_action_rescue"])
                self.assertFalse(w["fixed_terminal_correct"])

    def test_two_actions_never_less_capable_than_single_initial(self):
        w=m.eval_world(self.f108,self.native,self.pack,
                       self.source,self.q,self.id,"raw")
        for c in w["windows"]:
            if c["single_action_at_first_rescue"]:
                self.assertTrue(c["two_action_any_rescue"])
            if c["single_action_at_second_rescue"]:
                self.assertTrue(c["two_action_any_rescue"])

    def test_summary_counts_windows_and_full_native_budget(self):
        w=m.eval_world(self.f108,self.native,self.pack,
                       self.source,self.q,self.id,"raw")
        stats=m.aggregate([w])
        self.assertEqual(stats["worlds"],1)
        self.assertEqual(stats["windows"],10)
        self.assertLessEqual(stats["strict_two_action_synergies"],
                             stats["any_two_action_rescues"])

    def test_fail_closed_on_invalid_sha_and_duplicate_source(self):
        with self.assertRaises(m.Invalid):
            m.evaluate("untrusted")
        with self.assertRaises(m.Invalid):
            m.fixed_prefixes(self.native,self.pack,self.source[:2])

if __name__=="__main__":unittest.main()

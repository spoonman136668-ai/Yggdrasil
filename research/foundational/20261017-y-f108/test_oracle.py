"""F108 information availability, capacity stress and real native oracle tests."""
import importlib.util
import inspect
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location(
    "yf108_native_oracle_test",HERE/"oracle.py")
m=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=m
spec.loader.exec_module(m)

class F108Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg,cls.f107,cls.f104,cls.f102,cls.native=m.load()
        cls.pack=cls.native.codec()
        cls.pairs,cls.identity=m.pair(cls.f102,cls.native,-21001,-121,0,
                                      "rolling_interleaved_hubs")

    def test_frozen_prereg_first_and_unchanged_source_parents(self):
        self.assertEqual(m.gitblob(HERE/"prereg.json"),m.FREEZE)
        self.assertEqual(m.gitblob(HERE.parent/"20261017-y-f107"/"signed_role_diagnosis.py"),
                         m.F107_BLOB)
        self.assertEqual(m.gitblob(HERE.parent/"20261017-y-f102"/"delayed_credit.py"),
                         m.F102_BLOB)

    def test_new_negative_unregistered_native_sources(self):
        self.assertEqual(m.CAPS,(4,8,12))
        self.assertEqual(m.MODES,("raw","reverse_arrival"))
        self.assertEqual(len(self.pairs),2)
        raw,rev=self.pairs
        self.assertEqual(raw[0],"raw")
        self.assertEqual(rev[0],"reverse_arrival")
        self.assertEqual(raw[1],tuple(reversed(rev[1])))
        self.assertEqual(raw[2],rev[2])
        self.assertEqual(len(raw[1]),72)
        with self.assertRaises(ValueError):
            self.native.source(-21001,-121)
        with self.assertRaises(m.BadSource):
            m.pair(self.f102,self.native,761000,1460,0,
                   "rolling_interleaved_hubs")

    def test_full_source_public_answer_path_in_both_orderings(self):
        raw,rev=self.pairs
        a=m.path_public(self.f104,raw[1],raw[2])
        b=m.path_public(self.f104,rev[1],rev[2])
        self.assertEqual((a[0],a[1]),(b[0],b[1]))
        self.assertEqual(len(a[0]),len(a[1])+1)
        self.assertEqual(len(a[1]) in (4,6,8),True)

    def test_native_F60_at_full_twelve_records_unchanged(self):
        public=self.pairs[0][1]
        source=()
        verified=()
        for t,event in enumerate(public):
            source=self.native._f60_step(source,event,self.pack)
            verified=m.step(self.native,self.pack,verified,event,12)
            self.assertEqual(source,verified)
            self.native._valid_memory(verified,self.pack)
        self.assertEqual(len(source)<=12,True)

    def test_reduced_memory_explicitly_postevent_adapter_not_real_F60(self):
        public=self.pairs[0][1]
        for cap in (4,8):
            memory=()
            for t,event in enumerate(public):
                memory=m.step(self.native,self.pack,memory,event,cap)
                self.assertLessEqual(len(memory),cap)
                self.native._valid_memory(memory,self.pack)
        with self.assertRaises(m.BadSource):
            m.trim((),13)

    def test_true_source_native_action_enumerator_contains_local_F60(self):
        public=self.pairs[0][1]
        for cap in m.CAPS:
            memory=()
            for t,event in enumerate(public[:30]):
                baseline,states=m.candidate_states(
                    self.native,self.pack,memory,event,t,cap)
                self.assertEqual(sum(mem==baseline for _,mem in states),1)
                self.assertTrue(all(len(s)<=cap for _,s in states))
                self.assertGreaterEqual(len(states),1)
                memory=baseline

    def test_online_interface_never_accepts_eventual_target(self):
        self.assertEqual(tuple(inspect.signature(m.step).parameters),
                         ("native","pack","mem","event","cap"))
        self.assertEqual(tuple(inspect.signature(m.candidate_states).parameters),
                         ("native","pack","memory","event","t","cap"))
        self.assertEqual(tuple(inspect.signature(m.finish).parameters),
                         ("native","pack","mem","suffix","cap"))
        self.assertEqual(tuple(inspect.signature(m.analyze_episode).parameters),
                         ("f104","f102","native","pack","stream","q","cap",
                          "mode","source_id"))

    def test_single_real_episode_uses_six_full_counterfactual_checkpoints(self):
        mode,stream,q=self.pairs[0]
        c=m.analyze_episode(self.f104,self.f102,self.native,self.pack,
            stream,q,12,mode,self.identity)
        self.assertEqual(c["capacity_records"],12)
        self.assertLessEqual(c["native_persistent_bytes"],144)
        self.assertEqual(len(c["checkpoints"]),6)
        self.assertTrue(c["endpoint_answer_available_in_full_public_graph"])
        for row in c["checkpoints"]:
            self.assertGreaterEqual(row["legal_native_action_states"],1)
            self.assertEqual(len(row["candidate_outcomes"]),
                             row["legal_native_action_states"])
            self.assertEqual(sum(row[name] for name in (
                "proxy_true_positive","proxy_false_positive",
                "proxy_missed_rescue","proxy_true_negative")),1)
            self.assertTrue(row["online_fixed_controller_receives_only_prefix"])
            for option in row["candidate_outcomes"]:
                self.assertIn(option["true_terminal_correct"],(0,1))
                self.assertLessEqual(option["native_after_records"],12)
                self.assertLessEqual(option["native_after_records"]*12,144)

    def test_checkpoint_summary_counts_true_rescue_vs_proxy_separately(self):
        mode,stream,q=self.pairs[0]
        case=m.analyze_episode(self.f104,self.f102,self.native,self.pack,
            stream,q,4,mode,self.identity)
        s=m.summarize([case])
        self.assertEqual(s["world_count"],1)
        self.assertEqual(s["checkpoint_count"],6)
        self.assertEqual(sum(s[k] for k in (
           "proxy_true_positive","proxy_false_positive",
           "proxy_missed_rescue","proxy_true_negative")),6)
        self.assertLessEqual(case["native_persistent_bytes"],48)

    def test_invalid_source_head_and_changed_family_fail_closed(self):
        with self.assertRaises(m.BadSource):
            m.evaluate("fake")
        with self.assertRaises(m.BadSource):
            m.pair(self.f102,self.native,-21001,-121,0,
                   "delayed_public_joins")

if __name__=="__main__":unittest.main()

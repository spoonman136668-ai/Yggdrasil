"""F107 source-only signed direction equivariance, information and teacher checks."""
import importlib.util
import inspect
import sys
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location(
    "y_f107_signed_source_test", HERE/"signed_role_diagnosis.py")
m=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=m
spec.loader.exec_module(m)

class F107Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (cls.cfg,cls.f106,cls.f105,cls.f104,cls.parent,
         cls.f102,cls.native)=m.load()
        cls.pack=cls.native.codec()

    def test_first_precode_protocol_and_parent_science_identity(self):
        self.assertEqual(m.gitblob(HERE/"prereg.json"),m.PREREG_BLOB)
        self.assertEqual(m.gitblob(HERE.parent/"20261017-y-f106"/"identifiability.py"),
                         m.F106_BLOB)
        self.assertEqual(m.gitblob(HERE.parent/"20261017-y-f102"/"delayed_credit.py"),
                         m.F102_BLOB)

    def test_exact_new_paired_graphs_and_only_negative_seeds(self):
        pairs=[]
        for start,family,namespace in m.SOURCE:
            for i in range(8):
                c,source=m.paired_world(self.f102,self.native,
                                         start-i,family,namespace+i)
                self.assertEqual([x[0] for x in c],list(m.MODES))
                self.assertTrue(all(len(x[1])==72 for x in c))
                self.assertTrue(all(x[2]["start"]==c[0][2]["start"]
                                    and x[2]["answer"]==c[0][2]["answer"] for x in c))
                pairs.append(source)
        self.assertEqual(len(set(pairs)),16)
        self.assertTrue(all(start<0 and fam<0 for start,fam,_ in m.SOURCE))

    def test_single_edge_role_or_direction_bijection(self):
        original=((10,1,20),)
        q={"start":10,"ops":((1,1),),"answer":20}
        # transform operates on 72 edges; construct an actual new episode.
        sample,_=m.paired_world(self.f102,self.native,-20001,-111,0)
        raw=sample[0]
        for mode,stream,question in sample:
            self.assertEqual(len(stream),72)
            self.assertEqual(question["start"],raw[2]["start"])
            self.assertEqual(question["answer"],raw[2]["answer"])
            for (u,role,v),(a,newrole,b) in zip(raw[1],stream):
                inv=mode in ("edge_direction_only","both")
                ren=mode in ("role_only","both")
                self.assertEqual((a,b),((v,u) if inv else (u,v)))
                self.assertEqual(newrole,m.role(role) if ren else role)
            for (role,direction),(newrole,newdirection) in zip(
                    raw[2]["ops"],question["ops"]):
                self.assertEqual(newrole,m.role(role) if mode in ("role_only","both")
                                 else role)
                self.assertEqual(newdirection,-direction if mode in
                                 ("edge_direction_only","both") else direction)

    def test_signed_native_code_mapping_and_round_trip(self):
        self.assertEqual(m.signed_role(0,"both"),5)
        self.assertEqual(m.signed_role(3,"role_only"),1)
        self.assertEqual(m.signed_role(3,"edge_direction_only"),2)
        self.assertEqual(m.signed_role(7,"both"),2)
        self.assertEqual(m.signed_role(0,"raw"),0)
        with self.assertRaises(m.Invalid):m.signed_role(8,"raw")

    def test_full_public_answer_path_is_not_lost_by_any_transform(self):
        for first,family,namespace in m.SOURCE:
            case,_=m.paired_world(self.f102,self.native,
                                  first,family,namespace)
            original_nodes,original_codes=self.f104.source_path(case[0][1],case[0][2])
            for mode,stream,q in case:
                nodes,codes=m.source_path_contract(
                    self.f104,case[0][2],original_nodes,original_codes,
                    stream,q,mode)
                self.assertEqual(nodes,original_nodes)
                self.assertEqual(len(codes),len(original_codes))

    def test_native_F60_real_144B_actions_and_credit_accounting(self):
        pairs,_=m.paired_world(self.f102,self.native,-20001,-111,0)
        for mode,stream,q in pairs:
            nodes,codes=self.f104.source_path(stream,q)
            spans=self.f104.subpaths(nodes,codes)
            memory,checkpoints=m.native_trace(
                self.f105,self.f104,self.native,self.pack,stream,spans)
            self.native._valid_memory(memory,self.pack)
            self.assertLessEqual(len(memory)*12,144)
            self.assertEqual(len(checkpoints),6)
            for c in checkpoints:
                self.assertEqual(c["legal_actions"],
                    c["positive_direct"]+c["negative_direct"]+c["neutral_direct"])
                self.assertEqual(c["legal_actions"],
                    c["positive_eight_event"]+c["negative_eight_event"]+
                    c["neutral_eight_event"])
                self.assertLessEqual(c["eight_event_suffix_length"],8)
                self.assertTrue(c["online_memory_action_no_query_seen"])

    def test_no_online_interface_accepts_future_answer_or_path(self):
        self.assertEqual(tuple(inspect.signature(m.native_trace).parameters),
                         ("f105","f104","native","pack","stream","spans"))
        # spans are offline teacher-only in native_trace: F60 step itself
        # accepts public event, memory, current index and native codec.
        self.assertEqual(tuple(inspect.signature(
            self.native._f60_step).parameters),
            ("memory","event","packing"))

    def test_empty_bad_mode_and_invalid_head_fail_closed(self):
        with self.assertRaises(m.Invalid):
            m.transform((),{"start":0,"ops":(),"answer":0},"raw")
        with self.assertRaises(m.Invalid):
            m.signed_role(0,"unknown")
        with self.assertRaises(m.Invalid):
            m.evaluate("not-a-source-sha")

    def test_full_frozen_study_retains_true_mode_splits_and_no_science_claim(self):
        d=m.evaluate("a"*40)
        self.assertEqual(d["raw_base_cases"],16)
        self.assertEqual(d["paired_mode_cases"],64)
        self.assertEqual(len(d["blocks"]),2)
        self.assertEqual(set(d["summary_by_mode"]),set(m.MODES))
        self.assertTrue(d["checked_source_path_bijective_for_all_modes"])
        self.assertTrue(d["same_underlying_graph_for_each_mode"])
        self.assertTrue(d["no_F102_F106_consumed_diagnostics_reused"])
        self.assertTrue(d["all_future_query_and_label_access_offline_only"])
        self.assertTrue(d["no_new_online_policy_or_fitted_parameters"])
        self.assertFalse(d["source_information_loss"])
        self.assertFalse(d["scientific_acceptance"])
        self.assertFalse(d["Codex_used"])
        self.assertEqual(d["accepted_ref_mutations"],0)
        self.assertEqual(len(d["teacher_collapse_modes"])<=4,True)
        for block in d["blocks"]:
            self.assertEqual(block["cases"],8)
            for pair in block["paired_results"]:
                self.assertEqual(len(pair["modes"]),4)
                for mode in m.MODES:
                    x=pair["modes"][mode]
                    self.assertTrue(x["source_answer_path_preserved"])
                    self.assertEqual(len(x["checkpoints"]),6)
                    self.assertLessEqual(x["native_final_memory_records"]*12,144)
                    self.assertEqual(x["direct"]["positive"]+
                       x["direct"]["negative"]+x["direct"]["neutral"],
                       x["direct"]["action_labels"] )

if __name__=="__main__":unittest.main()

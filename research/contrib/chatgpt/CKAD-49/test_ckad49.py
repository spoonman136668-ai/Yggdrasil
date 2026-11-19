"""CKAD49 fixture-only engineering tests, no scored development seeds."""
from __future__ import annotations
import importlib.util
import unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("ckad49_local_fixture",HERE/"campaign.py")
M=importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

class CKAD49Fixture(unittest.TestCase):
    def test_prereg_and_no_scientific_first_use_from_fixtures(self):
        self.assertEqual(M.PREREG,"63d9ff3b5cabbe932f70ad5452c86d24cfb74c7f")
        self.assertEqual(M.DEV,(49111,49112))
        self.assertEqual((M.OLD,M.NOVEL_END,M.TOTAL),(80,192,256))
        self.assertEqual(len(M.STRUCTURES),16)
        self.assertEqual(len(M.RESTRICTED),4)
        self.assertTrue(set(M.DEV).isdisjoint(M.PILOT+M.PRIMARY))
        for seed in (*M.PILOT,*M.PRIMARY,48111,0):
            with self.assertRaisesRegex(ValueError,"CKAD49_ONLY_REGISTERED_DEV"):
                M.run(seed)
        with self.assertRaisesRegex(ValueError,"CKAD49_ONLY_REGISTERED_DEV"):
            M.source(M.PRIMARY[0],0)

    def test_truly_unlisted_exception_and_new_additive_operator(self):
        source0,w0=M.source(0,0)
        source1,w1=M.source(0,1)
        self.assertEqual((w0["operator"],w0["mask"]),("add",1))
        self.assertEqual((w1["operator"],w1["mask"]),("xor",7))
        self.assertNotIn(("add",1),M.RESTRICTED)
        self.assertNotIn(("xor",7),M.RESTRICTED)
        self.assertEqual(M.source(0,0),(source0,w0))
        self.assertNotEqual(source0,source1)
        self.assertEqual(len(source0),256)
        self.assertEqual(len({id for id,row in source0}),256)
        self.assertTrue(all(r["a1"] in (0,1) and r["a2"] in (0,1)
                            for _,r in source0[:80]))
        self.assertTrue(all(r["a1"] in (2,3) and r["a2"] in (2,3)
                            for _,r in source0[80:192]))
        self.assertTrue(all(r["a1"] in (0,1) and r["a2"] in (0,1)
                            for _,r in source0[192:]))
        self.assertNotEqual(M.effect("xor",1,3),M.effect("add",1,3))

    def test_eight_source_model_instances_learn_and_cold_restore(self):
        events,_=M.source(0,0)
        for obj in (M.Structural("discovered_feature_native"),
                    M.Structural("exact_full_BMA"),
                    M.Structural("old_XOR_restricted"),M.Tabular()):
            for t,event in enumerate(events):
                if t in M.PROBES:
                    before=obj.checkpoint()
                    p=obj.forecast(3,2,3)
                    self.assertTrue(0<p<1)
                    self.assertEqual(obj.checkpoint(),before)
                obj.observe(*event)
            self.assertEqual(obj.n,256)
            self.assertEqual(sum(sum(z) for z in obj.reward),256)
            raw=obj.checkpoint()
            cold=type(obj).restore(raw,M.sha(raw))
            self.assertEqual(cold.checkpoint(),raw)
            self.assertEqual(cold.forecast(3,2,3),obj.forecast(3,2,3))
            self.assertTrue(M.custody(obj,events[-1],{0,1,2,3})["cold_exact"])
            self.assertEqual(obj.checkpoint(),raw)

    def test_source_trained_feature_is_discovered_without_true_mapping(self):
        for world in (0,1):
            episodes,private=M.source(0,world)
            candidate=M.Structural("discovered_feature_native")
            full=M.Structural("exact_full_BMA")
            for episode in episodes:
                candidate.observe(*episode)
                full.observe(*episode)
            selected,p=candidate.selected()
            self.assertEqual(selected,(private["operator"],private["mask"]))
            self.assertGreater(p,.99)
            self.assertEqual(candidate.counts,full.counts)
            self.assertEqual(candidate.reward,full.reward)
            self.assertEqual(candidate.ledger,full.ledger)

    def test_same_latent_structure_used_for_both_interventions(self):
        events,_=M.source(0,1)
        model=M.Structural("exact_full_BMA")
        for event in events[:120]:model.observe(*event)
        before=model.checkpoint()
        reward=[(yes+1)/(no+yes+2) for no,yes in model.reward]
        expected=sum(w*p1*p2*reward[t] for i,w in enumerate(model.weights)
                     for mid,p1 in enumerate(model.transition(i,1,2))
                     for t,p2 in enumerate(model.transition(i,mid,3)))
        self.assertAlmostEqual(expected,model.forecast(1,2,3),delta=1e-13)
        self.assertEqual(model.checkpoint(),before)

    def test_new_operator_helps_on_additive_source_vs_old_XOR_control(self):
        events,secret=M.source(0,0)
        candidate=M.Structural("discovered_feature_native")
        old=M.Structural("old_XOR_restricted")
        for event in events:
            candidate.observe(*event)
            old.observe(*event)
        l_c=l_old=0
        for s in range(4):
            for a in range(4):
                for b in range(4):
                    truth=M.private_query(secret,s,a,b)
                    l_c+=M.expected_brier(candidate.forecast(s,a,b),truth)
                    l_old+=M.expected_brier(old.forecast(s,a,b),truth)
        self.assertLess(l_c,l_old)

    def test_out_of_grammar_state_action_lookup_favors_unrestricted_tabular(self):
        truth=[[1,3,0,2],[1,2,3,0],[0,3,2,1],[2,1,0,3]]
        model=M.Structural("discovered_feature_native")
        control=M.Tabular()
        for t in range(256):
            s=t%4;a=(t//4)%4;s1=truth[s][a]
            b=(a+1)%4;s2=truth[s1][b]
            row={"s0":s,"a1":a,"s1":s1,"a2":b,"s2":s2,
                 "y":int(s2 in (0,3))}
            ident=M.sha(f"ckad49-out-of-grammar-only|{t}")
            model.observe(ident,row)
            control.observe(ident,row)
        score_model=score_tabular=0
        for s in range(4):
            for a in range(4):
                outcome=truth[s][a]
                score_model+=sum(w*model.transition(i,s,a)[outcome]
                                 for i,w in enumerate(model.read_weights()))
                score_tabular+=control.transition(s,a)[outcome]
        self.assertGreater((score_tabular-score_model)/16,.2)
        self.assertEqual(model.n,control.n)

    def test_duplicate_conflict_rejected_without_changing_source(self):
        events,_=M.source(0,1)
        model=M.Structural("discovered_feature_native")
        for event in events[:101]:model.observe(*event)
        before=model.checkpoint()
        self.assertIs(model.observe(*events[100]),model)
        self.assertEqual(before,model.checkpoint())
        ident,row=events[100]
        with self.assertRaisesRegex(ValueError,"CKAD49_SOURCE_ID_CONFLICT"):
            model.observe(ident,dict(row,y=1-row["y"]))
        self.assertEqual(before,model.checkpoint())
        with self.assertRaisesRegex(ValueError,"CKAD49_COLD_SHA"):
            M.Structural.restore(before,"0"*64)
        with self.assertRaisesRegex(ValueError,"CKAD49_FOUR_STATE_OR_ACTION"):
            model.forecast(4,0,2)

    def test_frozen_science_screen_rejects_weak_effect(self):
        def fake(seed,c=.12,tab=.145,old=.165,exact=.122,
                 early=.125,cold=.12,correct=True):
            groups={}
            for phase in M.PHASES:
                candidate=(early if phase=="early_novel" else
                           cold if phase=="cold_return" else c)
                groups[phase]={"expected_brier":{
                    "discovered_feature_native":candidate,
                    "exact_full_BMA":exact,"unrestricted_tabular":tab,
                    "old_XOR_restricted":old,"uniform_negative":.25}}
            receipts=[{"arm":"discovered_feature_native" if i==0 else "unrestricted_tabular",
                       "cold_exact":True,"old_source_exact":True,
                       "duplicate_idempotent":True,"conflict_atomic":True,
                       "four_public_actions_witnessed":True,
                       "correct_feature_operator_by_last_probe":correct} for i in range(8)]
            return {"seed":seed,"model_receipts":receipts,"groups":groups}
        a,b=[fake(s) for s in M.DEV]
        self.assertEqual(M.classify([a,b]),"DEV_FEASIBLE_NOT_SCIENTIFIC")
        self.assertEqual(M.classify([a,fake(M.DEV[1],c=.14)]),"DEV_NO_GO")
        self.assertEqual(M.classify([a,fake(M.DEV[1],old=.13)]),"DEV_NO_GO")
        self.assertEqual(M.classify([a,fake(M.DEV[1],early=.15)]),"DEV_NO_GO")
        self.assertEqual(M.classify([a,fake(M.DEV[1],correct=False)]),"DEV_NO_GO")
        with self.assertRaisesRegex(AssertionError,"CKAD49_DEV_ORDER"):
            M.classify([b,a])

if __name__=="__main__":unittest.main()

"""WSP134 new-family public development: custody, controls and honest negatives."""
import json
from unittest import TestCase
from unittest.mock import patch
from types import SimpleNamespace
import source as S
import learner as N
import controls as C
import experiment as E

class OpenStructureTests(TestCase):
    def test_no_protected_or_unregistered_source_access_before_rng(self):
        self.assertEqual(len(S.KNOWN),64)
        self.assertEqual(len(S.UNFAMILIAR),32)
        self.assertEqual(len(S.TRANSFER),16)
        self.assertFalse(S.ALLOWED & S.PROTECTED)
        with patch.object(S.random,"Random",side_effect=AssertionError("PROTECTED_RANDOM_CALLED")):
            for seed in (131000,160000,169000,170000,171000,172000,173000,
                         174064,174800,174863,175032,175800,175863,
                         176016,176800,176863,177000,177063,
                         True,False,-1,"174000"):
                with self.subTest(seed=seed):
                    with self.assertRaises(PermissionError):S.world(seed)
                    with self.assertRaises(PermissionError):S._truth(seed)
                    with self.assertRaises(PermissionError):S.open_original(seed)
        self.assertNotIn("source",N.__dict__)
        self.assertNotIn("source",C.__dict__)
        self.assertNotIn("learner",C.__dict__)

    def test_source_budget_and_view_custody(self):
        v=S.world(174000)
        self.assertFalse(hasattr(v,"seed"))
        self.assertFalse(hasattr(v,"family"))
        self.assertFalse(hasattr(v,"truth"))
        self.assertFalse(hasattr(v,"hidden_operator"))
        self.assertEqual(len(v.records),64)
        self.assertEqual(len(v.legal),64)
        c=S.Custodian(v,174000)
        with self.assertRaises(PermissionError):
            S.Custodian(v,175000)
        effect=c.query(v.subject(0))
        self.assertIn(effect.effect,(0,1))
        with self.assertRaises(PermissionError):c.query(v.subject(0))
        for x in range(1,32):c.query(v.subject(x))
        self.assertEqual(len(c.held()),32)
        with self.assertRaises(PermissionError):c.query(v.subject(32))
        self.assertEqual(c.score_once({s:None for s,x in c.held()})["abstained"],32)
        with self.assertRaises(PermissionError):c.score_once({})
        t=S.world(176000)
        self.assertEqual(t.law_id,v.law_id)
        self.assertEqual(t.cohort,"transfer")
        self.assertEqual(len(t.legal),0)
        z=S.Custodian(t,176000)
        with self.assertRaises(PermissionError):z.query(t.subject(0))
        self.assertEqual(z.score_once({s:None for s,x in z.held()})["source_calls"],0)

    def test_independent_symbolic_and_numerical_action_policy_and_forgery(self):
        v=S.world(175000)
        a=N.DirectStructuralGrowth()
        b=C.IndependentSymbolicTree()
        c=S.Custodian(v,175000)
        remaining=set(v.legal)
        for _ in range(6):
            subject=a.choose(v,remaining)
            self.assertEqual(subject,b.choose(v,remaining))
            remaining.remove(subject)
            evidence=c.query(subject)
            a.observe(v,evidence)
            b.observe(v,evidence)
        for x in range(64):
            self.assertEqual(a.infer(v,v.subject(x)),b.infer(v,v.subject(x)))
        snapshot=a.snapshot()
        self.assertEqual(N.DirectStructuralGrowth.restore(snapshot,{v.law_id:v}).snapshot(),snapshot)
        obj=json.loads(snapshot)
        obj["payload"]["states"][str(v.law_id)]["nodes"][0][4]+=1
        with self.assertRaisesRegex(ValueError,"WSP134_SNAPSHOT_CHECKSUM_INVALID"):
            N.DirectStructuralGrowth.restore(N.canon(obj),{v.law_id:v})
        obj["sha256"]=N.digest(obj["payload"])
        with self.assertRaisesRegex(ValueError,"WSP134_FORGED_NUMERICAL_STATE"):
            N.DirectStructuralGrowth.restore(N.canon(obj),{v.law_id:v})

    def test_full_frozen_source_safe_experiment(self):
        result=E.run_development()
        print("WSP134_SOURCE_SAFE_RESULT_JSON="+S.canon(result))
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["original_first_use"])
        self.assertFalse(result["native_admission"])
        self.assertTrue(result["same_action_independent_symbolic_parity"])
        self.assertTrue(result["old_structures_unchanged"])
        self.assertTrue(result["cold_restore_pass"])
        self.assertEqual(result["paid_actions_per_world_per_arm"],32)
        self.assertEqual(result["total_target_actions_per_arm"],3072)
        self.assertEqual(result["worlds"],{"known":64,"unfamiliar":32,"transfer":16})
        self.assertEqual(result["transfer_exact_prediction_match"],1024)
        for group,count,calls in (("known",2048,2048),("unfamiliar",1024,1024),
                                  ("transfer",1024,0)):
            for arm in E.ARMS:
                z=result["scores"][group][arm]
                self.assertEqual(z["held"],count)
                self.assertEqual(z["source_calls"],calls)
                self.assertEqual(z["held"],z["correct"]+z["wrong_confident"]+z["abstained"])
            self.assertEqual(result["scores"][group]["DIRECT_GROW"],
                             result["scores"][group]["INDEPENDENT_SYMBOLIC"])
        self.assertIn(result["status"],("DEVELOPMENT_OPEN_STRUCTURE_SUPPORTED_WITHIN_GENERIC_SPLIT_PRIOR",
                                        "DEVELOPMENT_OPEN_STRUCTURE_NO_GO"))

"""AAI-09A source-only scientific boundary and custody; NO real science cohorts."""
import ast
import json
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import evaluate as ex
import models as m

class SourceCustody(unittest.TestCase):
    def test_disarmed_scientific_first_use(self):
        text=(HERE/"evaluate.py").read_text(encoding="utf8")
        self.assertIn('parser.error("AAI-09A SCIENTIFIC FIRST USE DISARMED',text)
        self.assertEqual(ex.PREREG,"d9e9f3f11d04cdcf99c5e5b1e0c7a5008e0c2026")
        self.assertFalse(json.loads((HERE/"prereg.json").read_text(encoding="utf8"))[
            "authority"]["AAI09A_scientific_first_use_authorized"])

    def test_synthetic_only_status(self):
        out=ex.source_only()
        self.assertEqual(out["phase"],"SOURCE_ONLY")
        self.assertFalse(out["scientific_first_use"])
        self.assertTrue(out["intact_A_after_B"])
        self.assertEqual(out["candidate_copy_decision_after_two_A"],2)

    def test_seeds_and_laws_frozen(self):
        self.assertEqual(ex.BUDGETS,(0,1,2,4))
        self.assertEqual(len(ex.DEV),16)
        self.assertEqual(len(ex.TRANSFER),64)
        self.assertEqual(len(ex.NEGATIVE),32)
        self.assertEqual(len(ex.MECHANICAL),4)
        self.assertEqual(ex.LAWS["transfer"]["A"],(.90,.06,.04))
        self.assertEqual(ex.LAWS["transfer"]["B"],(.05,.47,.48))
        self.assertEqual(ex.TRAIN_PER_REGIME,32)
        self.assertEqual(ex.BOOTSTRAP_DRAWS,2048)

    def test_information_and_counterfactual_fairness(self):
        source=(HERE/"evaluate.py").read_text(encoding="utf8")
        self.assertIn('models=cold_restore(after_B)',source)
        self.assertIn('seed_of(world,"challenge",i)',source)
        self.assertNotIn('seed_of(world,"challenge",condition,i)',source)
        self.assertIn('assert a["actions"]==b["actions"]',source)
        self.assertIn('assert a["oracle"]["action"]==b["oracle"]["action"]',source)
        self.assertIn('m.learn(observation)',source)
        self.assertIn('sample=official_episode(law,seed_of(world,"eval",condition,budget),action)',source)

    def test_official_env_no_privileged_policy_access(self):
        source=(HERE/"evaluate.py").read_text(encoding="utf8")
        tree=ast.parse(source)
        forbidden={"unwrapped","get_planning_env","transition_matrix"}
        self.assertFalse(any(isinstance(n,ast.Attribute) and n.attr in forbidden for n in ast.walk(tree)))
        self.assertIn("change_notification=False",source)
        self.assertIn("delta_change_notification=False",source)
        self.assertIn("obs,_discarded_info=env.reset",source)

    def test_onehot_source_expected_world(self):
        self.assertEqual(ex.ACTIONS,{"RIGHT":2,"UP":3})
        self.assertEqual(ex.ONEHOT,((1.,0.,0.),(0.,1.,0.),(0.,0.,1.)))
        self.assertEqual(ex.MAP[2],"GFHFSFFG")
        self.assertEqual(list(ex.MECHANICAL),[887950,887951,887952,887953])
        self.assertTrue(set(ex.MECHANICAL).isdisjoint(ex.TRANSFER))

    def test_paired_bootstrap_is_deterministic(self):
        a=[1,0,0,1,0,1,1,1]
        b=[0,1,0,0,0,1,0,1]
        self.assertEqual(ex.paired_bootstrap(a,b),ex.paired_bootstrap(a,b))
        self.assertEqual(len(ex.paired_bootstrap(a,b)),2)
        self.assertLessEqual(*ex.paired_bootstrap(a,b))

if __name__=="__main__":
    unittest.main()

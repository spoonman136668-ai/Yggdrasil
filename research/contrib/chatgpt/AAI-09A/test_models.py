"""AAI-09A unit / synthetic mechanical tests. No science seeds, no upstream."""
import ast
import json
import math
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from models import (Beta,BOCPD,ProtectedBank,Recent,Stationary,
                    LOG_MARGIN,BOCPD_HAZARD,LOGISTIC_EPOCHS,
                    NAMES,MATCHED,create,checkpoint,cold_restore,
                    shared_observation,origin_marker,preserved_original,
                    recalled_original,canonical)

class FrozenModelTests(unittest.TestCase):
    def test_frozen_pre_first_use_design(self):
        p=json.loads((HERE/"prereg.json").read_text(encoding="utf8"))
        self.assertEqual(p["id"],"AAI-09A")
        self.assertFalse(p["authority"]["AAI09A_scientific_first_use_authorized"])
        self.assertEqual(p["candidate"]["parameter_freeze"]["scratch_block"],2)
        self.assertAlmostEqual(LOG_MARGIN,math.log(4))
        self.assertAlmostEqual(BOCPD_HAZARD,1/12)
        self.assertEqual(LOGISTIC_EPOCHS,1200)
        self.assertEqual(len(NAMES),11)
        self.assertEqual(len(MATCHED),8)

    def test_persistent_bank_and_intact_old_A(self):
        model=ProtectedBank(2)
        for _ in range(24):
            model.learn(True)
        marker=origin_marker(model)
        self.assertEqual(marker["id"],0)
        for _ in range(24):
            model.learn(False)
        self.assertEqual(len(model.cores),2)
        self.assertTrue(preserved_original(model,marker))
        self.assertNotEqual(model.active_id,marker["id"])
        for _ in range(2):
            model.learn(True)
        self.assertTrue(recalled_original(model,marker,True))
        self.assertEqual(model.choose(),2)

    def test_one_slot_cannot_recall_other_model(self):
        model=ProtectedBank(1)
        for y in [True]*24+[False]*24+[True]*2:
            model.learn(y)
        self.assertEqual(len(model.cores),1)
        self.assertEqual(model.capacity,1)

    def test_independent_cold_forks_and_zero_probe_indistinguishability(self):
        models={name:create(name) for name in NAMES}
        for y in [True]*32+[False]*32:
            shared_observation(models,y)
        old=checkpoint(models)
        a=cold_restore(old)
        b=cold_restore(old)
        self.assertEqual(checkpoint(a),checkpoint(b))
        self.assertEqual([a[n].choose() for n in NAMES],
                         [b[n].choose() for n in NAMES])
        for y in [True,True]:
            shared_observation(a,y)
        for y in [False,False]:
            shared_observation(b,y)
        self.assertEqual(checkpoint(models),old)
        self.assertNotEqual(a["recent2"].choose(),b["recent2"].choose())

    def test_conventional_bocpd_probs_and_mass(self):
        x=BOCPD()
        for y in [True]*32+[False]*32:
            x.learn(y)
            self.assertAlmostEqual(sum(row[0] for row in x.rows),1,places=10)
            self.assertGreaterEqual(x.prediction(),0)
            self.assertLessEqual(x.prediction(),1)
        self.assertGreater(x.prediction(),0)

    def test_frozen_logistic_trains_on_full_data(self):
        x=create("logistic")
        for y in [True]*12+[False]*20:
            x.learn(y)
        self.assertEqual(len(x.history),32)
        self.assertEqual(x.choose(),3)
        self.assertFalse(x.dirty)
        restored=cold_restore({"logistic":canonical(x.state())})["logistic"]
        self.assertEqual(x.state(),restored.state())

    def test_disjoint_future_cohorts(self):
        p=json.loads((HERE/"prereg.json").read_text(encoding="utf8"))
        x=p["cohorts"]
        rs={k:set(range(v["start"],v["start"]+v["count"]))
            for k,v in x.items() if isinstance(v,dict)}
        for k in rs:
            for other in rs:
                if k!=other:
                    self.assertFalse(rs[k]&rs[other])
        self.assertEqual(rs["transfer"],set(range(888000,888064)))
        self.assertEqual(len(rs["negative"]),32)

    def test_no_simulator_privileged_state(self):
        source=(HERE/"models.py").read_text(encoding="utf8")
        program=ast.parse(source)
        self.assertFalse(any(isinstance(n,ast.Attribute) and n.attr in
                             {"unwrapped","get_planning_env","transition_matrix"}
                             for n in ast.walk(program)))
        self.assertFalse(any(isinstance(n,ast.Import) and any(
                             item.name in {"gymnasium","ns_gym","torch"} for item in n.names)
                             for n in ast.walk(program)))

if __name__=="__main__":
    unittest.main()

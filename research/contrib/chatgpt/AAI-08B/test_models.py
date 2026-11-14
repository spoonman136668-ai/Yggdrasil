"""AAI-08B pure mechanical/unit controls. No NS-Gym science seeds."""
import ast
import json
import math
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from models import (BLOCK,THRESHOLD,NAMES,MATCHED,Recent,RegimeCache,
                    create,shared_update,snapshot,cloned,a_origin_marker,
                    intact_retrieval,serialize)

class AAI08BUnit(unittest.TestCase):
    def test_original_candidate_freeze(self):
        self.assertEqual(BLOCK,5)
        self.assertAlmostEqual(THRESHOLD,math.log(3))
        self.assertEqual(RegimeCache(2).state(),{
            "capacity":2,"active":0,"slots":[[1,1]],"pending":[]})
        self.assertEqual(len(NAMES),9)
        self.assertEqual(len(MATCHED),5)

    def test_cold_fork_identical_before_new_evidence(self):
        models={n:create(n) for n in NAMES}
        for y in [True]*24+[False]*24:
            shared_update(models,y)
        original=snapshot(models)
        a=cloned(original)
        b=cloned(original)
        self.assertEqual(snapshot(a),snapshot(b))
        self.assertEqual({n:a[n].choose() for n in NAMES},
                         {n:b[n].choose() for n in NAMES})
        self.assertEqual(snapshot(models),original)

    def test_fork_isolation_without_regime_label(self):
        models={n:create(n) for n in NAMES}
        for y in [True]*24+[False]*24:
            shared_update(models,y)
        checkpoint=snapshot(models)
        a=cloned(checkpoint)
        b=cloned(checkpoint)
        for y in [True]*8:shared_update(a,y)
        for y in [False]*8:shared_update(b,y)
        self.assertEqual(snapshot(models),checkpoint)
        self.assertEqual(len(a["recent4"].window),4)
        self.assertFalse(a["recent4"].choose()==b["recent4"].choose())
        self.assertEqual(serialize(cloned(checkpoint)["candidate"]),
                         checkpoint["candidate"])

    def test_zero_probe_nonidentifiability(self):
        base={name:create(name) for name in NAMES}
        for y in [True]*24+[False]*24:shared_update(base,y)
        checkpoint=snapshot(base)
        a=cloned(checkpoint)
        stay=cloned(checkpoint)
        self.assertEqual({n:a[n].choose() for n in NAMES},
                         {n:stay[n].choose() for n in NAMES},
                         "Same visible history implies identical no-probe decisions")

    def test_active_original_requires_intact_counts(self):
        m=RegimeCache(2)
        origin=a_origin_marker(m)
        self.assertFalse(intact_retrieval(m,origin),"One slot cannot prove retrieval")
        m.slots.append(type(m.slots[0])())
        self.assertTrue(intact_retrieval(m,origin))
        m.slots[0].add([True])
        self.assertFalse(intact_retrieval(m,origin))

    def test_protocol_disjoint_and_requires_new_first_use_approval(self):
        p=json.loads((HERE/"prereg.json").read_text(encoding="utf8"))
        self.assertEqual(p["experiment_id"],"AAI-08B")
        self.assertFalse(p["authority"]["first_use_authorized"])
        self.assertEqual(p["protocol"]["budgets"],[0,1,2,4,8])
        self.assertEqual(p["protocol"]["cohorts"]["transfer"],{"first":895000,"count":64})
        self.assertEqual(p["benchmark"]["git_sha"],
                         "127df4b714fe4fcf680721d8e9278a96090acd7e")
        ranges=[range(p["protocol"]["cohorts"][n]["first"],
                      p["protocol"]["cohorts"][n]["first"]+
                      p["protocol"]["cohorts"][n]["count"])
                for n in ("mechanical_reserved","dev","transfer","negative")]
        for i in range(len(ranges)):
            for j in range(i+1,len(ranges)):
                self.assertTrue(set(ranges[i]).isdisjoint(ranges[j]))

    def test_forbidden_native_owner_edits(self):
        tree=ast.parse((HERE/"models.py").read_text(encoding="utf8"))
        imports=[x.module for x in ast.walk(tree) if isinstance(x,ast.ImportFrom)]
        self.assertTrue(set(imports)<=set())
        self.assertFalse(any(isinstance(x,ast.Attribute) and x.attr in
                         {"unwrapped","get_planning_env","transition_matrix"}
                         for x in ast.walk(tree)))

if __name__=="__main__":
    unittest.main()

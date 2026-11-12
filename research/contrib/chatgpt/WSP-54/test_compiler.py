"""WSP54 source-isolated engineering tests; only WSP53 SELFTEST fixtures."""
import json
from pathlib import Path
import sys
import unittest
from dataclasses import replace

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"WSP-53"))
from source import build_world
from compiler import GradientlessCausalCompiler,splits

def score(model,rows):
    correct=wrong=abstain=0
    for row in rows:
        outcome=model.predict(row.before,row.acoustic_bits)
        if outcome is None:
            abstain+=1
        elif outcome==row.after:
            correct+=1
        else:
            wrong+=1
    return {"correct":correct,"wrong_confident":wrong,
            "abstain":abstain,"total":len(rows)}

class CompilerContracts(unittest.TestCase):
    def test_zero_gradient_contracts(self):
        self.assertEqual(GradientlessCausalCompiler.gradient_steps,0)
        self.assertEqual(len(splits("000011110000")),1)
        m=GradientlessCausalCompiler(family="anchored_effect")
        r=build_world("anchored_effect","SELFTEST",9901,"identity").phase_a[0]
        for bad in (replace(r,action_cost=0),replace(r,reset_cost=1),
                    replace(r,acoustic_bits="invalid"),replace(r,before=(0,))):
            with self.assertRaises(ValueError):
                m.observe(bad)
        self.assertEqual(m.actions,0)
        with self.assertRaises(ValueError):
            m.seal_a()
        self.assertIsNone(m.predict(r.before,r.acoustic_bits))

    def test_selftest_zero_gradient_12_worlds(self):
        records=[]
        for family in ("anchored_effect","noncommuting_order"):
            for seed in (9901,9902):
                for encoding in ("identity","permuted","rotated"):
                    with self.subTest(family=family,seed=seed,encoding=encoding):
                        world=build_world(family,"SELFTEST",seed,encoding)
                        m=GradientlessCausalCompiler(family=family)
                        for row in world.phase_a:
                            m.observe(row)
                        a_receipt=m.seal_a()
                        score_a=score(m,world.heldout_a)
                        for row in world.phase_b:
                            m.observe(row)
                        b_receipt=m.seal_b()
                        m.use_phase("B")
                        score_b=score(m,world.heldout_b)
                        m.use_phase("A")
                        retained=score(m,world.heldout_a)
                        self.assertEqual(m.actions,60)
                        self.assertLessEqual(m.nodes,300000)
                        self.assertEqual(m.gradient_steps,0)
                        self.assertEqual(score_a,retained)
                        self.assertEqual(score_a["total"],48 if family=="noncommuting_order" else 144)
                        self.assertTrue(b_receipt["hypotheses_b"]<=512)
                        cold=GradientlessCausalCompiler.restore(m.snapshot())
                        self.assertEqual(cold.snapshot(),m.snapshot())
                        self.assertEqual(cold.capacity_bits(),m.capacity_bits())
                        self.assertEqual(cold.numeric_weight_count(),m.numeric_weight_count())
                        records.append({"family":family,"seed":seed,"encoding":encoding,
                            "a":score_a,"b":score_b,"a_hypotheses":a_receipt["hypotheses"],
                            "b_hypotheses":b_receipt["hypotheses_b"],
                            "incomplete":m.incomplete,"nodes":m.nodes,
                            "gradient_steps":m.gradient_steps,
                            "numeric_weights":m.numeric_weight_count(),
                            "persistent_bits":m.capacity_bits(),
                            "source_a":world.source_receipt()["phase_a"][1]})
        print("WSP54_SELFTEST_DIAGNOSTIC "+json.dumps(records,sort_keys=True,separators=(",",":")))
        self.assertEqual(len(records),12)

    def test_cold_tamper_and_no_extra_actions(self):
        w=build_world("noncommuting_order","SELFTEST",9901,"permuted")
        m=GradientlessCausalCompiler(family="noncommuting_order")
        for r in w.phase_a:
            m.observe(r)
        m.seal_a()
        for r in w.phase_b:
            m.observe(r)
        m.seal_b()
        with self.assertRaises(ValueError):
            m.observe(w.phase_a[0])
        with self.assertRaises(ValueError):
            GradientlessCausalCompiler.restore(m.snapshot().replace(
                "noncommuting_order","anchored_effect"))
        self.assertIsNone(m.predict(w.heldout_b[0].before,w.heldout_b[0].acoustic_bits))

if __name__=="__main__":
    unittest.main()

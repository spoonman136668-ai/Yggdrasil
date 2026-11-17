"""Fabricated input-only learning controls; no owner or original source effects."""
import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1] / "research/contrib/chatgpt/NCI-ACTIVE-A2/experiment.py"
sp = importlib.util.spec_from_file_location("nci_active_a2_sourcefree", HERE)
m = importlib.util.module_from_spec(sp)
sp.loader.exec_module(m)

class ActiveA2Tests(unittest.TestCase):
    def test_global_disjoint_source_and_held_identity(self):
        held, pool, initial, remaining = m.split_inputs()
        self.assertEqual((len(held),len(pool),len(initial),len(remaining)),(64,64,8,56))
        self.assertEqual(len(set(held) & set(pool)),0)
        self.assertEqual((held,pool,initial,remaining),m.split_inputs())

    def test_early_held_access_refused_even_for_known_world(self):
        held,pool,initial,remaining = m.split_inputs()
        w=m.FabricatedWorld(100,False,held,pool)
        with self.assertRaises(ValueError):
            w.held_outcome(held[0])
        with self.assertRaises(ValueError):
            w.observe(held[0])
        self.assertIn(w.observe(initial[0]),(0,1))
        w.unlock_evaluation()
        self.assertIn(w.held_outcome(held[0]),(0,1))
        with self.assertRaises(ValueError):
            w.observe(initial[0])

    def test_reproducible_equal_budget_and_no_outcome_policy_input(self):
        held,pool,initial,available = m.split_inputs()
        for seed in (100,109,215):
            for policy in m.POLICIES:
                a,_=m.choose_inputs(policy,seed,initial,available)
                b,_=m.choose_inputs(policy,seed,initial,available)
                self.assertEqual(a,b)
                self.assertEqual(len(a),24)
                self.assertTrue(all(mask in available for mask in a))
                if policy!="passive":
                    self.assertEqual(len(set(a)),24)
                else:
                    self.assertTrue(all((mask>>6)==(mask&1) for mask in a))
            active,_=m.choose_inputs("active",seed,initial,available)
            random,_=m.choose_inputs("random",seed,initial,available)
            def rank(xs):
                pivot={}
                for x in xs:m.rank_add(pivot,x)
                return len(pivot)
            self.assertGreaterEqual(rank(initial+active),rank(initial+random))

    def test_native_independent_parity_under_supplied_class(self):
        for seed in (100,101,112,131):
            held,pool,initial,remaining=m.split_inputs()
            w=m.FabricatedWorld(seed,False,held,pool)
            extra,_=m.choose_inputs("active",seed,initial,remaining)
            inputs=initial+extra
            labels=[w.observe(x) for x in inputs]
            native,raw=m.native_predictions(inputs,labels)
            independent=m.independent_predictions(inputs,labels)
            self.assertEqual(native,independent)
            self.assertIsNotNone(raw)
            w.unlock_evaluation()
            truth=[w.held_outcome(x) for x in held]
            self.assertEqual(m.metric(native,held,truth)["wrong"],0)

    def test_native_exact_rejects_deliberately_inconsistent_labels(self):
        xs=list(range(64))
        ys=[(i&1) for i in range(64)]
        # Conflict at same factual public input is invalid, not an inference.
        native,raw=m.native_predictions(xs+[0],ys+[1])
        self.assertIsNone(raw)
        self.assertTrue(all(v is None for v in native))
        self.assertEqual(native,m.independent_predictions(xs+[0],ys+[1]))

    def test_negative_source_free_and_no_hidden_held_use(self):
        text=HERE.read_text()
        for forbidden in ("CKAD-02/campaign", "CKAD-09/campaign",
                          "public_causal_cells_source", "old.dataset(",
                          "CausalGym", "original_dtr", "original_source.reset("):
            self.assertNotIn(forbidden,text)
        held,pool,initial,avail=m.split_inputs()
        self.assertTrue(all(m.terms_for(seed,False)!=m.terms_for(seed,True)
                            for seed in (100,105,121,131)))
        self.assertEqual(m.corrupt_labels(101,[0,1,2,3],[0,0,1,1]),
                         m.corrupt_labels(101,[0,1,2,3],[0,0,1,1]))

    def test_frozen_bootstrap_and_canonical_reproducibility(self):
        delta=[0.125 if i%3 else -0.125 for i in range(32)]
        self.assertEqual(m.bootstrap_lower(delta),m.bootstrap_lower(delta))
        self.assertGreaterEqual(m.bootstrap_lower(delta),-0.125)

if __name__ == "__main__":
    unittest.main()

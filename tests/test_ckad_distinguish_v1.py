"""CKAD-DISTINGUISH-V1 source-free negative and causal action controls."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
from yggdrasil.native_hypothesis_portfolio import canonical,digest
from yggdrasil.native_shared_operator_memory import NativeSharedOperatorMemory

ROOT=Path(__file__).resolve().parents[1]
CODE=ROOT/"research/contrib/chatgpt/CKAD-DISTINGUISH-V1/campaign.py"
spec=importlib.util.spec_from_file_location("ckad_distinguish_v1",CODE)
c=importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)

class DistinguishingTests(unittest.TestCase):
    def test_new_synthetic_cohorts_and_program_grammar(self):
        self.assertEqual(c.FIT,tuple(range(1501,1517)))
        self.assertEqual(c.TRANSFER,tuple(range(1601,1633)))
        self.assertEqual(c.SHIFT,tuple(range(1701,1733)))
        self.assertEqual(c.CORRUPT,tuple(range(1801,1833)))
        self.assertEqual(c.EFFECTS,12)
        self.assertEqual(c.FIT_EFFECTS,16)
        self.assertEqual(len(c.EXTRA_GATES),25)
        self.assertEqual(len(c.BROAD_PROGRAMS),3200)
        self.assertEqual(len(c.NARROW_PROGRAMS),1920)

    def test_disjoint_pool_held_and_source_budget_enforcement(self):
        held,pool=c.split_masks()
        self.assertEqual(len(held),len(pool))
        self.assertFalse(set(held)&set(pool))
        w=c.FabricatedSource(1601,"TRANSFER",held,pool,12)
        with self.assertRaises(ValueError):w.held(held[0])
        with self.assertRaises(ValueError):w.do(held[0])
        first=w.do(pool[0])
        self.assertIn(first,(0,1))
        with self.assertRaises(ValueError):w.do(pool[0])
        with self.assertRaises(ValueError):w.reveal()
        for m in pool[1:12]:w.do(m)
        self.assertEqual(w.calls,12)
        w.reveal()
        with self.assertRaises(ValueError):w.do(pool[12])
        self.assertIn(w.held(held[0]),(0,1))

    def test_shared_operator_is_unknown_and_local_coefficients_vary(self):
        held,pool=c.split_masks()
        train=c.FabricatedSource(1501,"FIT",held,pool,16)
        target=c.FabricatedSource(1601,"TRANSFER",held,pool,12)
        other=c.FabricatedSource(1602,"TRANSFER",held,pool,12)
        shifted=c.FabricatedSource(1701,"SHIFT",held,pool,12)
        self.assertEqual(train._params[1],target._params[1])
        self.assertEqual(train._params[1],other._params[1])
        self.assertNotEqual(shifted._params[1].bit_count(),train._params[1].bit_count())
        self.assertNotEqual(train.source_hash(),target.source_hash())
        self.assertEqual(target.source_hash(),
                c.FabricatedSource(1601,"TRANSFER",held,pool,12).source_hash())

    def test_training_fits_only_first_sixteen_worlds_and_cold(self):
        held,pool=c.split_masks()
        model,receipts,wall=c.train(held,pool)
        self.assertEqual(len(receipts),16)
        self.assertTrue(model._frozen)
        self.assertEqual(model.fit_worlds,16)
        self.assertGreaterEqual(model.global_gate_support.bit_count(),1)
        self.assertTrue(all(row["remaining_shared_gates"]>=1 for row in receipts))
        raw=model.checkpoint()
        cold=NativeSharedOperatorMemory.restore(raw,digest(raw))
        self.assertEqual(cold.checkpoint(),raw)

    def test_probes_are_input_only_no_oracle_and_unique(self):
        held,pool=c.split_masks()
        init=pool[:8]
        observations=[(m,0) for m in init]
        reference=(None,)*64
        proposed,info=c.discriminate(16,observations,pool,reference)
        self.assertEqual(len(proposed),4)
        self.assertEqual(len(set(proposed)),4)
        self.assertFalse(set(proposed)&set(init))
        self.assertFalse(set(proposed)&set(held))
        self.assertTrue(info["input_only"])
        self.assertEqual(info["future_effects_read"],0)
        self.assertEqual((proposed,info),
                         c.discriminate(16,observations,pool,reference))

    def test_one_familiar_world_all_four_equal_budget_and_symbolic_parity(self):
        held,pool=c.split_masks()
        trained,receipt,_=c.train(held,pool)
        prior={name:trained for name in c.POLICIES}
        # Unit checks isolate optional conventional dependency. The fully
        # scored CI primary installs pinned sklearn and does NOT patch CART.
        with patch.object(c,"cart_predict",lambda seed,observations:(None,)*64):
            later,record=c.evaluate(1601,"TRANSFER",16,prior,held,pool)
        self.assertEqual(len(record["scores"]),11)
        self.assertEqual(len(record["actors"]),4)
        self.assertTrue(all(x["source_effect_calls"]==12
                            for x in record["actors"].values()))
        self.assertEqual(record["scores"]["target"],
                         record["scores"]["independent_symbolic"])
        self.assertEqual(record["target_audit"]["source_effect_calls"],4)
        self.assertEqual(record["target_audit"]["future_effects_read"],0)
        self.assertTrue(all(later[name].fit_worlds==16
                            for name in c.POLICIES))
        original=tuple(trained.vector(slot) for slot in range(16))
        self.assertTrue(all(tuple(later[name].vector(slot) for slot in range(16))==original
                            for name in c.POLICIES))

    def test_corruption_two_initial_labels_only(self):
        held,pool=c.split_masks()
        labels=(0,1,0,1)
        for seed in c.CORRUPT[:3]:
            modified=c.tamper(seed,pool[:4],labels)
            self.assertEqual(sum(a!=b for a,b in zip(labels,modified)),2)
            self.assertEqual(modified,c.tamper(seed,pool[:4],labels))

    def test_bootstrap_determinism_and_no_hidden_source_imports(self):
        diff=[-0.125 if i%3 else 0.5 for i in range(32)]
        self.assertEqual(c.boot_lower(diff),c.boot_lower(diff))
        contents=CODE.read_text()
        for forbidden in ("from .causalgym", "OriginalWorld(", "original_source.do(",
                          "original_source.reset(", "CausalGym", "ckad09_generator"):
            self.assertNotIn(forbidden,contents)
        self.assertIn("scientific_pass",contents)
        self.assertIn("original_source_actions",contents)

if __name__=="__main__":
    unittest.main()

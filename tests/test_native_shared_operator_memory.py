"""Native shared causal operator learning: source-free test and negative custody."""
import importlib.util
import json
from pathlib import Path
import unittest
from yggdrasil.native_hypothesis_portfolio import (
    NativeHypothesisPortfolio,ALL_CANDIDATES,GATES,
    canonical,digest,SOURCE_MODE)
from yggdrasil.native_shared_operator_memory import (
    NativeSharedOperatorMemory,FIT_WORLDS,FULL_GATE_SUPPORT,
    gate_support,program_scope)

CAMPAIGN=Path(__file__).resolve().parents[1]/"research/contrib/chatgpt/CKAD-SHARED-V2/campaign.py"
s=importlib.util.spec_from_file_location("ckad_shared_v2_sourcefree",CAMPAIGN)
c=importlib.util.module_from_spec(s);s.loader.exec_module(c)

class SharedCausalMemoryTests(unittest.TestCase):
    def test_no_correct_gate_is_preinstalled_in_learner(self):
        self.assertEqual(FIT_WORLDS,16)
        self.assertEqual(len(GATES),15)
        self.assertEqual(NativeSharedOperatorMemory().global_gate_support,
                         FULL_GATE_SUPPORT)
        self.assertEqual(program_scope(FULL_GATE_SUPPORT),ALL_CANDIDATES)
        self.assertEqual(gate_support(ALL_CANDIDATES),FULL_GATE_SUPPORT)

    def test_disjoint_sources_and_hidden_truth(self):
        held,pool=c.held_split()
        self.assertEqual((len(held),len(pool)),(32,32))
        self.assertFalse(set(held)&set(pool))
        w=c.SimulatedWorld(717,"TRANSFER",held,pool,8)
        with self.assertRaises(ValueError):
            w.held_truth(held[0])
        with self.assertRaises(ValueError):
            w.effect(held[0])
        self.assertIn(w.effect(pool[0]),(0,1))
        with self.assertRaises(ValueError):
            w.effect(pool[0])
        with self.assertRaises(ValueError):
            w.unlock_held()

    def test_sealed_training_gate_from_only_witnesses(self):
        held,pool=c.held_split()
        model,history,receipts,vecs=c.train_shared(held,pool)
        self.assertEqual(len(history),FIT_WORLDS)
        self.assertEqual(len(receipts),FIT_WORLDS)
        self.assertTrue(model._frozen)
        self.assertGreater(model.global_gate_support,0)
        self.assertEqual(c.independent_gate_support(history),
                         model.global_gate_support)
        self.assertEqual(tuple(model.vector(s) for s in range(FIT_WORLDS)),
                         vecs)
        with self.assertRaises(ValueError):
            model.observe(0,42,0,digest(canonical([0,42,0,SOURCE_MODE])))
        self.assertTrue(all(len(h)==16 for h in history))

    def test_held_eval_cold_and_same_action_ablation(self):
        held,pool=c.held_split()
        trained,history,receipts,vecs=c.train_shared(held,pool)
        model,row=c.evaluate_world(717,"TRANSFER",16,held,pool,trained)
        self.assertEqual(row["charged_actors"]["target"]["effects"],8)
        self.assertEqual(row["charged_actors"]["no_memory_active"]["effects"],8)
        self.assertEqual(row["charged_actors"]["shared_random"]["effects"],8)
        self.assertEqual(row["metrics"]["shared"],
                         row["metrics"]["independent_symbolic"])
        self.assertEqual(len(row["metrics"]),7)
        self.assertEqual(tuple(model.vector(s) for s in range(16)),vecs)
        raw=model.checkpoint()
        self.assertEqual(NativeSharedOperatorMemory.restore(raw,digest(raw)).checkpoint(),raw)

    def test_no_false_shared_gate_custody_after_rehash(self):
        held,pool=c.held_split()
        trained,*_=c.train_shared(held,pool)
        raw=trained.checkpoint()
        doc=json.loads(raw)
        doc["gate_mask"]=(doc["gate_mask"]^1)
        forged=canonical(doc)
        with self.assertRaises(ValueError):
            NativeSharedOperatorMemory.restore(forged,digest(forged))
        with self.assertRaises(ValueError):
            NativeSharedOperatorMemory.restore(raw,"0"*64)

    def test_explicit_corrupted_evidence_is_only_two_initial_labels(self):
        held,pool=c.held_split()
        originals=(0,1,1,1)
        for seed in (901,902,916):
            changed=c.corruption(seed,pool[:4],originals)
            self.assertEqual(sum(a!=b for a,b in zip(changed,originals)),2)
            self.assertEqual(changed,c.corruption(seed,pool[:4],originals))

    def test_frozen_cohorts_and_sourcefree_contract(self):
        self.assertEqual(c.TRAIN,tuple(range(701,717)))
        self.assertEqual(c.TRANSFER,tuple(range(717,733)))
        self.assertEqual(c.SHIFT,tuple(range(801,817)))
        self.assertEqual(c.CORRUPT,tuple(range(901,917)))
        self.assertEqual(c.held_split(),c.held_split())
        content=CAMPAIGN.read_text()
        for forbidden in ("original_source.reset(", "original_source.do(",
                          "CausalGym", "DTR-protected", "old.dataset(",
                          "ckad09_generator"):
            self.assertNotIn(forbidden,content)

    def test_bootstrap_determinism(self):
        series=[0.125 if i%2 else -0.125 for i in range(16)]
        self.assertEqual(c.bootstrap_lower(series),c.bootstrap_lower(series))
        self.assertGreaterEqual(c.bootstrap_lower(series),-0.125)

if __name__=="__main__":
    unittest.main()

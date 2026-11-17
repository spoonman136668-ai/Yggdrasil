"""NCI-MISMATCH-A3 source-free controls; no protected source imports."""
import importlib.util
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/"research/contrib/chatgpt/NCI-MISMATCH-A3/experiment.py"
spec=importlib.util.spec_from_file_location("nci_mismatch_a3",PATH)
a3=importlib.util.module_from_spec(spec);spec.loader.exec_module(a3)
a2=a3.a2

class MismatchA3Tests(unittest.TestCase):
    def test_disjoint_held_and_exact_24_8_budget(self):
        held,pool,initial,available=a2.split_inputs()
        self.assertEqual(len(held),64)
        self.assertEqual(len(initial),8)
        self.assertEqual(len(available),56)
        for seed in (300,309,331,400,431):
            selected,_=a2.choose_inputs("active",seed,initial,available)
            fit=tuple(initial)+tuple(selected[:16])
            remaining=tuple(m for m in available if m not in fit)
            self.assertEqual(len(fit),24)
            self.assertEqual(len(remaining),40)
            base=[0]*128
            target=a3.audit_inputs(seed,fit,remaining,base,"target")
            random=a3.audit_inputs(seed,fit,remaining,base,"random")
            self.assertEqual(len(set(target)),8)
            self.assertEqual(len(set(random)),8)
            self.assertEqual(set(target)&set(fit),set())
            self.assertEqual(set(random)&set(fit),set())
            self.assertEqual(set(target)&set(held),set())
            self.assertEqual(target,a3.audit_inputs(seed,fit,remaining,base,"target"))
            self.assertEqual(random,a3.audit_inputs(seed,fit,remaining,base,"random"))

    def test_selector_does_not_read_unknown_truth_or_labels(self):
        held,pool,initial,available=a2.split_inputs()
        selected,_=a2.choose_inputs("active",300,initial,available)
        fit=tuple(initial)+tuple(selected[:16])
        remaining=tuple(m for m in available if m not in fit)
        known=[None]*128
        for m in remaining[::2]:
            known[m]=0
        c=a3.audit_inputs(300,fit,remaining,known,"target")
        self.assertGreaterEqual(sum(known[m] is not None for m in c),4)
        self.assertEqual(c,a3.audit_inputs(300,fit,remaining,known,"target"))
        self.assertEqual(len(set(c)),8)

    def test_source_actor_protects_held_until_seal(self):
        held,pool,initial,available=a2.split_inputs()
        w=a2.FabricatedWorld(400,True,held,pool)
        with self.assertRaises(ValueError):
            w.held_outcome(held[0])
        with self.assertRaises(ValueError):
            w.observe(held[0])
        self.assertIn(w.observe(initial[0]),(0,1))
        w.unlock_evaluation()
        with self.assertRaises(ValueError):
            w.observe(initial[0])

    def test_native_independent_parity_at_shared_fit(self):
        held,pool,initial,available=a2.split_inputs()
        for shifted,seed in ((False,300),(True,400)):
            w=a2.FabricatedWorld(seed,shifted,held,pool)
            extra,_=a2.choose_inputs("active",seed,initial,available)
            fit=tuple(initial)+tuple(extra[:16])
            labels=tuple(w.observe(m) for m in fit)
            preds,raw=a3.compute_native(fit,labels)
            self.assertEqual(preds,a2.independent_predictions(fit,labels))
            self.assertEqual(len(preds),128)
            if raw is not None:
                self.assertEqual(a3.digest(raw),a3.digest(raw))

    def test_separate_source_actors_share_truth_but_not_custody(self):
        held,pool,initial,available=a2.split_inputs()
        left=a2.FabricatedWorld(300,False,held,pool)
        right=a2.FabricatedWorld(300,False,held,pool)
        self.assertEqual(left.source_sha256,right.source_sha256)
        for m in initial:
            self.assertEqual(left.observe(m),right.observe(m))
        self.assertEqual(left.effect_calls,right.effect_calls)
        left.unlock_evaluation()
        with self.assertRaises(ValueError):
            right.held_outcome(held[0])

    def test_corruption_only_training_before_true_effect_audit(self):
        held,pool,initial,available=a2.split_inputs()
        active,_=a2.choose_inputs("active",300,initial,available)
        fit=tuple(initial)+tuple(active[:16])
        w=a2.FabricatedWorld(300,False,held,pool)
        outcomes=tuple(w.observe(m) for m in fit)
        a=tuple(a2.corrupt_labels(300,fit,outcomes))
        self.assertEqual(a,tuple(a2.corrupt_labels(300,fit,outcomes)))
        self.assertEqual(len(a),24)
        self.assertEqual(sorted(a),sorted(outcomes))

    def test_frozen_cohorts_and_no_original_environment_calls(self):
        self.assertEqual(a3.IN_SEEDS,tuple(range(300,332)))
        self.assertEqual(a3.SHIFT_SEEDS,tuple(range(400,432)))
        self.assertEqual((a3.FIT,a3.AUDIT,a3.EFFECTS,a3.MIN_IDENTIFIED),
                         (24,8,32,4))
        source=PATH.read_text()
        for forbidden in ("old.dataset(", "CausalGym", "from yggdrasil.original",
                          "original_source.reset(", "original_source.do("):
            self.assertNotIn(forbidden,source)

if __name__=="__main__":
    unittest.main()

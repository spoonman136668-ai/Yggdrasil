"""AAI-08A reserved mechanical cases and synthetic model tests only."""
import importlib.util
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("aai08a",ROOT/"evaluate.py")
x=importlib.util.module_from_spec(spec)
spec.loader.exec_module(x)

class ScienceMechanical(unittest.TestCase):
    def test_source_protocol_and_no_seed_overlap(self):
        self.assertEqual(x.PREREG,"db263b1de02fdaaec2152b44947a1e11b5305262")
        self.assertEqual(x.AMENDMENT,"57e8933f0376c226a62ab7252bb395482fa41eb2")
        self.assertEqual((len(x.DEV),len(x.TRANSFER),len(x.NEGATIVE)),(32,64,32))
        self.assertTrue(set(x.MECHANICAL).isdisjoint(x.DEV))

    def test_causal_laws_use_real_official_step(self):
        self.assertTrue(x.mechanistic_audit())

    def test_shared_two_slot_memory_is_cold_serializable(self):
        z=x.RegimeCache(2)
        for v in [True]*20+[False]*20+[True]*20:z.learn(v)
        self.assertLessEqual(len(z.slots),2)
        self.assertEqual(x.serial(z),x.serial(x.restore_model("candidate",x.serial(z))))

    def test_strong_baselines_receive_same_events(self):
        stream=[True]*12+[False]*12+[True]*12
        models=x.new_models()
        for e in stream:x.train_all(models,e)
        self.assertEqual(models["stationary"].slot.yes,1+24)
        self.assertEqual(len(models["logistic"].history),36)
        self.assertLessEqual(len(models["recent"].window),8)
        self.assertEqual(set(x.choices(models)),set(x.METHODS))

    def test_no_phase_leaks_into_learner_api(self):
        import ast
        t=ast.parse((ROOT/"evaluate.py").read_text(encoding="utf-8"))
        self.assertFalse(any(isinstance(n,ast.Attribute) and n.attr in
            ("unwrapped","transition_matrix","get_planning_env")
            for n in ast.walk(t)))

if __name__=="__main__":
    unittest.main()

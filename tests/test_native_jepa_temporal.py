"""YGG-JEPA2-03: original native source, cumulative learned weights, cold negatives."""
import json
import unittest
from pathlib import Path

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_jepa2_multilearner import NativeMultiLearner, STEPS as PRIOR_STEPS
from yggdrasil.native_jepa_temporal import (
    NativeTemporalMultiLearner, TemporalLatentSpecialist, STEPS,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research/contrib/chatgpt/YGG-JEPA2-02/seed-14071-states.json"


def old():
    state = json.loads(SOURCE.read_bytes())[0]
    raw = state["multi_learner_ascii"].encode("ascii")
    assert digest(raw) == state["multi_learner_sha256"]
    return raw, state


def new_event():
    return (
        digest(canonical(["JEPA3-NEW-WITNESSED-EVENT", 1])),
        ((0, 1), (0, 0)),
        {"s1":0, "x1":1, "s2":1, "x2":0, "y":1},
    )


class NativeTemporalTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw, cls.old_state = old()

    def bootstrap(self):
        return NativeTemporalMultiLearner.bootstrap(
            self.raw, digest(self.raw))

    def test_real_source_bootstrap_preserves_original_checkpoint(self):
        model = self.bootstrap()
        self.assertEqual(model.base.checkpoint(), self.raw)
        self.assertEqual(digest(model.base.native.checkpoint()),
                         self.old_state["native_original_sha256"])
        self.assertEqual(model.source_count, 240)
        self.assertEqual(model.transition.steps, 240*STEPS)
        self.assertEqual(model.reward.steps, 240*STEPS)
        checkpoint=model.checkpoint()
        restored=NativeTemporalMultiLearner.restore(checkpoint,digest(checkpoint))
        self.assertEqual(restored.checkpoint(),checkpoint)
        self.assertEqual(restored.base.checkpoint(),self.raw)

    def test_same_persistent_model_continues_all_four_learned_heads(self):
        model=self.bootstrap()
        identifier, views, row=new_event()
        before=model.checkpoint()
        forecast=model.predict(views,row["x1"],row["s2"],row["x2"])
        self.assertTrue(all(0<=x<=1 for k in forecast for x in forecast[k]))
        self.assertEqual(model.checkpoint(),before)
        updated=model.observe(identifier,views,row)
        self.assertEqual(updated.base.native.info()["count"],241)
        self.assertEqual(updated.source_count,240)
        self.assertEqual(updated.transition.steps,241*STEPS)
        self.assertEqual(updated.reward.steps,241*STEPS)
        self.assertEqual(updated.base.transition.steps,241*PRIOR_STEPS)
        self.assertEqual(updated.base.reward.steps,241*PRIOR_STEPS)
        self.assertEqual(updated.base.native._ledger[:240],
                         model.base.native._ledger)
        self.assertNotEqual(updated.base.checkpoint(),self.raw)
        self.assertEqual(model.checkpoint(),before)
        checkpoint=updated.checkpoint()
        cold=NativeTemporalMultiLearner.restore(checkpoint,digest(checkpoint))
        self.assertEqual(cold.checkpoint(),checkpoint)

    def test_idempotent_duplicate_and_conflicting_evidence_atomic(self):
        model=self.bootstrap()
        identifier,views,row=new_event()
        updated=model.observe(identifier,views,row)
        before=updated.checkpoint()
        self.assertIs(updated.observe(identifier,views,row),updated)
        invalid=dict(row);invalid["y"]^=1
        with self.assertRaises(ValueError):
            updated.observe(identifier,views,invalid)
        self.assertEqual(updated.checkpoint(),before)
        self.assertEqual(model.base.checkpoint(),self.raw)

    def test_rehashed_forged_temporal_parameters_rejected(self):
        model=self.bootstrap()
        raw=model.checkpoint()
        forged=json.loads(raw)
        forged["temporal_transition"]["encoder"][0][0]+=0.00001
        bad=canonical(forged)
        with self.assertRaises(ValueError):
            NativeTemporalMultiLearner.restore(bad,digest(bad))
        self.assertEqual(model.checkpoint(),raw)

    def test_rehashed_previous_expert_forgery_is_rejected_by_source_refit(self):
        old=json.loads(self.raw)
        old["transition"]["encoder"][0][0]+=0.00001
        forged=canonical(old)
        with self.assertRaises(ValueError):
            NativeTemporalMultiLearner.bootstrap(forged,digest(forged))
        # The archived prior checkpoint remains exactly intact.
        self.assertEqual(self.bootstrap().base.checkpoint(),self.raw)

    def test_history_is_witness_bound_and_gradients_finite(self):
        model=self.bootstrap()
        p=model.predict(((1,0),(1,1)),0,1,1)
        self.assertTrue(all(0<=x<=1 for v in p.values() for x in v))
        with self.assertRaises(ValueError):
            model.predict(((0,1),(0,2)),0,1,0)
        with self.assertRaises(ValueError):
            model.predict(((0,1),(0,0)),2,1,0)
        self.assertIsInstance(model.transition,TemporalLatentSpecialist)
        self.assertEqual(model.base.checkpoint(),self.raw)


if __name__=="__main__":
    unittest.main()


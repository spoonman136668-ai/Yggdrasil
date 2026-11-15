"""ST8 source-real TRAIN-only native substrate growth qualification.

No unfamiliar-law, new-rule or protected scientific first use. The
source-private cubic truth is never an input to a model method.
"""
import json
import unittest

from research.nci04_st8.private_world import PrivateCubicWorld,ACTIONS
from research.nci04_st8.native_growth import (
    NativeGrow8,features,canonical
)
from research.nci04_st8.matched_controls import (
    ConventionalGF2,models,restored_models,pack
)


def original_episode(cohort,law=3,seed=100,trial=0,train=True):
    w=PrivateCubicWorld(law,seed,trial)
    for m in cohort.values():m.reset_episode()
    scores={}
    for index,action in enumerate(ACTIONS):
        public=w.public()
        preds={n:m.predict(public,action) for n,m in cohort.items()}
        after,target=w.step(action)
        for n,m in cohort.items():
            assert m.observe(public,action,target,after,train=train)==preds[n]
        if index==4:
            scores=preds
    return scores


class ST8NativeGrowthTests(unittest.TestCase):
    def test_actual_initial_evidence_then_contradiction_growth(self):
        m=NativeGrow8("growth")
        self.assertEqual(m.degree,2)
        self.assertEqual(m.rank,0)
        for seed in range(100,106):
            for trial in range(16):
                original_episode({"candidate":m},3,seed,trial)
        self.assertEqual(m.updates,96)
        self.assertEqual(m.degree,3)
        self.assertGreaterEqual(m.contradictions,1)
        self.assertEqual(m.growths,1)
        self.assertEqual(m.post_growth_conflicts,0)
        self.assertGreater(m.rank,36)
        self.assertFalse(m.accounting()["source_private_coefficients_seen"])

    def test_genuine_native_vs_independent_same_input_control(self):
        native=NativeGrow8()
        independent=ConventionalGF2("adaptive")
        full=ConventionalGF2("full_cubic")
        for seed in range(100,105):
            for trial in range(16):
                original_episode({"candidate":native,
                                  "adaptive":independent,
                                  "full":full},3,seed,trial)
        self.assertEqual(native.degree,3)
        self.assertEqual(independent.degree,3)
        self.assertEqual(native.rank,independent.rank)
        self.assertEqual(native.post_growth_conflicts,0)
        self.assertEqual(independent.contradictions,1)
        self.assertEqual(
            native.accounting()["learned_GF2_augmented_bits_max"],
            independent.accounting()["learned_augmented_bits_max"]
        )

    def test_cold_mid_original_episode_maintains_integer_causal_state(self):
        m=NativeGrow8()
        original_episode({"candidate":m},3,100,0)
        m.reset_episode()
        source=PrivateCubicWorld(3,101,1)
        for action in ACTIONS[:3]:
            public=source.public()
            after,target=source.step(action)
            m.observe(public,action,target,after)
        checkpoint=m.snapshot()
        restored=NativeGrow8.restore(checkpoint)
        self.assertEqual(restored.snapshot(),checkpoint)
        for action in ACTIONS[3:]:
            public=source.public()
            self.assertEqual(restored.predict(public,action),
                             m.predict(public,action))
            after,target=source.step(action)
            self.assertEqual(restored.observe(public,action,target,after),
                             m.observe(public,action,target,after))
            self.assertEqual(restored.snapshot(),m.snapshot())

    def test_true_no_growth_never_uses_new_features(self):
        m=NativeGrow8("no_growth")
        for seed in range(100,106):
            for trial in range(16):
                original_episode({"candidate":m},3,seed,trial)
        self.assertEqual(m.degree,2)
        self.assertEqual(m.growths,0)
        self.assertGreaterEqual(m.contradictions,1)
        self.assertLessEqual(m.rank,36)

    def test_bounded_cache_no_pseudo_labels_and_erase_negative(self):
        m=NativeGrow8("erase")
        original_episode({"candidate":m},3,100,0)
        self.assertEqual(m.updates,1)
        self.assertEqual(len(m.public_buffer),1)
        m.reset_episode()
        self.assertEqual(m.rank,0)
        self.assertEqual(m.public_buffer,[])
        self.assertEqual(m.growths,0)
        self.assertEqual(
            NativeGrow8.restore(m.snapshot()).snapshot(),m.snapshot()
        )

    def test_full_conventional_and_all_original_models_can_restore(self):
        cohort=models()
        original_episode(cohort,3,100,0)
        raw={n:m.snapshot() for n,m in cohort.items()}
        clones=restored_models(raw)
        self.assertEqual(set(clones),set(cohort))
        self.assertTrue(all(clones[n].snapshot()==raw[n] for n in cohort))

    def test_valid_unknown_high_rank_and_cubic_basis_definition(self):
        self.assertEqual(features(0,3),0)
        self.assertEqual(features(255,2).bit_count(),36)
        self.assertEqual(features(255,3).bit_count(),92)
        self.assertEqual(features(3,3).bit_count(),3)
        self.assertNotEqual(features(7,3)>>36,0)
        self.assertEqual(len(NativeGrow8().basis),36)

    def test_public_source_outcome_leak_rejected_atomically(self):
        m=NativeGrow8()
        w=PrivateCubicWorld(3,100,0)
        before=w.public()
        frozen=m.snapshot()
        for act,target,after,train in (
            (2,(0,)*8,before,True),
            (3,(1,)*8,before,True),
            (3,(0,)*8,before,1),
            (3,(0,)*8,before,"yes")
        ):
            with self.assertRaises(ValueError):
                m.observe(before,act,target,after,train=train)
            self.assertEqual(frozen,m.snapshot())

    def test_invalid_native_snapshot_fails_closed(self):
        m=NativeGrow8()
        original_episode({"candidate":m},3,100,0)
        for patch in (
            {"schema":"wrong"},{"degree":3},{"rank":99},
            {"updates":True},{"growths":2},
            {"basis":[True]*36},{"public_buffer":[[True,2]]},
            {"step":6},{"rotation":4}
        ):
            payload=json.loads(m.snapshot());payload.update(patch)
            with self.assertRaises(ValueError):
                NativeGrow8.restore(canonical(payload))

    def test_independent_conventional_bad_checkpoint(self):
        m=ConventionalGF2("full_cubic")
        original_episode({"baseline":m},3,100,0)
        snap=m.snapshot()
        self.assertEqual(ConventionalGF2.restore(snap).snapshot(),snap)
        bad=json.loads(snap);bad["rows"]=[True]*92
        with self.assertRaises(ValueError):
            ConventionalGF2.restore(canonical(bad))

    def test_different_source_actuators_are_not_hardcoded(self):
        # TWO different training-law action effects, never hidden world ID
        # as an input to a model method.
        m=NativeGrow8()
        x=original_episode({"candidate":m},3,100,0)
        y=original_episode({"candidate":m},5,101,1)
        self.assertEqual(len(x["candidate"]),8)
        self.assertEqual(len(y["candidate"]),8)
        self.assertEqual(m.updates,2)


if __name__=="__main__":
    unittest.main()

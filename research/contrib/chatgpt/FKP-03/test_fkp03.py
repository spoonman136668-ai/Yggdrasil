"""FKP-03 focused negative, source-bound, deterministic development tests."""
from __future__ import annotations
import importlib
import unittest

source=importlib.import_module("source")
model=importlib.import_module("model")


class TestFKP03(unittest.TestCase):
    def test_original_public_source_invariants_and_first_use_fence(self):
        j=source.dev_preflight()
        self.assertEqual(j["spec_sha256"],source.SPEC_SHA256)
        self.assertTrue(j["public_dev_only"])
        self.assertFalse(j["protected_first_use"])
        self.assertEqual(len(j["fixtures"]),4)
        for seed in (1400,1463,2400,2415):
            with self.assertRaises(PermissionError):
                source.CausalWorld(seed)
            with self.assertRaises(PermissionError):
                source.CausalWorld(seed,protected_key=b"short")
        with self.assertRaises(ValueError):
            source.CausalWorld(400,protected_key=b"z"*32)

    def test_action_budget_repeats_held_partition(self):
        world=source.CausalWorld(400)
        public=world.public_view()
        self.assertEqual(len(set(public.intervention_choices)),64)
        self.assertEqual(len(set(public.held_inputs)),128)
        self.assertFalse(set(public.held_inputs)&set(public.intervention_choices))
        with self.assertRaises(ValueError):
            world.observe(-1)
        with self.assertRaises(ValueError):
            world.observe(True)
        with self.assertRaises(ValueError):
            world.observe(public.held_inputs[0])
        self.assertIn(world.observe(public.intervention_choices[0]),(0,1))
        with self.assertRaises(PermissionError):
            world.observe(public.intervention_choices[0])
        for action in public.intervention_choices[1:16]:
            self.assertIn(world.observe(action),(0,1))
        self.assertEqual(world.charged_actions,16)
        with self.assertRaises(PermissionError):
            world.observe(public.intervention_choices[16])
        self.assertEqual(len(world.development_only_labels(public.held_inputs)),128)
        with self.assertRaises(ValueError):
            world.development_only_labels(public.held_inputs[:-1])

    def test_foundation_learns_from_only_public_consequences(self):
        record=model.acquire_foundation()
        self.assertEqual(record["observations"],16384)
        self.assertEqual(record["worlds"],256)
        self.assertEqual(sum(record["learned_gate_counts"].values()),256)
        self.assertEqual(len(record["learned_gate_counts"]),4)
        self.assertEqual(len(record["checkpoint_sha256"]),64)

    def test_learned_three_input_compositions_are_complete(self):
        # Checks generic closure, not a source-privileged target rule.
        c=model.compose_generic_functions((6,7,8,14))
        self.assertEqual(len(c),256)
        self.assertEqual(model.generic_mask(c).bit_count(),218)
        self.assertEqual(model.family_mask().bit_count(),7)

    def test_causal_posterior_witnesses_and_cold_checkpoint(self):
        c=model.compose_generic_functions((6,7,8,14))
        p=model.Posterior(model.generic_mask(c))
        world=source.CausalWorld(400)
        pool=world.public_view().intervention_choices
        a=p.choose(pool,"information")
        y=world.observe(a)
        before=sum(m.bit_count() for m in p.masks)
        p.add(a,y)
        after=sum(m.bit_count() for m in p.masks)
        self.assertGreater(before,after)
        self.assertGreater(after,0)
        self.assertEqual(p.counts(a)[1]/p.counts(a)[0],float(y))
        saved,sha=p.checkpoint()
        self.assertEqual(len(sha),64)
        self.assertEqual(saved["restored"].probabilities(pool[:3]),p.probabilities(pool[:3]))
        with self.assertRaises(ValueError):
            p.add(a,y)
        with self.assertRaises(ValueError):
            p.add(-1,0)
        with self.assertRaises(ValueError):
            p.add(pool[1],2)

    def test_repeated_active_source_world_deterministic(self):
        mask=model.family_mask()
        first=model.execute_policy(400,mask,"information")
        second=model.execute_policy(400,mask,"information")
        self.assertEqual(first["queries"],second["queries"])
        self.assertEqual(first["answers"],second["answers"])
        self.assertEqual(first["prediction"],second["prediction"])
        self.assertEqual(first["checkpoint_sha256"],second["checkpoint_sha256"])
        self.assertEqual(len(set(first["queries"])),16)
        self.assertTrue(all(q in range(4096) for q in first["queries"]))
        held=source.CausalWorld(400).public_view().held_inputs
        matched=model.replay_exact_prior(first["queries"],first["answers"],held)
        self.assertEqual(first["prediction"],matched)


if __name__=="__main__":
    unittest.main()

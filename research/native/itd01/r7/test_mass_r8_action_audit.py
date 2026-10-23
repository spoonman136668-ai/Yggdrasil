"""Mass Research R8 exact public action-causal interface falsification tests."""
import ast
import inspect
import itertools
import unittest
from pathlib import Path
import mass_r8_action_audit as m
from native_cells import Colony


class PublicActionCausalInformation(unittest.TestCase):
    def test_two_frozen_families_have_indistinguishable_native_input_but_opposite_public_actions(self):
        for family in m.FAMILIES:
            with self.subTest(family=family):
                x=m.paired_worlds(family)
                self.assertEqual(x["worlds"],2)
                self.assertEqual(x["paired_public_action_interventions_per_world"],32)
                self.assertEqual(x["paired_delayed_public_outcomes_per_world"],32)
                self.assertEqual(x["first_public_feedback_tick"],[2,2])
                self.assertEqual(len(set(x["native_inputs_sha256"])),1)
                self.assertEqual(len(set(x["native_checkpoint_sha256"])),1)
                self.assertEqual(len(set(x["public_action_histories_sha256"])),2)
                self.assertTrue(x["all_paired_learned_states_equal_each_tick"])
                self.assertEqual(x["native_paired_mean_success"],.5)
                self.assertEqual(x["action_aware_control_updates_per_world"],
                                 [32,32])
                self.assertEqual(x["action_aware_control_success_per_world"],
                                 [1.,1.])
                self.assertFalse(x["independent_unfamiliar_task_family_transfer"])

    def test_paired_causal_laws_are_distinct_and_rewards_identical_under_complementary_interventions(self):
        for family in m.FAMILIES:
            for bits in m.SENSORS:
                with self.subTest(family=family,sensors=bits):
                    targets=[m._target(family,mode,bits) for mode in (0,1)]
                    self.assertEqual(targets[0]^targets[1],1)
                    for action in (0,1):
                        self.assertEqual(
                            m._public_result(family,0,bits,action),
                            m._public_result(family,1,bits,1-action))
        self.assertEqual(len(m.SENSORS),16)

    def test_independently_trained_public_action_memory_needs_actual_actions(self):
        for bits in m.SENSORS:
            control=m.ActionAwareEpisodicControl()
            with self.assertRaisesRegex(ValueError,"UNTRAINED_SENSOR"):
                control.choose(bits)
            control.observe_completed(bits,0,False)
            control.observe_completed(bits,1,True)
            self.assertEqual(control.choose(bits),1)
            self.assertEqual(control.public_updates,2)
            with self.assertRaisesRegex(AssertionError,"INCONSISTENT"):
                control.observe_completed(bits,1,False)

    def test_early_delayed_feedback_rejected_and_public_state_not_mutated(self):
        p=Colony()
        baseline=p.checkpoint()
        with self.assertRaisesRegex(ValueError,"EARLY_PRIVATE"):
            p.learn_completed_public_feedback(
                "A",(False,True,False,True),True,1)
        self.assertEqual(baseline,p.checkpoint())
        self.assertFalse(m.audit()["original_r7_cohorts_rerun"])
        self.assertEqual(p.checkpoint(),baseline)

    def test_exact_original_interface_omits_action_and_frozen_audit_has_no_source_generator(self):
        self.assertNotIn("action",inspect.signature(Colony.predict).parameters)
        self.assertNotIn("action",inspect.signature(
            Colony.learn_completed_public_feedback).parameters)
        s=Path(m.__file__).read_text(encoding="utf-8")
        tree=ast.parse(s)
        blocked={"study","gates","PublicDevGenerator","_examples",
                 "dispatch","subprocess","download","execute_development"}
        for node in ast.walk(tree):
            if isinstance(node,ast.Call):
                f=node.func
                name=f.id if isinstance(f,ast.Name) else (
                    f.attr if isinstance(f,ast.Attribute) else "?")
                self.assertNotIn(name,blocked)
        x=m.audit()
        self.assertEqual(x["disposition"],
              "YGG_R7_ACTION_OMITTED_CAUSAL_HISTORY_NONIDENTIFIABILITY_PROVED")
        self.assertEqual(x["tested_causal_law_families"],list(m.FAMILIES))
        self.assertEqual(x["per_model_cpu_or_rss_parity"],"NOT_QUALIFIED")
        self.assertEqual(x["scientific_admission"],"NONE")
        self.assertFalse(x["independently_unfamiliar_original_source_first_use"])

if __name__=="__main__":
    unittest.main()

"""NKR-14: frozen unseen-family, 256-completion bound, provenance negatives."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

from yggdrasil.native_operator_discovery import NativeOperatorDiscovery
from yggdrasil.native_intervention_repair import digest
from yggdrasil.public_causal_cells import PublicCausalCells

ROOT=Path(__file__).resolve().parents[1]
path=ROOT/"research/contrib/chatgpt/NKR-14/experiment.py"
spec=importlib.util.spec_from_file_location("nkr14_new_families",path)
study=importlib.util.module_from_spec(spec)
spec.loader.exec_module(study)


class UnseenOperatorFamilyTests(unittest.TestCase):
    def test_frozen_12_outside_family_development_and_bound(self):
        result=study.run_frozen()
        t=result["totals"]
        self.assertEqual(t["worlds"],12)
        self.assertEqual(t["cold_queries"],192)
        self.assertEqual(t["old_retention_correct"],384)
        self.assertEqual(t["unrestricted_control_correct"],96)
        self.assertEqual(t["unrestricted_control_coverage"],96)
        self.assertEqual(t["unrestricted_control_confident_wrong"],0)
        self.assertEqual(t["unrestricted_control_abstentions"],96)
        self.assertEqual(t["independent_consistent_truth_tables_per_world"],256)
        self.assertEqual(t["in_family_full_truth_table_matches"],0)
        self.assertEqual(t["visible_hidden_context_overlaps"],0)
        self.assertEqual(t["native_cold_coverage"]+
                         t["native_cold_abstentions"],192)
        self.assertEqual(t["native_cold_coverage"],
                         t["native_cold_correct"]+t["native_confident_wrong"])
        self.assertTrue(result["frozen_falsification_criteria_met"])
        self.assertFalse(result["science_pass"])
        self.assertFalse(result["native_accepted"])
        self.assertFalse(result["function_family_labels_visible_to_learner"])

    def test_every_true_mechanism_is_outside_preprogrammed_positive_and_family(self):
        for world in range(12):
            with self.subTest(world=world):
                truth=tuple(study.hidden_operator(world,x) for x in range(16))
                self.assertEqual(len(truth),16)
                self.assertTrue(set(truth)<={0,1})
                for mask in range(1,16):
                    conjunction=tuple(int((x&mask)==mask) for x in range(16))
                    self.assertNotEqual(truth,conjunction)

    def test_exact_256_unrestricted_completions_with_zero_cold_label_leak(self):
        for world in range(12):
            env=study.HiddenWorld(world)
            source=study.source_visible_actions(env)
            ctl=study.UnrestrictedBooleanEffectControl(source)
            self.assertEqual(len(source),16)
            self.assertEqual(len(ctl.effects),8)
            self.assertEqual(ctl.completions,256)
            self.assertEqual(set(ctl.effects),set(study.TRAIN))
            self.assertFalse(set(ctl.effects)&set(study.COLD))
            for x in study.COLD:
                self.assertEqual(ctl.predict(x,0),env.intervene(x,0))
                self.assertIsNone(ctl.predict(x,1))

    def test_warm_checkpoint_never_mutated_even_if_new_family_unsupported(self):
        before=PublicCausalCells().snapshot()
        for world in range(12):
            env=study.HiddenWorld(world)
            rows=study.warmup(env)
            warm=study.freeze_bundle(
                "nkr14-test-warm-"+digest(study.canonical(rows))[:16],rows)
            model=NativeOperatorDiscovery.from_warmup(warm,digest(warm))
            saved=model.checkpoint()
            public=study.source_visible_actions(env)
            # public source ID is derived only from observed bytes, not the
            # hidden world ID or its operator category.
            data=study.freeze_bundle(
                "nkr14-test-public-"+digest(study.canonical(public))[:16],public)
            changed,receipt=model.stage_public_interventions(data,digest(data))
            self.assertEqual(saved,model.checkpoint())
            if changed.operator_discovered:
                restored=NativeOperatorDiscovery(
                    changed.checkpoint(),changed.checkpoint_sha256)
                self.assertEqual(restored.operator_masks,changed.operator_masks)
                self.assertFalse(restored.predict(9,1)["native_accepted"])
            else:
                self.assertEqual(changed.checkpoint(),saved)
                self.assertIn(receipt["classification"],(
                    "INSUFFICIENT_CHANGE_EVIDENCE",
                    "UNSUPPORTED_CONTEXT_BASE_ABSTAIN",
                    "NO_SUPPORTED_NEW_OPERATOR_ABSTAIN"))
        self.assertEqual(PublicCausalCells().snapshot(),before)

    def test_bad_source_sequence_and_query_values_refuse_to_infer(self):
        env=study.HiddenWorld(0)
        train=study.source_visible_actions(env)
        reversed_rows=list(reversed(train))
        with self.assertRaisesRegex(ValueError,"NKR14_VISIBLE_INTERVENTION_CONTRACT"):
            study.UnrestrictedBooleanEffectControl(reversed_rows)
        control=study.UnrestrictedBooleanEffectControl(train)
        for query in ((16,1),(6,2),(-1,0),(True,1)):
            with self.subTest(query=query),self.assertRaises(ValueError):
                control.predict(*query)
        with self.assertRaises(ValueError):
            study.HiddenWorld(12)
        with self.assertRaises(ValueError):
            env.intervene(17,1)

    def test_all_unknown_binary_effects_remain_underdetermined(self):
        # Construct two complete truth tables with IDENTICAL eight training
        # effects but OPPOSITE outcome on a source-hidden query. No learner
        # with just these observations can know that cold output without a
        # prior about operator structure or an additional public action.
        env=study.HiddenWorld(8)
        data=study.source_visible_actions(env)
        fitted=study.UnrestrictedBooleanEffectControl(data)
        hidden=study.COLD[0]
        observed=fitted.effects
        low=dict(observed,**{})
        low[hidden]=0
        high=dict(observed)
        high[hidden]=1
        self.assertEqual({x:low[x] for x in study.TRAIN},
                         {x:high[x] for x in study.TRAIN})
        self.assertNotEqual(low[hidden],high[hidden])
        self.assertIsNone(fitted.predict(hidden,1))
        self.assertEqual(fitted.completions,1<<len(study.COLD))


if __name__=="__main__":
    unittest.main()

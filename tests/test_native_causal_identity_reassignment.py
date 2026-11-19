"""CKAD25-AC: identity aliases cannot transfer source risk without a mapping."""
from fractions import Fraction
import importlib.util
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parents[1] / "research/contrib/chatgpt/CKAD25-AC/run.py"


def child():
    spec=importlib.util.spec_from_file_location("ckad25ac_frozen_scope",HERE)
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


class SourceIdentityTransferNegatives(unittest.TestCase):
    def test_uniform_hidden_reassignment_erases_nonuniform_historical_prior(self):
        mod=child()
        ab=mod.parent()
        source,candidates=ab.roster(78999)
        laws=ab.generator(78999,source)
        # Deliberately imbalanced actual witnessed outcomes: address 1 occurs
        # twice and has contradictory outcomes, others one or zero.
        changed=candidates[1]
        packets=[
            mod.record(ab,laws["C"],[changed,candidates[0]],changed),
            mod.record(ab,laws["C"],[changed,candidates[2]],changed),
            mod.record(ab,laws["C"],[candidates[1],candidates[3]],changed),
        ]
        posterior=mod.uniform_hidden_role_mapping_marginal(
            packets,candidates,laws["C"],ab)
        self.assertEqual(posterior,{k:Fraction(1,4) for k in candidates})

    def test_action_role_permutation_has_no_effect_on_source_fit_evidence(self):
        mod=child()
        ab=mod.parent()
        source,candidates=ab.roster(78999)
        w=ab.generator(78999,source)["C"]
        baseline=mod.record(ab,w,source)
        role=candidates[0]
        # Every source-training action and arbitrary four diagnostic actions
        # remain bit-identical under the unobserved role reassignment.
        permuted={k:v for k,v in zip(candidates,reversed(candidates))}
        self.assertEqual(mod.record(ab,w,source,role),baseline)
        self.assertEqual(mod.record(ab,w,source,permuted[role]),baseline)
        self.assertNotEqual(mod.record(ab,w,candidates,role),
                            mod.record(ab,w,candidates,permuted[role]))

    def test_no_held_future_evidence_required_to_infer_conventional_null(self):
        mod=child()
        ab=mod.parent()
        source,candidates=ab.roster(78999)
        w=ab.generator(78999,source)["C"]
        prior=[mod.record(ab,w,candidates[:2],candidates[0])]
        original=list(map(list,prior[0]))
        mod.uniform_hidden_role_mapping_marginal(prior,candidates,w,ab)
        self.assertEqual(prior[0],original)


if __name__=="__main__":
    unittest.main()

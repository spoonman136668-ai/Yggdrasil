"""WSP-162: frozen source-free contradiction falsification.

No hidden regime label is supplied to a predictor. The evaluator simulates
two incompatible observed outcomes for exact same public state/action.
This is NOT independently sourced science or a learned contextual model.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import sys
import unittest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "WSP-159"))
sys.path.insert(0, str(HERE / "WSP-160"))
sys.path.insert(0, str(HERE / "WSP-161"))

from public_boundary import PublicTransition
from direct_weights import ProgrammedPublicDynamics
from projected_repair import ProjectedWeightRepair
from test_direct_weights import independent_batch_ridge
from overlap_certificate import certificate, paired_rmse, ex_post_midpoint_score

CHANGE = (0.4, -0.3, 0.2, -0.1)
SEEDS = (1019, 1231, 1429)


def old_target(state, action):
    sign = 2*action-1
    return tuple(
        state[k] +
        (0.06, -0.04, 0.03, -0.02)[k] +
        (0.05, -0.03, 0.025, -0.015)[k]*state[k % 3] +
        sign*(0.09, -0.065, 0.04, -0.025)[k] +
        sign*0.017*state[(k+1) % 3]
        for k in range(4)
    )


def fixture(seed):
    rng = random.Random(seed)
    # Exactly eight public corners with s3=0, each visited under both actions.
    contexts = [(tuple(float(v) for v in (*corner, 0.0)), action)
                for corner in itertools.product((-0.75, 0.75),
                                                (-0.5, 0.5), (-0.4, 0.4))
                for action in (0, 1)]
    assert len(contexts) == 16
    rng.shuffle(contexts)
    old_unique, new_unique = [], []
    for state, action in contexts:
        first = old_target(state, action)
        second = tuple(first[i]+CHANGE[i] for i in range(4))
        old_unique.append(PublicTransition.from_public(
            observation=state, action=action, next_observation=first,
            reward=1.0, terminated=False, truncated=False))
        new_unique.append(PublicTransition.from_public(
            observation=state, action=action, next_observation=second,
            reward=1.0, terminated=False, truncated=False))

    def repeat(rows, count):
        result = [row for _ in range(count) for row in rows]
        rng.shuffle(result)
        return result

    return (old_unique, new_unique, repeat(old_unique, 6),
            repeat(old_unique, 4), repeat(new_unique, 6),
            repeat(new_unique, 4))


def fit_native(rows, starting=None):
    model = starting if starting is not None else ProgrammedPublicDynamics()
    for row in rows:
        model = model.observe(
            row.observation, row.action, row.next_observation)
    return model


def rmse(rows, predict):
    squares = []
    for row in rows:
        out = predict(row.observation, row.action)
        squares.extend((out[k]-row.next_observation[k])**2
                       for k in range(4))
    return math.sqrt(math.fsum(squares)/(4*len(rows)))


def held_joint_rmse(old_valid, new_valid, predictor):
    # Disjoint ROWS from FIT, but deliberately repeat identical public INPUTS;
    # they are NOT novel input generalization and are never called so.
    if len(old_valid) != 64 or len(new_valid) != 64:
        raise AssertionError("frozen VALID budget")
    return math.sqrt((rmse(old_valid, predictor)**2 +
                      rmse(new_valid, predictor)**2)/2)


class OverlapImpossibilityTests(unittest.TestCase):
    def test_frozen_overlapping_witnesses_and_matched_controls(self):
        receipts = []
        for seed in SEEDS:
            (old_unique, new_unique, old_fit, old_valid,
             new_fit, new_valid) = fixture(seed)
            cert = certificate(old_unique, new_unique)
            self.assertEqual(cert["paired_contexts"], 16)
            self.assertEqual(cert["conflicting_contexts"], 16)
            self.assertGreater(cert["irreducible_joint_rmse"], 0.10)
            self.assertAlmostEqual(cert["irreducible_joint_rmse"],
                                   math.sqrt(0.3/16), places=12)
            midpoint = ex_post_midpoint_score(old_unique, new_unique)
            self.assertAlmostEqual(midpoint, cert["irreducible_joint_rmse"],
                                   places=12)

            old_base = fit_native(old_fit)
            frozen_sha = hashlib.sha256(old_base.checkpoint()).hexdigest()
            anchors = [(r.observation, r.action) for r in old_unique]
            protected = ProjectedWeightRepair(old_base, anchors)
            self.assertEqual(protected.protected_rank, 8)
            rejected = 0
            for row in new_fit:
                candidate, status = protected.observe(
                    row.observation, row.action, row.next_observation)
                self.assertIs(candidate, protected)
                self.assertEqual(status, "UNIDENTIFIABLE")
                rejected += 1
            self.assertEqual(rejected, 96)
            self.assertEqual(protected.seen, 0)
            self.assertEqual(protected._base.checkpoint(),old_base.checkpoint())
            old_drift = max(abs(
                protected.predict(row.observation,row.action)[k]-
                old_base.predict(row.observation,row.action)[k])
                for row in old_valid for k in range(4))
            self.assertEqual(old_drift, 0.0)
            self.assertEqual(hashlib.sha256(
                old_base.checkpoint()).hexdigest(), frozen_sha)

            continued = fit_native(new_fit, starting=old_base)
            # The conventional baseline sees exactly the same labels and
            # counts as continued native RLS; no hidden family identifiers.
            batch = independent_batch_ridge(
                old_fit + new_fit, with_action=True)

            joint_protected = held_joint_rmse(
                old_valid, new_valid, protected.predict)
            joint_continued = held_joint_rmse(
                old_valid, new_valid, continued.predict)
            joint_batch = held_joint_rmse(
                old_valid, new_valid, batch)
            for value in (joint_protected,joint_continued,joint_batch):
                self.assertGreaterEqual(
                    value+1e-10,cert["irreducible_joint_rmse"])
            self.assertAlmostEqual(
                paired_rmse(old_unique,new_unique,batch),
                joint_batch, places=12)
            self.assertNotIn("causal_gym", sys.modules)
            receipts.append({
                "seed":seed,
                "unique_public_input_identities":16,
                "old_fit":96,"new_fit":96,
                "old_valid":64,"new_valid":64,
                "contradictions":16,
                "irreducible_joint_rmse_floor":cert["irreducible_joint_rmse"],
                "ex_post_midpoint_joint_rmse":midpoint,
                "protected_joint_rmse":joint_protected,
                "continued_rls_joint_rmse":joint_continued,
                "fully_fitted_batch_ridge_joint_rmse":joint_batch,
                "frozen_base_old_rmse":rmse(old_valid,old_base.predict),
                "frozen_base_new_rmse":rmse(new_valid,old_base.predict),
                "continued_old_rmse":rmse(old_valid,continued.predict),
                "continued_new_rmse":rmse(new_valid,continued.predict),
                "projected_refusals":rejected,
                "protected_old_prediction_drift":old_drift,
                "old_model_sha256_unchanged":frozen_sha,
                "paired_public_fingerprint":cert["public_pair_sha256"],
                "original_external_source_actions":0
            })
        print("WSP162_FROZEN_OVERLAP_RESULTS="+json.dumps(
            receipts,sort_keys=True,separators=(",",":")))

    def test_exactly_same_public_inputs_force_nonzero_error(self):
        old,new,*_ = fixture(1019)
        cert=certificate(old,new)
        # Exact algebra on independent paired targets, not postscore tuning.
        for k in range(4):
            self.assertAlmostEqual(
                sum((new[i].next_observation[k]-
                     old[i].next_observation[k])**2 for i in range(16))/16,
                CHANGE[k]**2, places=12)
        midpoint=ex_post_midpoint_score(old,new)
        self.assertAlmostEqual(midpoint**2,
                               cert["irreducible_joint_mse"],places=12)
        frozen=fit_native(fixture(1019)[2])
        self.assertGreaterEqual(
            paired_rmse(old,new,frozen.predict)+1e-10,
            cert["irreducible_joint_rmse"])

    def test_negative_no_conflict_and_order_invariance(self):
        old,new,*_ = fixture(1231)
        self.assertEqual(certificate(old,old)["conflicting_contexts"],0)
        self.assertEqual(certificate(old,old)["irreducible_joint_rmse"],0)
        self.assertEqual(ex_post_midpoint_score(old,old),0)
        reversed_certificate=certificate(list(reversed(old)),
                                         list(reversed(new)))
        self.assertEqual(certificate(old,new),reversed_certificate)

    def test_mismatched_duplicate_or_privileged_public_data_refused(self):
        old,new,*_=fixture(1429)
        with self.assertRaisesRegex(ValueError,"NOT_IDENTICAL_PUBLIC"):
            certificate(old,new[1:])
        with self.assertRaisesRegex(ValueError,"DUPLICATE"):
            certificate(old,old[:15]+old[:1])
        with self.assertRaisesRegex(ValueError,"PUBLIC_RECORD"):
            certificate([dict(action=0)],new)
        with self.assertRaisesRegex(ValueError,"PUBLIC_FIELD_SET"):
            PublicTransition.from_public(**{
                **old[0].model_input(),"u_wind":0.123})
        bad=PublicTransition.from_public(**{
            **new[0].model_input(),"reward":-1})
        with self.assertRaisesRegex(ValueError,"ONLY_NEXT_STATE"):
            certificate(old,[bad]+new[1:])
        with self.assertRaisesRegex(ValueError,"PREDICTION"):
            paired_rmse(old,new,lambda s,a: (math.nan,0,0,0))
        with self.assertRaisesRegex(ValueError,"PREDICTION_SHAPE"):
            paired_rmse(old,new,lambda s,a: (0,0,0))

    def test_same_public_consequences_cannot_be_magic_repaired(self):
        old,new,old_fit,old_valid,new_fit,_=fixture(1019)
        model=fit_native(old_fit)
        anchors=[(r.observation,r.action) for r in old]
        project=ProjectedWeightRepair(model,anchors)
        old_checkpoint=project.checkpoint()
        updated,status=project.observe(
            new_fit[0].observation,
            new_fit[0].action,new_fit[0].next_observation)
        self.assertEqual(status,"UNIDENTIFIABLE")
        self.assertIs(updated,project)
        self.assertEqual(project.checkpoint(),old_checkpoint)
        restored=ProjectedWeightRepair.restore(old_checkpoint)
        self.assertEqual(restored.checkpoint(),old_checkpoint)
        self.assertEqual(
            [restored.predict(r.observation,r.action) for r in old_valid],
            [model.predict(r.observation,r.action) for r in old_valid])


if __name__=="__main__":
    unittest.main()

"""WSP160: source-free direct-weight engineering and matched controls.

Only fabricated numerical transitions. Do NOT import/instantiate causal_gym.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import random
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "WSP-159"))
from public_boundary import PublicTransition
from direct_weights import (
    ProgrammedPublicDynamics, MAGIC, WIDTH, OUTPUTS, MAX_ROWS, CHECKPOINT_BYTES
)


def fixtures(seed):
    rng = random.Random(seed)
    rows = []
    # Authored development-only linear state law; NO original source or
    # private source state/law is given to the learner.
    for _ in range(256):
        s = tuple(rng.uniform(-1.0, 1.0) for k in range(4))
        a = rng.randrange(2)
        sign = 2*a - 1
        next_state = tuple(
            s[k] + (0.07, -0.03, 0.04, -0.05)[k]
            + (0.05, 0.02, -0.04, 0.03)[k] * s[k]
            + 0.015 * s[(k+1) % 4]
            + sign * ((0.28, -0.19, 0.15, -0.13)[k]
                      + 0.035 * s[(k+2) % 4])
            for k in range(4)
        )
        record = PublicTransition.from_public(
            observation=s, action=a, next_observation=next_state,
            reward=1.0, terminated=False, truncated=False)
        rows.append(record)
    return rows[:192], rows[192:]


def independent_feature(s, action, with_action):
    if not with_action:
        return [1.0, *s]
    sign = float(2*action - 1)
    return [1.0, *s, sign, *(sign*v for v in s)]


def solve_gaussian(a, b):
    """Independent normal-equation solver with pivoting; does not read RLS."""
    n = len(b)
    aug = [list(a[i]) + [b[i]] for i in range(n)]
    for c in range(n):
        pivot = max(range(c, n), key=lambda i: abs(aug[i][c]))
        if abs(aug[pivot][c]) < 1e-14:
            raise AssertionError("independent ridge unexpectedly singular")
        aug[c], aug[pivot] = aug[pivot], aug[c]
        diag = aug[c][c]
        aug[c] = [z/diag for z in aug[c]]
        for i in range(n):
            if i == c:
                continue
            factor = aug[i][c]
            aug[i] = [aug[i][j]-factor*aug[c][j] for j in range(n+1)]
    return tuple(aug[i][-1] for i in range(n))


def independent_batch_ridge(train, with_action=True):
    width = 10 if with_action else 5
    gram = [[float(i==j) for j in range(width)] for i in range(width)]
    rhs = [[0.0 for _ in range(4)] for _ in range(width)]
    for r in train:
        v = independent_feature(r.observation, r.action, with_action)
        y = [r.next_observation[k] - r.observation[k] for k in range(4)]
        for i in range(width):
            for j in range(width):
                gram[i][j] += v[i]*v[j]
            for k in range(4):
                rhs[i][k] += v[i]*y[k]
    weights = tuple(solve_gaussian(gram, [rhs[i][k] for i in range(width)])
                    for k in range(4))
    def predict(obs, action):
        features = independent_feature(obs, action, with_action)
        return tuple(obs[k] + math.fsum(w*f for w, f in zip(weights[k], features))
                     for k in range(4))
    return predict


def rmse(rows, predict):
    total = 0.0
    for r in rows:
        got = predict(r.observation, r.action)
        total += math.fsum((got[k]-r.next_observation[k])**2 for k in range(4))
    return math.sqrt(total/(4*len(rows)))


class DirectWeightProgramTests(unittest.TestCase):
    def test_frozen_three_seed_matched_controls_and_new_weights(self):
        receipts = []
        for seed in (211, 337, 503):
            fit, valid = fixtures(seed)
            program = ProgrammedPublicDynamics()
            initial = program.checkpoint()
            self.assertEqual(program.seen, 0)
            for r in fit:
                program = program.observe(r.observation, r.action, r.next_observation)
            self.assertEqual(program.seen, 192)
            self.assertNotEqual(initial, program.checkpoint())
            control = independent_batch_ridge(fit, with_action=True)
            erased = independent_batch_ridge(fit, with_action=False)
            rng = random.Random(seed + 999)
            actions = [r.action for r in fit]
            rng.shuffle(actions)
            permuted = ProgrammedPublicDynamics()
            for r, wrong_action in zip(fit, actions):
                permuted = permuted.observe(r.observation, wrong_action, r.next_observation)
            exact = ProgrammedPublicDynamics.restore(program.checkpoint())
            self.assertEqual(exact.checkpoint(), program.checkpoint())
            native_error = rmse(valid, program.predict)
            matched_error = rmse(valid, control)
            erased_error = rmse(valid, erased)
            permuted_error = rmse(valid, permuted.predict)
            zero_error = rmse(valid, lambda s, a: s)
            max_diff = max(abs(program.predict(r.observation,r.action)[i]-
                               control(r.observation,r.action)[i])
                           for r in valid for i in range(4))
            self.assertLessEqual(max_diff, 1e-8)
            self.assertLess(native_error, 0.10)
            self.assertGreater(erased_error-native_error, 0.01)
            self.assertGreater(permuted_error, native_error)
            self.assertEqual(
                [program.predict(r.observation,r.action) for r in valid],
                [exact.predict(r.observation,r.action) for r in valid])
            receipts.append(dict(
                seed=seed, fit_rows=len(fit), valid_rows=len(valid),
                native_rmse=round(native_error, 9),
                batch_ridge_rmse=round(matched_error, 9),
                action_erased_rmse=round(erased_error, 9),
                permuted_action_rmse=round(permuted_error, 9),
                zero_rmse=round(zero_error, 9),
                max_ridge_prediction_gap=max_diff,
                checkpoint_bytes=len(program.checkpoint()),
                checkpoint_sha256=hashlib.sha256(program.checkpoint()).hexdigest(),
                original_source_actions=0))
        self.assertNotIn("causal_gym", sys.modules)
        print("WSP160_FROZEN_SOURCEFREE_METRICS=" +
              json.dumps(receipts, sort_keys=True, separators=(",", ":")))

    def test_immutable_updates_cold_continuation(self):
        fit, valid = fixtures(211)
        p = ProgrammedPublicDynamics()
        original = p.checkpoint()
        after = p.observe(fit[0].observation, fit[0].action,
                          fit[0].next_observation)
        self.assertEqual(p.seen, 0)
        self.assertEqual(p.checkpoint(), original)
        self.assertEqual(after.seen, 1)
        cold = ProgrammedPublicDynamics.restore(after.checkpoint())
        follow = fit[1]
        self.assertEqual(cold.observe(follow.observation, follow.action,
                                      follow.next_observation).checkpoint(),
                         after.observe(follow.observation, follow.action,
                                       follow.next_observation).checkpoint())
        self.assertEqual(ProgrammedPublicDynamics.restore(original).checkpoint(), original)
        self.assertEqual(len(original), CHECKPOINT_BYTES)

    def test_invalid_public_fields_cannot_enter_weights(self):
        p = ProgrammedPublicDynamics()
        for action in (-1, 2, "0", 1.0, True, None):
            with self.subTest(action=action), self.assertRaises(ValueError):
                p.observe([0,0,0,0], action, [1,1,1,1])
        for observation in ([0,0,0], [0,0,0,0,0], "x", None, [0,True,0,0],
                            [0,float("inf"),0,0], [0,float("nan"),0,0],
                            [10**1000,0,0,0]):
            with self.subTest(observation=str(observation)[:32]), self.assertRaises(ValueError):
                p.observe(observation, 1, [1,1,1,1])
            with self.subTest(next_observation=str(observation)[:32]), self.assertRaises(ValueError):
                p.observe([0,0,0,0], 1, observation)
        with self.assertRaises(TypeError):
            p.observe([0,0,0,0], 1, [1,1,1,1], private_wind=0.2)
        with self.assertRaises(ValueError):
            p.observe([1e308]*4, 1, [-1e308]*4)

    def test_corrupt_checkpoint_fails_closed(self):
        r = fixtures(211)[0][0]
        state = ProgrammedPublicDynamics().observe(r.observation, r.action,
                                                    r.next_observation)
        raw = state.checkpoint()
        for bad in (raw[:-1], b"XXXX"+raw[4:], raw+b"extra", "str",
                    raw[:12]+bytes((raw[12]^1,))+raw[13:]):
            with self.subTest(size=len(bad) if type(bad)==bytes else -1):
                with self.assertRaises(ValueError):
                    ProgrammedPublicDynamics.restore(bad)
        # Rehashed malicious covariance must not bypass shape / SPD diagonal.
        modified = bytearray(raw)
        struct.pack_into(">d", modified, 6, -1.0)
        modified[-32:] = hashlib.sha256(modified[:-32]).digest()
        with self.assertRaisesRegex(ValueError, "DIAGONAL"):
            ProgrammedPublicDynamics.restore(bytes(modified))
        # Rehashed nonfinite coefficient is forbidden even with a valid digest.
        modified = bytearray(raw)
        struct.pack_into(">d", modified, 6 + 8*100, math.nan)
        modified[-32:] = hashlib.sha256(modified[:-32]).digest()
        with self.assertRaisesRegex(ValueError, "NONFINITE"):
            ProgrammedPublicDynamics.restore(bytes(modified))

    def test_hard_observation_budget(self):
        p = ProgrammedPublicDynamics()
        maximum = p._from_state(p._weights, p._inverse, MAX_ROWS)
        with self.assertRaisesRegex(ValueError, "CAP"):
            maximum.observe([0,0,0,0], 0, [0,0,0,0])
        restored = ProgrammedPublicDynamics.restore(maximum.checkpoint())
        self.assertEqual(restored.seen, MAX_ROWS)

    def test_untrained_zero_update_and_public_state(self):
        p = ProgrammedPublicDynamics()
        self.assertEqual(p.predict((1,2,3,4),0), (1.,2.,3.,4.))
        self.assertEqual(p.predict((1,2,3,4),1), (1.,2.,3.,4.))
        with self.assertRaises(ValueError):
            p.predict((1,float("inf"),3,4), 0)


if __name__ == "__main__":
    unittest.main()

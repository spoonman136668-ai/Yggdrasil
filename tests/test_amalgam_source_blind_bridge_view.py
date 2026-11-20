"""Pure fixture tests: privileged raw Gym info must never reach policy views."""
from dataclasses import FrozenInstanceError, fields
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] /
          "research/contrib/chatgpt/CAUSAL-AMALGAM/source_blind_bridge_view.py")
SPEC = spec_from_file_location("amalgam_source_blind_view_for_tests", SOURCE)
VIEW = module_from_spec(SPEC)
import sys
sys.modules[SPEC.name] = VIEW
SPEC.loader.exec_module(VIEW)


def observation(state=20, time=0, *, notify=False):
    return {"state": state, "relative_time": time,
            "env_change": {"P": int(notify)},
            "delta_change": {"P": 0.85 if notify else 0.0}}


def private_info(prob=None):
    if prob is None:
        prob = [0.9, 0.06, 0.04]
    return {"prob": prob, "transition_prob": prob,
            "Ground Truth Env Change": {"P": 1},
            "Ground Truth Delta Change": {"P": 0.85},
            "source_family": "PRIVILEGED", "hidden_seed": 996100,
            "unwrapped_transition": {"unsafe": True}}


class SourceBlindBridgeViewTests(unittest.TestCase):
    def test_reset_discards_probability_and_all_private_metadata(self):
        a = VIEW.from_reset((observation(), private_info([.90, .06, .04])))
        b = VIEW.from_reset((observation(), private_info([.05, .47, .48])))
        self.assertEqual(a, b)
        self.assertEqual(a.state, 20)
        self.assertEqual(a.step, 0)
        self.assertIsNone(a.reward)
        self.assertFalse(a.terminated)
        self.assertFalse(a.truncated)

    def test_step_discard_info_across_different_hidden_regimes(self):
        for state, reward, terminated in ((21, 0, False), (13, -1, True),
                                          (23, 1, True)):
            with self.subTest(state=state):
                raw_a = (observation(state, 1), reward, terminated, False,
                         private_info([.9, .06, .04]))
                raw_b = (observation(state, 1), reward, terminated, False,
                         private_info([.05, .47, .48]))
                self.assertEqual(VIEW.from_step(raw_a, step=1),
                                 VIEW.from_step(raw_b, step=1))

    def test_ground_truth_change_notifications_are_not_observable(self):
        unnotified = VIEW.from_step((observation(22, 1, notify=False),
                                   0, False, False, private_info()), step=1)
        source_notified = VIEW.from_step((observation(22, 1, notify=True),
                                        0, False, False, private_info()), step=1)
        self.assertEqual(unnotified, source_notified)
        self.assertEqual([x.name for x in fields(VIEW.PublicView)],
                         ["state", "step", "reward", "terminated", "truncated"])

    def test_private_info_is_never_inspected(self):
        class Poison:
            def __getattribute__(self, name):
                raise AssertionError("private info attribute was accessed")
            def __iter__(self):
                raise AssertionError("private info was iterated")
            def __repr__(self):
                raise AssertionError("private info was serialized")
        x = VIEW.from_reset((observation(), Poison()))
        y = VIEW.from_step((observation(21, 1), 0, False, False, Poison()),
                           step=1)
        self.assertEqual(x.state, 20)
        self.assertEqual(y.state, 21)

    def test_returns_immutable_new_primitives_without_original_reference(self):
        info = private_info()
        obs = observation(21, 1)
        result = VIEW.from_step((obs, 0, False, False, info), step=1)
        obs["state"] = 13
        info["prob"][0] = -999
        self.assertEqual(result.state, 21)
        self.assertFalse(hasattr(result, "__dict__"))
        with self.assertRaises(FrozenInstanceError):
            result.state = 13

    def test_only_public_transition_and_reward_consequences_visible(self):
        x = VIEW.from_step((observation(13, 4), -1, True, False,
                            private_info()), step=4)
        self.assertEqual((x.state, x.step, x.reward, x.terminated,
                          x.truncated), (13, 4, -1, True, False))

    def test_reset_and_step_shapes_reject_bad_raw_payload(self):
        for invalid in ({}, (), (observation(),),
                        (observation(), {}, "extra")):
            with self.subTest(reset_type=str(type(invalid))):
                with self.assertRaisesRegex(ValueError, "SOURCE_BLIND_RESET_SHAPE"):
                    VIEW.from_reset(invalid)
        for invalid in ({}, (), (observation(21, 1), 0),
                        (observation(21, 1), 0, False, False)):
            with self.subTest(step_type=str(type(invalid))):
                with self.assertRaisesRegex(ValueError, "SOURCE_BLIND_STEP_SHAPE"):
                    VIEW.from_step(invalid, step=1)

    def test_observation_rejects_unrecognized_fields_instead_of_forwarding(self):
        bad = observation()
        bad["source_probability"] = [0.05, .47, .48]
        with self.assertRaisesRegex(ValueError, "SOURCE_BLIND_OBSERVATION_SCHEMA"):
            VIEW.from_reset((bad, private_info()))
        bad = observation()
        del bad["relative_time"]
        with self.assertRaisesRegex(ValueError, "SOURCE_BLIND_OBSERVATION_SCHEMA"):
            VIEW.from_reset((bad, {}))

    def test_invalid_state_type_or_bounds_fail_closed(self):
        for val in (True, 20.0, "20", -1, 40):
            with self.subTest(state=val):
                with self.assertRaisesRegex(ValueError, "SOURCE_BLIND_PUBLIC_STATE"):
                    VIEW.from_reset((observation(state=val), {}))

    def test_elapsed_time_must_be_independent_exact_nonbool_integer(self):
        for val in (None, True, 0, 1.0, -1, 1000001):
            with self.subTest(value=val):
                with self.assertRaisesRegex(ValueError, "SOURCE_BLIND_PUBLIC_STEP"):
                    VIEW.from_step((observation(21, 1), 0, False, False, {}),
                                   step=val)
        with self.assertRaisesRegex(ValueError, "SOURCE_BLIND_PUBLIC_STEP"):
            VIEW.from_step((observation(21, 2), 0, False, False, {}), step=1)
        with self.assertRaisesRegex(ValueError, "SOURCE_BLIND_PUBLIC_STEP"):
            VIEW.from_reset((observation(20, 1), {}))

    def test_reward_must_be_original_binary_source_terminal_scalar(self):
        for reward in (True, 0.0, "0", -2, 2):
            with self.subTest(reward=reward):
                with self.assertRaisesRegex(ValueError, "SOURCE_BLIND_SCALAR_REWARD"):
                    VIEW.from_step((observation(21, 1), reward, False, False, {}),
                                   step=1)

    def test_terminated_truncated_flags_must_be_literal_bools(self):
        for terminated, truncated in ((1, False), (True, 0), (None, True)):
            with self.subTest(terminated=terminated, truncated=truncated):
                with self.assertRaisesRegex(ValueError, "SOURCE_BLIND_TERMINAL_FLAGS"):
                    VIEW.from_step((observation(21, 1), 0, terminated, truncated, {}),
                                   step=1)

    def test_public_record_independent_of_order_and_keys_of_info(self):
        left = VIEW.from_step((observation(21, 2), 0, False, False,
                              private_info([.90, .06, .04])), step=2)
        right = VIEW.from_step((observation(21, 2), 0, False, False,
                               {"Ground Truth Delta Change": {"P": 11},
                                "prob": [0, 1, 0], "oracle_action": 3}), step=2)
        self.assertEqual(left, right)

    def test_view_has_no_effectful_source_or_training_api(self):
        public_methods = [name for name in dir(VIEW) if not name.startswith("_")]
        self.assertNotIn("env", public_methods)
        self.assertNotIn("step_source", public_methods)
        self.assertNotIn("reset_source", public_methods)
        self.assertNotIn("train", public_methods)


if __name__ == "__main__":
    unittest.main()

"""Source-free adversarial tests for the public MiniGrid event contract."""
import copy
import unittest

from research.native.itd02.minigrid_memory_event_contract import (
    MISSION, PUBLIC_EVENT_KEYS, SOURCE, project_reset, project_step,
    public_receipt_digest, validate_episode,
)


class PoisonInfo(dict):
    def __iter__(self):
        raise AssertionError("raw info must not be iterated")

    def items(self):
        raise AssertionError("raw info must not be copied")

    def keys(self):
        raise AssertionError("raw info must not be inspected")

    def get(self, *args, **kwargs):
        raise AssertionError("raw info must not be queried")


def public_obs(marker=0, direction=0):
    image = [[[0, 0, 0] for _ in range(7)] for _ in range(7)]
    image[2][3][0] = marker
    return {"image": image, "direction": direction, "mission": MISSION}


def synthetic_public_chain(seed=73, marker=4):
    reset = project_reset(
        (public_obs(marker), PoisonInfo(hidden_grid="SECRET", success_pos=(8, 9), failure_pos=(4, 2))),
        episode_seed=seed, source_receipt=dict(SOURCE))
    step1 = project_step(
        (public_obs(marker, 1), 0.0, False, False,
         PoisonInfo(grid="PRIVATE", object_type="cue", hidden_goal=1)),
        episode_seed=seed, seq=1, action=0, source_receipt=dict(SOURCE))
    step2 = project_step(
        (public_obs(marker, 2), 0.0, False, False,
         PoisonInfo(u=0.25, success_pos=(1, 2))),
        episode_seed=seed, seq=2, action=2, source_receipt=dict(SOURCE))
    terminal = project_step(
        (public_obs(marker, 0), 0.64, True, False,
         PoisonInfo(success_pos=(9, 9), hidden_layout=[1, 2, 3])),
        episode_seed=seed, seq=3, action=1, source_receipt=dict(SOURCE))
    return [reset, step1, step2, terminal]


class MiniGridMemoryPublicEventTests(unittest.TestCase):
    def test_projectors_drop_poison_info_and_keep_raw_public_observation(self):
        events = synthetic_public_chain()
        self.assertTrue(all(set(e) == PUBLIC_EVENT_KEYS for e in events))
        self.assertEqual(events[0]["observation"], public_obs(4))
        self.assertEqual(events[1]["observation"], public_obs(4, 1))
        payload = repr(events)
        for private in ("success_pos", "failure_pos", "hidden_grid", "hidden_goal", "'u'"):
            self.assertNotIn(private, payload)
        self.assertEqual([e["seq"] for e in validate_episode(events)], [0, 1, 2, 3])

    def test_same_public_observation_can_be_reused_without_hidden_context(self):
        a = public_obs(2, 1)
        b = public_obs(2, 1)
        self.assertEqual(a, b)
        self.assertEqual(project_reset((a, {}), episode_seed=1, source_receipt=dict(SOURCE))["observation"],
                         project_reset((b, {}), episode_seed=2, source_receipt=dict(SOURCE))["observation"])
        # This confirms wire compatibility only; it is not a memory-performance result.

    def test_receipt_digest_is_stable_and_binds_public_history(self):
        events = synthetic_public_chain()
        self.assertEqual(public_receipt_digest(events), public_receipt_digest(events))
        changed = synthetic_public_chain(marker=7)
        self.assertNotEqual(public_receipt_digest(events), public_receipt_digest(changed))
        self.assertEqual(len(public_receipt_digest(events)), 64)

    def test_rejects_wrong_source_tuple_shape_mission_and_observation_keys(self):
        bad = dict(SOURCE)
        bad["commit"] = "f" * 40
        with self.assertRaisesRegex(ValueError, "SOURCE_PIN_MISMATCH"):
            project_reset((public_obs(), PoisonInfo()), episode_seed=0, source_receipt=bad)
        for obs in (
            None,
            {"image": [[[0, 0, 0]]], "direction": 0, "mission": MISSION},
            {"image": public_obs()["image"], "direction": 4, "mission": MISSION},
            {"image": public_obs()["image"], "direction": 0, "mission": "other"},
            {"image": public_obs()["image"], "direction": 0, "mission": MISSION, "private": 1},
        ):
            with self.subTest(observation=type(obs).__name__):
                with self.assertRaises(ValueError):
                    project_reset((obs, {}), episode_seed=1, source_receipt=dict(SOURCE))

    def test_rejects_invalid_pixels_actions_rewards_flags_and_shapes(self):
        image = public_obs()["image"]
        bad_img = copy.deepcopy(image)
        bad_img[0][0][0] = 256
        bad_results = [
            (public_obs(), True, False, False, {}),
            (public_obs(), float("nan"), False, False, {}),
            (public_obs(), 1.1, True, False, {}),
            (public_obs(), 0.0, 1, False, {}),
            (public_obs(), 0.0, False, "false", {}),
            ({"image": bad_img, "direction": 0, "mission": MISSION}, 0.0, False, False, {}),
            (public_obs(), 0.0, False, False),
        ]
        for result in bad_results:
            with self.subTest(result=repr(result)[:60]):
                with self.assertRaises(ValueError):
                    project_step(result, episode_seed=1, seq=1, action=2, source_receipt=dict(SOURCE))
        for action in (-1, 7, True, 1.0, "2", None):
            with self.subTest(action=action):
                with self.assertRaises(ValueError):
                    project_step((public_obs(), 0.0, False, False, {}),
                                 episode_seed=1, seq=1, action=action, source_receipt=dict(SOURCE))

    def test_episode_order_seed_and_terminal_closure_are_enforced(self):
        events = synthetic_public_chain()
        extra = [dict(e) for e in events]
        extra[1]["hidden_state"] = 5
        with self.assertRaisesRegex(ValueError, "NONPUBLIC_EVENT_FIELDS"):
            validate_episode(extra)
        changed = [dict(e) for e in events]
        changed[2]["seq"] = 8
        with self.assertRaisesRegex(ValueError, "EVENT_SEQUENCE_DRIFT"):
            validate_episode(changed)
        changed = [dict(e) for e in events]
        changed[1]["episode_seed"] = 99
        with self.assertRaisesRegex(ValueError, "EPISODE_SEED_DRIFT"):
            validate_episode(changed)
        changed = [dict(e) for e in events]
        changed.append(dict(changed[3], seq=4))
        with self.assertRaisesRegex(ValueError, "EVENT_AFTER_TERMINAL|EVENT_SEQUENCE_DRIFT"):
            validate_episode(changed)
        with self.assertRaisesRegex(ValueError, "INVALID_EPISODE_LENGTH"):
            validate_episode(events[:1])


if __name__ == "__main__":
    unittest.main()

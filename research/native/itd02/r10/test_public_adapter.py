"""R10 bounded source-only PUBLIC PIXEL fixtures, not original DoorKey episodes."""
import copy
import json
import subprocess
import sys
import unittest
from research.native.itd02.r10.public_adapter import (
    ACTION_NAMES, DoorKeyPublicAdapter, MISSION, digest, public_cues, public_observation,
)


def frame(front=(1, 0, 0), held=(1, 0, 0), direction=0):
    image = [[[1, 0, 0] for _ in range(7)] for _ in range(7)]
    image[3][5] = list(front)
    image[3][6] = list(held)
    return {"image": image, "direction": direction, "mission": MISSION}


def independent_public_reader(observation):
    """Separate same-public-information conventional parser, no native adapter imports."""
    patch = observation["image"]
    front = patch[3][5]
    carried = patch[3][6] if patch[3][6][0] in (5, 6, 7) else None
    return tuple(front), tuple(carried) if carried else None, observation["direction"]


class SourceOnlyTests(unittest.TestCase):
    def test_all_seven_legal_source_action_ids_preserved(self):
        self.assertEqual(ACTION_NAMES, ("left", "right", "forward", "pickup", "drop", "toggle", "done"))
        for action in range(7):
            bridge = DoorKeyPublicAdapter()
            observation = frame()
            bridge.reset_public(observation)
            self.assertEqual(bridge.submit(action), action)
            event = bridge.complete(observation, 0, False, False)
            self.assertEqual(event["action"], action)
            self.assertEqual(event["action_name"], ACTION_NAMES[action])
            self.assertIsNone(event["pose_delta"])
            self.assertEqual(bridge.events, 1)

    def test_public_key_and_door_changes_reliably_observed(self):
        bridge = DoorKeyPublicAdapter()
        start = frame(front=(5, 4, 0))  # YELLOW KEY, public only.
        bridge.reset_public(start)
        bridge.submit(3)
        holding = frame(front=(1, 0, 0), held=(5, 4, 0))
        picked = bridge.complete(holding, 0, False, False)
        self.assertTrue(picked["visible_key_pickup"])
        self.assertEqual(picked["carried_after"], [5, 4, 0])
        # Intermediate publicly returned chosen action; not a synthetic hidden teleport.
        bridge.submit(2)
        locked = frame(front=(4, 4, 2), held=(5, 4, 0))
        bridge.complete(locked, 0, False, False)
        bridge.submit(5)
        open_door = frame(front=(4, 4, 0), held=(5, 4, 0))
        opened = bridge.complete(open_door, 0, False, False)
        self.assertTrue(opened["visible_door_opened"])
        self.assertEqual(opened["front_before"], [4, 4, 2])
        self.assertEqual(opened["front_after"], [4, 4, 0])
        self.assertEqual(opened["before_public_sha256"], digest(locked))
        self.assertEqual(opened["after_public_sha256"], digest(open_door))
        self.assertIsNone(opened["pose_delta"])
        self.assertEqual(bridge.events, 3)

    def test_public_observation_only_rejects_private_or_invalid_metadata(self):
        valid = frame()
        for key, value in (("env_grid", []), ("carrying", True), ("agent_pos", [1, 2]), ("hidden_door_state", 2), ("goal_position", [4, 4])):
            obs = copy.deepcopy(valid)
            obs[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                public_observation(obs)
        wrong = [frame(direction=True), frame(direction=4)]
        wrong += [{**frame(), "mission": "private evaluation task"}]
        wrong += [{**frame(), "image": [[[1, 0, 0]]] * 7}]
        wrong += [{**frame(), "image": [[[1, 0, 0] for _ in range(7)] for _ in range(6)]}]
        wrong += [{**frame(), "image": "private"}]
        for obs in wrong:
            with self.assertRaises(ValueError):
                public_observation(obs)
        state = frame(front=(4, 4, 3))
        with self.assertRaises(ValueError):
            public_observation(state)

    def test_invalid_actions_and_failures_are_transactional(self):
        bridge = DoorKeyPublicAdapter()
        start = frame()
        bridge.reset_public(start)
        for action in (-1, 7, 1.0, True, "pickup", None):
            before = bridge.checkpoint()
            with self.subTest(action=action), self.assertRaises(ValueError):
                bridge.submit(action)
            self.assertEqual(bridge.checkpoint(), before)
        bridge.submit(3)
        before = bridge.checkpoint()
        with self.assertRaises(ValueError):
            bridge.submit(5)
        self.assertEqual(bridge.checkpoint(), before)
        for args in [(frame(), float("nan"), False, False), (frame(), 0.0, 1, False), (frame(), 0.0, False, "false"), (frame(), 2.0, False, False), ({**frame(), "env_grid": []}, 0, False, False)]:
            with self.assertRaises(ValueError):
                bridge.complete(*args)
            self.assertEqual(bridge.checkpoint(), before)
        bridge.complete(frame(), 0, False, False)
        self.assertEqual(bridge.events, 1)
        with self.assertRaises(ValueError):
            bridge.complete(frame(), 0, False, False)

    def test_terminal_and_reset_gates(self):
        adapter = DoorKeyPublicAdapter()
        with self.assertRaises(ValueError):
            adapter.submit(3)
        with self.assertRaises(ValueError):
            adapter.complete(frame(), 0, False, False)
        adapter.reset_public(frame())
        adapter.submit(5)
        with self.assertRaises(ValueError):
            adapter.reset_public(frame())
        adapter.complete(frame(), 0.9, True, False)
        with self.assertRaises(ValueError):
            adapter.submit(0)
        adapter.reset_public(frame(front=(4, 4, 2)))
        self.assertEqual(adapter.events, 0)
        self.assertEqual(adapter.ledger, [])
        self.assertFalse(adapter.terminal)

    def test_same_public_information_conventional_parser_exact(self):
        examples = [frame(), frame(front=(4, 4, 2)), frame(front=(4, 4, 0), held=(5, 4, 0)),
                    frame(front=(0, 0, 0), held=(5, 4, 0)), frame(front=(5, 4, 0), direction=3)]
        for observation in examples:
            a = public_cues(observation)
            bfront, bcarry, bheading = independent_public_reader(observation)
            self.assertEqual(tuple(a["front"]), bfront)
            self.assertEqual(tuple(a["carried"]) if a["carried"] else None, bcarry)
            self.assertEqual(a["direction"], bheading)

    def test_door_change_not_inferred_when_not_directly_visible(self):
        cases = [
            (2, frame(front=(4, 4, 2)), frame(front=(4, 4, 0))),  # only action 5 can be observed toggle
            (5, frame(front=(4, 4, 2)), frame(front=(4, 0, 0))),  # door color changed
            (5, frame(front=(0, 0, 0)), frame(front=(4, 4, 0))),  # prior door not visible
            (5, frame(front=(4, 4, 2)), frame(front=(4, 4, 1))),  # not opened
            (5, frame(front=(4, 4, 2)), frame(front=(4, 4, 0), direction=1)),  # turned / different direction
        ]
        for action, before, after in cases:
            a = DoorKeyPublicAdapter()
            a.reset_public(before)
            a.submit(action)
            self.assertFalse(a.complete(after, 0, False, False)["visible_door_opened"])

    def test_checkpoint_exact_cold_process_and_corruption_rejection(self):
        a = DoorKeyPublicAdapter()
        a.reset_public(frame(front=(5, 4, 0)))
        a.submit(3)
        a.complete(frame(front=(1, 0, 0), held=(5, 4, 0)), 0, False, False)
        a.submit(5)  # Pending preserved exactly through cold OS restore.
        encoded = a.checkpoint()
        self.assertEqual(DoorKeyPublicAdapter.restore(encoded).checkpoint(), encoded)
        script = ("import sys,json;from research.native.itd02.r10.public_adapter import DoorKeyPublicAdapter;"
                  "a=DoorKeyPublicAdapter.restore(sys.stdin.buffer.read());"
                  "print(json.dumps({'pending':a.pending,'events':a.events,'held':a.current['image'][3][6],"
                  "'image_only':sorted(a.current)}))")
        p = subprocess.run([sys.executable, "-B", "-c", script], input=encoded, capture_output=True, timeout=15)
        self.assertEqual(p.returncode, 0, p.stderr.decode())
        self.assertEqual(json.loads(p.stdout), {"pending": 5, "events": 1, "held": [5, 4, 0], "image_only": ["direction", "image", "mission"]})
        bad = json.loads(encoded)
        bad["state"]["pending"] = 6
        with self.assertRaises(ValueError):
            DoorKeyPublicAdapter.restore(json.dumps(bad).encode())
        # Even if a caller recalculates a digest, invalid action metadata is rejected.
        bad = json.loads(encoded)
        bad["state"]["ledger"][0]["action_name"] = "toggle"
        bad["sha256"] = digest(bad["state"])
        with self.assertRaises(ValueError):
            DoorKeyPublicAdapter.restore(json.dumps(bad).encode())


if __name__ == "__main__":
    unittest.main()

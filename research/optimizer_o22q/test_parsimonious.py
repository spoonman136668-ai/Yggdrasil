"""O22-Q exact public-source-only parsimonious controls with original role guard."""
import json
import subprocess
import sys
import unittest

from research.optimizer_o22q.parsimonious import MinimalSourceBeta


def after(b, moved, blocked):
    x = list(b)
    if moved:
        x[0] += 1
    x[5] = int(blocked)
    return x


class ParsimoniousSourceControls(unittest.TestCase):
    def setUp(self):
        self.before = [2, 3, 0, 6, 6, 1]

    def test_original_action_selected_event_ownership(self):
        m = MinimalSourceBeta()
        with self.assertRaises(ValueError):
            m.learn(self.before, 4, after(self.before, False, False))
        with self.assertRaises(ValueError):
            m.learn(self.before, 0, after(self.before, False, False) + [99])
        with self.assertRaises(ValueError):
            m.learn(self.before[:5], 0, after(self.before, False, False))
        self.assertEqual(m.events, 0)

    def test_source_effect_condition_uses_true_selected_action_and_front(self):
        m = MinimalSourceBeta("action_front")
        for _ in range(4):
            m.learn(self.before, 0, after(self.before, False, True))
            m.learn(self.before, 1, after(self.before, False, False))
        self.assertGreater(m.predict(self.before, 0)[0],
                           m.predict(self.before, 1)[0])
        self.assertEqual(m.events, 8)
        self.assertEqual(m.actions, {"0": 4, "1": 4, "2": 0})

    def test_contradictory_events_update_without_protected_world(self):
        m = MinimalSourceBeta()
        for _ in range(5):
            m.learn(self.before, 0, after(self.before, False, True))
        p = m.predict(self.before, 0)[0]
        for _ in range(7):
            m.learn(self.before, 0, after(self.before, False, False))
        self.assertLess(m.predict(self.before, 0)[0], p)

    def test_no_action_control_does_not_claim_action_learning(self):
        no_action = MinimalSourceBeta("front")
        b = self.before
        no_action.learn(b, 0, after(b, False, True))
        self.assertEqual(no_action.predict(b, 0), no_action.predict(b, 1))
        self.assertEqual(no_action.predict(b, 1), no_action.predict(b, 2))

    def test_action_front_control_independent_from_heading_and_goal(self):
        m = MinimalSourceBeta("action_front")
        for _ in range(3):
            m.learn(self.before, 2, after(self.before, True, True))
        b = [4, 5, 3, 1, 2, 1]
        self.assertEqual(m.predict(b, 2), m.predict(self.before, 2))

    def test_external_cold_python_process_and_checksum(self):
        for mode in ("action_front", "action", "front"):
            m = MinimalSourceBeta(mode)
            for a in (0, 1, 2):
                m.learn(self.before, a, after(self.before, a == 2, a == 1))
            cp = m.checkpoint()
            self.assertEqual(MinimalSourceBeta.restore(cp).checkpoint(), cp)
            proc = (
                "import json,sys;"
                "from research.optimizer_o22q.parsimonious import MinimalSourceBeta;"
                "m=MinimalSourceBeta.restore(sys.stdin.buffer.read());"
                "print(json.dumps({'p':m.predict([2,3,0,6,6,1],1),"
                "'events':m.events,'mode':m.mode}))"
            )
            got = subprocess.run([sys.executable, "-B", "-c", proc],
                                 input=cp, capture_output=True, timeout=20)
            self.assertEqual(got.returncode, 0, got.stderr.decode())
            self.assertEqual(json.loads(got.stdout),
                             {"p": list(m.predict(self.before, 1)),
                              "events": 3, "mode": mode})
            tampered = json.loads(cp)
            tampered["body"]["events"] = 4
            with self.assertRaises(ValueError):
                MinimalSourceBeta.restore(json.dumps(tampered).encode())

    def test_model_persistent_sample_counts_are_not_partial(self):
        m = MinimalSourceBeta()
        m.learn(self.before, 0, after(self.before, True, False))
        cp = json.loads(m.checkpoint())
        cp["body"]["counts"]["0:1"][0] = 0
        cp["sha256"] = __import__("hashlib").sha256(
            json.dumps(cp["body"], sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        with self.assertRaises(ValueError):
            MinimalSourceBeta.restore(json.dumps(cp).encode())


if __name__ == "__main__":
    unittest.main(verbosity=2)

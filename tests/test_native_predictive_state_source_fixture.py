"""Original-science-seed-free engineering source tests; no hidden oracle labels."""
import importlib.util
from pathlib import Path
import unittest
from yggdrasil.native_predictive_state_split import PredictiveStateSplit
from yggdrasil.native_predictive_state_controls import ARMS, MatchedHistoryControls

HERE = Path(__file__).resolve().parents[1] / "research/contrib/chatgpt/YGG-CAP04/source_fixture.py"
spec = importlib.util.spec_from_file_location("cap04_engineering_source_fixture", HERE)
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)

class SourceFixtureTests(unittest.TestCase):
    def test_fixture_identity_is_fenced_from_registered_science(self):
        for seed in fixture.RESERVED_SCIENTIFIC_SEEDS:
            with self.assertRaisesRegex(ValueError, "REGISTERED_SCIENCE_FORBIDDEN"):
                fixture.generate(seed)
            with self.assertRaisesRegex(ValueError, "REGISTERED_SCIENCE_FORBIDDEN"):
                fixture.generate(str(seed))
        with self.assertRaisesRegex(ValueError, "BUDGET"):
            fixture.generate(n=97)
        with self.assertRaisesRegex(ValueError, "BUDGET"):
            fixture.generate(n=0)

    def test_actual_historical_cause_is_not_a_current_action_alias(self):
        for name in fixture.FIXTURE_IDS:
            events = fixture.generate(name)
            self.assertEqual(len(fixture.ACTION_CYCLE), 16)
            # These are engineering fixtures; 16 reachable consecutive
            # action-pair combinations are necessary for an independent
            # preceding-action relation, not proof the learner discovered one.
            for start, stop in ((1, 32), (32, 72), (72, 96)):
                pairs = {(events[i - 1]["action"], events[i]["action"])
                         for i in range(start, stop)}
                self.assertEqual(len(pairs), 16)
                for current in fixture.ARMS:
                    self.assertEqual({previous for previous, observed in pairs
                                      if observed == current}, set(fixture.ARMS))
            # Historical fixture schedule made previous action a deterministic
            # function of current action: exactly four supported ordered pairs.
            old = [fixture.ARMS[(i + int(name == fixture.FIXTURE_IDS[1])) % 4]
                   for i in range(96)]
            self.assertEqual(len({(old[i - 1], old[i])
                                  for i in range(32, 72)}), 4)

    def test_chronology_and_two_stage_real_witness_clock(self):
        for name in fixture.FIXTURE_IDS:
            events = fixture.generate(name)
            self.assertEqual(events, fixture.generate(name))
            self.assertEqual(len(events), 96)
            self.assertEqual(len(set(x["id"] for x in events)), 96)
            native = PredictiveStateSplit()
            controls = MatchedHistoryControls()
            old_checkpoint = (native.checkpoint(), controls.checkpoint())
            for i, row in enumerate(events):
                self.assertEqual(set(row), {"id", "views", "action", "s2", "y", "post"})
                if i:
                    last = events[i - 1]["post"]
                    self.assertEqual(row["views"], ((last[0], last[1]), (last[1], last[2])))
                self.assertEqual(row["action"], fixture.ARMS[
                    fixture.ACTION_CYCLE[(i + int(name == fixture.FIXTURE_IDS[1])) % 16]])
                self.assertEqual(row["post"][1], row["s2"])
                native.forecast(row["views"], row["action"], "transition")
                controls.forecast(row["views"], row["action"], "transition")
                native.forecast(row["views"], row["action"], "residual", row["s2"])
                control_p = controls.forecast(row["views"], row["action"], "residual", row["s2"])
                self.assertEqual(set(control_p), set(ARMS))
                self.assertEqual((native.count, controls.count), (i, i))
                native.observe(row["id"], row["views"], row["action"], row["s2"], row["y"], row["post"])
                controls.observe(row["id"], row["views"], row["action"], row["s2"], row["y"], row["post"])
            self.assertEqual((native.count, controls.count), (96, 96))
            self.assertNotEqual(native.checkpoint(), old_checkpoint[0])
            self.assertNotEqual(controls.checkpoint(), old_checkpoint[1])

if __name__ == "__main__": unittest.main()

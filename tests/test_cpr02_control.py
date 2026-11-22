"""Matched-information two-probe negative comparator; synthetic only."""
import importlib.util
from pathlib import Path
import sys
import unittest

path = Path(__file__).with_name('test_cpr02_confirmation.py')
spec = importlib.util.spec_from_file_location('cpr02_confirmation_fixture', path)
fix = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = fix
spec.loader.exec_module(fix)


def compare(primary, probes):
    assert len(primary) == len(probes)
    monitor = fix.fresh()
    prior = 0
    raw, confirmed, probe_only = [], [], []
    for i, (y, probe_y) in enumerate(zip(primary, probes, strict=True), start=1):
        route, observed = fix.step(monitor, y, probe_y, i)
        if route['raw_alarm']:
            raw.append(i)
        if observed['confirmed_change']:
            confirmed.append(i)
        # Exact same independently observed probe labels and frozen expert forecast.
        mismatch = 900_000 > 100_000 if probe_y == 0 else 100_000 > 100_000
        prior = prior + 1 if mismatch else 0
        if prior == 2:
            probe_only.append(i)
    return raw, confirmed, probe_only


class MatchedProbeControlTests(unittest.TestCase):
    def test_same_information_control_removes_unique_robustness_claim(self):
        raw, cpr, control = compare([1]*64 + [0]*8 + [1]*8, [1]*80)
        self.assertEqual((raw, cpr, control), ([75], [], []))

    def test_control_confirms_sustained_shift_earlier(self):
        raw, cpr, control = compare([1]*16 + [0]*32, [1]*16 + [0]*32)
        self.assertEqual(raw, [27])
        self.assertEqual(cpr, [29])
        self.assertEqual(control, [18])  # 11 steps faster with same probe stream.

    def test_correlated_probe_noise_remains_negative_for_both(self):
        s = [1]*64 + [0]*16 + [1]*8
        raw, cpr, control = compare(s, s)
        self.assertEqual((raw, cpr, control), ([75], [77], [66]))


if __name__ == '__main__':
    unittest.main()

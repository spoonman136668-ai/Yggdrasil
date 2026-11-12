"""Focused negative, provenance and primitive-discovery checks (not PRIMARY)."""
import hashlib
import unittest
from synthesis import gate, catalog, LearnedProgram
from world import World
from battery import one_episode
from pathlib import Path


class TestWSP51(unittest.TestCase):
    def test_primitive_range(self):
        for width in (4, 6, 8):
            n = 1 << width
            for k in range(width + 4):
                for x in range(n):
                    self.assertTrue(0 <= gate(x, k, width) < n)

    def test_catalog_unique_and_programs(self):
        for width in (4, 6):
            bank = catalog(width)
            self.assertEqual(len(set(bank.maps)), len(bank.maps))
            self.assertEqual(len(bank.maps), len(bank.tapes))
            self.assertEqual(bank.maps[0], tuple(range(1 << width)))
            self.assertTrue(all(len(tape) <= 3 for tape in bank.tapes))

    def test_composed_families_representable(self):
        for width in (4, 6, 8):
            bank = catalog(width)
            for family in ("inc_rol_xorbit", "xor_rol_dec", "rol_xorbit_inc"):
                world = World(width, family, "unit_positive")
                outputs = tuple(world.apply(1, x) for x in range(1 << width))
                self.assertIn(outputs, bank.maps, (width, family))

    def test_incremental_elimination_exact_batch(self):
        bank = catalog(4)
        world = World(4, "xor_rol_dec", "incremental")
        mask = bank.full_mask
        rows = []
        for x in (0, 1, 2, 3, 5, 8, 13):
            y = world.apply(1, x)
            rows.append((x, y))
            mask &= sum(1 << i for i, mapping in enumerate(bank.maps) if mapping[x] == y)
            self.assertEqual(mask, bank.matching(rows))
            self.assertNotEqual(mask, 0)

    def test_no_hidden_world_or_rule(self):
        obj = LearnedProgram(4)
        self.assertFalse(obj.cycle.valid)
        self.assertIsNone(obj.apply(1, 0))
        self.assertIsNone(obj.suggest_probe())
        self.assertEqual(obj.live, obj.bank.full_mask)

    def test_invalid_cycle_abstains(self):
        model = LearnedProgram(4)
        for i in range(16):
            model.record_cycle(0, i)
            model.observe(0, 0, 0)
        model.certify(0)
        self.assertFalse(model.cycle.valid)
        self.assertIsNone(model.apply(1, 7))
        self.assertEqual(model.live, model.bank.full_mask)

    def test_observed_facts_cannot_be_overridden(self):
        model = LearnedProgram(4)
        for x in range(16):
            model.record_cycle(x, x)
            model.observe(0, x, (x + 1) % 16)
        model.certify(0)
        self.assertTrue(model.cycle.valid)
        model.observe(1, 3, 9)
        self.assertEqual(model.apply(1, 3), 9)
        self.assertEqual(model.apply(0, 3), 4)
        with self.assertRaises(ValueError):
            model.observe(1, 3, 8)

    def test_cold_and_tamper(self):
        model = LearnedProgram(4)
        for x in range(16):
            model.record_cycle(x, x)
            model.observe(0, x, (x + 1) % 16)
        model.certify(0)
        model.observe(1, 0, 3)
        model.observe(1, 3, 7)
        raw = model.snapshot()
        restored = LearnedProgram.restore(raw)
        self.assertEqual(restored.snapshot(), raw)
        self.assertEqual([restored.apply(1, x) for x in range(16)],
                         [model.apply(1, x) for x in range(16)])
        for tampered in (raw + b"0", raw[:-1], raw.replace(b"width", b"widtx")):
            with self.assertRaises(ValueError):
                LearnedProgram.restore(tampered)

    def test_frozen_coordinate_parent(self):
        p = Path(__file__).resolve().parents[1] / "WSP-50" / "coordinates.py"
        self.assertTrue(p.is_file())
        self.assertIn("class CycleModel:", p.read_text(encoding="utf-8"))

    def test_real_trajectory_and_encodings(self):
        expected = None
        for kind in ("identity", "linear_bijection", "random_permutation"):
            episodes, rows, times = one_episode(4, "inc_rol_xorbit", 101, kind, "DEV")
            self.assertTrue(episodes[1]["cycle_valid"])
            self.assertEqual(episodes[1]["observed_recall"], episodes[1]["unique_facts"])
            self.assertEqual(episodes[1]["wrong_known"], 0)
            self.assertLessEqual(episodes[1]["action_replies"], 8192)
            self.assertEqual(episodes[1]["action_replies"], len(rows))
            if expected is not None:
                self.assertEqual(rows, expected)
            expected = rows

    def test_random_negative_retains_and_abstains_if_unproven(self):
        episodes, rows, timings = one_episode(4, "random_map", 101, "random_permutation", "DEV")
        last = episodes[-1]
        self.assertEqual(last["observed_recall"], last["unique_facts"])
        self.assertEqual(last["unseen"], last["correct"] + last["wrong_known"] + last["abstain"])

    def test_broken_spine_certification(self):
        episodes, rows, timings = one_episode(4, "broken_spine", 101, "identity", "DEV")
        self.assertFalse(episodes[-1]["cycle_valid"])
        self.assertEqual(episodes[-1]["observed_recall"], episodes[-1]["unique_facts"])


if __name__ == "__main__":
    unittest.main()

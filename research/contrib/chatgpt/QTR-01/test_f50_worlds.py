"""F50 exhaustive symbolic source-law admission, no DEV target first-use."""
import json
import tempfile
import unittest
from pathlib import Path
import f50_worlds as f


def fixture_target():
    return ("xor",
            ("and", ("and", ("and", f.leaf(0), f.leaf(1)), f.leaf(30)), f.leaf(2)),
            ("xor", f.leaf(10), f.leaf(20)))


class TestF50Worlds(unittest.TestCase):
    def test_protocol_blob_and_high_first_freeze(self):
        p = f.freeze()
        self.assertEqual(f.BANK_SIZES, (4096, 2048, 1024))
        self.assertEqual(f.DEV_SEEDS, (4013, 4057, 4099))
        self.assertEqual(f.RESERVED_SEEDS, (4127, 4159))
        self.assertEqual(f.PREREG_BLOB, "4bd3c4e0d3de0e3910094e38c14a0141c97ad380")
        self.assertEqual(p["task"]["source_training_namespace"], "F50/train/v1")
        self.assertEqual(f.N_VARIABLES, 33)
        self.assertFalse(hasattr(f, "target_ast"))
        self.assertFalse(hasattr(f, "target_law"))
        self.assertFalse(hasattr(f, "target_observations"))
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "frozen.json"
            raw = f.PREREG.read_bytes()
            path.write_bytes(raw + b" ")
            with self.assertRaisesRegex(f.F50Rejected, "PREREG_BLOB_DRIFT"):
                f.freeze(path)

    def test_anf_exact_semantics_on_exhaustive_five_variable_cube(self):
        a, b, c, d, e = [f.leaf(i) for i in range(5)]
        formulas = [
            a, ("not", a), ("and", a, b), ("or", a, b),
            ("xor", a, b), ("xor", ("and", a, b), ("and", c, d)),
            ("or", ("not", b), ("xor", ("and", a, c), ("and", d, e))),
        ]
        for node in formulas:
            with self.subTest(node=node):
                for value in range(32):
                    direct = f.evaluate(node, value, 0, 0, 0)
                    poly = 0
                    for mask in f.anf(node):
                        poly ^= int((mask & value) == mask)
                    self.assertEqual(direct, poly)
        self.assertTrue(f.exact_equal(("or", a, b),
                                      ("xor", ("xor", a, b), ("and", a, b))))
        self.assertTrue(f.exact_equal(("not", ("not", a)), a))
        self.assertTrue(f.exact_equal(("and", a, a), a))
        self.assertFalse(f.exact_equal(("xor", a, b), ("or", a, b)))
        self.assertTrue(f.exact_equal(("xor", f.leaf(32), f.leaf(0)),
                                      ("xor", f.leaf(0), f.leaf(32))))
        self.assertIn(32, f.dependencies(("xor", f.leaf(32), f.leaf(0))))

    def test_exact_source_banks_all_high_first_sizes(self):
        for size in f.BANK_SIZES:
            with self.subTest(size=size):
                report = f.source_bank_admission(size)
                bank = f.source_bank(size)
                self.assertEqual(report["distinct_full_function_laws"], size)
                self.assertEqual(report["target_outcomes_consumed"], 0)
                self.assertTrue(all(f.ast_depth(node) <= 3 for node in bank))
                self.assertEqual(len(set(map(f.anf, bank))), size)
                self.assertEqual(len(report["source_identity_stream_sha256"]), 64)
                self.assertEqual(f.source_bank(size), bank)

    def test_source_fit_validation_law_custody_and_public_rows(self):
        size = 1024
        fit, valid = f.source_split(size)
        self.assertEqual(len(fit), size * 4 // 5)
        self.assertEqual(len(valid), size - len(fit))
        self.assertFalse(fit & valid)
        self.assertEqual(fit | valid, set(range(size)))
        self.assertEqual(set(i for i, _ in f.fit_source_laws(size)), fit)
        self.assertEqual(set(i for i, _ in f.validation_source_laws_for_pretrain_only(size)), valid)
        source_id = min(fit)
        rows = f.source_training_row(size, source_id)
        self.assertEqual(len(rows), 64)
        for index, (trajectory, outcomes) in enumerate(rows[:8]):
            self.assertEqual(f.validate_trajectory(trajectory), trajectory)
            truth = f._episode_truth(f.source_bank(size)[source_id], trajectory)
            self.assertEqual(len(outcomes), 3)
            for step in range(3):
                self.assertEqual(outcomes[step], truth[step] ^ f._noise_bit(size, source_id, index, step))
        self.assertEqual(rows, f.source_training_row(size, source_id))
        with self.assertRaisesRegex(f.F50Rejected, "SPLIT_FENCE"):
            f.source_training_row(size, min(valid))
        with self.assertRaisesRegex(f.F50Rejected, "SPLIT_FENCE"):
            f.source_training_row(size, source_id, validation=True)
        self.assertEqual(len(f.source_training_row(size, min(valid), validation=True)), 64)

    def test_public_candidates_and_sealed_inputs_are_disjoint(self):
        size, seed = 1024, 4013
        public = f.public_candidate_pool(size, seed)
        heldout = f.sealed_heldout_inputs_for_evaluator_only(size, seed)
        training = f._source_trajectory_registry(size)[1]
        self.assertEqual(len(public), f.PUBLIC_QUERIES)
        self.assertEqual(len(heldout), f.HELDOUT_QUERIES)
        self.assertEqual(len(set(public)), 512)
        self.assertEqual(len(set(heldout)), 512)
        self.assertFalse(set(public) & set(heldout))
        self.assertFalse(set(public) & training)
        self.assertFalse(set(heldout) & training)
        self.assertEqual(public, f.public_candidate_pool(size, seed))
        self.assertEqual(heldout, f.sealed_heldout_inputs_for_evaluator_only(size, seed))

    def test_target_like_fixture_exact_admission_no_target_first_use(self):
        fixture = fixture_target()
        self.assertEqual(f.ast_depth(fixture), 4)
        result = f.check_fixture_novelty(1024, fixture)
        self.assertTrue(result["exact_nonmembership"])
        self.assertEqual(result["target_outcomes_consumed"], 0)
        self.assertEqual(result["scientific_pass"], False)
        source = next(node for node in f.source_bank(1024) if f.ast_depth(node) == 2)
        same = ("not", ("not", source))
        self.assertEqual(f.ast_depth(same), 4)
        with self.assertRaisesRegex(f.F50Rejected, "EXACT_SOURCE_COLLISION"):
            f.check_fixture_novelty(1024, same)
        with self.assertRaisesRegex(f.F50Rejected, "DEPTH_INVALID"):
            f.check_fixture_novelty(1024, ("and", f.leaf(0), f.leaf(1)))

    def test_all_protected_seeds_and_malformed_actions_fail_closed(self):
        for seed in (4127, 4159, 163, 167, 173, True, 0, -1):
            with self.subTest(seed=seed):
                with self.assertRaises(f.F50Rejected):
                    f.public_candidate_pool(1024, seed)
                with self.assertRaises(f.F50Rejected):
                    f.sealed_heldout_inputs_for_evaluator_only(1024, seed)
        for size in (True, 512, 8192, 0):
            with self.assertRaises(f.F50Rejected):
                f.source_bank(size)
        for episode in ((0, 2, 3, 4), (7, 7, 11, 0),
                        (1, 3, 7, 2), (7, 11, 13, 8),
                        (True, 11, 13, 2), (1024, 11, 13, 2)):
            with self.assertRaises(f.F50Rejected):
                f.validate_trajectory(episode)
        for name in ("target_ast", "target_law", "target_observation", "evaluate_target"):
            self.assertFalse(hasattr(f, name))


if __name__ == "__main__":
    unittest.main()

"""G35 admission-preflight falsification tests; no primary execution."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "ygg_db01_g35_preflight", HERE / "g35_preflight.py")
preflight = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = preflight
SPEC.loader.exec_module(preflight)


class G35ProspectiveAdmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidate = json.loads((HERE / "g35_candidate.json").read_text("utf-8"))

    def clone(self):
        return copy.deepcopy(self.candidate)

    def test_current_unfrozen_candidate_is_blocked(self):
        result = preflight.inspect(self.clone())
        self.assertEqual(result["preflight"], "BLOCKED_MISSING_EVIDENCE")
        self.assertFalse(result["primary_execution_allowed"])
        self.assertFalse(result["source_and_custody_authenticated"])
        self.assertFalse(result["scientific_acceptance_allowed"])
        self.assertEqual(len(result["missing_evidence"]), 12)
        self.assertEqual(len(result["planning_digest_sha256"]), 64)

    def test_fixed_budget_is_pure_analytic_proxy_not_runtime_claim(self):
        expected = {
            "development_cell_updates_per_case": 256,
            "moore_neighbor_visits_per_case": 1600,
            "neighbor_channel_reads_proxy": 25600,
            "logical_state_float_bytes": 2048,
            "logical_genome_float_bytes": 3184,
        }
        result = preflight.inspect(self.clone())["resource_proxy"]
        for name, value in expected.items():
            self.assertEqual(result[name], value)
        self.assertIn("actual_python_memory", result["not_measured"])
        self.assertIn("wall_time", result["not_measured"])
        self.assertIn("learning_budget", result["not_measured"])

    def test_planned_balanced_pairing_disjoint_not_actual_cohort(self):
        design = self.candidate["proposed_design"]
        self.assertEqual(len(design["fit_seed_ids"]), 8)
        self.assertEqual(len(design["transfer_seed_ids"]), 8)
        self.assertTrue(set(design["fit_seed_ids"]).isdisjoint(
            design["transfer_seed_ids"]))
        self.assertEqual(design["planned_outcomes_per_seed"], [0, 1])
        self.assertEqual(len(design["conditions"]), 6)
        self.assertNotIn("no_feedback", design["energy_matched_conditions"])
        self.assertTrue(preflight.inspect(self.clone())[
            "planned_cohort_class_balance_is_not_observed_labels"])

    def test_forbid_implicit_primary_execution_or_acceptance(self):
        for key in self.candidate["authority"]:
            value = self.clone()
            value["authority"][key] = True
            with self.assertRaisesRegex(ValueError, "authority"):
                preflight.inspect(value)
        value = self.clone()
        value["status"] = "FROZEN"
        with self.assertRaisesRegex(ValueError, "identity/status"):
            preflight.inspect(value)
        value = self.clone()
        value["primary_results"] = {"claim": "pass"}
        with self.assertRaisesRegex(ValueError, "schema keys"):
            preflight.inspect(value)

    def test_forbid_seed_overlap_imbalanced_and_budget_drift(self):
        value = self.clone()
        value["proposed_design"]["transfer_seed_ids"][0] = 11
        with self.assertRaisesRegex(ValueError, "overlap"):
            preflight.inspect(value)
        value = self.clone()
        value["proposed_design"]["fit_seed_ids"].pop()
        with self.assertRaisesRegex(ValueError, "unbalanced"):
            preflight.inspect(value)
        value = self.clone()
        value["proposed_design"]["capacity"]["genome_parameters"] = 399
        with self.assertRaisesRegex(ValueError, "budget drift"):
            preflight.inspect(value)
        value = self.clone()
        value["proposed_design"]["per_case_condition_budget"]["sham"][
            "cell_updates"] = 257
        with self.assertRaisesRegex(ValueError, "condition budget"):
            preflight.inspect(value)

    def test_forbid_false_energy_equivalence_and_missing_controls(self):
        value = self.clone()
        value["proposed_design"]["energy_matched_conditions"].append(
            "no_feedback")
        with self.assertRaisesRegex(ValueError, "conditions/energy"):
            preflight.inspect(value)
        value = self.clone()
        del value["proposed_design"]["per_case_condition_budget"][
            "polarity_flip"]
        with self.assertRaisesRegex(ValueError, "budgets"):
            preflight.inspect(value)
        value = self.clone()
        value["proposed_design"]["planned_outcomes_per_seed"] = [1, 1]
        with self.assertRaisesRegex(ValueError, "labels"):
            preflight.inspect(value)

    def test_invalid_identity_missing_custody_and_hash_fail_closed(self):
        for key, bad in (("task_manifest_sha256", "fake"),
                         ("evaluator_commit_sha", "0" * 39),
                         ("independent_custodian", " "),
                         ("task_source_url", 1234)):
            value = self.clone()
            value["external_evidence"][key] = bad
            with self.assertRaises(ValueError):
                preflight.inspect(value)
        value = self.clone()
        del value["external_evidence"]["task_license"]
        with self.assertRaisesRegex(ValueError, "evidence field"):
            preflight.inspect(value)

    def test_even_plausible_self_declarations_never_admit_primary(self):
        value = self.clone()
        for name in preflight.EVIDENCE_FIELDS:
            value["external_evidence"][name] = (
                "0" * 64 if name in preflight.HASH_FIELDS else
                "1" * 40 if name in preflight.COMMIT_FIELDS else
                "unverified-self-declaration")
        result = preflight.inspect(value)
        self.assertEqual(result["missing_evidence"], [])
        self.assertEqual(
            result["preflight"], "STRUCTURE_ONLY_EXTERNAL_AUTHENTICITY_UNVERIFIED")
        self.assertFalse(result["source_and_custody_authenticated"])
        self.assertFalse(result["primary_execution_allowed"])

    def test_digest_determinism_and_tamper_identity(self):
        value = self.clone()
        self.assertEqual(preflight.canonical_digest(value),
                         preflight.canonical_digest(self.clone()))
        different = self.clone()
        different["proposed_design"]["fit_seed_ids"][0] = 41
        self.assertNotEqual(preflight.canonical_digest(value),
                            preflight.canonical_digest(different))


if __name__ == "__main__":
    unittest.main()

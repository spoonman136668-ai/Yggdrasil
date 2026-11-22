"""Development-only public action identity negatives; no scored seed use."""
import importlib.util
from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] /
          "research/contrib/chatgpt/WSCM-TRANSFER-02/public_action_identity.py")
SPEC = importlib.util.spec_from_file_location("wscm_public_action_identity", SOURCE)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def request(action, state):
    return {"public_view": list(state), "external_action_id": action}


def observed(store, action, vector, witness_base=0):
    for i, state in enumerate(MOD.STATES):
        store = store.observe(request(action, state), vector[i], f"{witness_base+i:064x}")
    return store


class PublicActionIdentityTests(unittest.TestCase):
    def test_unknown_and_partial_evidence_abstain(self):
        model = MOD.PublicActionSignatures()
        self.assertIsNone(model.signature(100))
        model = model.observe(request(100, (0, 0)), 1, "a" * 64)
        self.assertIsNone(model.signature(100))
        self.assertIsNone(model.equivalent(100, 200))

    def test_completed_public_truth_table_and_renamed_action(self):
        model = observed(MOD.PublicActionSignatures(), 100, (0, 0, 1, 1), 1)
        model = observed(model, 90017, (0, 0, 1, 1), 5)
        self.assertEqual(model.signature(100), (0, 0, 1, 1))
        self.assertIs(model.equivalent(100, 90017), True)

    def test_changed_function_not_equivalent(self):
        model = observed(MOD.PublicActionSignatures(), 100, (0, 0, 1, 1), 1)
        model = observed(model, 90017, (0, 1, 0, 1), 5)
        self.assertIs(model.equivalent(100, 90017), False)

    def test_conflicting_observations_cause_abstention(self):
        model = observed(MOD.PublicActionSignatures(), 100, (0, 0, 1, 1), 1)
        model = model.observe(request(100, (0, 0)), 1, "b" * 64)
        self.assertIsNone(model.signature(100))

    def test_conflicting_witness_replay_rejected(self):
        first = MOD.PublicActionSignatures().observe(request(9, (0, 0)), 1, "a" * 64)
        self.assertIs(first.observe(request(9, (0, 0)), 1, "a" * 64), first)
        with self.assertRaisesRegex(ValueError, "PUBLIC_WITNESS_CONFLICT"):
            first.observe(request(9, (0, 0)), 0, "a" * 64)
        self.assertEqual(len(first._events), 1)

    def test_private_metadata_and_invalid_types_rejected(self):
        base = request(9, (0, 0))
        for extra in ("role", "phase", "law", "id_to_role", "future_outcome"):
            with self.subTest(extra=extra):
                with self.assertRaisesRegex(ValueError, "PUBLIC_ACTION_REQUEST_INVALID"):
                    MOD.PublicActionSignatures().observe({**base, extra: 1}, 1, "a" * 64)
        for bad in (True, "9", 9.0, -1, 2**31):
            with self.subTest(id=bad):
                with self.assertRaisesRegex(ValueError, "PUBLIC_ACTION_REQUEST_INVALID"):
                    MOD.PublicActionSignatures().observe(request(bad, (0, 0)), 1, "a" * 64)
        with self.assertRaisesRegex(ValueError, "PUBLIC_OUTCOME_INVALID"):
            MOD.PublicActionSignatures().observe(base, True, "a" * 64)

    def test_public_state_and_witness_validation(self):
        for state in ((2, 0), (True, 0), [1], "01"):
            with self.subTest(state=state):
                with self.assertRaisesRegex(ValueError, "PUBLIC_ACTION_REQUEST_INVALID"):
                    MOD.PublicActionSignatures().observe(request(9, state), 1, "a" * 64)
        for witness in ("A" * 64, "z" * 64, "1" * 63, None):
            with self.subTest(witness=witness):
                with self.assertRaisesRegex(ValueError, "PUBLIC_WITNESS_ID_INVALID"):
                    MOD.PublicActionSignatures().observe(request(9, (0, 0)), 1, witness)

    def test_snapshot_cold_restore_is_exact(self):
        model = observed(MOD.PublicActionSignatures(), 100, (0, 0, 1, 1), 1)
        raw = model.checkpoint()
        restored = MOD.PublicActionSignatures.restore(raw, MOD.PublicActionSignatures.checkpoint_sha256(raw))
        self.assertEqual(restored.checkpoint(), raw)
        self.assertEqual(restored.signature(100), model.signature(100))

    def test_cold_restore_rejects_bad_pin_and_altered_bytes(self):
        raw = MOD.PublicActionSignatures().checkpoint()
        digest = MOD.PublicActionSignatures.checkpoint_sha256(raw)
        with self.assertRaisesRegex(ValueError, "PUBLIC_CHECKPOINT_PIN"):
            MOD.PublicActionSignatures.restore(raw, "0" * 64)
        with self.assertRaisesRegex(ValueError, "PUBLIC_CHECKPOINT_PIN"):
            MOD.PublicActionSignatures.restore(raw + b" ", digest)

    def test_duplicate_or_altered_checkpoint_rejected_even_rehashed(self):
        model = MOD.PublicActionSignatures().observe(request(9, (0, 0)), 1, "a" * 64)
        raw = model.checkpoint()
        import json
        d = json.loads(raw)
        d["events"].append(d["events"][0])
        altered = MOD._canonical(d)
        with self.assertRaisesRegex(ValueError, "PUBLIC_CHECKPOINT_REJECTED"):
            MOD.PublicActionSignatures.restore(altered, MOD.PublicActionSignatures.checkpoint_sha256(altered))
        d = json.loads(raw)
        d["leaked_role"] = 0
        altered = MOD._canonical(d)
        with self.assertRaisesRegex(ValueError, "PUBLIC_CHECKPOINT_REJECTED"):
            MOD.PublicActionSignatures.restore(altered, MOD.PublicActionSignatures.checkpoint_sha256(altered))

    def test_caps_are_non_evicting_and_fail_closed(self):
        model = MOD.PublicActionSignatures()
        for id_ in range(MOD.MAX_ACTIONS):
            model = model.observe(request(id_, (0, 0)), 1, f"{id_+1:064x}")
        with self.assertRaisesRegex(ValueError, "PUBLIC_ACTION_CAPACITY"):
            model.observe(request(90017, (0, 0)), 1, "f" * 64)
        self.assertEqual(len(model._events), MOD.MAX_ACTIONS)

    def test_no_oracle_import_or_claim_of_native_semantics(self):
        source = SOURCE.read_text(encoding="utf-8")
        self.assertNotIn("import contract", source)
        self.assertNotIn("ID_TO_ROLE", source)
        self.assertNotIn("PHASE_LAW", source)
        self.assertNotIn("NativeEpisodeExperience", source)


if __name__ == "__main__":
    unittest.main()

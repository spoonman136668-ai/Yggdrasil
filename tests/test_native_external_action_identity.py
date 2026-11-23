"""Source-free interface and adversarial controls; no protected trial seeds."""
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] /
          "yggdrasil/native_external_action_identity.py")
SPEC = importlib.util.spec_from_file_location("native_external_identity", SOURCE)
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def receipt(action, state, result, source_id):
    doc = {"schema": M.RECEIPT_SCHEMA, "source_mode": M.SOURCE_MODE,
           "source_id": f"{source_id:064x}", "public_view": list(state),
           "external_action_id": action, "outcome": result}
    raw = M._canonical(doc)
    return raw, hashlib.sha256(raw).hexdigest()


def append(learner, action, states, outputs, first_id=1):
    for i, (state, outcome) in enumerate(zip(states, outputs)):
        raw, pin = receipt(action, state, outcome, first_id + i)
        learner = learner.observe_public_receipt({"public_view": list(state),
                                                   "external_action_id": action},
                                                  raw, pin)
    return learner


class NativeActionIdentityAdversarialTests(unittest.TestCase):
    def test_returned_opaque_ids_need_actual_public_witnesses(self):
        m = append(M.NativeExternalActionIdentity(), 1301, M.STATES,
                   (0, 0, 1, 1))
        self.assertEqual(m.observed_signature(1301), (0, 0, 1, 1))
        self.assertIsNone(m.observed_signature(90017))
        self.assertIsNone(m.observed_equivalent(1301, 90017))
        m2 = append(m, 90017, M.STATES, (0, 0, 1, 1), 10)
        self.assertIs(m2.observed_equivalent(1301, 90017), True)
        self.assertIsNone(m.observed_signature(90017))

    def test_nonidentical_public_effects_not_falsely_bound(self):
        m = append(M.NativeExternalActionIdentity(), 1301, M.STATES,
                   (0, 0, 1, 1))
        m = append(m, 90017, M.STATES, (0, 1, 0, 1), 10)
        self.assertIs(m.observed_equivalent(1301, 90017), False)

    def test_ambiguous_outcome_requires_abstention(self):
        m = append(M.NativeExternalActionIdentity(), 1301, M.STATES,
                   (0, 0, 1, 1))
        raw, pin = receipt(1301, (0, 0), 1, 9)
        m = m.observe_public_receipt({"public_view": [0, 0],
                                      "external_action_id": 1301}, raw, pin)
        self.assertIsNone(m.observed_signature(1301))

    def test_independent_public_receipt_action_mismatch_rejected(self):
        m = M.NativeExternalActionIdentity()
        raw, pin = receipt(90017, (0, 1), 1, 1)
        with self.assertRaisesRegex(ValueError, "WSCM_PUBLIC_RECEIPT_MISMATCH"):
            m.observe_public_receipt({"public_view": [0, 1],
                                      "external_action_id": 1301}, raw, pin)
        self.assertEqual(m._rows, ())

    def test_untrusted_claim_of_source_authenticity_rejected(self):
        raw, _ = receipt(9, (1, 0), 1, 1)
        doc = json.loads(raw)
        for mode in ("authenticated", "real_world", "owner_approved"):
            doc["source_mode"] = mode
            forged = M._canonical(doc)
            with self.assertRaisesRegex(ValueError, "WSCM_FIXTURE_ONLY"):
                M.NativeExternalActionIdentity().observe_public_receipt(
                    {"public_view": [1, 0], "external_action_id": 9},
                    forged, M.NativeExternalActionIdentity.sha256(forged))

    def test_hidden_role_law_phase_future_answer_leak_refused(self):
        raw, _ = receipt(9, (1, 0), 1, 1)
        for field in ("role", "phase", "law", "id_to_role", "future_outcome"):
            doc = json.loads(raw)
            doc[field] = "hidden"
            forged = M._canonical(doc)
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, "WSCM_FIXTURE_ONLY"):
                    M.NativeExternalActionIdentity().observe_public_receipt(
                        {"public_view": [1, 0], "external_action_id": 9},
                        forged, M.NativeExternalActionIdentity.sha256(forged))

    def test_request_type_aliases_and_private_metadata_refused(self):
        raw, pin = receipt(9, (1, 0), 1, 1)
        for candidate in (True, 9.0, "9", -1, 2**31):
            with self.subTest(candidate=candidate):
                with self.assertRaisesRegex(ValueError, "WSCM_PUBLIC_REQUEST"):
                    M.NativeExternalActionIdentity().observe_public_receipt(
                        {"public_view": [1, 0], "external_action_id": candidate}, raw, pin)
        with self.assertRaisesRegex(ValueError, "WSCM_PUBLIC_REQUEST"):
            M.NativeExternalActionIdentity().observe_public_receipt(
                {"public_view": [1, 0], "external_action_id": 9, "role": 1}, raw, pin)

    def test_pinned_source_bytes_and_conflicting_replays(self):
        m = M.NativeExternalActionIdentity()
        raw, pin = receipt(9, (1, 0), 1, 1)
        with self.assertRaisesRegex(ValueError, "WSCM_RECEIPT_PIN"):
            m.observe_public_receipt({"public_view": [1, 0],
                                      "external_action_id": 9}, raw, "f" * 64)
        m = m.observe_public_receipt({"public_view": [1, 0],
                                      "external_action_id": 9}, raw, pin)
        self.assertIs(m.observe_public_receipt({"public_view": [1, 0],
                                                "external_action_id": 9}, raw, pin), m)
        raw2, pin2 = receipt(9, (1, 0), 0, 1)
        with self.assertRaisesRegex(ValueError, "WSCM_SOURCE_REPLAY_CONFLICT"):
            m.observe_public_receipt({"public_view": [1, 0],
                                      "external_action_id": 9}, raw2, pin2)

    def test_byte_identical_checkpoint_and_no_phase_or_role(self):
        m = append(M.NativeExternalActionIdentity(), 1301, M.STATES,
                   (0, 0, 1, 1))
        raw = m.checkpoint()
        m2 = M.NativeExternalActionIdentity.restore(raw, M.NativeExternalActionIdentity.sha256(raw))
        self.assertEqual(raw, m2.checkpoint())
        self.assertEqual(m2.observed_signature(1301), m.observed_signature(1301))
        self.assertNotIn("role", json.loads(raw))
        self.assertNotIn("phase", json.loads(raw))

    def test_rehashed_tampered_checkpoint_still_rejected(self):
        m = append(M.NativeExternalActionIdentity(), 9, ((0, 0),), (1,))
        doc = json.loads(m.checkpoint())
        doc["records"].append(doc["records"][0])
        raw = M._canonical(doc)
        with self.assertRaisesRegex(ValueError, "WSCM_CHECKPOINT_REJECTED"):
            M.NativeExternalActionIdentity.restore(raw, M.NativeExternalActionIdentity.sha256(raw))
        doc["records"].pop()
        doc["scientific_pass"] = True
        raw = M._canonical(doc)
        with self.assertRaisesRegex(ValueError, "WSCM_CHECKPOINT_REJECTED"):
            M.NativeExternalActionIdentity.restore(raw, M.NativeExternalActionIdentity.sha256(raw))

    def test_rehashed_outcome_edit_cannot_fake_stored_receipt(self):
        m = append(M.NativeExternalActionIdentity(), 9, ((0, 0),), (1,))
        doc = json.loads(m.checkpoint())
        doc["records"][0][3] = 0
        raw = M._canonical(doc)
        with self.assertRaisesRegex(ValueError, "WSCM_CHECKPOINT_REJECTED"):
            M.NativeExternalActionIdentity.restore(
                raw, M.NativeExternalActionIdentity.sha256(raw))

    def test_stable_action_capacity_no_eviction(self):
        m = M.NativeExternalActionIdentity()
        for action in range(M.MAX_ACTIONS):
            raw, pin = receipt(action, (0, 0), 1, action + 1)
            m = m.observe_public_receipt({"public_view": [0, 0],
                                          "external_action_id": action}, raw, pin)
        raw, pin = receipt(90017, (0, 0), 1, 100)
        with self.assertRaisesRegex(ValueError, "WSCM_ACTION_CAPACITY"):
            m.observe_public_receipt({"public_view": [0, 0],
                                      "external_action_id": 90017}, raw, pin)
        self.assertEqual(len(m._rows), M.MAX_ACTIONS)

    def test_six_fresh_four_id_regimes_cold_preserve_old_evidence(self):
        """Fixture-only capacity/retention, not learned transfer or native world use."""
        self.assertGreaterEqual(M.MAX_ACTIONS, 24)
        laws = {
            "A": ((0, 0, 1, 1), (0, 1, 0, 1),
                  (0, 1, 1, 0), (0, 0, 0, 1)),
            "B": ((1, 1, 0, 0), (1, 0, 1, 0),
                  (0, 1, 1, 1), (1, 1, 1, 0)),
            "C": ((0, 0, 1, 1), (1, 0, 0, 1),
                  (1, 0, 1, 1), (0, 1, 1, 1)),
        }
        sequence = ("A", "B", "A", "C", "B", "A")
        m = M.NativeExternalActionIdentity()
        witnessed = {}
        source_id = 1
        first_a = 31000
        for phase, law in enumerate(sequence):
            for role in range(4):
                action = 31000 + 100 * phase + 9 * role
                expected = laws[law][role]
                self.assertIsNone(m.observed_signature(action))
                for idx, view in enumerate(M.STATES):
                    raw, pin = receipt(action, view, expected[idx], source_id)
                    source_id += 1
                    previous = m
                    m = m.observe_public_receipt(
                        {"public_view": list(view), "external_action_id": action},
                        raw, pin)
                    self.assertIsNone(previous.observed_signature(action))
                    if idx != 3:
                        self.assertIsNone(m.observed_signature(action))
                self.assertEqual(m.observed_signature(action), expected)
                witnessed[action] = expected
            old = m.checkpoint()
            cold = M.NativeExternalActionIdentity.restore(old, M.NativeExternalActionIdentity.sha256(old))
            self.assertEqual(cold.checkpoint(), old)
            for action, expected in witnessed.items():
                self.assertEqual(cold.observed_signature(action), expected)
            self.assertEqual(m.checkpoint(), old)
        self.assertEqual(len(witnessed), 24)
        self.assertEqual(source_id - 1, 96)
        returned_a = 31000 + 2 * 100
        self.assertIs(m.observed_equivalent(first_a, returned_a), True)
        self.assertIs(m.observed_equivalent(first_a, 31000 + 1 * 100), False)
        raw, pin = receipt(90017, (0, 0), 1, source_id)
        m2 = m.observe_public_receipt(
            {"public_view": [0, 0], "external_action_id": 90017}, raw, pin)
        self.assertIsNone(m2.observed_signature(90017))
        self.assertEqual(m2.observed_signature(first_a), witnessed[first_a])
        self.assertEqual(m.checkpoint(), old)

    def test_32_distinct_id_capacity_and_256_event_cold_limit(self):
        """Full bounded checkpoint restores; 33rd ID and 257th event fail."""
        self.assertEqual(M.MAX_ACTIONS, 32)
        m = M.NativeExternalActionIdentity()
        source_id = 1
        for action in range(32):
            for repeat in range(2):
                for view in M.STATES:
                    raw, pin = receipt(action, view, view[0], source_id)
                    source_id += 1
                    m = m.observe_public_receipt(
                        {"public_view": list(view), "external_action_id": action},
                        raw, pin)
        self.assertEqual(source_id - 1, M.MAX_EVENTS)
        self.assertEqual(len(m._rows), 256)
        raw = m.checkpoint()
        self.assertLessEqual(len(raw), M.MAX_CHECKPOINT_BYTES)
        cold = M.NativeExternalActionIdentity.restore(raw, M.NativeExternalActionIdentity.sha256(raw))
        self.assertEqual(cold.checkpoint(), raw)
        for action in range(32):
            self.assertEqual(cold.observed_signature(action), (0, 0, 1, 1))
        extra, extra_pin = receipt(99999, (0, 0), 1, source_id)
        with self.assertRaisesRegex(ValueError, "WSCM_EVENT_CAPACITY"):
            m.observe_public_receipt(
                {"public_view": [0, 0], "external_action_id": 99999}, extra, extra_pin)
        self.assertEqual(raw, m.checkpoint())

    def test_max_events_remain_cold_restorable(self):
        m = M.NativeExternalActionIdentity()
        for event in range(M.MAX_EVENTS):
            raw, pin = receipt(7, (0, 0), event % 2, event + 1)
            m = m.observe_public_receipt({"public_view": [0, 0],
                                          "external_action_id": 7}, raw, pin)
        saved = m.checkpoint()
        self.assertLessEqual(len(saved), M.MAX_CHECKPOINT_BYTES)
        restored = M.NativeExternalActionIdentity.restore(saved, M.NativeExternalActionIdentity.sha256(saved))
        self.assertEqual(saved, restored.checkpoint())
        raw, pin = receipt(7, (0, 0), 1, 1000)
        with self.assertRaisesRegex(ValueError, "WSCM_EVENT_CAPACITY"):
            m.observe_public_receipt({"public_view": [0, 0],
                                      "external_action_id": 7}, raw, pin)
        self.assertEqual(m.checkpoint(), saved)

    def test_no_oracle_or_authority_escalation_in_native_component(self):
        source = SOURCE.read_text("utf-8")
        self.assertNotIn("ID_TO_ROLE", source)
        self.assertNotIn("PHASE_LAW", source)
        self.assertNotIn("NativeEpisodeExperience", source.split("class NativeExternalActionIdentity:")[0])
        self.assertNotIn("native_accepted", source)
        self.assertNotIn("scientific_pass", source)


if __name__ == "__main__":
    unittest.main()

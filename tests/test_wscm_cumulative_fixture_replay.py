"""Opt-in fixture-only cumulative cold reuse; never original-source science."""
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_property_knowledge import NativePropertyKnowledge
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner, EXPERIENCE_SOURCE
from yggdrasil.native_causal_amalgam import NativeCausalAmalgam
from yggdrasil.native_jepa2_multilearner import ActionLatentSpecialist
from yggdrasil.native_jepa_temporal import TemporalLatentSpecialist
from yggdrasil.native_dtr_history import SOURCE_PIN as DTR_PIN
from yggdrasil.native_stochastic_history import SOURCE_PIN as MDP_PIN
from yggdrasil.native_external_action_identity import RECEIPT_SCHEMA, SOURCE_MODE

ROOT = Path(__file__).resolve().parents[1]


def property_parent():
    p = NativePropertyKnowledge("ckad13-test", entities=8, context_bits=3)
    rows = [[e, b, (e >> b) & 1] for e in range(8) for b in range(3)]
    p = p.stage_properties(rows, digest(canonical(rows)), source_namespace="ckad13-test")
    raw = p.checkpoint()
    return NativeCumulativeLearner(raw, digest(raw))


def parent():
    m = property_parent()
    rows = [[x & 7, x >> 3, int(sum((x >> b) & 1 for b in range(3)) >= 2)]
            for x in range(16)]
    m = m.observe(0, rows, digest(canonical(rows)), source_ref="a" * 64)
    mdp = (ROOT / "research/contrib/chatgpt/NKR-20/source_fixture.json").read_bytes()
    dtr = (ROOT / "research/contrib/chatgpt/CKAD-16/source_public_fit.json").read_bytes()
    m = m.observe_cached_history(mdp, MDP_PIN, 23)
    return m.observe_cached_dtr(dtr, DTR_PIN, 64)


def receipt(action, view, result, number):
    doc = {"schema": RECEIPT_SCHEMA, "source_mode": SOURCE_MODE,
           "source_id": f"{number:064x}", "public_view": list(view),
           "external_action_id": action, "outcome": result}
    raw = canonical(doc)
    return {"public_view": list(view), "external_action_id": action}, raw, digest(raw)


def episode(system):
    identifier = f"{500:064x}"
    views = ((0, 0), (0, 1))
    row = {"s1": 0, "x1": 0, "s2": 1, "x2": 0, "y": 1}
    return system.observe_experience(
        identifier, views, row, source_sha256=EXPERIENCE_SOURCE,
        packet_sha256=digest(canonical([identifier, views, row])))


class WSCMCumulativeReplayTest(unittest.TestCase):
    def test_original_parent_gate_and_no_ghost_fixture(self):
        request, raw, pin = receipt(1301, (0, 0), 0, 1)
        m = property_parent()
        original = m.checkpoint()
        with self.assertRaisesRegex(ValueError, "EPISODE_REQUIRES_INTEGRATED_PARENT"):
            m.observe_external_fixture(request, raw, pin)
        self.assertIsNone(m.observed_external_fixture_value((0, 0), 1301))
        self.assertEqual(m.checkpoint(), original)

    def test_cumulative_opaque_evidence_cold_and_mixed_binary(self):
        m = parent()
        original = m.checkpoint()
        views = ((0, 0), (0, 1), (1, 0), (1, 1))
        for i, view in enumerate(views):
            request, raw, pin = receipt(1301, view, view[0], i + 1)
            prior = m.checkpoint()
            updated = m.observe_external_fixture(request, raw, pin)
            self.assertEqual(m.checkpoint(), prior)
            self.assertEqual(updated._episode_reader()._ledger,
                             m._episode_reader()._ledger)
            m = updated
        self.assertNotEqual(m.checkpoint(), original)
        self.assertEqual(m.observed_external_fixture_value((1, 0), 1301), 1)
        self.assertIsNone(m.observed_external_fixture_value((0, 0), 90017))
        cold = NativeCumulativeLearner.restore(m.checkpoint(), digest(m.checkpoint()))
        self.assertEqual(cold.checkpoint(), m.checkpoint())
        advanced = episode(cold)
        self.assertEqual(advanced._episode_reader().info()["count"], 1)
        self.assertEqual(advanced.observed_external_fixture_value((1, 0), 1301), 1)
        again = NativeCumulativeLearner.restore(
            advanced.checkpoint(), digest(advanced.checkpoint()))
        self.assertEqual(again.checkpoint(), advanced.checkpoint())

    def test_amalgam_replays_external_and_binary_suffix(self):
        heads = (ActionLatentSpecialist("transition"), ActionLatentSpecialist("reward"),
                 TemporalLatentSpecialist("transition"), TemporalLatentSpecialist("reward"))
        base = NativeCausalAmalgam(parent(), heads, "a" * 64, "b" * 64)
        request, raw, pin = receipt(1301, (0, 0), 0, 1)
        passive = base.observe_external_fixture(request, raw, pin)
        self.assertIs(passive.observe_external_fixture(request, raw, pin), passive)
        self.assertEqual([h.steps for h in base._heads],
                         [h.steps for h in passive._heads])
        mixed = episode(passive)
        request2, raw2, pin2 = receipt(1301, (1, 0), 1, 2)
        mixed = mixed.observe_external_fixture(request2, raw2, pin2)
        saved = mixed.checkpoint()
        # This isolates Amalgam's actual replay/verification logic while
        # replacing only the unrelated 1,025-witness + donor activation source.
        with patch.object(NativeCausalAmalgam, "activate", return_value=base):
            restored = NativeCausalAmalgam.restore(
                saved, digest(saved), native_parent=b"", native_pin="a" * 64,
                donor_parent=b"", donor_pin="b" * 64)
        self.assertEqual(restored.checkpoint(), saved)
        self.assertEqual(restored.native._episode_reader().info()["count"], 1)
        self.assertIsNone(restored.native.observed_external_fixture_value((0, 0), 1301))

    def test_reject_forged_authority_and_conflicting_receipt_without_mutation(self):
        m = parent()
        start = m.checkpoint()
        request, raw, pin = receipt(1301, (0, 0), 0, 1)
        doc = json.loads(raw)
        doc["source_mode"] = "authenticated"
        forged = canonical(doc)
        with self.assertRaises(ValueError):
            m.observe_external_fixture(request, forged, digest(forged))
        with self.assertRaisesRegex(ValueError, "WSCM_PUBLIC_RECEIPT_MISMATCH"):
            m.observe_external_fixture(
                {"public_view": [1, 1], "external_action_id": 1301}, raw, pin)
        self.assertEqual(m.checkpoint(), start)
        staged = m.observe_external_fixture(request, raw, pin)
        conflicting, other, other_pin = receipt(1301, (0, 0), 1, 1)
        with self.assertRaisesRegex(ValueError, "WSCM_SOURCE_REPLAY_CONFLICT"):
            staged.observe_external_fixture(conflicting, other, other_pin)
        self.assertEqual(staged.observe_external_fixture(request, raw, pin), staged)

    def test_consolidation_preserves_passive_memory_on_exact_checkpoint(self):
        m = parent()
        for i, view in enumerate(((0, 0), (0, 1), (1, 0), (1, 1))):
            request, raw, pin = receipt(1301, view, view[0], i + 1)
            m = m.observe_external_fixture(request, raw, pin)
        m = episode(m)
        old = m.checkpoint()
        before_state = m._episode_reader().info()["state_sha256"]
        consolidated = m.consolidate_experience()
        self.assertEqual(consolidated.checkpoint(), old)
        self.assertEqual(consolidated._episode_reader().info()["state_sha256"],
                         before_state)
        self.assertEqual(consolidated.observed_external_fixture_value(
            (1, 0), 1301), 1)
        self.assertEqual(m.checkpoint(), old)
        cold = NativeCumulativeLearner.restore(old, digest(old))
        self.assertEqual(cold.consolidate_experience().checkpoint(), old)

    def test_consolidation_does_not_create_ghost_or_promote_fixture(self):
        m = parent()
        m = episode(m)
        initial = m.checkpoint()
        self.assertEqual(m.consolidate_experience().checkpoint(), initial)
        request, raw, pin = receipt(1301, (0, 0), 0, 1)
        after = m.observe_external_fixture(request, raw, pin)
        original_bank = m._episode_reader()._transition.snapshot()
        original_info = m._episode_reader().info()["state_sha256"]
        cold = after.consolidate_experience()
        self.assertEqual(cold.checkpoint(), after.checkpoint())
        self.assertEqual(cold._episode_reader()._transition.snapshot(),
                         original_bank)
        self.assertEqual(cold._episode_reader().info()["state_sha256"],
                         original_info)
        self.assertIsNone(cold.observed_external_fixture_value((0, 0), 1301))
        self.assertEqual(m.checkpoint(), initial)

    def test_24_fresh_ids_amalgam_cold_ledger_and_specialist_isolation(self):
        """Source-free six-phase cold replay, not original-donor activation."""
        heads = (ActionLatentSpecialist("transition"), ActionLatentSpecialist("reward"),
                 TemporalLatentSpecialist("transition"), TemporalLatentSpecialist("reward"))
        base = NativeCausalAmalgam(parent(), heads, "a" * 64, "b" * 64)
        untouched_native = base.native.checkpoint()
        untouched_heads = tuple(h.steps for h in base._heads)
        states = ((0, 0), (0, 1), (1, 0), (1, 1))
        signatures = {}
        m = base
        source_id = 1000
        for phase in range(6):
            for slot in range(4):
                action = 31000 + phase * 100 + slot * 9
                # Harness-only fixture outcomes; learner gets only signed
                # publicly witnessed request+outcome, no phase or role field.
                truth = tuple((state[0] ^ (state[1] & (slot & 1)) ^
                               (phase & 1)) for state in states)
                self.assertIsNone(m.native.observed_external_fixture_value(
                    (0, 0), action))
                for index, state in enumerate(states):
                    request, raw, pin = receipt(action, state, truth[index], source_id)
                    source_id += 1
                    previous = m
                    m = m.observe_external_fixture(request, raw, pin)
                    self.assertEqual(previous.native.checkpoint(),
                                     (base.native.checkpoint() if phase == slot == index == 0
                                      else previous.native.checkpoint()))
                    if index < 3:
                        self.assertIsNone(m.native.observed_external_fixture_value(
                            (0, 0), action))
                signatures[action] = truth
            frozen = m.checkpoint()
            with patch.object(NativeCausalAmalgam, "activate", return_value=base):
                cold = NativeCausalAmalgam.restore(
                    frozen, digest(frozen), native_parent=b"", native_pin="a" * 64,
                    donor_parent=b"", donor_pin="b" * 64)
            self.assertEqual(cold.checkpoint(), frozen)
            self.assertEqual(tuple(h.steps for h in cold._heads), untouched_heads)
            self.assertEqual(cold.native._episode_reader()._ledger,
                             base.native._episode_reader()._ledger)
            for action, truth in signatures.items():
                for index, state in enumerate(states):
                    self.assertEqual(cold.native.observed_external_fixture_value(
                        state, action), truth[index])
            self.assertEqual(base.native.checkpoint(), untouched_native)
        self.assertEqual(source_id - 1000, 96)
        self.assertEqual(len(signatures), 24)
        binary = episode(m)
        frozen = binary.checkpoint()
        with patch.object(NativeCausalAmalgam, "activate", return_value=base):
            cold = NativeCausalAmalgam.restore(
                frozen, digest(frozen), native_parent=b"", native_pin="a" * 64,
                donor_parent=b"", donor_pin="b" * 64)
        self.assertEqual(cold.checkpoint(), frozen)
        self.assertEqual(cold.native._episode_reader().info()["count"], 1)
        for action, truth in signatures.items():
            self.assertEqual(cold.native.observed_external_fixture_value(
                (1, 0), action), truth[2])
        self.assertEqual(m.native._episode_reader().info()["count"], 0)

    def test_32_ids_256_rows_integrated_capacity_and_cold_preservation(self):
        """The cumulative/native envelope must not silently evict prior IDs."""
        m = parent()
        before = m.checkpoint()
        native_before = m._episode_reader().info()["state_sha256"]
        states = ((0, 0), (0, 1), (1, 0), (1, 1))
        for action_index in range(32):
            action = 50000 + 97 * action_index
            for index, state in enumerate(states):
                request, raw, pin = receipt(action, state, state[0],
                                            2000 + 8 * action_index + index)
                m = m.observe_external_fixture(request, raw, pin)
            self.assertEqual(m.observed_external_fixture_value((1, 0), action), 1)
        saved128 = m.checkpoint()
        new_request, new_raw, new_pin = receipt(99001, (0, 0), 0, 9000)
        with self.assertRaisesRegex(ValueError, "WSCM_ACTION_CAPACITY"):
            m.observe_external_fixture(new_request, new_raw, new_pin)
        self.assertEqual(m.checkpoint(), saved128)
        cold128 = NativeCumulativeLearner.restore(saved128, digest(saved128))
        self.assertEqual(cold128.checkpoint(), saved128)
        for action_index in range(32):
            action = 50000 + 97 * action_index
            for index, state in enumerate(states):
                request, raw, pin = receipt(action, state, state[0],
                                            2000 + 8 * action_index + 4 + index)
                m = m.observe_external_fixture(request, raw, pin)
        saved256 = m.checkpoint()
        self.assertEqual(len(m._episode_reader()._external_action_fixture._rows), 256)
        with self.assertRaisesRegex(ValueError, "WSCM_EVENT_CAPACITY"):
            request, raw, pin = receipt(50000, (0, 0), 0, 9001)
            m.observe_external_fixture(request, raw, pin)
        self.assertEqual(m.checkpoint(), saved256)
        cold256 = NativeCumulativeLearner.restore(saved256, digest(saved256))
        self.assertEqual(cold256.checkpoint(), saved256)
        self.assertEqual(cold256.consolidate_experience().checkpoint(), saved256)
        self.assertEqual(cold256._episode_reader().info()["state_sha256"],
                         native_before)
        self.assertEqual(cold256._episode_reader()._ledger, ())
        for action_index in range(32):
            action = 50000 + 97 * action_index
            for state in states:
                self.assertEqual(cold256.observed_external_fixture_value(
                    state, action), state[0])
        self.assertEqual(m.info()["accepted_native"], False)
        self.assertEqual(m.info()["scientific_pass"], False)
        self.assertEqual(parent().checkpoint(), before)


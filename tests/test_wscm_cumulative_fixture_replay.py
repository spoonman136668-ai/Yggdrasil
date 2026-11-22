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

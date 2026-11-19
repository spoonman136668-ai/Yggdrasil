"""Quine retention veto: immutable, loss-specific, source-free negative controls."""
from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace
import unittest

from yggdrasil.native_context_basis import canonical, digest

PATH = (Path(__file__).resolve().parents[1] / "research/contrib/chatgpt/"
        "CAUSAL-AMALGAM/quine_retention.py")
SPEC = spec_from_file_location("amalgam_quine_retention", PATH)
QUINE = module_from_spec(SPEC)
SPEC.loader.exec_module(QUINE)


def evidence(count=24):
    return tuple((f"witness-{i}", ((i, 0), (i, 1)), 0, i % 2, 0, i % 2)
                 for i in range(count))


class FakeSystem:
    """Fake forecast adapter, NOT a substitute scientific learner."""

    def __init__(self, events, changes=None, *, mutated=False):
        self.events = tuple(events)
        self.changes = dict(changes or {})
        self.native = SimpleNamespace(
            _episode_reader=lambda: SimpleNamespace(_ledger=self.events),
            experience_context_forecast=self.forecast,
        )
        self.mutated = mutated

    def forecast(self, view, first, *terminal):
        index = view[0]
        kind = "reward" if terminal else "transition"
        if (index, kind) in self.changes:
            return self.changes[index, kind]
        outcome = index % 2
        # Regressions can be exposed without any stochastic source actions.
        return Fraction(3, 4) if outcome else Fraction(1, 4)

    def checkpoint(self):
        return canonical({
            "events": self.events,
            "changes": [[i, kind, str(value)]
                        for (i, kind), value in sorted(self.changes.items())],
        })

    def observe_experience(self, identifier, views, row, *, source_sha256, packet_sha256):
        candidate = (identifier, views, row["x1"], row["s2"], row["x2"], row["y"])
        if packet_sha256 != digest(canonical([identifier, views, row])):
            raise ValueError("source packet mismatch")
        if any(event[0] == identifier for event in self.events):
            if candidate not in self.events:
                raise ValueError("conflicting replay")
            return self
        return FakeSystem(self.events + (candidate,), self.changes)


class FakeSelector:
    """Source-free mock of a selectable policy, NOT a scientific predictor."""

    def __init__(self, system, evidence=None, *, minimum_gain=Fraction(1, 100)):
        self.system = system
        self.window = 16
        self.minimum_count = 4
        self.minimum_gain = minimum_gain
        self.enable_reward = False
        self._evidence = {} if evidence is None else dict(evidence)

    def forecast(self, views, first, *terminal):
        key = (views[0][0], first, *terminal)
        if key in self._evidence:
            # Changes policy routing without changing the native predictor.
            return Fraction(9, 10)
        return self.system.native.experience_context_forecast(views[0], first, *terminal)

    def observe_experience(self, identifier, views, row, *, source_sha256, packet_sha256):
        updated = self.system.observe_experience(
            identifier, views, row, source_sha256=source_sha256,
            packet_sha256=packet_sha256)
        return self if updated is self.system else FakeSelector(
            updated, self._evidence, minimum_gain=self.minimum_gain)


class QuineRetentionTests(unittest.TestCase):
    def setUp(self):
        self.anchor = FakeSystem(evidence())
        self.current = self.anchor
        self.windows = {"mastered-A": (0, 12), "mastered-B": (12, 24)}
        self.manifest = QUINE.select_quines(self.anchor, self.windows)
        self.pin = digest(canonical(self.manifest))
        self.next_event = ("next-24", ((24, 0), (24, 1)), 0, 0, 0, 0)

    def proposal(self, changes=None, current=None):
        parent = current or self.current
        return FakeSystem(parent.events + (self.next_event,), changes or parent.changes)

    def test_selects_fixed_high_surprise_charged_witnesses_without_replay(self):
        self.assertEqual(self.manifest["schema"], QUINE.SCHEMA)
        self.assertEqual(self.manifest["quines_per_regime"], 8)
        selected = []
        for name, group in self.manifest["regimes"].items():
            self.assertEqual(len(group["quines"]), 8)
            for item in group["quines"]:
                selected.append(item["index"])
                self.assertIn(item["signed_reward_proxy"], (-1, 1))
        self.assertEqual(len(set(selected)), 16)
        self.assertEqual(self.manifest, QUINE.select_quines(self.anchor, self.windows))
        self.assertIn("not_prequential", self.manifest["ranking"])

    def test_improved_candidate_admitted_without_overwriting_anchor(self):
        candidate = self.proposal()
        chosen, report = QUINE.assess_update(
            self.anchor, self.current, candidate, self.manifest, self.pin)
        self.assertIs(chosen, candidate)
        self.assertEqual(report["status"], "ADMIT_RESEARCH_CANDIDATE")
        self.assertEqual(report["quines_checked"], 16)
        self.assertIsNone(report["rejected_shadow_checkpoint_sha256"])
        self.assertEqual(len(self.anchor.events), 24)

    def test_one_bad_quine_blocks_shared_overwrite(self):
        candidate = self.proposal({(0, "transition"): Fraction(9, 10)})
        chosen, report = QUINE.assess_update(
            self.anchor, self.current, candidate, self.manifest, self.pin)
        self.assertIs(chosen, self.current)
        self.assertEqual(report["status"], "VETO_SHARED_STATE_OVERWRITE")
        self.assertEqual(report["rejected_shadow_checkpoint_sha256"],
                         digest(candidate.checkpoint()))
        self.assertGreater(report["largest_single_quine_delta"], 0.02)
        self.assertEqual(report["speciation"], "proposal_only_not_activated")

    def test_reward_drift_alone_blocks_update(self):
        candidate = self.proposal({(0, "reward"): Fraction(9, 10)})
        chosen, report = QUINE.assess_update(
            self.anchor, self.current, candidate, self.manifest, self.pin)
        self.assertIs(chosen, self.current)
        self.assertFalse(report["regimes"]["mastered-A"]["pass"])

    def test_non_quine_regime_drift_still_blocks_update(self):
        selected = {item["index"] for item in
                    self.manifest["regimes"]["mastered-A"]["quines"]}
        omitted = set(range(0, 12)) - selected
        self.assertEqual(len(omitted), 4)
        candidate = self.proposal({
            (index, "transition"): Fraction(9, 10) if index % 2 == 0 else Fraction(1, 10)
            for index in omitted
        })
        chosen, report = QUINE.assess_update(
            self.anchor, self.current, candidate, self.manifest, self.pin)
        self.assertIs(chosen, self.current)
        self.assertLessEqual(report["largest_single_quine_delta"], 0.02)
        self.assertGreater(report["regimes"]["mastered-A"]["familiar_transition_drift"], 0.02)

    def test_rejected_proposal_preserves_previously_admitted_witness(self):
        first, _ = QUINE.assess_update(
            self.anchor, self.current, self.proposal(), self.manifest, self.pin)
        next_after_first = ("next-25", ((25, 0), (25, 1)), 0, 1, 0, 1)
        second = FakeSystem(first.events + (next_after_first,),
                            {(0, "transition"): Fraction(9, 10)})
        kept, _ = QUINE.assess_update(self.anchor, first, second,
                                      self.manifest, self.pin)
        self.assertIs(kept, first)
        self.assertEqual(len(kept.events), 25)
        self.assertEqual(len(self.anchor.events), 24)

    def test_rejects_tampering_overlap_omission_and_multi_witness_jump(self):
        candidate = self.proposal()
        with self.assertRaisesRegex(ValueError, "exactly 1/50"):
            QUINE.assess_update(self.anchor, self.current, candidate,
                                self.manifest, self.pin,
                                max_brier_drift=Fraction(1, 2))
        with self.assertRaisesRegex(ValueError, "pin mismatch"):
            QUINE.assess_update(self.anchor, self.current, candidate,
                                self.manifest, "0" * 64)
        with self.assertRaisesRegex(ValueError, "Overlapping"):
            QUINE.select_quines(self.anchor, {"a": (0, 12), "b": (10, 22)})
        with self.assertRaisesRegex(ValueError, "cannot supply"):
            QUINE.select_quines(self.anchor, {"a": (0, 3)})
        rewritten = FakeSystem((("forged",),) + self.anchor.events[1:]
                               + (self.next_event,))
        with self.assertRaisesRegex(ValueError, "prefix"):
            QUINE.assess_update(self.anchor, self.current, rewritten,
                                self.manifest, self.pin)
        two = FakeSystem(self.anchor.events + (self.next_event, self.next_event))
        with self.assertRaisesRegex(ValueError, "exactly one"):
            QUINE.assess_update(self.anchor, self.current, two,
                                self.manifest, self.pin)

    def test_selector_only_old_world_regression_vetoes_unchanged_native(self):
        anchor = FakeSelector(self.anchor)
        manifest = QUINE.select_quines(anchor, self.windows)
        pin = digest(canonical(manifest))
        native_candidate = self.proposal()
        changed = {(0, 0): ((Fraction(1, 2), Fraction(0)),)}
        candidate = FakeSelector(native_candidate, changed)
        chosen, report = QUINE.assess_update(
            anchor, anchor, candidate, manifest, pin)
        self.assertIs(chosen, anchor)
        self.assertEqual(report["status"], "VETO_SHARED_STATE_OVERWRITE")
        self.assertGreater(report["largest_single_quine_delta"], .02)
        self.assertEqual(self.anchor.forecast((0, 0), 0),
                         candidate.system.forecast((0, 0), 0))

    def test_selector_mode_bypass_and_config_drift_fail_closed(self):
        anchor = FakeSelector(self.anchor)
        manifest = QUINE.select_quines(anchor, self.windows)
        pin = digest(canonical(manifest))
        raw = self.proposal()
        with self.assertRaisesRegex(ValueError, "bypass"):
            QUINE.assess_update(anchor, anchor, raw, manifest, pin)
        with self.assertRaisesRegex(ValueError, "bypass"):
            QUINE.assess_update(self.anchor, anchor, FakeSelector(raw),
                                self.manifest, self.pin)
        with self.assertRaisesRegex(ValueError, "configuration changed"):
            QUINE.assess_update(
                anchor, anchor,
                FakeSelector(raw, minimum_gain=Fraction(1, 20)),
                manifest, pin)

    def test_selector_replay_custody_detects_routing_divergence(self):
        evidence = {(0, 0): ((Fraction(1, 2), Fraction(0)),)}
        original = FakeSelector(self.anchor, evidence)
        restored = FakeSelector(FakeSystem(evidence_all := self.anchor.events),
                                evidence.copy())
        report = QUINE.verify_selector_replay(original, restored)
        self.assertEqual(report["readout_witnesses"], len(evidence_all))
        self.assertEqual(report["source_actions"], 0)
        with self.assertRaisesRegex(ValueError, "custody differs"):
            QUINE.verify_selector_replay(original, FakeSelector(self.anchor))
        with self.assertRaisesRegex(ValueError, "requires active selectors"):
            QUINE.verify_selector_replay(self.anchor, FakeSystem(self.anchor.events))

    def test_selector_guarded_observe_stays_single_shared_state(self):
        anchor = FakeSelector(self.anchor)
        manifest = QUINE.select_quines(anchor, self.windows)
        pin = digest(canonical(manifest))
        identifier, views, first, state, second, reward = self.next_event
        row = {"s1": views[0][0], "x1": first, "s2": state,
               "x2": second, "y": reward}
        packet = digest(canonical([identifier, views, row]))
        selected, result = QUINE.guarded_observe(
            anchor, anchor, manifest, pin, identifier, views, row,
            source_sha256="pinned-fixture", packet_sha256=packet)
        self.assertEqual(result["status"], "ADMIT_RESEARCH_CANDIDATE")
        self.assertEqual(len(selected.system.events), 25)
        self.assertEqual(len(anchor.system.events), 24)

    def test_atomic_guarded_observe_and_idempotent_replay(self):
        identifier, views, first, state, second, reward = self.next_event
        row = {"s1": views[0][0], "x1": first, "s2": state,
               "x2": second, "y": reward}
        packet = digest(canonical([identifier, views, row]))
        selected, report = QUINE.guarded_observe(
            self.anchor, self.current, self.manifest, self.pin,
            identifier, views, row,
            source_sha256="pinned-fixture", packet_sha256=packet)
        self.assertEqual(report["status"], "ADMIT_RESEARCH_CANDIDATE")
        self.assertEqual(len(selected.events), 25)
        unchanged, replay = QUINE.guarded_observe(
            self.anchor, selected, self.manifest, self.pin, identifier,
            views, row, source_sha256="pinned-fixture", packet_sha256=packet)
        self.assertIs(unchanged, selected)
        self.assertEqual(replay["status"], "IDEMPOTENT_WITNESS")
        self.assertEqual(len(self.anchor.events), 24)


if __name__ == "__main__":
    unittest.main()

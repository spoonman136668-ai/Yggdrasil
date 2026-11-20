"""Cumulative envelope source-free tests: no trained or owner source touched."""
import json
from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest
from yggdrasil.native_context_basis import canonical, digest
from tests.test_amalgam_quine_retention import QUINE, FakeSystem, FakeSelector, evidence

P = (Path(__file__).resolve().parents[1] /
     "research/contrib/chatgpt/CAUSAL-AMALGAM/cumulative_checkpoint.py")
S = spec_from_file_location("amalgam_cumulative_checkpoint", P)
B = module_from_spec(S)
S.loader.exec_module(B)


def restore_core(raw, expected):
    if digest(raw) != expected:
        raise ValueError("Restore source-pinned core mismatch")
    data = json.loads(raw)
    events = tuple((e[0], tuple(tuple(view) for view in e[1]), *e[2:])
                   for e in data["events"])
    changes = {(index, kind): Fraction(value)
               for index, kind, value in data["changes"]}
    return FakeSystem(events, changes)


def restore_selector(system, receipt):
    window, minimum, gain, rewards = receipt["config"]
    history = {tuple(key): tuple((QUINE.decode_selector_fraction(a),
                                  QUINE.decode_selector_fraction(b)) for a, b in rows)
               for key, rows in receipt["evidence"]}
    selector = FakeSelector(system, history, minimum_gain=Fraction(gain))
    selector.window, selector.minimum_count = window, minimum
    selector.enable_reward = rewards
    return selector


class EnvelopeTests(unittest.TestCase):
    def setUp(self):
        old = FakeSystem(evidence())
        new = FakeSystem(old.events +
                         (("accepted-24", ((24, 0), (24, 1)), 0, 0, 0, 1),))
        routed = {(0, 0): ((Fraction(1, 2), Fraction(0)),)}
        self.anchor = FakeSelector(old, routed)
        self.active = FakeSelector(new, routed)
        self.quines = QUINE.select_quines(
            self.anchor, {"mastered-A": (0, 12), "mastered-B": (12, 24)})
        self.pin = digest(canonical(self.quines))
        self.cursor = {"source_sha256": "a" * 64,
                       "owner_lease_sha256": "b" * 64, "next_ordinal": 26}
        event = ("vetoed-25", ((25, 0), (25, 1)), 0, 1, 0, 0)
        identifier, views, first, state, second, reward = event
        row = {"s1": views[0][0], "x1": first,
               "s2": state, "x2": second, "y": reward}
        self.veto = canonical({
            "schema": B.VETO_SCHEMA, "event": event,
            "source_sha256": "a" * 64,
            "packet_sha256": digest(canonical([identifier, views, row])),
            "active_before_sha256": "c" * 64,
            "rejected_candidate_sha256": "d" * 64})

    def seal(self, **kw):
        args = {"cursor": self.cursor, "veto_receipts": [self.veto],
                "guard": QUINE}
        args.update(kw)
        return B.seal(self.anchor, self.active, self.quines, self.pin, **args)

    def restore(self, raw, pin):
        return B.recover(raw, pin, restore_core=restore_core,
                         build_selector=restore_selector, guard=QUINE)

    def test_roundtrip_preserves_native_heads_routing_and_veto(self):
        raw, pin = self.seal()
        result = self.restore(raw, pin)
        self.assertEqual(result["anchor"].system.checkpoint(),
                         self.anchor.system.checkpoint())
        self.assertEqual(result["active"].system.checkpoint(),
                         self.active.system.checkpoint())
        self.assertEqual(QUINE._selector_receipt(result["active"]),
                         QUINE._selector_receipt(self.active))
        self.assertEqual(result["cursor"], self.cursor)
        self.assertEqual(result["veto_receipts"], (self.veto,))
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["owner_custody_verified"])
        self.assertEqual(result["source_actions"], 0)

    def test_idempotent_receipt_and_conflicting_id(self):
        raw, pin = self.seal(veto_receipts=[self.veto, self.veto])
        self.assertEqual(len(self.restore(raw, pin)["veto_receipts"]), 1)
        conflict = json.loads(self.veto)
        conflict["source_sha256"] = "e" * 64
        with self.assertRaisesRegex(ValueError, "VETO_CONFLICT"):
            self.seal(veto_receipts=[self.veto, canonical(conflict)])

    def test_rejects_accepted_witness_as_veto(self):
        receipt = json.loads(self.veto)
        receipt["event"][0] = "accepted-24"
        identifier, views, first, state, second, reward = receipt["event"]
        row = {"s1": views[0][0], "x1": first,
               "s2": state, "x2": second, "y": reward}
        receipt["packet_sha256"] = digest(canonical([identifier, views, row]))
        with self.assertRaisesRegex(ValueError, "VETO_ACCEPTED"):
            self.seal(veto_receipts=[canonical(receipt)])

    def test_rejects_forged_model_selector_and_old_readout(self):
        raw, _ = self.seal()
        changes = [
            ("active", "core_ascii", "forged"),
            ("active", "selector", None),
            ("active", "historical_readout_sha256", "f" * 64),
        ]
        for parent, key, value in changes:
            data = json.loads(raw)
            data[parent][key] = value
            broken = canonical(data)
            with self.subTest(field=key), self.assertRaises(ValueError):
                self.restore(broken, digest(broken))
        with self.assertRaisesRegex(ValueError, "BUNDLE_PIN"):
            self.restore(raw, "0" * 64)

    def test_rejects_forged_receipt_cursor_and_science_flag(self):
        raw, _ = self.seal()
        for field in ("receipt", "cursor", "scientific_pass"):
            data = json.loads(raw)
            if field == "receipt":
                data["vetoes"][0]["ascii"] = "forged"
            elif field == "cursor":
                data["cursor"]["next_ordinal"] = -1
            else:
                data["scientific_pass"] = True
            broken = canonical(data)
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.restore(broken, digest(broken))

    def test_rejects_wrong_packet_and_missing_restorer(self):
        record = json.loads(self.veto)
        record["packet_sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "VETO_PACKET"):
            self.seal(veto_receipts=[canonical(record)])
        raw, pin = self.seal()
        with self.assertRaisesRegex(ValueError, "RESTORE_CALLBACKS"):
            B.recover(raw, pin, restore_core=None,
                      build_selector=None, guard=QUINE)


if __name__ == "__main__":
    unittest.main()

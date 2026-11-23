"""Original native implementation: local repair archaeology and cold retention."""
import hashlib
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest
from fractions import Fraction

from yggdrasil.native_episode_experience import NativeEpisodeExperience

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research/contrib/chatgpt/WSCM-STRUCTURAL-01/repair_versions.py"
spec = spec_from_file_location("wscm_versions", SOURCE)
api = module_from_spec(spec)
spec.loader.exec_module(api)


def event(index, *, context, transition):
    identifier = hashlib.sha256(f"structural-01/{index}".encode()).hexdigest()
    views = ((context, 0), (context, 1))
    row = {"s1": context, "x1": 0, "s2": transition, "x2": 0, "y": context}
    return identifier, views, row


def make_repair(*, extra_return=0):
    native = NativeEpisodeExperience()
    for i in range(48):
        native = native.observe(*event(i, context=i % 2, transition=i % 2))
    old_ckpt = native.checkpoint()
    third = None
    for i in range(48, 51):
        ident, views, row = event(i, context=0, transition=1)
        native = native.observe(ident, views, row)
        third = ident
    for i in range(51, 51 + extra_return):
        native = native.observe(*event(i, context=0, transition=0))
    return native, old_ckpt, third


def read(native, evidence, version="before", **override):
    args = dict(last_evidence_id=evidence, target="transition", slot=0,
                action=0, version=version)
    args.update(override)
    return api.read_repair_version(native, **args)


class StructuralRepairTests(unittest.TestCase):
    def test_actual_native_repair_overwrites_live_counts(self):
        m, old, evid = make_repair()
        self.assertEqual(m._transition._counts[0][0], [0, 3])
        self.assertEqual(read(m, evid)["counts"], [24, 0])
        self.assertEqual(read(m, evid, "reset")["counts"], [0, 3])
        self.assertEqual(read(m, evid, "live")["counts"], [0, 3])
        self.assertEqual(read(m, evid)["probability"], Fraction(1, 26))
        self.assertEqual(read(m, evid, "reset")["probability"], Fraction(4, 5))
        self.assertNotEqual(m.checkpoint(), old)

    def test_cold_restore_recovers_exact_pre_repair_readout(self):
        m, _, ident = make_repair()
        blob = m.checkpoint()
        cold = NativeEpisodeExperience.restore(blob, hashlib.sha256(blob).hexdigest())
        self.assertEqual(cold.checkpoint(), blob)
        self.assertEqual(cold.consolidate().checkpoint(), blob)
        for variant in ("before", "reset", "live"):
            self.assertEqual(read(m, ident, variant), read(cold, ident, variant))

    def test_further_old_observations_do_not_destroy_archived_variant(self):
        m, _, ident = make_repair(extra_return=8)
        self.assertEqual(read(m, ident)["probability"], Fraction(1, 26))
        self.assertEqual(read(m, ident, "reset")["probability"], Fraction(4, 5))
        self.assertEqual(read(m, ident, "live")["probability"], Fraction(4, 13))
        self.assertEqual(m._transition._counts[0][0], [8, 3])

    def test_archived_version_survives_eight_familiar_return_events_and_cold(self):
        m, _, ident = make_repair(extra_return=8)
        checkpoint = m.checkpoint()
        cold = NativeEpisodeExperience.restore(
            checkpoint, hashlib.sha256(checkpoint).hexdigest())
        self.assertEqual(cold.checkpoint(), checkpoint)
        self.assertEqual(read(cold, ident, "before")["counts"], [24, 0])
        self.assertEqual(read(cold, ident, "reset")["counts"], [0, 3])
        self.assertEqual(read(cold, ident, "live")["counts"], [8, 3])
        self.assertEqual(cold.info()["repairs"], m.info()["repairs"])

    def test_read_only_does_not_mutate_any_checkpoint(self):
        m, _, ident = make_repair()
        before = m.checkpoint()
        for _ in range(4):
            for version in ("before", "reset", "live"):
                read(m, ident, version)
        self.assertEqual(m.checkpoint(), before)

    def test_no_evidence_no_forged_recall(self):
        m, _, ident = make_repair()
        with self.assertRaisesRegex(ValueError, "VERSION_RECEIPT_NOT_UNIQUE"):
            read(m, "0" * 64)
        with self.assertRaisesRegex(ValueError, "VERSION_WITNESS_ID"):
            read(m, "not-sha")
        with self.assertRaisesRegex(ValueError, "VERSION_RECEIPT_NOT_UNIQUE"):
            read(m, ident, slot=1)

    def test_wrong_target_action_version_rejected(self):
        m, _, ident = make_repair()
        for key, bad, error in [("target", "reward", "VERSION_TARGET"),
                                ("action", 1, "VERSION_RECEIPT_NOT_UNIQUE"),
                                ("version", "oracle", "VERSION_KIND"),
                                ("slot", -1, "VERSION_SLOT")]:
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, error):
                read(m, ident, **{key: bad})

    def test_no_repair_means_no_historical_epoch_is_invented(self):
        m = NativeEpisodeExperience(repair=False)
        for i in range(51):
            c=i%2 if i<48 else 0
            s=c if i<48 else 1
            m=m.observe(*event(i, context=c, transition=s))
        self.assertEqual(m.info()["repairs"], [])
        with self.assertRaisesRegex(ValueError, "VERSION_RECEIPT_NOT_UNIQUE"):
            read(m, event(50, context=0, transition=1)[0])

    def test_archived_state_has_no_fake_repairs(self):
        import os
        path = os.environ.get("WSCM_ARCHIVED_JOINT_PATH")
        if not path:
            self.skipTest("Source-pinned archived fixture not supplied")
        import json
        from pathlib import Path
        joint_bytes = Path(path).read_bytes()
        self.assertEqual(hashlib.sha256(joint_bytes).hexdigest(),
                         "576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8")
        joint = json.loads(joint_bytes)
        native = json.loads(joint["native_ascii"])
        evidence = native["experience_ascii"].encode("ascii")
        original = NativeEpisodeExperience.restore(
            evidence, hashlib.sha256(evidence).hexdigest())
        self.assertEqual(len(original._ledger), 1025)
        self.assertEqual(original.info()["repairs"], [])
        self.assertEqual(original.info()["state_sha256"],
                         "3c6433c9e60a0f7e6b750327ae7b705984fb20b25e8bd04fe16a3e9a31c9dde8")


if __name__ == "__main__":
    unittest.main()

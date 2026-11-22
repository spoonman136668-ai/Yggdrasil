"""Opt-in native-state envelope, source-free negatives; NOT scientific first use."""
import hashlib
import json
import unittest

from yggdrasil.native_episode_experience import (
    NativeEpisodeExperience, EXTERNAL_FIXTURE_SCHEMA,
)
from yggdrasil.native_external_action_identity import (
    NativeExternalActionIdentity, RECEIPT_SCHEMA, SOURCE_MODE, _canonical,
)
from yggdrasil.native_context_basis import digest


STATES = ((0, 0), (0, 1), (1, 0), (1, 1))
BIT_FN = (0, 0, 1, 1)


def fixture(action, state, outcome, identifier):
    document = {
        "schema": RECEIPT_SCHEMA, "source_mode": SOURCE_MODE,
        "source_id": f"{identifier:064x}",
        "public_view": list(state), "external_action_id": action,
        "outcome": outcome,
    }
    raw = _canonical(document)
    return raw, hashlib.sha256(raw).hexdigest()


def put(native, action, states=STATES, outcomes=BIT_FN, start=100):
    for i, (state, outcome) in enumerate(zip(states, outcomes)):
        raw, pin = fixture(action, state, outcome, start + i)
        native = native.observe_external_fixture(
            {"public_view": list(state), "external_action_id": action}, raw, pin)
    return native


def native_episode(native, identifier=1, state=0):
    return native.observe(
        f"{identifier:064x}",
        ((state, 0), (state, 0)),
        {"s1": 0, "x1": 0, "s2": state, "x2": 0, "y": state},
    )


class NativeEpisodeExternalFixtureGate(unittest.TestCase):
    def test_default_checkpoint_and_forecast_unchanged(self):
        base = native_episode(NativeEpisodeExperience())
        raw = base.checkpoint()
        self.assertNotEqual(json.loads(raw)["schema"], EXTERNAL_FIXTURE_SCHEMA)
        prior = base.forecast((0, 0), 0)
        staged = put(base, 1301, states=((0, 0),), outcomes=(0,))
        self.assertEqual(base.checkpoint(), raw)
        self.assertEqual(base.forecast((0, 0), 0), prior)
        self.assertEqual(staged.forecast((0, 0), 0), prior)
        self.assertEqual(staged._ledger, base._ledger)
        self.assertIsNone(staged.observed_external_fixture_value((0, 0), 1301))

    def test_external_id_is_not_binary_native_action(self):
        native = NativeEpisodeExperience()
        with self.assertRaises(ValueError):
            native.forecast((0, 0), 1301)
        self.assertIsNone(native.observed_external_fixture_value((0, 0), 1301))
        staged = put(native, 1301)
        self.assertEqual(staged.observed_external_fixture_value((1, 0), 1301), 1)
        self.assertEqual(staged.observed_external_fixture_value((0, 1), 1301), 0)
        self.assertEqual(len(staged._ledger), 0)

    def test_no_renamed_id_transfer_before_own_witnesses(self):
        native = put(NativeEpisodeExperience(), 1301)
        self.assertIsNone(native.observed_external_fixture_value((0, 0), 90017))
        for index in range(3):
            raw, pin = fixture(90017, STATES[index], BIT_FN[index], 200 + index)
            native = native.observe_external_fixture(
                {"public_view": list(STATES[index]),
                 "external_action_id": 90017}, raw, pin)
        self.assertIsNone(native.observed_external_fixture_value((0, 0), 90017))
        raw, pin = fixture(90017, STATES[3], BIT_FN[3], 203)
        native = native.observe_external_fixture(
            {"public_view": list(STATES[3]), "external_action_id": 90017}, raw, pin)
        self.assertEqual(native.observed_external_fixture_value((1, 1), 90017), 1)
        self.assertTrue(native._external_action_fixture.observed_equivalent(1301, 90017))

    def test_native_and_fixture_cold_checkpoint_jointly_pinned(self):
        original = native_episode(NativeEpisodeExperience())
        staged = put(original, 1301)
        raw = staged.checkpoint()
        doc = json.loads(raw)
        self.assertEqual(doc["schema"], EXTERNAL_FIXTURE_SCHEMA)
        self.assertFalse(doc["scientific_pass"])
        self.assertFalse(doc["native_accepted"])
        self.assertEqual(doc["native_checkpoint"], json.loads(original.checkpoint()))
        self.assertEqual(doc["native_sha256"], digest(original.checkpoint()))
        clone = NativeEpisodeExperience.restore(raw, digest(raw))
        self.assertEqual(clone.checkpoint(), raw)
        self.assertEqual(clone.info(), staged.info())
        self.assertEqual(clone.forecast((1, 0), 0), staged.forecast((1, 0), 0))
        self.assertEqual(clone.observed_external_fixture_value((1, 0), 1301), 1)
        self.assertNotEqual(clone.info()["external_action_fixture_sha256"],
                            clone.info()["state_sha256"])

    def test_original_observe_preserves_external_identity(self):
        staged = put(NativeEpisodeExperience(), 1301)
        updated = native_episode(staged)
        self.assertEqual(updated.observed_external_fixture_value((1, 0), 1301), 1)
        self.assertEqual(len(updated._ledger), 1)
        raw = updated.checkpoint()
        cold = NativeEpisodeExperience.restore(raw, digest(raw))
        self.assertEqual(cold.checkpoint(), raw)
        self.assertEqual(cold._ledger, updated._ledger)

    def test_context_checkpoint_v2_survives_opt_in_envelope(self):
        native = NativeEpisodeExperience()
        for n in range(8):
            native = native_episode(native, n + 1, n % 2)
        context = native.begin_context()
        self.assertEqual(json.loads(context.checkpoint())["schema"],
                         "yggdrasil.ckad.native-episode-experience.v2")
        staged = put(context, 1301, states=((0, 0),), outcomes=(0,))
        saved = staged.checkpoint()
        cold = NativeEpisodeExperience.restore(saved, digest(saved))
        self.assertEqual(cold.checkpoint(), saved)
        self.assertEqual(cold.context_forecast((0, 0), 0),
                         context.context_forecast((0, 0), 0))

    def test_identical_replay_idempotent_conflict_fails(self):
        native = NativeEpisodeExperience()
        raw, pin = fixture(1301, (0, 0), 0, 100)
        a = native.observe_external_fixture(
            {"public_view": [0, 0], "external_action_id": 1301}, raw, pin)
        self.assertIs(a.observe_external_fixture(
            {"public_view": [0, 0], "external_action_id": 1301}, raw, pin), a)
        raw2, pin2 = fixture(1301, (0, 0), 1, 100)
        with self.assertRaisesRegex(ValueError, "WSCM_SOURCE_REPLAY_CONFLICT"):
            a.observe_external_fixture(
                {"public_view": [0, 0], "external_action_id": 1301}, raw2, pin2)
        self.assertEqual(a._ledger, native._ledger)

    def test_forged_role_or_real_custody_still_refused(self):
        native = NativeEpisodeExperience()
        raw, _ = fixture(1301, (0, 0), 0, 100)
        for extra, value in (("role", "hidden"), ("phase", "A"),
                             ("source_mode", "authenticated")):
            doc = json.loads(raw)
            doc[extra] = value
            forged = _canonical(doc)
            with self.subTest(extra=extra):
                with self.assertRaises(ValueError):
                    native.observe_external_fixture(
                        {"public_view": [0, 0], "external_action_id": 1301},
                        forged, hashlib.sha256(forged).hexdigest())

    def test_rehashed_accepted_or_nested_checkpoint_refused(self):
        native = put(NativeEpisodeExperience(), 1301, states=((0, 0),),
                     outcomes=(0,))
        for key in ("native_accepted", "scientific_pass"):
            doc = json.loads(native.checkpoint())
            doc[key] = True
            raw = _canonical(doc)
            with self.assertRaises(ValueError):
                NativeEpisodeExperience.restore(raw, digest(raw))
        doc = json.loads(native.checkpoint())
        doc["native_checkpoint"] = dict(doc)
        doc["native_checkpoint"]["schema"] = EXTERNAL_FIXTURE_SCHEMA
        raw = _canonical(doc)
        with self.assertRaises(ValueError):
            NativeEpisodeExperience.restore(raw, digest(raw))

    def test_rehashed_outcome_tampering_still_refused(self):
        native = put(NativeEpisodeExperience(), 1301, states=((0, 0),),
                     outcomes=(0,))
        doc = json.loads(native.checkpoint())
        doc["fixture_checkpoint"]["records"][0][3] = 1
        forged = _canonical(doc)
        with self.assertRaises(ValueError):
            NativeEpisodeExperience.restore(forged, digest(forged))
        doc["fixture_sha256"] = digest(_canonical(doc["fixture_checkpoint"]))
        twice_rehashed = _canonical(doc)
        with self.assertRaises(ValueError):
            NativeEpisodeExperience.restore(twice_rehashed, digest(twice_rehashed))

    def test_rehashed_native_base_cannot_repair_prior_history(self):
        native = put(native_episode(NativeEpisodeExperience()), 1301,
                     states=((0, 0),), outcomes=(0,))
        doc = json.loads(native.checkpoint())
        doc["native_checkpoint"]["episodes"][0][3] = 1
        doc["native_sha256"] = digest(_canonical(doc["native_checkpoint"]))
        corrupted = _canonical(doc)
        with self.assertRaises(ValueError):
            NativeEpisodeExperience.restore(corrupted, digest(corrupted))

    def test_no_mutation_on_wrong_request(self):
        base = native_episode(NativeEpisodeExperience())
        original = base.checkpoint()
        raw, pin = fixture(1301, (0, 0), 0, 100)
        with self.assertRaisesRegex(ValueError, "WSCM_PUBLIC_RECEIPT_MISMATCH"):
            base.observe_external_fixture(
                {"public_view": [0, 1], "external_action_id": 1301}, raw, pin)
        self.assertEqual(base.checkpoint(), original)

    def test_fixture_cannot_promote_causal_bank(self):
        base = native_episode(NativeEpisodeExperience())
        baseline = base.info()["state_sha256"]
        alt = put(base, 1301)
        self.assertEqual(alt.info()["state_sha256"], baseline)
        self.assertEqual(alt._transition.snapshot(), base._transition.snapshot())
        self.assertEqual(alt._terminal.snapshot(), base._terminal.snapshot())
        self.assertEqual(alt.info()["external_action_source_mode"],
                         "engineering_fixture_only")

    def test_existing_checkpoint_unmodified_and_no_external_ghost(self):
        base = NativeEpisodeExperience()
        raw = base.checkpoint()
        cold = NativeEpisodeExperience.restore(raw, digest(raw))
        self.assertEqual(cold.checkpoint(), raw)
        self.assertIsNone(cold._external_action_fixture)
        self.assertNotIn("external_action_fixture_count", cold.info())


if __name__ == "__main__":
    unittest.main()

"""Gate28 source-free public CVH10 DTR → native-shape candidate grammar.

Original third-party environments are never imported, instantiated or stepped.
The preserved Gate25 failing negative tests remain untouched.
"""
from collections import namedtuple
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import EXPERIENCE_SOURCE
from yggdrasil.native_episode_experience import _views

HERE = Path(__file__).resolve().parents[1] / (
    "research/contrib/chatgpt/CAUSAL-AMALGAM")
SPEC = spec_from_file_location("gate28_public_dtr_candidate",
                               HERE / "dtr_candidate_episode.py")
CANDIDATE = module_from_spec(SPEC)
sys.modules[SPEC.name] = CANDIDATE
SPEC.loader.exec_module(CANDIDATE)

STAGED_SPEC = spec_from_file_location(
    "gate28_original_staged_readout", HERE / "staged_public_readout.py")
STAGED = module_from_spec(STAGED_SPEC)
STAGED_SPEC.loader.exec_module(STAGED)

PublicConsequence = namedtuple("PublicConsequence", CANDIDATE.FIELDS)
EXTRA_FIELDS = namedtuple("IllegalConsequence", (*CANDIDATE.FIELDS, "hidden_info"))
IDENTIFIER = sha256(b"Gate28-sourcefree-only-not-real-source").hexdigest()


def episode(s1=0, x1=0, s2=0, x2=0, y=0, *, named=True):
    a = (s1, x1, 0, s2, False, False)
    b = (s2, x2, y, 0, True, False)
    if named:
        return (PublicConsequence(*a), PublicConsequence(*b))
    return a, b


class DTRCandidateEpisodeTests(unittest.TestCase):
    def test_32_binary_fully_public_rows_exact_native_shape(self):
        for case in range(32):
            bits = tuple((case >> k) & 1 for k in range(5))
            with self.subTest(bits=bits):
                c = CANDIDATE.candidate_from_public_episode(
                    episode(*bits, named=False), identifier=IDENTIFIER)
                self.assertEqual(c.row_bits, bits)
                self.assertEqual(c.as_row(), dict(zip(
                    CANDIDATE.ROW_FIELDS, bits, strict=True)))
                self.assertEqual(c.views, ((bits[0], 0), (bits[0], 0)))
                self.assertEqual(_views(c.views), c.views)
                self.assertFalse(c.independent_second_view_observed)
                self.assertFalse(c.terminal_after_is_source_observation)
                self.assertFalse(c.native_ingestion_authorized)

    def test_32_cvh10_field_order_namedtuple_compatibility(self):
        for case in range(32):
            bits = tuple((case >> k) & 1 for k in range(5))
            with self.subTest(case=case):
                named = CANDIDATE.candidate_from_public_episode(
                    episode(*bits), identifier=IDENTIFIER)
                plain = CANDIDATE.candidate_from_public_episode(
                    episode(*bits, named=False), identifier=IDENTIFIER)
                self.assertEqual(named, plain)

    def test_cvh10_public_digest_matches_exact_six_field_serialization(self):
        rows = episode(1, 0, 1, 1, 0)
        candidate = CANDIDATE.candidate_from_public_episode(
            rows, identifier=IDENTIFIER)
        self.assertEqual(candidate.public_transcript_sha256,
                         digest(canonical([list(r) for r in rows])))
        self.assertEqual(candidate.candidate_packet_sha256,
                         digest(canonical([
                             IDENTIFIER, candidate.views, candidate.as_row()])))
        # Reinterpreting a packet hash as source origin is forbidden.
        self.assertNotEqual(candidate.public_transcript_sha256,
                            candidate.candidate_packet_sha256)
        self.assertNotEqual(candidate.source_commit_git_sha1,
                            EXPERIENCE_SOURCE)

    def test_identical_transcript_different_ids_have_distinct_packet(self):
        rows = episode(1, 1, 0, 1, 1)
        first = CANDIDATE.candidate_from_public_episode(
            rows, identifier=IDENTIFIER)
        other_id = sha256(b"Gate28-sourcefree-second-id").hexdigest()
        second = CANDIDATE.candidate_from_public_episode(
            rows, identifier=other_id)
        self.assertEqual(first.public_transcript_sha256,
                         second.public_transcript_sha256)
        self.assertNotEqual(first.candidate_packet_sha256,
                            second.candidate_packet_sha256)
        self.assertEqual(first, CANDIDATE.candidate_from_public_episode(
            rows, identifier=IDENTIFIER))

    def test_only_exact_two_public_six_field_records_accepted(self):
        for invalid in (
            (), (episode()[0],), (*episode(), episode()[0]),
            {"rows": episode()},
            ((0, 0, 0, 0, False), episode()[1]),
            ((0, 0, 0, 0, False, False, {"hidden": 1}), episode()[1]),
            ((0, 0, 0, 0, False, False, None), episode()[1]),
            ({"before": 0, "action": 0, "info": {"u": 1}}, episode()[1]),
        ):
            with self.subTest(variant=str(type(invalid))):
                with self.assertRaisesRegex(
                        ValueError, "DTR_CANDIDATE_"):
                    CANDIDATE.candidate_from_public_episode(
                        invalid, identifier=IDENTIFIER)
        extra = EXTRA_FIELDS(*(tuple(episode()[0]) + ({"u": 1},)))
        with self.assertRaisesRegex(ValueError,
                                     "DTR_CANDIDATE_SIX_PUBLIC_FIELDS_REQUIRED"):
            CANDIDATE.candidate_from_public_episode(
                (extra, episode()[1]), identifier=IDENTIFIER)

    def test_source_rows_must_be_public_binary_not_float_or_bool(self):
        for index in range(4):
            for invalid in (-1, 2, 0.0, 1.0, True, False, "1", None):
                rows = [list(v) for v in episode()]
                rows[0][index] = invalid
                with self.subTest(index=index, value=str(invalid)):
                    with self.assertRaisesRegex(
                            ValueError, "DTR_CANDIDATE_PUBLIC_BIT"):
                        CANDIDATE.candidate_from_public_episode(
                            tuple(tuple(r) for r in rows),
                            identifier=IDENTIFIER)

    def test_first_stage_is_nonterminal_and_rewardless(self):
        for index, invalid in ((2, 1), (4, True), (5, True)):
            rows = [list(v) for v in episode()]
            rows[0][index] = invalid
            with self.subTest(index=index):
                with self.assertRaisesRegex(
                        ValueError, "DTR_CANDIDATE_STAGE0_"):
                    CANDIDATE.candidate_from_public_episode(
                        tuple(tuple(r) for r in rows), identifier=IDENTIFIER)

    def test_second_stage_requires_history_match_terminal_and_sentinel(self):
        for index, invalid, reason in (
            (0, 1, "HISTORY_MISMATCH"),
            (3, 1, "TERMINAL_ABSENCE_SENTINEL"),
            (4, False, "STAGE1_TERMINAL_REQUIRED"),
            (5, True, "STAGE1_TERMINAL_REQUIRED"),
        ):
            rows = [list(v) for v in episode()]
            rows[1][index] = invalid
            with self.subTest(index=index):
                with self.assertRaisesRegex(ValueError, "DTR_CANDIDATE_" + reason):
                    CANDIDATE.candidate_from_public_episode(
                        tuple(tuple(r) for r in rows), identifier=IDENTIFIER)
        rows = [list(r) for r in episode()]
        rows[1][3] = None
        with self.assertRaisesRegex(ValueError, "DTR_CANDIDATE_PUBLIC_BIT"):
            CANDIDATE.candidate_from_public_episode(
                tuple(tuple(r) for r in rows), identifier=IDENTIFIER)

    def test_flags_are_literal_booleans_and_identifier_opaque_sha256(self):
        for index in (4, 5):
            for value in (0, 1, None, "False"):
                rows = [list(r) for r in episode()]
                rows[1][index] = value
                with self.subTest(index=index, value=value):
                    with self.assertRaisesRegex(
                            ValueError, "DTR_CANDIDATE_BOOLEAN_TERMINATION"):
                        CANDIDATE.candidate_from_public_episode(
                            tuple(tuple(r) for r in rows),
                            identifier=IDENTIFIER)
        for value in ("gate28/0", "f" * 63, "g" * 64, None):
            with self.subTest(value=value):
                with self.assertRaisesRegex(
                        ValueError, "DTR_CANDIDATE_OPAQUE_IDENTIFIER"):
                    CANDIDATE.candidate_from_public_episode(
                        episode(), identifier=value)

    def test_candidate_is_immutable_and_row_copy_detached(self):
        rows = [list(r) for r in episode(1, 1, 1, 0, 1)]
        c = CANDIDATE.candidate_from_public_episode(
            tuple(tuple(r) for r in rows), identifier=IDENTIFIER)
        rows[0][0] = 0
        self.assertEqual(c.as_row()["s1"], 1)
        new_row = c.as_row()
        new_row["s1"] = 0
        self.assertEqual(c.as_row()["s1"], 1)
        self.assertFalse(hasattr(c, "__dict__"))
        with self.assertRaises(FrozenInstanceError):
            c.views = ((0, 0), (0, 0))

    def test_cannot_forge_owner_attestation_or_training_authority(self):
        c = CANDIDATE.candidate_from_public_episode(
            episode(1, 0, 1, 0, 1), identifier=IDENTIFIER)
        for key, value in (
            ("native_ingestion_authorized", True),
            ("original_source_birth_attested", True),
            ("source_firstuse_execution_allowed", True),
            ("independent_second_view_observed", True),
            ("terminal_after_is_source_observation", True),
            ("canonical_model_updates", 1),
            ("source_commit_git_sha1", "0" * 40),
        ):
            with self.subTest(key=key):
                with self.assertRaisesRegex(
                        ValueError, "DTR_CANDIDATE_ADMISSION_FORBIDDEN"):
                    replace(c, **{key: value})
        with self.assertRaisesRegex(ValueError,
                                     "DTR_CANDIDATE_PACKET_DRIFT"):
            replace(c, candidate_packet_sha256="0" * 64)
        p = c.public_receipt()
        self.assertFalse(p["native_ingestion_authorized"])
        self.assertFalse(p["original_source_birth_attested"])
        self.assertNotIn("source_sha256", p)
        self.assertNotIn("owner_signed_lease", p)
        self.assertEqual(c.canonical_model_updates, 0)

    def test_readout_with_fake_model_preserves_order_but_uses_dev_source_pin(self):
        # This deliberately exposes why the shape-only candidate CANNOT
        # authenticate original DTR first-use: the original staged readout
        # hardcodes development EXPERIENCE_SOURCE into mock admission.
        c = CANDIDATE.candidate_from_public_episode(
            episode(1, 1, 0, 1, 1), identifier=IDENTIFIER)
        class FakeNative:
            def __init__(self):
                self.calls = []
            def experience_context_forecast(self, view, *actions):
                self.calls.append((view, actions))
                return Fraction(1, 2)

        class FakeModel:
            def __init__(self):
                self.native = FakeNative()
                self.specialist_calls = []
                self.witnesses = []
            def specialist_forecasts(self, views, *actions):
                self.specialist_calls.append((views, actions))
                return (Fraction(1, 2), Fraction(1, 2))
            def observe_experience(self, identifier, views, row,
                                   *, source_sha256, packet_sha256):
                self.witnesses.append(
                    (identifier, views, row, source_sha256, packet_sha256))
                return "MOCK_ONLY_NOT_ACCEPTED"

        fake = FakeModel()
        staged = STAGED.StagedPublicReadout(fake, c.identifier, c.views)
        self.assertEqual(staged.first_action(c.row_bits[1]),
                         (Fraction(1, 2),) * 3)
        self.assertEqual(fake.native.calls, [(c.views[0], (1,))])
        staged.observe_transition(c.row_bits[2])
        self.assertEqual(staged.second_action(c.row_bits[3]),
                         (Fraction(1, 2),) * 3)
        self.assertEqual(
            fake.native.calls[-1], (c.views[0], (1, 0, 1)))
        self.assertEqual(staged.observe_reward(c.row_bits[4]),
                         "MOCK_ONLY_NOT_ACCEPTED")
        self.assertEqual(len(fake.witnesses), 1)
        ident, views, row, source, packet = fake.witnesses[0]
        self.assertEqual((ident, views, row),
                         (c.identifier, c.views, c.as_row()))
        self.assertEqual(packet, c.candidate_packet_sha256)
        self.assertEqual(source, EXPERIENCE_SOURCE)
        self.assertNotEqual(source, c.source_commit_git_sha1)
        self.assertFalse(c.native_ingestion_authorized)
        with self.assertRaisesRegex(ValueError, "STAGED_REWARD_ORDER"):
            staged.observe_reward(c.row_bits[4])

    def test_source_identity_is_git_not_original_source_owner_custody(self):
        c = CANDIDATE.candidate_from_public_episode(
            episode(), identifier=IDENTIFIER)
        self.assertEqual(c.schema, CANDIDATE.SCHEMA)
        self.assertEqual(c.source_repo, "CausalAILab/Causal-Gymnasium")
        self.assertEqual(c.source_commit_git_sha1,
                         "c94e9a4cd3641588b6b8507e71ccee5c27032bdf")
        self.assertEqual(c.source_dtr_git_blob_sha1,
                         "6af2371dce21804140ea141ccb7be14e003ba275")
        self.assertEqual(c.cvh10_bridge_git_blob_sha1,
                         "8431fdae76f4fb6579b6e9cb4df598aea9657688")
        self.assertEqual(len(c.source_commit_git_sha1), 40)
        self.assertEqual(len(EXPERIENCE_SOURCE), 64)
        self.assertFalse(c.source_firstuse_execution_allowed)
        self.assertFalse(c.original_source_birth_attested)


if __name__ == "__main__":
    unittest.main()

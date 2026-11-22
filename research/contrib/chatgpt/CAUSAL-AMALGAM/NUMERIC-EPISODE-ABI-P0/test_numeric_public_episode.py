"""Entirely synthetic, source-free interface qualification; no world actions."""
import hashlib
import json
import math
import unittest

from numeric_public_episode import NumericPublicEpisodeLog, PublicStep, MAX_EVENTS

SOURCE = "a" * 64


def packet(step, *, action=0, before=(-0.0, 1.25), after=(0.0, -3.5),
           reward=0.25, terminated=False, truncated=False):
    identifier = hashlib.sha256(("synthetic-p0-" + str(step)).encode()).hexdigest()
    return {"source_sha256": SOURCE, "identifier": identifier, "step": step,
            "before": before, "action": action, "after": after, "reward": reward,
            "terminated": terminated, "truncated": truncated}


class NumericPublicABI(unittest.TestCase):
    def test_all_five_actions_have_different_identity_no_binary_mapping(self):
        checksums = set()
        for action in range(5):
            a = NumericPublicEpisodeLog(SOURCE, 2).append(packet(0, action=action))
            checksums.add(hashlib.sha256(a.checkpoint()).hexdigest())
            self.assertEqual(a.steps[0].action, action)
            self.assertFalse(a.proof_of_scope()["native_admission"])
            with self.assertRaisesRegex(ValueError, "NOT_NATIVE_ABI"):
                a.require_native_abi()
        self.assertEqual(len(checksums), 5)

    def test_float_hex_is_exact_and_negative_zero_survives_cold_restore(self):
        a = NumericPublicEpisodeLog(SOURCE, 2).append(packet(0))
        data = a.checkpoint()
        self.assertIn(b"-0x0.0p+0", data)
        cold = NumericPublicEpisodeLog.restore(data, hashlib.sha256(data).hexdigest())
        self.assertEqual(cold.checkpoint(), data)
        self.assertEqual(math.copysign(1.0, cold.steps[0].before[0]), -1.0)
        self.assertEqual(math.copysign(1.0, cold.steps[0].after[0]), 1.0)
        self.assertEqual(cold.steps[0].reward.hex(), (0.25).hex())

    def test_preserves_precise_subnormal_no_reward_bins_or_stage(self):
        tiny = float.fromhex("0x0.0000000000001p-1022")
        a = NumericPublicEpisodeLog(SOURCE, 2).append(
            packet(0, before=(tiny, -0.0), after=(1.75, tiny), reward=-tiny))
        raw = a.checkpoint()
        b = NumericPublicEpisodeLog.restore(raw, hashlib.sha256(raw).hexdigest())
        self.assertEqual(b.steps[0].reward.hex(), (-tiny).hex())
        self.assertFalse(b.proof_of_scope()["ckad_two_stage_synthesized"])
        self.assertNotIn("x1", json.loads(raw)["steps"][0])
        self.assertNotIn("x2", json.loads(raw)["steps"][0])

    def test_immutable_append_and_no_gap_or_replay(self):
        origin = NumericPublicEpisodeLog(SOURCE, 2)
        first = origin.append(packet(0))
        second = first.append(packet(1, action=4))
        self.assertEqual((len(origin.steps), len(first.steps), len(second.steps)), (0, 1, 2))
        with self.assertRaisesRegex(ValueError, "CHRONOLOGICAL_STEP"):
            second.append(packet(3))
        altered = packet(2)
        altered["identifier"] = first.steps[0].identifier
        with self.assertRaisesRegex(ValueError, "REPLAYED_IDENTIFIER"):
            second.append(altered)

    def test_termination_and_truncation_stop_next_step(self):
        for flag in ("terminated", "truncated"):
            obj = NumericPublicEpisodeLog(SOURCE, 2).append(packet(0, **{flag: True}))
            with self.assertRaisesRegex(ValueError, "AFTER_TERMINAL"):
                obj.append(packet(1))
            self.assertEqual(len(obj.steps), 1)

    def test_reject_private_info_forged_authority_and_unexpected_source(self):
        for extra in ("info", "task_id", "weather", "owner_authorized", "scientific_pass"):
            p = packet(0)
            p[extra] = True
            with self.assertRaisesRegex(ValueError, "EXACT_PUBLIC_FIELDS"):
                NumericPublicEpisodeLog(SOURCE, 2).append(p)
        p = packet(0)
        p["source_sha256"] = "b" * 64
        with self.assertRaisesRegex(ValueError, "SOURCE_PIN_MISMATCH"):
            NumericPublicEpisodeLog(SOURCE, 2).append(p)

    def test_action_strict_types_and_scalar_reward(self):
        for action in (True, False, 1.0, -1, 5, "3", None):
            with self.assertRaisesRegex(ValueError, "FIVE_ACTION_IDENTITY"):
                NumericPublicEpisodeLog(SOURCE, 2).append(packet(0, action=action))
        for reward in (True, 1, "0.3", math.inf, -math.inf, math.nan):
            with self.assertRaisesRegex(ValueError, "SCALAR_REWARD"):
                NumericPublicEpisodeLog(SOURCE, 2).append(packet(0, reward=reward))

    def test_vector_shape_types_and_finiteness(self):
        for before in ((1.0,), [1.0, 2.0], (True, 1.0), (0, 1.0),
                       (0.0, float("nan")), (0.0, float("inf"))):
            with self.assertRaisesRegex(ValueError, "PUBLIC_VECTOR"):
                NumericPublicEpisodeLog(SOURCE, 2).append(packet(0, before=before))
        for shape in (0, -1, True, 129, 2.0):
            with self.assertRaisesRegex(ValueError, "SHAPE_BOUNDS"):
                NumericPublicEpisodeLog(SOURCE, shape)

    def test_packet_step_identifier_source_strict(self):
        for change, tag in [({"step": 1}, "CHRONOLOGICAL_STEP"),
                            ({"step": True}, "CHRONOLOGICAL_STEP"),
                            ({"identifier": "A" * 64}, "IDENTIFIER_PIN"),
                            ({"identifier": "1"}, "IDENTIFIER_PIN")]:
            p = packet(0)
            p.update(change)
            with self.assertRaisesRegex(ValueError, tag):
                NumericPublicEpisodeLog(SOURCE, 2).append(p)

    def test_integrity_digest_cold_and_public_schema(self):
        obj = NumericPublicEpisodeLog(SOURCE, 2).append(packet(0))
        raw = obj.checkpoint()
        pin = hashlib.sha256(raw).hexdigest()
        self.assertEqual(NumericPublicEpisodeLog.restore(raw, pin).checkpoint(), raw)
        with self.assertRaisesRegex(ValueError, "CHECKPOINT_DIGEST"):
            NumericPublicEpisodeLog.restore(raw + b" ", pin)
        fake = json.loads(raw)
        fake["owner_approved"] = True
        injected = json.dumps(fake).encode()
        with self.assertRaisesRegex(ValueError, "CHECKPOINT_SCHEMA"):
            NumericPublicEpisodeLog.restore(injected, hashlib.sha256(injected).hexdigest())
        self.assertTrue(all(obj.proof_of_scope()[k] is False for k in
                            ("source_owner_authenticated", "native_admission",
                             "original_world_first_use", "scientific_gain_verified",
                             "can_act", "can_train", "can_deploy")))

    def test_reject_noncanonical_json_even_with_recomputed_hash(self):
        obj = NumericPublicEpisodeLog(SOURCE, 2).append(packet(0))
        payload = obj.checkpoint().replace(b'"step":0', b'"step":0, "step":0')
        with self.assertRaisesRegex(ValueError, "CHECKPOINT_CANONICAL"):
            NumericPublicEpisodeLog.restore(payload, hashlib.sha256(payload).hexdigest())

    def test_capacity_2048_and_2049_fail_without_model_growth(self):
        # The research buffer stores 2,048 *already-supplied* public packets.
        # No upstream source is constructed, sampled or stepped.
        log = NumericPublicEpisodeLog(SOURCE, 2)
        for step in range(MAX_EVENTS):
            log = log.append(packet(step, action=step % 5))
        self.assertEqual(len(log.steps), 2048)
        with self.assertRaisesRegex(ValueError, "STEP_CAPACITY"):
            log.append(packet(2048))


if __name__ == "__main__":
    unittest.main(verbosity=2)

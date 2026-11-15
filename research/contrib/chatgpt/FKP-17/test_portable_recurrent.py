"""Portable recurrent exact weights and corruption-negative qualification.

One-epoch source-safe CPU smoke never satisfies FKP-17 science/first-use.
"""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import portable_recurrent as portable
import recurrent_control as recurrent
import source_fixture as source


class GRUPortableSmoke(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        train = source.collect_public(source.TRAIN[2],
                                      source.public_actions(source.TRAIN[2], 24))
        validation = source.collect_public(source.VALIDATION[2],
                                           source.public_actions(source.VALIDATION[2], 8))
        cls.model = recurrent.source_safe_dev_smoke(train, validation)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="fkp17-gru-")
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "weights.json"
        self.model.begin_world()
        self.receipt = portable.export_public_gru(self.model, self.path)

    def test_bit_exact_snapshot_cold_replay_and_public_choice(self):
        loaded = portable.restore_public_gru(self.path,
                                             self.model.foundation_sha256)
        self.assertEqual(loaded.state_receipt(), self.model.state_receipt())
        self.assertEqual(loaded.foundation_sha256, self.model.foundation_sha256)
        self.assertEqual(loaded.learned_bytes, self.model.learned_bytes)
        self.assertEqual(loaded.training_receipt, self.model.training_receipt)
        self.assertEqual(self.receipt["checkpoint_sha256"],
                         hashlib.sha256(self.path.read_bytes()).hexdigest())
        for observation in ((0,) * 8, tuple(range(8)), (15,) * 8):
            self.assertEqual(loaded.choose_public(observation),
                             self.model.choose_public(observation))
        row = source.collect_public(source.TRAIN[4], (1,))[0]
        loaded.observe_public(row)
        self.assertNotEqual(loaded.state_receipt(), self.model.state_receipt())
        loaded.begin_world()
        self.assertEqual(loaded.state_receipt(), self.model.state_receipt())

    def test_cannot_claim_truncated_smoke_as_full_training(self):
        loaded = portable.restore_public_gru(self.path,
                                             self.model.foundation_sha256)
        with self.assertRaisesRegex(ValueError, "NOT_FULLY_TRAINED"):
            recurrent.assert_science_ready(loaded,
                                           loaded.foundation_sha256)

    def test_wrong_prior_digest_does_not_restore(self):
        with self.assertRaisesRegex(ValueError, "SOURCE_OR_VERSION"):
            portable.restore_public_gru(self.path, "0" * 64)
        with self.assertRaises(ValueError):
            portable.restore_public_gru(self.path, "short")

    def test_patched_envelope_fails_digest(self):
        saved = json.loads(self.path.read_text("ascii"))
        saved["payload"]["training_receipt"]["selected_epoch"] = 23
        self.path.write_text(json.dumps(saved), encoding="ascii")
        with self.assertRaisesRegex(ValueError, "PAYLOAD_TAMPER"):
            portable.restore_public_gru(self.path, self.model.foundation_sha256)

    def test_layer_content_tamper_rejected_even_with_recomputed_manifest(self):
        saved = json.loads(self.path.read_text("ascii"))
        layer = saved["payload"]["tensors"][0]
        layer["data"] = "AA=="  # wrong bytes but syntactically valid base64
        saved["payload_sha256"] = hashlib.sha256(
            portable._canonical(saved["payload"])).hexdigest()
        self.path.write_text(json.dumps(saved), encoding="ascii")
        with self.assertRaisesRegex(ValueError, "PARAMETER_SIZE"):
            portable.restore_public_gru(self.path, self.model.foundation_sha256)

    def test_shape_tamper_and_unexpected_tensor_cannot_restore(self):
        saved = json.loads(self.path.read_text("ascii"))
        saved["payload"]["tensors"][0]["shape"] = [1]
        saved["payload_sha256"] = hashlib.sha256(
            portable._canonical(saved["payload"])).hexdigest()
        self.path.write_text(json.dumps(saved), encoding="ascii")
        with self.assertRaisesRegex(ValueError, "LAYER_IDENTITY"):
            portable.restore_public_gru(self.path, self.model.foundation_sha256)

    def test_duplicate_keys_and_oversized_file_rejected(self):
        self.path.write_text('{"payload":{}, "payload":{}}', encoding="ascii")
        with self.assertRaisesRegex(ValueError, "DUPLICATE_JSON_KEY"):
            portable.restore_public_gru(self.path, self.model.foundation_sha256)
        self.path.write_bytes(b"x" * (portable.MAX_FILE_BYTES + 1))
        with self.assertRaisesRegex(ValueError, "SIZE_LIMIT"):
            portable.restore_public_gru(self.path, self.model.foundation_sha256)

    def test_non_model_and_dirty_world_refused_export(self):
        with self.assertRaises(ValueError):
            portable.export_public_gru(object(), self.path)
        self.model.begin_world()
        row = source.collect_public(source.TRAIN[0], (0,))[0]
        self.model.observe_public(row)
        with self.assertRaisesRegex(ValueError, "NONCOLD_WORLD"):
            portable.export_public_gru(self.model, self.path)

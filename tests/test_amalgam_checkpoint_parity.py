"""The portability check must keep hashes exact and numerical tolerance bounded."""

from copy import deepcopy
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from yggdrasil.native_jepa2_multilearner import ActionLatentSpecialist
from yggdrasil.native_jepa_temporal import TemporalLatentSpecialist

RESEARCH = Path(__file__).resolve().parents[1] / "research/contrib/chatgpt/CAUSAL-AMALGAM"
SPEC = spec_from_file_location("amalgam_checkpoint_parity_for_tests", RESEARCH / "checkpoint_replay_parity.py")
AUDIT = module_from_spec(SPEC)
with patch.object(sys, "path", [str(RESEARCH), *sys.path]):
    SPEC.loader.exec_module(AUDIT)

COMMIT = "a" * 40


def platforms():
    document = {
        "trace_sha256":"1" * 64, "native_sha256":"2" * 64, "joint_sha256":"3" * 64,
        "witness_count": 1097,
        "heads": [ActionLatentSpecialist(kind).as_data() for kind in AUDIT.KINDS]
        + [TemporalLatentSpecialist(kind).data() for kind in AUDIT.KINDS],
        "probabilities": [0.5] * 160,
    }
    models = {f"example/{i}": deepcopy(document) for i in range(9)}
    models["anchor"] = deepcopy(document)
    linux = {"schema": AUDIT.SCHEMA, "candidate": COMMIT, "platform": "Linux",
             "models": models, "source_actions": 0}
    windows = deepcopy(linux)
    windows["platform"] = "Windows"
    return linux, windows


class ReplayParityTests(unittest.TestCase):
    def test_small_specialist_difference_is_counted_but_not_called_byte_exact(self):
        linux, windows = platforms()
        changed = windows["models"]["example/2"]
        changed["heads"][0]["encoder_bias"][0] += AUDIT.NUMERIC_SOURCE_TOLERANCE / 4
        changed["probabilities"][0] += AUDIT.NUMERIC_SOURCE_TOLERANCE / 4
        changed["joint_sha256"] = "4" * 64
        observed = AUDIT.compare(linux, windows, COMMIT)["verified"]["example/2"]
        self.assertFalse(observed["checkpoint_bytes_equal"])
        self.assertGreater(observed["max_parameter_delta"], 0)
        self.assertGreater(observed["max_probe_delta"], 0)

    def test_native_state_and_trace_must_match_exactly(self):
        for field in ("native_sha256", "trace_sha256"):
            with self.subTest(field=field):
                linux, windows = platforms()
                windows["models"]["example/3"][field] = "4" * 64
                with self.assertRaisesRegex(ValueError, "Exact checkpoint identity differs"):
                    AUDIT.compare(linux, windows, COMMIT)

    def test_specialist_weights_and_predictions_cannot_escape_tolerance(self):
        linux, windows = platforms()
        windows["models"]["example/4"]["heads"][0]["encoder_bias"][0] += 1e-6
        with self.assertRaisesRegex(ValueError, "JEPA3_SOURCE_BIAS_PARITY"):
            AUDIT.compare(linux, windows, COMMIT)
        linux, windows = platforms()
        windows["models"]["example/4"]["probabilities"][0] += 1e-6
        with self.assertRaisesRegex(ValueError, "readout difference"):
            AUDIT.compare(linux, windows, COMMIT)

    def test_stamp_mismatch_cannot_qualify_a_different_commit(self):
        linux, windows = platforms()
        with self.assertRaisesRegex(ValueError, "Mismatched source"):
            AUDIT.compare(linux, windows, "b" * 40)

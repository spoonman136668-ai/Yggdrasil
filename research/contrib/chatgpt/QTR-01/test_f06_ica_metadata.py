"""F06 read-only ICA metadata: no source contact, independent synthetic negatives."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest

spec = importlib.util.spec_from_file_location("qtr_f06", Path(__file__).with_name("f06_ica_metadata.py"))
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)


def data(**overrides):
    d = {"modelId": m.MODEL, "source": m.SOURCE, "index": m.INDEX,
         "explanations": [{"description": "unverified synthetic label"}],
         "activations": [{"text": "do not disclose synthetic example"}]}
    d.update(overrides)
    return json.dumps(d).encode("utf-8")


class F06Test(unittest.TestCase):
    def test_fixed_url(self):
        self.assertEqual(m.URL, "https://www.neuronpedia.org/api/feature/qwen3.6-27b/32-icalens-res/77")

    def test_identity_source_field(self):
        got = m.profile(data())
        self.assertTrue(got["identifiable_record"])
        self.assertEqual(got["result"], "SOURCE_RECORD_IDENTIFIABLE_ONLY")
        self.assertFalse(got["causal_concept_proven"])

    def test_identity_source_id(self):
        got = m.profile(data(source=None, sourceId=m.SOURCE))
        self.assertTrue(got["identifiable_record"])

    def test_identity_mismatch_fails(self):
        for mismatch in ({"modelId": "qwen3-32b"}, {"source": "other"}, {"index": "99"}):
            with self.subTest(mismatch=mismatch), self.assertRaisesRegex(m.BadSource, "IDENTITY_MISMATCH"):
                m.profile(data(**mismatch))

    def test_malformed_and_oversized_fail(self):
        for payload in (b"", b"{", b"[]", b'{"modelId": NaN}', b"x" * (m.BOUND + 1)):
            with self.subTest(prefix=payload[:15]), self.assertRaises(m.BadSource):
                m.profile(payload)

    def test_raw_text_not_recorded(self):
        output = json.dumps(m.profile(data()))
        self.assertNotIn("unverified synthetic label", output)
        self.assertNotIn("do not disclose synthetic example", output)

    def test_explanation_never_proves_causality(self):
        out = m.profile(data(explanations=[{"description": "a completely independent causal explanation", "scores": [{"value": 1.0}]}]))
        self.assertFalse(out["causal_intervention_performed"])
        self.assertFalse(out["native_recipient_alignment_proven"])

    def test_bad_shapes_rejected(self):
        for field in ("explanations", "activations"):
            with self.subTest(field=field), self.assertRaisesRegex(m.BadSource, "INVALID_METADATA_SHAPE"):
                m.profile(data(**{field: {"bad": True}}))


if __name__ == "__main__":
    unittest.main()

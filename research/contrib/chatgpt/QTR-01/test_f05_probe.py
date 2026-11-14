"""F05 offline negative controls; neither donor model nor public feature service runs."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest

p = Path(__file__).with_name("f05_probe.py")
spec = importlib.util.spec_from_file_location("qtr_f05", p)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)


class TestF05(unittest.TestCase):
    def example(self, **kw):
        return json.dumps(dict(modelId=m.MODEL, sourceId=m.SOURCE, index="37427", **kw)).encode()

    def test_fixed_scope(self):
        self.assertEqual(m.INDICES, ("37427", "51972"))
        self.assertEqual(m.URL_PREFIX, "https://www.neuronpedia.org/api/feature/")

    def test_source_identity_fail_closed(self):
        for bad in [{"modelId":"other"}, {"sourceId":"other"}, {"index":"0"}]:
            d = json.loads(self.example())
            d.update(bad)
            with self.assertRaisesRegex(m.InvalidInput,"SOURCE_IDENTITY"):
                m.summarize("37427", json.dumps(d).encode())

    def test_explanation_does_not_prove_knowledge(self):
        obj = m.summarize("37427", self.example(explanations=[
            {"description":"a plausible but unsupported scientific explanation","scores":[{"value":1.0}]}]))
        self.assertEqual(obj["availability"], "EXPLANATION_CANDIDATE_ONLY")
        self.assertFalse(obj["causal_intervention_validation"])
        self.assertFalse(obj["recipient_alignment_validation"])
        self.assertFalse(obj["independent_semantic_validation"])

    def test_empty_explanations_not_equated_to_no_feature(self):
        obj = m.summarize("37427", self.example(explanations=[]))
        self.assertEqual(obj["availability"], "INSUFFICIENT_EXPLANATION_EVIDENCE")

    def test_no_raw_text_exported(self):
        text = "private-raw-auto-interpretation-not-for-training"
        obj = m.summarize("37427", self.example(explanations=[{"description":text}],
                                               activations=[{"raw":text}]))
        self.assertNotIn(text, json.dumps(obj))
        self.assertEqual(obj["explanation_objects"], 1)

    def test_invalid_payload_and_response_size(self):
        for payload in (b"", b"x", b"[]", b"z" * (m.MAX_BYTES+1)):
            with self.assertRaises(m.InvalidInput):
                m.summarize("37427", payload)

    def test_bad_structure(self):
        for field in ("explanations","activations"):
            with self.assertRaises(m.InvalidInput):
                m.summarize("37427", self.example(**{field:{"unexpected":"shape"}})

    def test_nonpreregistered_feature_fails(self):
        with self.assertRaises(m.InvalidInput):
            m.summarize("3", self.example())


if __name__ == "__main__":
    unittest.main()

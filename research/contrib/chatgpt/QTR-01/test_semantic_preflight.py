"""Source-free negative controls for metadata-only QTR F04."""
import importlib.util
from pathlib import Path
import sys
import unittest

p = Path(__file__).with_name("semantic_preflight.py")
s = importlib.util.spec_from_file_location("qtr_f04", p)
m = importlib.util.module_from_spec(s)
sys.modules[s.name] = m
s.loader.exec_module(m)


class F04Tests(unittest.TestCase):
    def test_pinned(self):
        self.assertIn(m.REV, m.URL)
        self.assertNotIn("/main/", m.URL)

    def test_numeric_ids_are_not_knowledge_labels(self):
        got = m.screen(b'{"selected":[{"layer":21,"feat":11,"kind":"top","score":1}]}')
        self.assertEqual(got["natural_language_descriptor_records"], 0)
        self.assertEqual(got["outcome"], "NO_GO_UNLABELLED_INTERFACE_FOR_SEMANTIC_TRANSPLANT")

    def test_long_label_does_not_equal_causal_proof(self):
        got = m.screen(b'{"items":[{"feat":5,"explanation":"captures some patterns in source code",'
                       b'"positive_examples":["x"],"negative_examples":["y"]}]}')
        self.assertEqual(got["descriptors_with_id_and_probe_fields"], 1)
        self.assertFalse(got["source_feature_semantics_proven"])
        self.assertFalse(got["recipient_alignment_proven"])

    def test_short_category_labels_not_mistaken_for_concepts(self):
        got = m.screen(b'{"selected":[{"feat":1,"label":"code"}]}')
        self.assertEqual(got["natural_language_descriptor_records"], 0)

    def test_malformed_rejected(self):
        for bad in (b"", b"{", b"null", b"x" * (m.MAX + 1)):
            with self.subTest(bad=bad[:20]), self.assertRaises(m.InvalidInput):
                m.screen(bad)

    def test_excess_nesting_rejected(self):
        with self.assertRaisesRegex(m.InvalidInput, "COMPLEXITY_LIMIT"):
            m.screen(("[" * 35 + "0" + "]" * 35).encode())


if __name__ == "__main__":
    unittest.main()

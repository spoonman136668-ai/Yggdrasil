"""F07 source-free negative controls; no donor execution or HTTP in tests."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest

path = Path(__file__).with_name("f07_matrix_inventory.py")
spec = importlib.util.spec_from_file_location("qtr_f07", path)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)


def fixture(**kwargs):
    data = {"id": m.REPO_ID, "sha": "0" * 40, "cardData": {"license": "apache-2.0"},
            "siblings": [
                {"rfilename": "blocks.L.32.hook_resid_post/model.safetensors"},
                {"rfilename": "README.md"},
            ]}
    data.update(kwargs)
    return json.dumps(data).encode("utf-8")


class SourceInventoryTests(unittest.TestCase):
    def test_fixed_source(self):
        self.assertEqual(m.URL, "https://huggingface.co/api/models/neuronpedia/icalens-qwen3.6-27b")

    def test_matrix_file_not_equated_to_verified_vector(self):
        r = m.classify_metadata(fixture())
        self.assertEqual(r["explicit_layer32_matrix_candidates"], 1)
        self.assertFalse(r["actual_matrix_sha256_verified"])
        self.assertFalse(r["transplantation_eligible"])

    def test_wrong_repo_fails(self):
        with self.assertRaisesRegex(m.InvalidMetadata, "IDENTITY"):
            m.classify_metadata(fixture(id="unrelated/repo"))

    def test_missing_or_bad_revision_fails(self):
        for sha in ("main", "", "unknown", "z" * 40):
            with self.subTest(sha=sha), self.assertRaisesRegex(m.InvalidMetadata, "REVISION"):
                m.classify_metadata(fixture(sha=sha))

    def test_wrong_layer_not_false_positive(self):
        x = fixture(siblings=[{"rfilename": "blocks.L.31.hook_resid_post/model.safetensors"}])
        r = m.classify_metadata(x)
        self.assertEqual(r["explicit_layer32_matrix_candidates"], 0)
        self.assertEqual(r["numeric_artifact_file_count"], 1)

    def test_missing_license_is_explicitly_unverified(self):
        r = m.classify_metadata(fixture(cardData={}))
        self.assertEqual(r["declared_license"], "UNVERIFIED")
        self.assertFalse(r["transplantation_eligible"])

    def test_bounded_and_json_guards(self):
        for payload in (b"", b"{", b"[]", b"x" * (m.LIMIT + 1)):
            with self.subTest(sample=payload[:12]), self.assertRaises(m.InvalidMetadata):
                m.classify_metadata(payload)

    def test_path_guards(self):
        for name in ("/secret", "../../escape", "a" * 550):
            with self.subTest(name=name[:20]), self.assertRaisesRegex(m.InvalidMetadata, "UNSAFE"):
                m.classify_metadata(fixture(siblings=[{"rfilename": name}]))


if __name__ == "__main__":
    unittest.main()

"""NKR-05 source-free full-image compiler and typed mmap query negatives."""
from __future__ import annotations

from hashlib import sha256
from io import BytesIO
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from yggdrasil.native_factual_weights import NativeFactualWeights, canonical, digest

RUNNER = Path(__file__).with_name("build_full_image.py")
spec = importlib.util.spec_from_file_location("nkr05_builder_fixture", RUNNER)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

FACTS = (
    (5, 2, 7), (1, 2, 4), (1, 2, 3), (3, 7, 9),
    (4, 7, 10), (1, 2, 3), (99, 99, 1), (3, 7, 9),
    (99, 3, 7), (2, 8, 6), (1, 4, 8), (9, 7, 10),
    (1, 2, 11), (1, 3, 12), (12, 2, 14), (1, 3, 15),
    (7, 8, 11), (6, 2, 2), (13, 5, 19), (15, 1, 8),
    (11, 5, 20), (12, 5, 99), (12, 5, 100), (5, 2, 20),
)


def raw_fixture():
    return b"".join(f"Q{s}\tP{p}\tQ{o}\n".encode("ascii")
                    for s, p, o in FACTS)


def build_fixture(root, *, chunk_rows=5):
    raw = raw_fixture()
    return builder.compile_train_stream(
        BytesIO(raw), root,
        expected_rows=len(FACTS), expected_bytes=len(raw),
        expected_sha=sha256(raw).hexdigest(),
        expected_relations=len({row[1] for row in FACTS}),
        chunk_rows=chunk_rows, max_seconds=60)


class NativeFullImageTests(unittest.TestCase):
    def test_full_source_stream_sorted_cold_and_exact_binary_membership(self):
        with tempfile.TemporaryDirectory() as temp:
            receipt = build_fixture(Path(temp), chunk_rows=5)
            self.assertEqual(receipt["records"], len(FACTS))
            self.assertEqual(receipt["numeric_slots"], 3 * len(FACTS))
            self.assertEqual(receipt["numeric_bytes"], 12 * len(FACTS))
            self.assertEqual(receipt["duplicates_retained"], 2)
            self.assertTrue(receipt["full_source_cold_restore"])
            self.assertFalse(receipt["official_valid_test_opened"])
            self.assertFalse(receipt["native_accepted"])
            with NativeFactualWeights(Path(temp)/"facts.uint32le",
                                      Path(temp)/"manifest.json",
                                      receipt["manifest_sha256"]) as memory:
                self.assertEqual(len(memory), len(FACTS))
                self.assertEqual([memory.row_at(i) for i in range(len(memory))],
                                 sorted(FACTS))
                for triple in FACTS:
                    self.assertTrue(memory.has_fact(*triple))
                self.assertFalse(memory.has_fact(1, 2, 999))
                self.assertFalse(memory.has_fact(1, 7, 9))

    def test_multi_relation_source_provenance_path_hypotheses(self):
        with tempfile.TemporaryDirectory() as temp:
            receipt = build_fixture(Path(temp))
            with NativeFactualWeights(Path(temp)/"facts.uint32le",
                                      Path(temp)/"manifest.json",
                                      receipt["manifest_sha256"]) as m:
                self.assertEqual(m.objects(1, 2),
                                 [3, 3, 4, 11])
                self.assertEqual(m.objects(1, 2, after=3), [4, 11])
                self.assertEqual(m.objects(1, 2, limit=2), [3, 3])
                proposal = m.two_hop_candidates(1, 2, 7)
                self.assertEqual(proposal["classification"],
                                 "UNVERIFIED_PATH_HYPOTHESES")
                self.assertEqual(proposal["objects"], [9, 10])
                self.assertEqual(proposal["evidence_source_sha256"],
                                 sha256(raw_fixture()).hexdigest())
                self.assertEqual(m.objects(1, 99), [])
                with self.assertRaises(ValueError):
                    m.objects(1, 2, limit=0)
                with self.assertRaises(ValueError):
                    m.two_hop_candidates(1, 2, 7, max_intermediates=0)
                with self.assertRaises(ValueError):
                    m.has_fact(True, 2, 3)
            with self.assertRaises(ValueError):
                m.has_fact(1, 2, 3)

    def test_manifest_and_file_tamper_strictly_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            receipt = build_fixture(Path(temp))
            p = Path(temp)/"facts.uint32le"
            meta = Path(temp)/"manifest.json"
            original = p.read_bytes()
            p.write_bytes(original[:-1] + bytes((original[-1] ^ 1,)))
            with self.assertRaisesRegex(ValueError, "NKR05_IMAGE_HASH_DRIFT"):
                NativeFactualWeights(p, meta, receipt["manifest_sha256"])
            p.write_bytes(original)
            with self.assertRaisesRegex(ValueError, "NKR05_MANIFEST_PIN_MISMATCH"):
                NativeFactualWeights(p, meta, "0"*64)
            j = json.loads(meta.read_bytes())
            j["accepted_native"] = True
            meta.write_bytes(canonical(j))
            with self.assertRaisesRegex(ValueError, "NKR05_UNSUPPORTED_ACCEPTANCE_CLAIM"):
                NativeFactualWeights(p, meta, digest(meta.read_bytes()))
            j["accepted_native"] = False
            j["scientific_pass"] = True
            meta.write_bytes(canonical(j))
            with self.assertRaisesRegex(ValueError, "NKR05_UNSUPPORTED_ACCEPTANCE_CLAIM"):
                NativeFactualWeights(p, meta, digest(meta.read_bytes()))

    def test_source_inventory_and_sha_fail_closed_before_final_image(self):
        raw = raw_fixture()
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)
            with self.assertRaisesRegex(ValueError, "NKR05_FROZEN_TRAIN_SHA"):
                builder.compile_train_stream(BytesIO(raw), p,
                    expected_rows=len(FACTS), expected_bytes=len(raw),
                    expected_sha="0"*64,
                    expected_relations=len({x[1] for x in FACTS}), chunk_rows=7)
            self.assertFalse((p/"facts.uint32le").exists())
            self.assertFalse((p/"manifest.json").exists())
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)
            with self.assertRaisesRegex(ValueError, "NKR05_FULL_TRAIN_INVENTORY_OVERFLOW"):
                builder.compile_train_stream(BytesIO(raw), p,
                    expected_rows=len(FACTS)-1, expected_bytes=len(raw),
                    expected_sha=sha256(raw).hexdigest(),
                    expected_relations=len({x[1] for x in FACTS}), chunk_rows=7)
            self.assertFalse((p/"facts.uint32le").exists())

    def test_reject_invalid_qp_line_and_duplicate_artifact_output(self):
        original = raw_fixture()
        replacement = original.replace(b"Q5\tP2\tQ7\n", b"Q5\tP2\tBAD\n")
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                builder.compile_train_stream(BytesIO(replacement), Path(temp),
                    expected_rows=len(FACTS), expected_bytes=len(replacement),
                    expected_sha=sha256(replacement).hexdigest(),
                    expected_relations=len({x[1] for x in FACTS}), chunk_rows=5)
        with tempfile.TemporaryDirectory() as temp:
            build_fixture(Path(temp))
            with self.assertRaisesRegex(ValueError, "NKR05_REFUSE_OVERWRITE"):
                build_fixture(Path(temp))

    def test_reject_bad_manifest_row_counts_noncanonical_json_and_nonimage(self):
        with tempfile.TemporaryDirectory() as temp:
            receipt = build_fixture(Path(temp))
            p = Path(temp)/"facts.uint32le"
            m = Path(temp)/"manifest.json"
            j = json.loads(m.read_bytes())
            j["records"] += 1
            m.write_bytes(canonical(j))
            with self.assertRaisesRegex(ValueError, "NKR05_MANIFEST_COUNTS_INVALID"):
                NativeFactualWeights(p, m, digest(m.read_bytes()))
            j["records"] -= 1
            j["data_kind"] = "invented causal counterfactual"
            m.write_bytes(canonical(j))
            with self.assertRaisesRegex(ValueError, "NKR05_SOURCE_KIND_INVALID"):
                NativeFactualWeights(p, m, digest(m.read_bytes()))
            j["data_kind"] = "historical-train-only-QPQ"
            m.write_text(json.dumps(j, indent=2), encoding="ascii")
            with self.assertRaisesRegex(ValueError, "NKR05_MANIFEST_NONCANONICAL"):
                NativeFactualWeights(p, m, digest(m.read_bytes()))


if __name__ == "__main__":
    unittest.main()

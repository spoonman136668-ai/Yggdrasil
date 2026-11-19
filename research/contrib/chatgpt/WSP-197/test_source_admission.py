"""WSP-197 source-free engineering fixtures; not an original biological experiment."""
from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

import source_admission as s

SEQUENCE = "MQYKLILNGKTLKGETTTEAVDAATAEKVFKQYANDNGVDGEWTYDDATKTFTVTE"


class AdmissionTests(unittest.TestCase):
    def fixture(self, root: Path):
        contents = {
            "GB1_sequence.fasta": ">GB1\n" + SEQUENCE,
            "Olson2014_TableS2_wildtype.txt": "Input Count\tSelection Count\n1\t2\n",
            "Olson2014_TableS2_singles.txt":
                "WT amino acid\tPosition\tMutation\tInput Count\tSelection Count\n"
                "Q\t2\tA\t1\t2\nY\t3\tC\t2\t3\n",
            "Olson2014_TableS2_doubles.txt":
                "W1\tPos1\tM1\tW2\tPos2\tM2\tI\tS\tfitness1\tfitness2\n"
                "Q\t2\tA\tY\t3\tC\t1\t2\t9.99\t-8.88\n",
        }
        spec = {}
        for name, content in contents.items():
            data = content.encode("utf-8")
            (root / name).write_bytes(data)
            sha = hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()
            spec[name] = (len(data), sha)
        return spec

    def test_byte_and_genotype_counts_no_fitness_exposed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec = self.fixture(root)
            result = s.metadata(root, spec)
            self.assertEqual(result["byte_and_genotype_metadata_gate"], "PASS")
            self.assertEqual(result["single_genotypes"], 2)
            self.assertEqual(result["double_genotypes"], 1)
            self.assertEqual(result["unique_mutation_positions"], 2)
            self.assertFalse(result["count_or_fitness_values_parsed"])
            self.assertFalse(result["science_experiment_executed"])
            self.assertNotIn("9.99", str(result))
            self.assertNotIn("-8.88", str(result))

    def test_corrupted_original_bytes_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec = self.fixture(root)
            p = root / "Olson2014_TableS2_doubles.txt"
            p.write_bytes(p.read_bytes() + b"extra")
            with self.assertRaisesRegex(s.SourceRejected, "SOURCE_SIZE_MISMATCH"):
                s.metadata(root, spec)

    def test_reference_allele_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec = self.fixture(root)
            name = "Olson2014_TableS2_doubles.txt"
            p = root / name
            p.write_text(p.read_text().replace("Q\t2\tA", "M\t2\tA"))
            data = p.read_bytes()
            spec[name] = (len(data), hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest())
            with self.assertRaisesRegex(s.SourceRejected, "REFERENCE_ALLELE_MISMATCH"):
                s.metadata(root, spec)

    def test_duplicate_genotype_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec = self.fixture(root)
            name = "Olson2014_TableS2_doubles.txt"
            p = root / name
            p.write_text(p.read_text() + "Y\t3\tC\tQ\t2\tA\t4\t5\t1\t1\n")
            data = p.read_bytes()
            spec[name] = (len(data), hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest())
            with self.assertRaisesRegex(s.SourceRejected, "DUPLICATE_DOUBLE_GENOTYPE"):
                s.metadata(root, spec)

    def test_same_site_double_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec = self.fixture(root)
            name = "Olson2014_TableS2_doubles.txt"
            p = root / name
            p.write_text(p.read_text().replace("Y\t3\tC", "Q\t2\tC"))
            data = p.read_bytes()
            spec[name] = (len(data), hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest())
            with self.assertRaisesRegex(s.SourceRejected, "SAME_SITE_DOUBLE"):
                s.metadata(root, spec)

    def test_missing_original_file_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec = self.fixture(root)
            (root / "GB1_sequence.fasta").unlink()
            with self.assertRaisesRegex(s.SourceRejected, "MISSING_OR_SYMLINK"):
                s.metadata(root, spec)


if __name__ == "__main__":
    unittest.main()

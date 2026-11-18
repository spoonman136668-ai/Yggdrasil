"""Developer-only WSP185 metadata parser tests; never original measurements."""
from __future__ import annotations

import ast
import io
import zipfile
from pathlib import Path
import unittest

from roster_probe import roster_entry, REQUIRED


def fixture(header="flag,load_in,rpm_in,pressure_intake", lines=None):
    if lines is None:
        lines = ["0,0.1,100,4", "0,0.2,120,5", "",
                 "0,0.3,140", "0,0.4,200,6"]
    content = "\n".join([header, *lines])+"\n"
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as writer:
        writer.writestr("actuators_random_walk_1.csv", content.encode())
    buffer.seek(0)
    return buffer


class RosterProbeTests(unittest.TestCase):
    def test_counts_blank_malformed_and_sha_without_reporting_targets(self):
        with zipfile.ZipFile(fixture()) as archive:
            info = archive.getinfo("actuators_random_walk_1.csv")
            d = roster_entry(archive, info)
        self.assertEqual(d["physical_record_count"], 4)
        self.assertEqual(d["empty_csv_records"], 1)
        self.assertEqual(d["wrong_width_records"], 1)
        self.assertEqual(d["field_count"], 4)
        self.assertFalse(d["preregistered_count_10000_matches"])
        self.assertIn("load_in", d["required_fields_present"])
        self.assertIn("hatch", d["required_fields_missing"])
        self.assertNotIn("100", str(d))
        self.assertEqual(len(d["file_sha256"]), 64)

    def test_reject_invalid_duplicate_header(self):
        with zipfile.ZipFile(fixture(header="flag,load_in,load_in")) as archive:
            with self.assertRaisesRegex(ValueError, "INVALID_COLUMNS"):
                roster_entry(archive, archive.infolist()[0])

    def test_original_numeric_sensor_values_not_examined_or_output(self):
        src = Path(__file__).with_name("roster_probe.py").read_text("utf-8")
        nodes = ast.parse(src)
        imports = {item.name.split(".")[0] for n in ast.walk(nodes)
                   if isinstance(n, ast.Import) for item in n.names}
        imports |= {n.module.split(".")[0] for n in ast.walk(nodes)
                    if isinstance(n, ast.ImportFrom) and n.module}
        self.assertFalse(imports & {"requests", "pandas", "numpy",
                                    "torch", "gym", "openai", "boto3"})
        for forbidden in ("float(row", "int(row", "env.step(",
                          "model.fit(", "source_first_use_authority"):
            self.assertNotIn(forbidden, src)


if __name__ == "__main__":
    unittest.main()

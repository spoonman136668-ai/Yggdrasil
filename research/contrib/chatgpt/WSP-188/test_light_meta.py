"""WSP188 original-source metadata-only engineering checks."""
from __future__ import annotations
import ast
import io
from pathlib import Path
import tempfile
import unittest
import zipfile
from light_meta import roster_entry,ROSTER,REQUIRED,diagnose


class LightMetadataTests(unittest.TestCase):
    def test_reused_byte_count_helper_only(self):
        data=io.BytesIO()
        with zipfile.ZipFile(data,"w",zipfile.ZIP_DEFLATED) as z:
            z.writestr("actuators_white.csv",
                "red,green,blue,pol_1,pol_2,l_31,l_32,vis_1,vis_2,vis_3\n"+
                "1,2,3,4,5,6,7,8,9,10\n"+
                "11,12,13,14,15,16,17,18,19,20\n")
        data.seek(0)
        with zipfile.ZipFile(data) as z:
            m=roster_entry(z,z.infolist()[0])
        self.assertEqual(m["physical_record_count"],2)
        self.assertEqual(m["wrong_width_records"],0)
        self.assertEqual(m["empty_csv_records"],0)
        self.assertEqual(len(set(REQUIRED)-set(m["header_fields"])),0)
        self.assertEqual(len(m["file_sha256"]),64)

    def test_wrong_upstream_archive_refused(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"author.zip"
            p.write_bytes(b"not an archived public physical source")
            with self.assertRaisesRegex(ValueError,"PUBLISHED_SOURCE_HASH"):
                diagnose(p)

    def test_no_sensor_numbers_used_for_models(self):
        source=Path(__file__).with_name("light_meta.py").read_text("utf-8")
        imports={x.name.split(".")[0] for n in ast.walk(ast.parse(source))
                 if isinstance(n,ast.Import) for x in n.names}
        self.assertFalse(imports&{"torch","numpy","pandas","gym","requests","openai"})
        for forbidden in ("float(row","int(row","model.fit(","env.step(","urlopen("):
            self.assertNotIn(forbidden,source)
        self.assertEqual(len(ROSTER),3)


if __name__=="__main__":
    unittest.main()

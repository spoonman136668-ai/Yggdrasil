"""WSP102 source-only archive preflight negatives; never fetch remote in tests."""
from io import BytesIO
import sys
import tarfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from source_custody import SOURCE_URL, _check_url, inspect_bytes


def _tar(members):
    out=BytesIO()
    with tarfile.open(fileobj=out, mode="w:gz") as archive:
        for path, kind, data in members:
            t=tarfile.TarInfo(path)
            if kind=="file":
                t.size=len(data)
                archive.addfile(t,BytesIO(data))
            elif kind=="symlink":
                t.type=tarfile.SYMTYPE
                t.linkname="elsewhere"
                archive.addfile(t)
            elif kind=="dir":
                t.type=tarfile.DIRTYPE
                archive.addfile(t)
            else:
                raise AssertionError("invalid fixture")
    return out.getvalue()


class SourceCustodyTests(unittest.TestCase):
    def test_exact_allowlist_and_https_required(self):
        self.assertEqual(_check_url(SOURCE_URL), SOURCE_URL)
        for u in ("http://web.informatik.uni-mannheim.de/pi1/kge-datasets/wikidata5m.tar.gz",
                  "https://example.com/pi1/kge-datasets/wikidata5m.tar.gz",
                  "https://web.informatik.uni-mannheim.de/other/anything",
                  SOURCE_URL+"?token=1",
                  SOURCE_URL+"#fragment",
                  "file:///etc/passwd"):
            with self.assertRaises(ValueError):
                _check_url(u)

    def test_archive_members_metadata_only(self):
        blob=_tar([("wikidata5m_transductive_train.txt","file",
                    b"Q1\tP31\tQ5\n"),("val.txt","file",b"Q2\tP17\tQ3\n")])
        got=inspect_bytes(blob)
        self.assertEqual([x["path"] for x in got["members"]],
                         ["wikidata5m_transductive_train.txt","val.txt"])
        self.assertEqual(got["total_uncompressed_bytes"],22)
        self.assertTrue(all("content" not in d for d in got["members"]))

    def test_path_traversal_rejected(self):
        for path in ("../secret", "/tmp/secret", "a//bad", "a/../b", "a\\bad"):
            with self.subTest(path=path):
                with self.assertRaises(ValueError):
                    inspect_bytes(_tar([(path,"file",b"X")]))

    def test_duplicate_path_rejected(self):
        with self.assertRaises(ValueError):
            inspect_bytes(_tar([("same","file",b"a"),("same","file",b"b")]))

    def test_special_files_forbidden(self):
        with self.assertRaises(ValueError):
            inspect_bytes(_tar([("link","symlink",b"")]))

    def test_not_archive_or_empty_rejected(self):
        for blob in (b"not-a-gzip",_tar([])):
            with self.assertRaises((ValueError,tarfile.TarError,EOFError)):
                inspect_bytes(blob)


if __name__=="__main__":
    unittest.main()

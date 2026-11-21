"""G38 lossless codec integrity tests; no world action or native model change."""
from hashlib import sha256
from pathlib import Path
from importlib.util import module_from_spec, spec_from_file_location
import os
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile

HERE = Path(__file__).resolve().parents[1] / "research/contrib/chatgpt/CAUSAL-AMALGAM"
SPEC = spec_from_file_location("amalgam_g38_codec", HERE / "segmented_episode_checkpoint.py")
SEG = module_from_spec(SPEC)
SPEC.loader.exec_module(SEG)

ARCHIVE_PATHS = (
    Path(os.environ.get("YGG_G38_ORIGINAL_LINUX", "/nonexistent/g38-original-linux.zip")),
    Path(os.environ.get("YGG_G38_ORIGINAL_WINDOWS", "/nonexistent/g38-original-windows.zip")),
)
EXPECTED_ZIPS = (
    'b8504c3a9f0e44185380687f7ce3f0a7ad0347c5be03c1cd51dc3aa1bbc1051d',
    'bb2b689f84caf939b76bea669eff7efb26506b602eed81ac79a81b42efb0a5a6',
)
EXPECTED_EPISODE_SHA = '9158254b80f147d7eb7516d630f6003441df4b8373375b994d864ee1d55568f4'


def fixture(count=3):
    rows = [(f'{i+1:064x}', [[0, 1], [1, 0]], 0, i % 2, 1, 1)
            for i in range(count)]
    return SEG.canonical({'schema':'yggdrasil.ckad.native-episode-experience.v6',
                          'episode_limit':1152,'repair':True,
                          'state_sha256':'a'*64,'episodes':rows})


class CodecTests(unittest.TestCase):
    def test_roundtrip_every_boundary(self):
        for n in (0, 1, 31, 32, 33, 1025, 1152):
            with self.subTest(n=n):
                raw = fixture(n)
                manifest,chunks = SEG.seal(raw)
                self.assertEqual(SEG.restore(manifest,chunks),raw)
                self.assertEqual(len(chunks),(n + 31)//32)
                self.assertEqual(SEG.seal(raw),(manifest,chunks))

    def test_fail_closed_missing_reordered_tampered(self):
        manifest,chunks=SEG.seal(fixture(65))
        with self.assertRaisesRegex(ValueError,'G38_SEGMENT_COUNT'):
            SEG.restore(manifest,chunks[:-1])
        with self.assertRaisesRegex(ValueError,'G38_CHUNK_COMPRESSED_PIN'):
            SEG.restore(manifest,(chunks[1],chunks[0],chunks[2]))
        corrupted=bytearray(chunks[0]); corrupted[4]^=1
        with self.assertRaisesRegex(ValueError,'G38_CHUNK_COMPRESSED_PIN'):
            SEG.restore(manifest,(bytes(corrupted),*chunks[1:]))
        doc=json.loads(manifest)
        doc['segments'][1]['start']=40
        with self.assertRaisesRegex(ValueError,'G38_CHUNK_ORDER'):
            SEG.restore(SEG.canonical(doc),chunks)
        doc=json.loads(manifest)
        doc['native_metadata']['repair']=False
        with self.assertRaisesRegex(ValueError,'G38_METADATA'):
            SEG.restore(SEG.canonical(doc),chunks)
        doc=json.loads(manifest)
        doc['native_checkpoint_sha256']='f'*64
        with self.assertRaisesRegex(ValueError,'G38_ROOT_PIN'):
            SEG.restore(SEG.canonical(doc),chunks)

    def test_rejected_duplicate_even_with_resealed_segment(self):
        doc=json.loads(fixture(3))
        doc['episodes'][2][0]=doc['episodes'][0][0]
        with self.assertRaisesRegex(ValueError,'G38_ROW_IDENTITY'):
            SEG.seal(SEG.canonical(doc))
        doc=json.loads(fixture(3));doc['episodes'][2][2]=True
        with self.assertRaisesRegex(ValueError,'G38_ROW_DATA'):
            SEG.seal(SEG.canonical(doc))
        with self.assertRaisesRegex(ValueError,'G38_NATIVE_CANONICAL'):
            SEG.seal(b'{"schema":  "changed"}')
        with self.assertRaisesRegex(ValueError,'G38_EPISODES_BOUNDS'):
            SEG.seal(fixture(1153))


    def test_g41_v7_extended_codec_and_v6_veto(self):
        """Shape-only DEV input; NOT a native state or verified scientific trial."""
        doc=json.loads(fixture(2048))
        doc['schema']='yggdrasil.ckad.native-episode-experience.v7'
        doc['episode_limit']=2048
        v7=SEG.canonical(doc)
        self.assertGreater(len(v7),SEG.MAX_CHECKPOINT_BYTES)
        manifest,chunks=SEG.seal(v7)
        self.assertEqual(json.loads(manifest)['schema'],SEG.EXTENDED_SCHEMA)
        self.assertEqual(len(chunks),64)
        self.assertEqual(SEG.restore(manifest,chunks),v7)
        wrong=json.loads(manifest);wrong['schema']=SEG.SCHEMA
        with self.assertRaisesRegex(ValueError,'G38_NATIVE_ENVELOPE_VERSION'):
            SEG.restore(SEG.canonical(wrong),chunks)
        doc['schema']='yggdrasil.ckad.native-episode-experience.v6'
        doc['episode_limit']=1152
        with self.assertRaisesRegex(ValueError,'G38_RAW_BOUNDS'):
            SEG.seal(SEG.canonical(doc))
        doc['schema']='yggdrasil.ckad.native-episode-experience.v7'
        doc['episode_limit']=2048
        doc['episodes'].append([f'{4097:064x}',[[0,1],[1,0]],0,0,1,1])
        with self.assertRaisesRegex(ValueError,'G38_EPISODES_BOUNDS'):
            SEG.seal(SEG.canonical(doc))

    def test_original_both_archived_instances_and_fresh_process(self):
        original_raw=[]
        for path,expected_zip in zip(ARCHIVE_PATHS,EXPECTED_ZIPS,strict=True):
            if not path.is_file():
                self.skipTest('Original action archive absent; test not required by CI')
            with self.subTest(path=path.name):
                self.assertEqual(sha256(path.read_bytes()).hexdigest(),expected_zip)
                with zipfile.ZipFile(path) as bundle:
                    joint=json.loads(bundle.read('amalgam-joint-state.json'))
                    native=json.loads(joint['native_ascii'])
                    raw=native['experience_ascii'].encode('ascii')
                self.assertEqual(sha256(raw).hexdigest(),EXPECTED_EPISODE_SHA)
                manifest,chunks=SEG.seal(raw)
                self.assertEqual(SEG.restore(manifest,chunks),raw)
                self.assertEqual(len(chunks),33)
                original_raw.append(raw)
                with tempfile.TemporaryDirectory() as d:
                    base=Path(d)
                    (base/'manifest.json').write_bytes(manifest)
                    for i,part in enumerate(chunks):
                        (base/f'{i:03d}.bin').write_bytes(part)
                    child=subprocess.check_output([sys.executable,'-B','-c',
                        'import pathlib,sys; from importlib.util import module_from_spec,spec_from_file_location; '
                        'spec=spec_from_file_location("g38",sys.argv[2]); '
                        'S=module_from_spec(spec); spec.loader.exec_module(S); '
                        'p=pathlib.Path(sys.argv[1]); m=(p/"manifest.json").read_bytes(); '
                        'chunks=tuple((p/f"{i:03d}.bin").read_bytes() for i in range(33)); '
                        'print(S._digest(S.restore(m,chunks)))',str(base),str(HERE / "segmented_episode_checkpoint.py")],
                        cwd=str(Path(__file__).parent),timeout=30).decode().strip()
                    self.assertEqual(child,EXPECTED_EPISODE_SHA)
        if len(original_raw)==2:
            self.assertEqual(original_raw[0],original_raw[1])


if __name__=='__main__': unittest.main()

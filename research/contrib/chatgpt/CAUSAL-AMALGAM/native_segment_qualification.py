"""G39 exact-source native cold-restore qualification for the G38 DEV envelope.

Read-only, local, fail-closed. Requires the unmodified pinned Yggdrasil source
and BOTH immutable original research archives. No world/actor/queue operation.
The report is engineering cold-parity evidence, not scientific retention.
"""
import argparse
from hashlib import sha1, sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
import segmented_episode_checkpoint as CODEC

SOURCE_BLOBS = {
    'yggdrasil/native_episode_experience.py': '5a18b00a4c4131526e71f51d63dfd9eb9471c81e',
    'yggdrasil/native_cumulative_learner.py': '1bdeaa4277fc9b34bbf7c0f36c6d0a4cc00e1ca4',
    'yggdrasil/native_context_basis.py': 'd5159e9b7ba196ee283ae7140faa031d4b7c4291',
    'yggdrasil/public_causal_cells.py': 'de8722f38d987ef7bcb4b7a0c23466b8e6f25712',
}
ZIP_HASHES = {
    'linux': 'b8504c3a9f0e44185380687f7ce3f0a7ad0347c5be03c1cd51dc3aa1bbc1051d',
    'windows': 'bb2b689f84caf939b76bea669eff7efb26506b602eed81ac79a81b42efb0a5a6',
}
NATIVE_SHA = '5720151e18b52f7219763027c2ad9c7c37476e099b4334e42417615adb7f959d'
EPISODE_SHA = '9158254b80f147d7eb7516d630f6003441df4b8373375b994d864ee1d55568f4'
VIEWS = ((0, 0), (0, 1), (1, 0), (1, 1))


def require(ok, code):
    if not ok:
        raise ValueError('G39_' + code)


def sha(raw):
    return sha256(raw).hexdigest()


def pin_sources(root=ROOT):
    """No partial shadow imports: fail before loading real native classes."""
    for path, expected in SOURCE_BLOBS.items():
        item = root / path
        require(item.is_file(), 'NATIVE_SOURCE_ABSENT:' + path)
        raw = item.read_bytes()
        actual = sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        require(actual == expected, 'NATIVE_SOURCE_DRIFT:' + path)


def extract_original(path, label):
    require(path.is_file(), 'ARCHIVE_ABSENT:' + label)
    require(sha(path.read_bytes()) == ZIP_HASHES[label], 'ARCHIVE_PIN:' + label)
    with zipfile.ZipFile(path) as z:
        name = 'amalgam-joint-state.json'
        matches = [i for i in z.infolist() if i.filename == name]
        require(len(matches) == 1 and matches[0].file_size < 4 * 1024 * 1024,
                'ARCHIVE_ENTRY:' + label)
        joint = json.loads(z.read(matches[0]))
    native_raw = joint['native_ascii'].encode('ascii')
    require(sha(native_raw) == NATIVE_SHA, 'ORIGINAL_NATIVE_PIN:' + label)
    episode_raw = json.loads(native_raw)['experience_ascii'].encode('ascii')
    require(sha(episode_raw) == EPISODE_SHA, 'ORIGINAL_EPISODE_PIN:' + label)
    return native_raw, episode_raw


def original_native_readback(native_raw, episode_raw):
    """Calls the real classes at exact pinned source blob hashes."""
    pin_sources()
    from yggdrasil.native_episode_experience import NativeEpisodeExperience
    from yggdrasil.native_cumulative_learner import NativeCumulativeLearner
    native_episode = NativeEpisodeExperience.restore(episode_raw, EPISODE_SHA)
    require(native_episode.checkpoint() == episode_raw, 'EPISODE_COLD_BYTES')
    require(native_episode.consolidate().checkpoint() == episode_raw,
            'EPISODE_CONSOLIDATION_BYTES')
    require(native_episode.info()['count'] == 1025, 'EPISODE_WITNESS_COUNT')
    require(len(native_episode._context_models) == 29, 'FULL_CONTEXT_29_EXPERTS')
    native = NativeCumulativeLearner.restore(native_raw, NATIVE_SHA)
    require(native.checkpoint() == native_raw, 'NATIVE_COLD_BYTES')
    require(native._episode_reader().checkpoint() == episode_raw,
            'NATIVE_EMBEDDED_EPISODE_BYTES')
    plans = {str(view): native.experience_context_plan(view) for view in VIEWS}
    require(len(plans) == 4, 'FULL_VIEW_PLAN_COUNT')
    for view in VIEWS:
        plan = plans[str(view)]
        require(type(plan) is dict and plan['first_action'] in (0, 1)
                and len(plan['first_values']) == 2
                and len(plan['second_actions']) == 2,
                'PLAN_SHAPE')
    return {'native_sha256': sha(native.checkpoint()),
            'episode_sha256': sha(native_episode.checkpoint()),
            'expert_count': len(native_episode._context_models),
            'episode_count': native_episode.info()['count'],
            'plan_sha256': sha(CODEC.canonical(plans)),
            'plans': plans}


def cold_child(segment_dir):
    pin_sources()
    root = Path(segment_dir)
    manifest = (root / 'manifest.json').read_bytes()
    info = json.loads(manifest)
    chunks = tuple((root / f'{i:03d}.bin').read_bytes()
                   for i in range(len(info['segments'])))
    episode_raw = CODEC.restore(manifest, chunks)
    native_raw = (root / 'native-raw.json').read_bytes()
    require(sha(native_raw) == NATIVE_SHA, 'COLD_NATIVE_PIN')
    require(json.loads(native_raw)['experience_ascii'].encode('ascii') == episode_raw,
            'COLD_EPISODE_EQUAL')
    return original_native_readback(native_raw, episode_raw)


def qualify(linux, windows):
    pin_sources()  # Fail closed before any model loading or archive processing.
    originals = [extract_original(path, label) for path, label in
                 ((linux, 'linux'), (windows, 'windows'))]
    require(originals[0] == originals[1], 'CROSS_OS_ORIGINAL_MISMATCH')
    native_raw, episode_raw = originals[0]
    manifest, segments = CODEC.seal(episode_raw)
    require(CODEC.restore(manifest, segments) == episode_raw, 'CODEC_ORIGINAL_BYTES')
    with TemporaryDirectory(prefix='g39-real-native-') as d:
        folder = Path(d)
        (folder / 'manifest.json').write_bytes(manifest)
        (folder / 'native-raw.json').write_bytes(native_raw)
        for i, part in enumerate(segments):
            (folder / f'{i:03d}.bin').write_bytes(part)
        parent = original_native_readback(native_raw, episode_raw)
        results = []
        for _ in range(2):
            raw = subprocess.check_output([sys.executable, '-B', str(Path(__file__)),
                                           '--child', str(folder)], timeout=180)
            results.append(json.loads(raw))
        require(parent == results[0] == results[1], 'COLD_PROCESS_PARITY')
    # Never misrepresent old/familiar Brier or novel transfer without independent outcomes.
    return {'status': 'G39_ORIGINAL_CLASS_COLD_PARITY_PASS',
            'original_repo_abi': SOURCE_BLOBS,
            'source_archive_sha256': ZIP_HASHES,
            'manifest_sha256': sha(manifest),
            'segment_count': len(segments),
            'native_checkpoint_sha256': parent['native_sha256'],
            'episode_checkpoint_sha256': parent['episode_sha256'],
            'expert_count': parent['expert_count'],
            'episode_count': parent['episode_count'],
            'plan_sha256': parent['plan_sha256'],
            'cold_child_count': len(results),
            'scientific_gain_verified': False,
            'native_capacity_extended': False,
            'protected_first_use': False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--linux', type=Path)
    p.add_argument('--windows', type=Path)
    p.add_argument('--child', type=Path)
    a = p.parse_args()
    require((a.child is None) != (a.linux is None and a.windows is None)
            and ((a.linux is None) == (a.windows is None)), 'ARGUMENT_SHAPE')
    report = cold_child(a.child) if a.child else qualify(a.linux, a.windows)
    print(json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    main()

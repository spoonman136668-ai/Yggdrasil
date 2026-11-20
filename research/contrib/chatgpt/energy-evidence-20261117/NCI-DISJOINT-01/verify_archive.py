"""Verify byte custody of NCI-DISJOINT-01 original source/results; no model execution."""
import argparse
import base64
import hashlib
import io
import json
from pathlib import Path
import tarfile


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    args = argparse.ArgumentParser()
    args.add_argument('--output', type=Path, required=True)
    opts = args.parse_args()
    base = Path(__file__).resolve().parent
    m = json.loads((base / 'manifest.json').read_text('utf-8'))
    assert m['schema'] == 'nci-disjoint01.archived-source-custody.v1'
    encoded = (base / 'evidence.tar.xz.b64').read_bytes()
    assert digest(encoded) == m['encoded_sha256']
    payload = base64.b64decode(encoded.strip(), validate=True)
    assert len(payload) == m['tar_bytes']
    assert digest(payload) == m['tar_sha256']
    raw_members = {}
    with tarfile.open(fileobj=io.BytesIO(payload), mode='r:xz') as archive:
        assert set(archive.getnames()) == set(m['members'])
        for member in archive:
            assert member.isfile() and member.name in m['members']
            assert not member.name.startswith(('/', '\\')) and '/' not in member.name
            raw = archive.extractfile(member).read()
            assert len(raw) == m['members'][member.name]['bytes']
            assert digest(raw) == m['members'][member.name]['sha256']
            raw_members[member.name] = raw
    assert not opts.output.exists() or not any(opts.output.iterdir())
    opts.output.mkdir(parents=True, exist_ok=True)
    for name, raw in raw_members.items():
        assert not (opts.output / name).exists()
        (opts.output / name).write_bytes(raw)
    print('NCI_DISJOINT01_ORIGINAL_SOURCE_CUSTODY_PASS', len(raw_members))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""ENERGY-69: fail-closed, read-only evidence custody verification."""
import base64
import hashlib
import io
import json
import tarfile
from pathlib import Path


def check():
    here = Path(__file__).resolve().parent
    manifest = json.loads((here / 'archive_manifest.json').read_text(encoding='utf-8'))
    assert manifest['schema'] == 'energy69.b64part-archive.v1'
    payload = b''
    for part in manifest['parts']:
        raw = (here / part['name']).read_bytes()
        assert len(raw) == part['bytes'], part['name']
        assert hashlib.sha256(raw).hexdigest() == part['sha256'], part['name']
        payload += raw
    assert len(payload) == manifest['base64_bytes']
    archive = base64.b64decode(payload, validate=True)
    assert len(archive) == manifest['archive_bytes']
    assert hashlib.sha256(archive).hexdigest() == manifest['archive_sha256']
    with tarfile.open(fileobj=io.BytesIO(archive), mode='r:xz') as handle:
        names = handle.getnames()
        assert len(names) == len(set(names)) and 'manifest.json' in names
        assert all(not name.startswith('/') and '..' not in Path(name).parts for name in names)
        internal = json.loads(handle.extractfile('manifest.json').read().decode('utf-8'))
        assert internal['schema'] == 'energy69.original-evidence-manifest.v1'
        assert internal['protocol_git_commit'] == manifest['prereg_commit']
        assert internal['experiment_source_sha256'] == manifest['source_sha256']
        for name, rec in internal['files'].items():
            full = ('source/' if name.endswith('.py') else 'screen/') + name
            obj = handle.extractfile(full).read()
            assert len(obj) == rec['bytes'], full
            assert hashlib.sha256(obj).hexdigest() == rec['sha256'], full
    print('ENERGY69_ARCHIVE_CUSTODY_PASS', manifest['archive_sha256'], len(archive), len(names))


if __name__ == '__main__':
    check()

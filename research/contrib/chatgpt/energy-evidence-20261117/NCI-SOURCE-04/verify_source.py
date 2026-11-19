#!/usr/bin/env python3
"""Verify and reconstruct exact NCI-SOURCE-04 audit source without overwrites."""
import argparse
import base64
import hashlib
import json
import lzma
from pathlib import Path


def git_blob(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True, type=Path)
    args = ap.parse_args()
    here = Path(__file__).resolve().parent
    m = json.loads((here/'manifest.json').read_bytes())
    assert m['schema'] == 'nci-source-04.source-custody.v1'
    coded = (here/'audit_staged_caller.py.xz.b64').read_bytes()
    assert len(coded) == m['encoded_bytes'] and git_blob(coded) == m['encoded_git_blob']
    data = lzma.decompress(base64.b64decode(coded.strip(), validate=True))
    assert len(data) == m['source_bytes']
    assert hashlib.sha256(data).hexdigest() == m['source_sha256']
    assert hashlib.sha256((here/'result.json').read_bytes()).hexdigest() == m['result_sha256']
    assert args.out.exists() is False, 'REFUSE_OVERWRITE_OUTPUT_DIRECTORY'
    args.out.mkdir(parents=True)
    (args.out/'audit_staged_caller.py').write_bytes(data)
    print('NCI_SOURCE04_BYTE_CUSTODY_PASS', m['source_sha256'])


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""ENERGY-71 byte custody reconstruction; never executes trained model code."""
import argparse,base64,hashlib,json,lzma
from pathlib import Path


def sha1_git_blob(payload):
    return hashlib.sha1(b'blob '+str(len(payload)).encode('ascii')+b'\0'+payload).hexdigest()


def main():
    args=argparse.ArgumentParser()
    args.add_argument('--out',type=Path,required=True)
    opt=args.parse_args()
    root=Path(__file__).resolve().parent
    manifest=json.loads((root/'archive_manifest.json').read_text('utf-8'))
    assert manifest['schema']=='energy71.artifact-custody.v1'
    output={}
    for name,spec in sorted(manifest['evidence'].items()):
        parts=[]
        for part in spec['parts']:
            content=(root/part['path']).read_bytes()
            assert len(content)==part['bytes'],part['path']
            assert sha1_git_blob(content)==part['blob_sha1'],part['path']
            parts.append(content.strip())
        encoded=b''.join(parts)
        raw=lzma.decompress(base64.b64decode(encoded,validate=True))
        assert len(raw)==spec['raw_bytes'],name
        assert hashlib.sha256(raw).hexdigest()==spec['raw_sha256'],name
        output[name]=raw
    assert hashlib.sha256(output['experiment.py']).hexdigest()==manifest['source_sha256']
    if opt.out.exists():
        assert opt.out.is_dir()
    else:
        opt.out.mkdir(parents=True,exist_ok=False)
    for name,raw in output.items():
        dest=opt.out/name
        assert not dest.exists(),'refuse overwrite: '+str(dest)
        dest.write_bytes(raw)
    print('ENERGY71_FULL_BYTE_CUSTODY_PASS',len(output),manifest['frozen_before_scoring_commit'])


if __name__=='__main__':
    main()

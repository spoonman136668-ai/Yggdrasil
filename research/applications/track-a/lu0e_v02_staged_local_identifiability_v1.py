#!/usr/bin/env python3
import base64, gzip, hashlib
from pathlib import Path

HERE=Path(__file__).parent
STEM=Path(__file__).stem
PARTS=sorted(HERE.glob(STEM + '.source.chunk*.b64'))

EXPECTED_PARTS=4
EXPECTED_B64_CHARS=6728
EXPECTED_B64_SHA256='f815b0c121f3583447c6abe85604c72b07bdad3f2697ad59c00f0a2aa57460e7'
EXPECTED_GZIP_BYTES=5045
EXPECTED_GZIP_SHA256='cc113f9e6ec530146b526d5f4db2cc33c2964bc8af262db64ef09baefb760e5a'
EXPECTED_SOURCE_BYTES=15981
EXPECTED_SOURCE_SHA256='1285839a69545b3a1623bcecc8f1e40d5954197e6afead5b8d58f91a6f141778'

if len(PARTS)!=EXPECTED_PARTS:
    raise SystemExit(f'LU0E source part-count mismatch: {len(PARTS)}')
encoded=''.join(p.read_text(encoding='ascii').strip() for p in PARTS)
if len(encoded)!=EXPECTED_B64_CHARS:
    raise SystemExit(f'LU0E base64 char-count mismatch: {len(encoded)}')
if hashlib.sha256(encoded.encode('ascii')).hexdigest()!=EXPECTED_B64_SHA256:
    raise SystemExit('LU0E base64 hash mismatch')
gz=base64.b64decode(encoded,validate=True)
if len(gz)!=EXPECTED_GZIP_BYTES:
    raise SystemExit(f'LU0E gzip byte-count mismatch: {len(gz)}')
if hashlib.sha256(gz).hexdigest()!=EXPECTED_GZIP_SHA256:
    raise SystemExit('LU0E gzip hash mismatch')
src=gzip.decompress(gz)
if len(src)!=EXPECTED_SOURCE_BYTES:
    raise SystemExit(f'LU0E source byte-count mismatch: {len(src)}')
if hashlib.sha256(src).hexdigest()!=EXPECTED_SOURCE_SHA256:
    raise SystemExit('LU0E source hash mismatch')
exec(compile(src,str(Path(__file__)),'exec'),globals(),globals())

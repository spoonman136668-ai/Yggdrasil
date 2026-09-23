#!/usr/bin/env python3
import base64, gzip, hashlib
from pathlib import Path

HERE=Path(__file__).parent
STEM=Path(__file__).stem
PARTS=sorted(HERE.glob(STEM + '.source.chunk*.b64'))

EXPECTED_PARTS=4
EXPECTED_B64_CHARS=7332
EXPECTED_B64_SHA256='729ad3e7d711e4209589473f958c0154b685470060bf4d5e06879dc7ff378397'
EXPECTED_GZIP_BYTES=5499
EXPECTED_GZIP_SHA256='b10cf60a8d32a2f6d9cb699edc9b2196452ed5c3ea95df955f0d7ddb74921bd6'
EXPECTED_SOURCE_BYTES=17800
EXPECTED_SOURCE_SHA256='b57ac5d76c6e4e8ceb7dc9ba94aa54bce6ca5207c26739f91e9d1d5d0fb62557'

if len(PARTS)!=EXPECTED_PARTS:
    raise SystemExit(f'TASK1F source part-count mismatch: {len(PARTS)}')
encoded=''.join(p.read_text(encoding='ascii').strip() for p in PARTS)
if len(encoded)!=EXPECTED_B64_CHARS:
    raise SystemExit(f'TASK1F base64 char-count mismatch: {len(encoded)}')
if hashlib.sha256(encoded.encode('ascii')).hexdigest()!=EXPECTED_B64_SHA256:
    raise SystemExit('TASK1F base64 hash mismatch')
gz=base64.b64decode(encoded,validate=True)
if len(gz)!=EXPECTED_GZIP_BYTES:
    raise SystemExit(f'TASK1F gzip byte-count mismatch: {len(gz)}')
if hashlib.sha256(gz).hexdigest()!=EXPECTED_GZIP_SHA256:
    raise SystemExit('TASK1F gzip hash mismatch')
src=gzip.decompress(gz)
if len(src)!=EXPECTED_SOURCE_BYTES:
    raise SystemExit(f'TASK1F source byte-count mismatch: {len(src)}')
if hashlib.sha256(src).hexdigest()!=EXPECTED_SOURCE_SHA256:
    raise SystemExit('TASK1F source hash mismatch')
exec(compile(src,str(Path(__file__)),'exec'),globals(),globals())

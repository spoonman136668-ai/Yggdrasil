#!/usr/bin/env python3
import base64, gzip, hashlib
from pathlib import Path

HERE=Path(__file__).parent
STEM=Path(__file__).stem
PARTS=sorted(HERE.glob(STEM + '.source.chunk*.b64'))

EXPECTED_PARTS=3
EXPECTED_B64_CHARS=5904
EXPECTED_B64_SHA256='b141106f4c74c8b61d935de3dfff42f6d86ba9bbb6f16ce7fc64ae0ae193de31'
EXPECTED_GZIP_BYTES=4427
EXPECTED_GZIP_SHA256='21c1a751c98a7586ead0224ee7af11ee85265ec513fd1f90f631c6558f8f39f3'
EXPECTED_SOURCE_BYTES=15476
EXPECTED_SOURCE_SHA256='c1578a0d21d1125a26d81664adc0c3a78a3a23e9a4a2a4865d526e41af7d2207'

if len(PARTS)!=EXPECTED_PARTS:
    raise SystemExit(f'TASK1E source part-count mismatch: {len(PARTS)}')
encoded=''.join(p.read_text(encoding='ascii').strip() for p in PARTS)
if len(encoded)!=EXPECTED_B64_CHARS:
    raise SystemExit(f'TASK1E base64 char-count mismatch: {len(encoded)}')
if hashlib.sha256(encoded.encode('ascii')).hexdigest()!=EXPECTED_B64_SHA256:
    raise SystemExit('TASK1E base64 hash mismatch')
gz=base64.b64decode(encoded,validate=True)
if len(gz)!=EXPECTED_GZIP_BYTES:
    raise SystemExit(f'TASK1E gzip byte-count mismatch: {len(gz)}')
if hashlib.sha256(gz).hexdigest()!=EXPECTED_GZIP_SHA256:
    raise SystemExit('TASK1E gzip hash mismatch')
src=gzip.decompress(gz)
if len(src)!=EXPECTED_SOURCE_BYTES:
    raise SystemExit(f'TASK1E source byte-count mismatch: {len(src)}')
if hashlib.sha256(src).hexdigest()!=EXPECTED_SOURCE_SHA256:
    raise SystemExit('TASK1E source hash mismatch')
exec(compile(src,str(Path(__file__)),'exec'),globals(),globals())

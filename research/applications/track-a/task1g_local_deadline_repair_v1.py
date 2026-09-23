#!/usr/bin/env python3
import base64, gzip, hashlib
from pathlib import Path

HERE=Path(__file__).parent
STEM=Path(__file__).stem
PARTS=sorted(HERE.glob(STEM + '.source.chunk*.b64'))

EXPECTED_PARTS=4
EXPECTED_B64_CHARS=6676
EXPECTED_B64_SHA256='fa7a7a56431ba98b38aca1369d152c65237be381bfdf1e4910c68a7a76442d8e'
EXPECTED_GZIP_BYTES=5006
EXPECTED_GZIP_SHA256='8df6b8feb73862cf643bd820416d91a7120356c2b002d94074bc69fbeead051e'
EXPECTED_SOURCE_BYTES=15987
EXPECTED_SOURCE_SHA256='dc46ac0cc462f5f3ff93c56c28db4ed7da92ce67654d1633b4d3014e9ae01197'

if len(PARTS)!=EXPECTED_PARTS:
    raise SystemExit(f'TASK1G source part-count mismatch: {len(PARTS)}')
encoded=''.join(p.read_text(encoding='ascii').strip() for p in PARTS)
if len(encoded)!=EXPECTED_B64_CHARS:
    raise SystemExit(f'TASK1G base64 char-count mismatch: {len(encoded)}')
if hashlib.sha256(encoded.encode('ascii')).hexdigest()!=EXPECTED_B64_SHA256:
    raise SystemExit('TASK1G base64 hash mismatch')
gz=base64.b64decode(encoded,validate=True)
if len(gz)!=EXPECTED_GZIP_BYTES:
    raise SystemExit(f'TASK1G gzip byte-count mismatch: {len(gz)}')
if hashlib.sha256(gz).hexdigest()!=EXPECTED_GZIP_SHA256:
    raise SystemExit('TASK1G gzip hash mismatch')
src=gzip.decompress(gz)
if len(src)!=EXPECTED_SOURCE_BYTES:
    raise SystemExit(f'TASK1G source byte-count mismatch: {len(src)}')
if hashlib.sha256(src).hexdigest()!=EXPECTED_SOURCE_SHA256:
    raise SystemExit('TASK1G source hash mismatch')
exec(compile(src,str(Path(__file__)),'exec'),globals(),globals())

#!/usr/bin/env python3
import base64, gzip, hashlib
from pathlib import Path

HERE=Path(__file__).parent
STEM=Path(__file__).stem
PARTS=sorted(HERE.glob(STEM + '.source.chunk*.b64'))

EXPECTED_PARTS=3
EXPECTED_B64_CHARS=5844
EXPECTED_B64_SHA256='cfab9d8e472030e98e7624a3d3f88f711436f434db9cb8791241bf7f6c3f20ed'
EXPECTED_GZIP_BYTES=4381
EXPECTED_GZIP_SHA256='ec64b6300c6452e6890ffb01384df8b4dcdc7281c89c3dda1b3c383dcae5e7ed'
EXPECTED_SOURCE_BYTES=13906
EXPECTED_SOURCE_SHA256='b2ef10e618871a081871d8858b3fcd153228cb831a643dc068bd3b30d9f6358f'

if len(PARTS)!=EXPECTED_PARTS:
    raise SystemExit(f'LU0B source part-count mismatch: {len(PARTS)}')
encoded=''.join(p.read_text(encoding='ascii').strip() for p in PARTS)
if len(encoded)!=EXPECTED_B64_CHARS:
    raise SystemExit(f'LU0B base64 char-count mismatch: {len(encoded)}')
if hashlib.sha256(encoded.encode('ascii')).hexdigest()!=EXPECTED_B64_SHA256:
    raise SystemExit('LU0B base64 hash mismatch')
gz=base64.b64decode(encoded,validate=True)
if len(gz)!=EXPECTED_GZIP_BYTES:
    raise SystemExit(f'LU0B gzip byte-count mismatch: {len(gz)}')
if hashlib.sha256(gz).hexdigest()!=EXPECTED_GZIP_SHA256:
    raise SystemExit('LU0B gzip hash mismatch')
src=gzip.decompress(gz)
if len(src)!=EXPECTED_SOURCE_BYTES:
    raise SystemExit(f'LU0B source byte-count mismatch: {len(src)}')
if hashlib.sha256(src).hexdigest()!=EXPECTED_SOURCE_SHA256:
    raise SystemExit('LU0B source hash mismatch')
exec(compile(src,str(Path(__file__)),'exec'),globals(),globals())

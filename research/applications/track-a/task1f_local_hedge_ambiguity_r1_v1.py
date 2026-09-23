#!/usr/bin/env python3
import base64, gzip, hashlib
from pathlib import Path

HERE=Path(__file__).parent
STEM=Path(__file__).stem
PARTS=sorted(HERE.glob(STEM + '.source.chunk*.b64'))

EXPECTED_PARTS=4
EXPECTED_B64_CHARS=7504
EXPECTED_B64_SHA256='930a9144d0c52bad8b7386a8cc292e20012b392689a1f298dcd5e5ef8d17d7d5'
EXPECTED_GZIP_BYTES=5626
EXPECTED_GZIP_SHA256='b518b459f2ce7fed80bd80de4aebc0bb75ea226159a2efd964b00a370ecff91f'
EXPECTED_SOURCE_BYTES=18265
EXPECTED_SOURCE_SHA256='a3122a9f4f6da6c138cc12944528f5e2e3ef608e904067ef30da7feab7d640f4'

if len(PARTS)!=EXPECTED_PARTS:
    raise SystemExit(f'TASK1F-R1 source part-count mismatch: {len(PARTS)}')
encoded=''.join(p.read_text(encoding='ascii').strip() for p in PARTS)
if len(encoded)!=EXPECTED_B64_CHARS:
    raise SystemExit(f'TASK1F-R1 base64 char-count mismatch: {len(encoded)}')
if hashlib.sha256(encoded.encode('ascii')).hexdigest()!=EXPECTED_B64_SHA256:
    raise SystemExit('TASK1F-R1 base64 hash mismatch')
gz=base64.b64decode(encoded,validate=True)
if len(gz)!=EXPECTED_GZIP_BYTES:
    raise SystemExit(f'TASK1F-R1 gzip byte-count mismatch: {len(gz)}')
if hashlib.sha256(gz).hexdigest()!=EXPECTED_GZIP_SHA256:
    raise SystemExit('TASK1F-R1 gzip hash mismatch')
src=gzip.decompress(gz)
if len(src)!=EXPECTED_SOURCE_BYTES:
    raise SystemExit(f'TASK1F-R1 source byte-count mismatch: {len(src)}')
if hashlib.sha256(src).hexdigest()!=EXPECTED_SOURCE_SHA256:
    raise SystemExit('TASK1F-R1 source hash mismatch')
exec(compile(src,str(Path(__file__)),'exec'),globals(),globals())

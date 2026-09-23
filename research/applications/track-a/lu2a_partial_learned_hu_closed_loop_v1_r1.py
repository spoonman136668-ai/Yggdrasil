#!/usr/bin/env python3
import base64, gzip, hashlib
from pathlib import Path

HERE=Path(__file__).parent
PARTS=sorted(HERE.glob('lu2a_partial_learned_hu_closed_loop_v1.source.chunk*.b64'))

EXPECTED_PARTS=5
EXPECTED_B64_CHARS=9760
EXPECTED_GZIP_BYTES=7320
EXPECTED_SOURCE_BYTES=23066
EXPECTED_SOURCE_SHA256='251fcb655a04b109dc9716a021acef9f956333ca265685246f41868923627f35'

if len(PARTS)!=EXPECTED_PARTS:
    raise SystemExit(f'LU2A-R1 source part-count mismatch: {len(PARTS)}')
encoded=''.join(p.read_text(encoding='ascii').strip() for p in PARTS)
if len(encoded)!=EXPECTED_B64_CHARS:
    raise SystemExit(f'LU2A-R1 base64 char-count mismatch: {len(encoded)}')
padded=encoded + ('=' * ((4 - len(encoded) % 4) % 4))
gz=base64.b64decode(padded,validate=True)
if len(gz)!=EXPECTED_GZIP_BYTES:
    raise SystemExit(f'LU2A-R1 gzip byte-count mismatch: {len(gz)}')
src=gzip.decompress(gz)
if len(src)!=EXPECTED_SOURCE_BYTES:
    raise SystemExit(f'LU2A-R1 source byte-count mismatch: {len(src)}')
if hashlib.sha256(src).hexdigest()!=EXPECTED_SOURCE_SHA256:
    raise SystemExit('LU2A-R1 source hash mismatch')
exec(compile(src,str(Path(__file__)),'exec'),globals(),globals())

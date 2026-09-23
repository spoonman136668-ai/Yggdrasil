#!/usr/bin/env python3
import base64, gzip, hashlib
from pathlib import Path

HERE=Path(__file__).parent
STEM=Path(__file__).stem
PARTS=sorted(HERE.glob(STEM + '.source.chunk*.b64'))

EXPECTED_PARTS=4
EXPECTED_B64_CHARS=6276
EXPECTED_B64_SHA256='cb871c72c783e2e00404a35210c977063cd150a635651bdbb210a931f4a5a56e'
EXPECTED_GZIP_BYTES=4705
EXPECTED_GZIP_SHA256='2f4bf869396d2fd48b80248418d3ce544862e314d77a34b747c25aa02e4b1156'
EXPECTED_SOURCE_BYTES=13204
EXPECTED_SOURCE_SHA256='e4abb65ac7abf2909cb8df5ceb7f3bfd8bcf142bf5a7c6453e90fbd4e828f7c1'

if len(PARTS)!=EXPECTED_PARTS:
    raise SystemExit(f'LU1C source part-count mismatch: {len(PARTS)}')
encoded=''.join(p.read_text(encoding='ascii').strip() for p in PARTS)
if len(encoded)!=EXPECTED_B64_CHARS:
    raise SystemExit(f'LU1C base64 char-count mismatch: {len(encoded)}')
if hashlib.sha256(encoded.encode('ascii')).hexdigest()!=EXPECTED_B64_SHA256:
    raise SystemExit('LU1C base64 hash mismatch')
gz=base64.b64decode(encoded,validate=True)
if len(gz)!=EXPECTED_GZIP_BYTES:
    raise SystemExit(f'LU1C gzip byte-count mismatch: {len(gz)}')
if hashlib.sha256(gz).hexdigest()!=EXPECTED_GZIP_SHA256:
    raise SystemExit('LU1C gzip hash mismatch')
src=gzip.decompress(gz)
if len(src)!=EXPECTED_SOURCE_BYTES:
    raise SystemExit(f'LU1C source byte-count mismatch: {len(src)}')
if hashlib.sha256(src).hexdigest()!=EXPECTED_SOURCE_SHA256:
    raise SystemExit('LU1C source hash mismatch')
exec(compile(src,str(Path(__file__)),'exec'),globals(),globals())

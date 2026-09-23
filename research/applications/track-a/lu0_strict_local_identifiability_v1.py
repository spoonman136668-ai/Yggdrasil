#!/usr/bin/env python3
import base64, gzip, hashlib
from pathlib import Path

HERE=Path(__file__).parent
STEM=Path(__file__).stem
PARTS=sorted(HERE.glob(STEM + '.source.chunk*.b64'))

EXPECTED_PARTS=3
EXPECTED_B64_CHARS=4128
EXPECTED_B64_SHA256='fbec3addfc0ffc78a5e0546568308ce78dc04478fea03f811770f51c98482b5f'
EXPECTED_GZIP_BYTES=3094
EXPECTED_GZIP_SHA256='c7f3dd019e2802f008af4a80340e68c24b971411d0e784ff33ea0a2b0d0d463a'
EXPECTED_SOURCE_BYTES=8684
EXPECTED_SOURCE_SHA256='c77dd0cb2e7c919f2ec7fafc12aa0eae5509c36d82c468a41ad68a70e4401dcd'

if len(PARTS)!=EXPECTED_PARTS:
    raise SystemExit(f'LU0 source part-count mismatch: {len(PARTS)}')
encoded=''.join(p.read_text(encoding='ascii').strip() for p in PARTS)
if len(encoded)!=EXPECTED_B64_CHARS:
    raise SystemExit(f'LU0 base64 char-count mismatch: {len(encoded)}')
if hashlib.sha256(encoded.encode('ascii')).hexdigest()!=EXPECTED_B64_SHA256:
    raise SystemExit('LU0 base64 hash mismatch')
gz=base64.b64decode(encoded,validate=True)
if len(gz)!=EXPECTED_GZIP_BYTES:
    raise SystemExit(f'LU0 gzip byte-count mismatch: {len(gz)}')
if hashlib.sha256(gz).hexdigest()!=EXPECTED_GZIP_SHA256:
    raise SystemExit('LU0 gzip hash mismatch')
src=gzip.decompress(gz)
if len(src)!=EXPECTED_SOURCE_BYTES:
    raise SystemExit(f'LU0 source byte-count mismatch: {len(src)}')
if hashlib.sha256(src).hexdigest()!=EXPECTED_SOURCE_SHA256:
    raise SystemExit('LU0 source hash mismatch')
exec(compile(src,str(Path(__file__)),'exec'),globals(),globals())

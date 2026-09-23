#!/usr/bin/env python3
import base64, gzip, hashlib
from pathlib import Path

HERE=Path(__file__).parent
STEM=Path(__file__).stem
PARTS=sorted(HERE.glob(STEM + '.source.chunk*.b64'))

EXPECTED_PARTS=3
EXPECTED_B64_CHARS=5796
EXPECTED_B64_SHA256='50617d740dfe6e600d47245387251d6f96468c6226218fde4149394c35f339b6'
EXPECTED_GZIP_BYTES=4347
EXPECTED_GZIP_SHA256='7f133d458328aae02230d73ff036a061a4fd94f64b753113d68de9a5827ce14d'
EXPECTED_SOURCE_BYTES=12351
EXPECTED_SOURCE_SHA256='ecc52037e85ac684722e2a0ed2e01641e45e3d239134a5b4b104dc8dbfdd883c'

if len(PARTS)!=EXPECTED_PARTS:
    raise SystemExit(f'LU1B source part-count mismatch: {len(PARTS)}')
encoded=''.join(p.read_text(encoding='ascii').strip() for p in PARTS)
if len(encoded)!=EXPECTED_B64_CHARS:
    raise SystemExit(f'LU1B base64 char-count mismatch: {len(encoded)}')
if hashlib.sha256(encoded.encode('ascii')).hexdigest()!=EXPECTED_B64_SHA256:
    raise SystemExit('LU1B base64 hash mismatch')
gz=base64.b64decode(encoded,validate=True)
if len(gz)!=EXPECTED_GZIP_BYTES:
    raise SystemExit(f'LU1B gzip byte-count mismatch: {len(gz)}')
if hashlib.sha256(gz).hexdigest()!=EXPECTED_GZIP_SHA256:
    raise SystemExit('LU1B gzip hash mismatch')
src=gzip.decompress(gz)
if len(src)!=EXPECTED_SOURCE_BYTES:
    raise SystemExit(f'LU1B source byte-count mismatch: {len(src)}')
if hashlib.sha256(src).hexdigest()!=EXPECTED_SOURCE_SHA256:
    raise SystemExit('LU1B source hash mismatch')
exec(compile(src,str(Path(__file__)),'exec'),globals(),globals())

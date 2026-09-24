#!/usr/bin/env python3
import base64, gzip, hashlib
from pathlib import Path

HERE=Path(__file__).parent
STEM=Path(__file__).stem
PARTS=sorted(HERE.glob(STEM + '.source.chunk*.b64'))

EXPECTED_PARTS=1
EXPECTED_B64_CHARS=2008
EXPECTED_B64_SHA256='a7d591d6edb4ed5bca098be113c8953a90e942ed6d237f3def5d8c10a03014f5'
EXPECTED_GZIP_BYTES=1506
EXPECTED_GZIP_SHA256='6eb9f343f626291af7be7e75350d259a7e6cc7594fac8efaca98162f120abbba'
EXPECTED_SOURCE_BYTES=3630
EXPECTED_SOURCE_SHA256='aa6f9529713cbb91d486b1176b968f48af27a797291894db16a8a329b7a2e1fb'

if len(PARTS)!=EXPECTED_PARTS:
    raise SystemExit(f'LU2G source part-count mismatch: {len(PARTS)}')
encoded=''.join(p.read_text(encoding='ascii').strip() for p in PARTS)
if len(encoded)!=EXPECTED_B64_CHARS:
    raise SystemExit(f'LU2G base64 char-count mismatch: {len(encoded)}')
if hashlib.sha256(encoded.encode('ascii')).hexdigest()!=EXPECTED_B64_SHA256:
    raise SystemExit('LU2G base64 hash mismatch')
gz=base64.b64decode(encoded,validate=True)
if len(gz)!=EXPECTED_GZIP_BYTES:
    raise SystemExit(f'LU2G gzip byte-count mismatch: {len(gz)}')
if hashlib.sha256(gz).hexdigest()!=EXPECTED_GZIP_SHA256:
    raise SystemExit('LU2G gzip hash mismatch')
src=gzip.decompress(gz)
if len(src)!=EXPECTED_SOURCE_BYTES:
    raise SystemExit(f'LU2G source byte-count mismatch: {len(src)}')
if hashlib.sha256(src).hexdigest()!=EXPECTED_SOURCE_SHA256:
    raise SystemExit('LU2G source hash mismatch')
exec(compile(src,str(Path(__file__)),'exec'),globals(),globals())

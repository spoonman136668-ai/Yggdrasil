#!/usr/bin/env python3
import base64, gzip, hashlib
from pathlib import Path

HERE=Path(__file__).parent
STEM=Path(__file__).stem
PARTS=sorted(HERE.glob(STEM + '.source.chunk*.b64'))

EXPECTED_PARTS=3
EXPECTED_B64_CHARS=5768
EXPECTED_B64_SHA256='a4d861bcaf3b09749449b5bb3ba4158081f44321cb9a337ef170f61aa947f650'
EXPECTED_GZIP_BYTES=4326
EXPECTED_GZIP_SHA256='ac80d99c6e9055dea01d2bdb86fa96eb6dc712eca2ce280448867813e8aa4388'
EXPECTED_SOURCE_BYTES=15217
EXPECTED_SOURCE_SHA256='eca65242ea0b83a3448dcc28bf360141e819286000dfdb747c5c34969d18fd57'

if len(PARTS)!=EXPECTED_PARTS:
    raise SystemExit(f'TASK1D source part-count mismatch: {len(PARTS)}')
encoded=''.join(p.read_text(encoding='ascii').strip() for p in PARTS)
if len(encoded)!=EXPECTED_B64_CHARS:
    raise SystemExit(f'TASK1D base64 char-count mismatch: {len(encoded)}')
if hashlib.sha256(encoded.encode('ascii')).hexdigest()!=EXPECTED_B64_SHA256:
    raise SystemExit('TASK1D base64 hash mismatch')
gz=base64.b64decode(encoded,validate=True)
if len(gz)!=EXPECTED_GZIP_BYTES:
    raise SystemExit(f'TASK1D gzip byte-count mismatch: {len(gz)}')
if hashlib.sha256(gz).hexdigest()!=EXPECTED_GZIP_SHA256:
    raise SystemExit('TASK1D gzip hash mismatch')
src=gzip.decompress(gz)
if len(src)!=EXPECTED_SOURCE_BYTES:
    raise SystemExit(f'TASK1D source byte-count mismatch: {len(src)}')
if hashlib.sha256(src).hexdigest()!=EXPECTED_SOURCE_SHA256:
    raise SystemExit('TASK1D source hash mismatch')
exec(compile(src,str(Path(__file__)),'exec'),globals(),globals())

#!/usr/bin/env python3
import base64, gzip, hashlib
from pathlib import Path

HERE=Path(__file__).parent
STEM=Path(__file__).stem
PARTS=sorted(HERE.glob(STEM + '.source.chunk*.b64'))

EXPECTED_PARTS=3
EXPECTED_B64_CHARS=4904
EXPECTED_B64_SHA256='7d3668681bf4e6dc4f1e89ff22c744d0706508291c8476ff146d1527efdfb9e6'
EXPECTED_GZIP_BYTES=3677
EXPECTED_GZIP_SHA256='c564cc3b793740b2a7096cbcf09da70718d492fc4043821dff250beaff0fccba'
EXPECTED_SOURCE_BYTES=12463
EXPECTED_SOURCE_SHA256='d33f8b4a4ee8b4866b34f36060759fedfa0511a0ca8b7e697bbcb8bbd1e1464d'

if len(PARTS)!=EXPECTED_PARTS:
    raise SystemExit(f'TASK1C source part-count mismatch: {len(PARTS)}')
encoded=''.join(p.read_text(encoding='ascii').strip() for p in PARTS)
if len(encoded)!=EXPECTED_B64_CHARS:
    raise SystemExit(f'TASK1C base64 char-count mismatch: {len(encoded)}')
if hashlib.sha256(encoded.encode('ascii')).hexdigest()!=EXPECTED_B64_SHA256:
    raise SystemExit('TASK1C base64 hash mismatch')
gz=base64.b64decode(encoded,validate=True)
if len(gz)!=EXPECTED_GZIP_BYTES:
    raise SystemExit(f'TASK1C gzip byte-count mismatch: {len(gz)}')
if hashlib.sha256(gz).hexdigest()!=EXPECTED_GZIP_SHA256:
    raise SystemExit('TASK1C gzip hash mismatch')
src=gzip.decompress(gz)
if len(src)!=EXPECTED_SOURCE_BYTES:
    raise SystemExit(f'TASK1C source byte-count mismatch: {len(src)}')
if hashlib.sha256(src).hexdigest()!=EXPECTED_SOURCE_SHA256:
    raise SystemExit('TASK1C source hash mismatch')
exec(compile(src,str(Path(__file__)),'exec'),globals(),globals())

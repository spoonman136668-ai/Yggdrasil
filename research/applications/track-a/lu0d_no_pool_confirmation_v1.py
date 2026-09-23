#!/usr/bin/env python3
import base64, gzip, hashlib
from pathlib import Path

HERE=Path(__file__).parent
STEM=Path(__file__).stem
PARTS=sorted(HERE.glob(STEM + '.source.chunk*.b64'))

EXPECTED_PARTS=3
EXPECTED_B64_CHARS=5144
EXPECTED_B64_SHA256='f0092dbbb72a8d99af5f7075b58e6957d41958fa8a9613581d494ed1e305b715'
EXPECTED_GZIP_BYTES=3858
EXPECTED_GZIP_SHA256='37913416f239cd07e25e49b41b13c12a9be7e838e400fb48d58e06c9189a9724'
EXPECTED_SOURCE_BYTES=13990
EXPECTED_SOURCE_SHA256='16bd83660cee18d71ea2a26a48032d1a376dee2f9f9a8ad0a1e1b21bb0d23440'

if len(PARTS)!=EXPECTED_PARTS:
    raise SystemExit(f'LU0D source part-count mismatch: {len(PARTS)}')
encoded=''.join(p.read_text(encoding='ascii').strip() for p in PARTS)
if len(encoded)!=EXPECTED_B64_CHARS:
    raise SystemExit(f'LU0D base64 char-count mismatch: {len(encoded)}')
if hashlib.sha256(encoded.encode('ascii')).hexdigest()!=EXPECTED_B64_SHA256:
    raise SystemExit('LU0D base64 hash mismatch')
gz=base64.b64decode(encoded,validate=True)
if len(gz)!=EXPECTED_GZIP_BYTES:
    raise SystemExit(f'LU0D gzip byte-count mismatch: {len(gz)}')
if hashlib.sha256(gz).hexdigest()!=EXPECTED_GZIP_SHA256:
    raise SystemExit('LU0D gzip hash mismatch')
src=gzip.decompress(gz)
if len(src)!=EXPECTED_SOURCE_BYTES:
    raise SystemExit(f'LU0D source byte-count mismatch: {len(src)}')
if hashlib.sha256(src).hexdigest()!=EXPECTED_SOURCE_SHA256:
    raise SystemExit('LU0D source hash mismatch')
exec(compile(src,str(Path(__file__)),'exec'),globals(),globals())

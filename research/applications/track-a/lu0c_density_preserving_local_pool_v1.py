#!/usr/bin/env python3
import base64, gzip, hashlib
from pathlib import Path

HERE=Path(__file__).parent
STEM=Path(__file__).stem
PARTS=sorted(HERE.glob(STEM + '.source.chunk*.b64'))

EXPECTED_PARTS=5
EXPECTED_B64_CHARS=9960
EXPECTED_B64_SHA256='df5050154df87de69417b5ac6be19e8ac99a53c9acc71cde1643b1fddef9e935'
EXPECTED_GZIP_BYTES=7469
EXPECTED_GZIP_SHA256='6c74f8ac395b31d0d6c1b404f495579a4fc15562a15165e72043e3dc8f3f4a25'
EXPECTED_SOURCE_BYTES=28556
EXPECTED_SOURCE_SHA256='57476bf302ad3117a496b5ffabb33f69d3a99d1d89eb683be2d6073c662d45ae'

if len(PARTS)!=EXPECTED_PARTS:
    raise SystemExit(f'LU0C source part-count mismatch: {len(PARTS)}')
encoded=''.join(p.read_text(encoding='ascii').strip() for p in PARTS)
if len(encoded)!=EXPECTED_B64_CHARS:
    raise SystemExit(f'LU0C base64 char-count mismatch: {len(encoded)}')
if hashlib.sha256(encoded.encode('ascii')).hexdigest()!=EXPECTED_B64_SHA256:
    raise SystemExit('LU0C base64 hash mismatch')
gz=base64.b64decode(encoded,validate=True)
if len(gz)!=EXPECTED_GZIP_BYTES:
    raise SystemExit(f'LU0C gzip byte-count mismatch: {len(gz)}')
if hashlib.sha256(gz).hexdigest()!=EXPECTED_GZIP_SHA256:
    raise SystemExit('LU0C gzip hash mismatch')
src=gzip.decompress(gz)
if len(src)!=EXPECTED_SOURCE_BYTES:
    raise SystemExit(f'LU0C source byte-count mismatch: {len(src)}')
if hashlib.sha256(src).hexdigest()!=EXPECTED_SOURCE_SHA256:
    raise SystemExit('LU0C source hash mismatch')
exec(compile(src,str(Path(__file__)),'exec'),globals(),globals())

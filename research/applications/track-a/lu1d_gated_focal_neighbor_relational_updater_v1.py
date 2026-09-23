#!/usr/bin/env python3
import base64, gzip, hashlib
from pathlib import Path

HERE=Path(__file__).parent
STEM=Path(__file__).stem
PARTS=sorted(HERE.glob(STEM + '.source.chunk*.b64'))

EXPECTED_PARTS=4
EXPECTED_B64_CHARS=6368
EXPECTED_B64_SHA256='f32581967886939bcefc4d07bf77819ac210249f96d97a1e482d3f2e00d36964'
EXPECTED_GZIP_BYTES=4776
EXPECTED_GZIP_SHA256='54de5eba252b9058f5335e2ddce5428bffb091ba25ab5cdcd91d8cad129c7f64'
EXPECTED_SOURCE_BYTES=13562
EXPECTED_SOURCE_SHA256='8d74638a49c3206f5fa7461967de1d2151be7ef87980a2de86f5d83076934b1f'

if len(PARTS)!=EXPECTED_PARTS:
    raise SystemExit(f'LU1D source part-count mismatch: {len(PARTS)}')
encoded=''.join(p.read_text(encoding='ascii').strip() for p in PARTS)
if len(encoded)!=EXPECTED_B64_CHARS:
    raise SystemExit(f'LU1D base64 char-count mismatch: {len(encoded)}')
if hashlib.sha256(encoded.encode('ascii')).hexdigest()!=EXPECTED_B64_SHA256:
    raise SystemExit('LU1D base64 hash mismatch')
gz=base64.b64decode(encoded,validate=True)
if len(gz)!=EXPECTED_GZIP_BYTES:
    raise SystemExit(f'LU1D gzip byte-count mismatch: {len(gz)}')
if hashlib.sha256(gz).hexdigest()!=EXPECTED_GZIP_SHA256:
    raise SystemExit('LU1D gzip hash mismatch')
src=gzip.decompress(gz)
if len(src)!=EXPECTED_SOURCE_BYTES:
    raise SystemExit(f'LU1D source byte-count mismatch: {len(src)}')
if hashlib.sha256(src).hexdigest()!=EXPECTED_SOURCE_SHA256:
    raise SystemExit('LU1D source hash mismatch')
exec(compile(src,str(Path(__file__)),'exec'),globals(),globals())

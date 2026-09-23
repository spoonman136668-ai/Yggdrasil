#!/usr/bin/env python3
import base64, gzip, hashlib
from pathlib import Path

HERE=Path(__file__).parent
STEM=Path(__file__).stem
PARTS=sorted(HERE.glob(STEM + '.source.chunk*.b64'))

EXPECTED_PARTS=4
EXPECTED_B64_CHARS=6604
EXPECTED_B64_SHA256='ca05287ca5318011868482baf009c29ce6b1014f786e82d77098521e45c426b6'
EXPECTED_GZIP_BYTES=4951
EXPECTED_GZIP_SHA256='a2455d35710e540d5da7f83a7c4df6710d4af850a1a17a2e7403a9e7e6597134'
EXPECTED_SOURCE_BYTES=13963
EXPECTED_SOURCE_SHA256='38c3d42786426d4ace4a779b69d49509d65a7eb31f9bfa3c4209e603879d0b2a'

if len(PARTS)!=EXPECTED_PARTS:
    raise SystemExit(f'LU1E source part-count mismatch: {len(PARTS)}')
encoded=''.join(p.read_text(encoding='ascii').strip() for p in PARTS)
if len(encoded)!=EXPECTED_B64_CHARS:
    raise SystemExit(f'LU1E base64 char-count mismatch: {len(encoded)}')
if hashlib.sha256(encoded.encode('ascii')).hexdigest()!=EXPECTED_B64_SHA256:
    raise SystemExit('LU1E base64 hash mismatch')
gz=base64.b64decode(encoded,validate=True)
if len(gz)!=EXPECTED_GZIP_BYTES:
    raise SystemExit(f'LU1E gzip byte-count mismatch: {len(gz)}')
if hashlib.sha256(gz).hexdigest()!=EXPECTED_GZIP_SHA256:
    raise SystemExit('LU1E gzip hash mismatch')
src=gzip.decompress(gz)
if len(src)!=EXPECTED_SOURCE_BYTES:
    raise SystemExit(f'LU1E source byte-count mismatch: {len(src)}')
if hashlib.sha256(src).hexdigest()!=EXPECTED_SOURCE_SHA256:
    raise SystemExit('LU1E source hash mismatch')
exec(compile(src,str(Path(__file__)),'exec'),globals(),globals())

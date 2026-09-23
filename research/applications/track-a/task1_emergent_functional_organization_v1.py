#!/usr/bin/env python3
import base64, gzip, hashlib
from pathlib import Path

HERE=Path(__file__).parent
STEM=Path(__file__).stem
PARTS=sorted(HERE.glob(STEM + '.source.chunk*.b64'))
EXPECTED_PARTS=8
EXPECTED_B64_CHARS=14676
EXPECTED_B64_SHA256='3195eb81f9de5759b0d569d5b20bf1c0c1846a6780385d0cd49c23ca88515cc3'
EXPECTED_GZIP_BYTES=11007
EXPECTED_GZIP_SHA256='bca4388ad5e5eaffe14e9a8c2a74e9590c8d027281681105931cb2fa734b4268'
EXPECTED_SOURCE_BYTES=37394
EXPECTED_SOURCE_SHA256='567c37e3e2171bc3cfc15b996c447e87b7ac5cdafb7bc299ba104284ae826e12'

if len(PARTS)!=EXPECTED_PARTS:
    raise SystemExit(f'TASK1 source part-count mismatch: {len(PARTS)}')
encoded=''.join(p.read_text(encoding='ascii').strip() for p in PARTS)
if len(encoded)!=EXPECTED_B64_CHARS:
    raise SystemExit(f'TASK1 base64 char-count mismatch: {len(encoded)}')
if hashlib.sha256(encoded.encode('ascii')).hexdigest()!=EXPECTED_B64_SHA256:
    raise SystemExit('TASK1 base64 hash mismatch')
gz=base64.b64decode(encoded,validate=True)
if len(gz)!=EXPECTED_GZIP_BYTES:
    raise SystemExit(f'TASK1 gzip byte-count mismatch: {len(gz)}')
if hashlib.sha256(gz).hexdigest()!=EXPECTED_GZIP_SHA256:
    raise SystemExit('TASK1 gzip hash mismatch')
src=gzip.decompress(gz)
if len(src)!=EXPECTED_SOURCE_BYTES:
    raise SystemExit(f'TASK1 source byte-count mismatch: {len(src)}')
if hashlib.sha256(src).hexdigest()!=EXPECTED_SOURCE_SHA256:
    raise SystemExit('TASK1 source hash mismatch')
exec(compile(src,str(Path(__file__)),'exec'),globals(),globals())

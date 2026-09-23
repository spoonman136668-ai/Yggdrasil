#!/usr/bin/env python3
import base64, gzip, hashlib
from pathlib import Path

HERE=Path(__file__).parent
STEM=Path(__file__).stem
PARTS=sorted(HERE.glob(STEM + '.source.chunk*.b64'))

EXPECTED_PARTS=4
EXPECTED_B64_CHARS=8176
EXPECTED_B64_SHA256='dbd3a1f9b8ca99a91276e3d9ed4bd66cb9f3b7a9185272b14648052836ec7767'
EXPECTED_GZIP_BYTES=6130
EXPECTED_GZIP_SHA256='4c22c2aea31961330d7324bde7209e01bda909fb640170c1c670337e75460649'
EXPECTED_SOURCE_BYTES=17518
EXPECTED_SOURCE_SHA256='c493e9353b98563139fafb8c5dd5a46b8152b780f6148b248c7e17f57f304700'

if len(PARTS)!=EXPECTED_PARTS:
    raise SystemExit(f'LU1A source part-count mismatch: {len(PARTS)}')
encoded=''.join(p.read_text(encoding='ascii').strip() for p in PARTS)
if len(encoded)!=EXPECTED_B64_CHARS:
    raise SystemExit(f'LU1A base64 char-count mismatch: {len(encoded)}')
if hashlib.sha256(encoded.encode('ascii')).hexdigest()!=EXPECTED_B64_SHA256:
    raise SystemExit('LU1A base64 hash mismatch')
gz=base64.b64decode(encoded,validate=True)
if len(gz)!=EXPECTED_GZIP_BYTES:
    raise SystemExit(f'LU1A gzip byte-count mismatch: {len(gz)}')
if hashlib.sha256(gz).hexdigest()!=EXPECTED_GZIP_SHA256:
    raise SystemExit('LU1A gzip hash mismatch')
src=gzip.decompress(gz)
if len(src)!=EXPECTED_SOURCE_BYTES:
    raise SystemExit(f'LU1A source byte-count mismatch: {len(src)}')
if hashlib.sha256(src).hexdigest()!=EXPECTED_SOURCE_SHA256:
    raise SystemExit('LU1A source hash mismatch')
exec(compile(src,str(Path(__file__)),'exec'),globals(),globals())

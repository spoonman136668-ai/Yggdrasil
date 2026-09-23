#!/usr/bin/env python3
import base64, gzip, hashlib
from pathlib import Path

HERE=Path(__file__).parent
STEM=Path(__file__).stem
PARTS=sorted(HERE.glob(STEM + '.source.chunk*.b64'))

EXPECTED_PARTS=5
EXPECTED_B64_CHARS=9760
EXPECTED_GZIP_BYTES=7320
EXPECTED_SOURCE_BYTES=27655
EXPECTED_SOURCE_SHA256='be2af2e8a496532122957011e15ebbaf83bf55004caadb3e61931a2ed85e555e'

if len(PARTS)!=EXPECTED_PARTS:
    raise SystemExit(f'LU2A source part-count mismatch: {len(PARTS)}')
encoded=''.join(p.read_text(encoding='ascii').strip() for p in PARTS)
if len(encoded)!=EXPECTED_B64_CHARS:
    raise SystemExit(f'LU2A base64 char-count mismatch: {len(encoded)}')
# Historical recovery chunks omit the two terminal '=' padding characters.
padded=encoded + ('=' * ((4 - len(encoded) % 4) % 4))
gz=base64.b64decode(padded,validate=True)
if len(gz)!=EXPECTED_GZIP_BYTES:
    raise SystemExit(f'LU2A gzip byte-count mismatch: {len(gz)}')
src=gzip.decompress(gz)
if len(src)!=EXPECTED_SOURCE_BYTES:
    raise SystemExit(f'LU2A source byte-count mismatch: {len(src)}')
if hashlib.sha256(src).hexdigest()!=EXPECTED_SOURCE_SHA256:
    raise SystemExit('LU2A source hash mismatch')
exec(compile(src,str(Path(__file__)),'exec'),globals(),globals())

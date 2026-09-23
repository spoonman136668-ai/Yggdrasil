#!/usr/bin/env python3
import base64, gzip, hashlib
from pathlib import Path

HERE=Path(__file__).parent
STEM=Path(__file__).stem
PARTS=sorted(HERE.glob(STEM + '.source.chunk*.b64'))

EXPECTED_PARTS=3
EXPECTED_B64_CHARS=4868
EXPECTED_B64_SHA256='6b2a61879f94ecfec63f708a800ec9a1b4bf11a66d72eecf778604e573cf7582'
EXPECTED_GZIP_BYTES=3650
EXPECTED_GZIP_SHA256='4cdcd93a3982d29f9fdef6e7735bad7caa9d0af6057af5865a7986ac7e8c6ebe'
EXPECTED_SOURCE_BYTES=12748
EXPECTED_SOURCE_SHA256='e8d409c5eb8e750123aae4979fd1091611a915c22f7cf977e420345186aef6b9'

if len(PARTS)!=EXPECTED_PARTS:
    raise SystemExit(f'TASK1B source part-count mismatch: {len(PARTS)}')
encoded=''.join(p.read_text(encoding='ascii').strip() for p in PARTS)
if len(encoded)!=EXPECTED_B64_CHARS:
    raise SystemExit(f'TASK1B base64 char-count mismatch: {len(encoded)}')
if hashlib.sha256(encoded.encode('ascii')).hexdigest()!=EXPECTED_B64_SHA256:
    raise SystemExit('TASK1B base64 hash mismatch')
gz=base64.b64decode(encoded,validate=True)
if len(gz)!=EXPECTED_GZIP_BYTES:
    raise SystemExit(f'TASK1B gzip byte-count mismatch: {len(gz)}')
if hashlib.sha256(gz).hexdigest()!=EXPECTED_GZIP_SHA256:
    raise SystemExit('TASK1B gzip hash mismatch')
src=gzip.decompress(gz)
if len(src)!=EXPECTED_SOURCE_BYTES:
    raise SystemExit(f'TASK1B source byte-count mismatch: {len(src)}')
if hashlib.sha256(src).hexdigest()!=EXPECTED_SOURCE_SHA256:
    raise SystemExit('TASK1B source hash mismatch')
exec(compile(src,str(Path(__file__)),'exec'),globals(),globals())

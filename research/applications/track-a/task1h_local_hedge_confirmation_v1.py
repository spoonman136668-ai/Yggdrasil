#!/usr/bin/env python3
import base64, gzip, hashlib
from pathlib import Path

HERE=Path(__file__).parent
STEM=Path(__file__).stem
PARTS=sorted(HERE.glob(STEM + '.source.chunk*.b64'))

EXPECTED_PARTS=3
EXPECTED_B64_CHARS=5784
EXPECTED_B64_SHA256='7875afd9e96adbfcb16502584c3d355ff9cbc6a936745b9bdfbbed8ae47d0750'
EXPECTED_GZIP_BYTES=4336
EXPECTED_GZIP_SHA256='6216d22a9bf789a984bf0bb295f07a7a15126de440000b120fcb01edcf3a9221'
EXPECTED_SOURCE_BYTES=15363
EXPECTED_SOURCE_SHA256='076e67aef313943fdcd5545ed8c888b6630431638bd158be4e705d81ebebe445'

if len(PARTS)!=EXPECTED_PARTS:
    raise SystemExit(f'TASK1H source part-count mismatch: {len(PARTS)}')
encoded=''.join(p.read_text(encoding='ascii').strip() for p in PARTS)
if len(encoded)!=EXPECTED_B64_CHARS:
    raise SystemExit(f'TASK1H base64 char-count mismatch: {len(encoded)}')
if hashlib.sha256(encoded.encode('ascii')).hexdigest()!=EXPECTED_B64_SHA256:
    raise SystemExit('TASK1H base64 hash mismatch')
gz=base64.b64decode(encoded,validate=True)
if len(gz)!=EXPECTED_GZIP_BYTES:
    raise SystemExit(f'TASK1H gzip byte-count mismatch: {len(gz)}')
if hashlib.sha256(gz).hexdigest()!=EXPECTED_GZIP_SHA256:
    raise SystemExit('TASK1H gzip hash mismatch')
src=gzip.decompress(gz)
if len(src)!=EXPECTED_SOURCE_BYTES:
    raise SystemExit(f'TASK1H source byte-count mismatch: {len(src)}')
if hashlib.sha256(src).hexdigest()!=EXPECTED_SOURCE_SHA256:
    raise SystemExit('TASK1H source hash mismatch')
exec(compile(src,str(Path(__file__)),'exec'),globals(),globals())

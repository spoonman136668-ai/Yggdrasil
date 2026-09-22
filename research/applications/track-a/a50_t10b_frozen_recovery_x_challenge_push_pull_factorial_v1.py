#!/usr/bin/env python3
import base64
import gzip
import hashlib
from pathlib import Path

HERE = Path(__file__).parent
STEM = Path(__file__).stem
PARTS = sorted(HERE.glob(STEM + '.source.part*.b64'))

if len(PARTS) != 7:
    raise SystemExit(f'A50 source part count mismatch: {len(PARTS)}')

EXPECTED_B64 = '0a1abef095bce7a0e68bafbfb5053579d6380b82ceaca6d07f73806f7ee1b413'
EXPECTED_GZIP = '219c92fd38ef3d23ad5dc37a6888b24aeb285a6c67236facbd30378122f02774'
EXPECTED_SOURCE = '9dcaacc649b24ecbd971589f769f27ab69ebbffa17607c07a8627e4726eaf720'

encoded = ''.join(''.join(p.read_text().split()) for p in PARTS)

got_b64 = hashlib.sha256(encoded.encode()).hexdigest()
if got_b64 != EXPECTED_B64:
    raise SystemExit(f'A50 source bundle hash mismatch: {got_b64}')

archive = base64.b64decode(encoded, validate=True)

got_gzip = hashlib.sha256(archive).hexdigest()
if got_gzip != EXPECTED_GZIP:
    raise SystemExit(f'A50 source archive hash mismatch: {got_gzip}')

src = gzip.decompress(archive)

got_source = hashlib.sha256(src).hexdigest()
if got_source != EXPECTED_SOURCE:
    raise SystemExit(f'A50 source hash mismatch: {got_source}')

exec(compile(src, str(Path(__file__)), 'exec'), globals(), globals())

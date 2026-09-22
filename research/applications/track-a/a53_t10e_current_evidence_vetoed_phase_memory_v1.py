#!/usr/bin/env python3
import base64
import gzip
import hashlib
from pathlib import Path

HERE = Path(__file__).parent
STEM = Path(__file__).stem
PARTS = sorted(HERE.glob(STEM + '.source.part*.b64'))

if len(PARTS) != 7:
    raise SystemExit(f'A53 source part count mismatch: {len(PARTS)}')

EXPECTED_B64 = '00995e97bc233f0e7ebea549a9308cb3a1a9f5bc19877e49e15638a0f068fa37'
EXPECTED_GZIP = 'a2a50019e3fce2394ddcd92a1e9ce794f1164ac8ed5cc7543e3d04e91ed07c6e'
EXPECTED_SOURCE = 'dd19ce7c9b5745087e28b7be965da83f45a876c732e8e1991d123dcf21604656'

encoded = ''.join(''.join(p.read_text().split()) for p in PARTS)
if hashlib.sha256(encoded.encode()).hexdigest() != EXPECTED_B64:
    raise SystemExit('A53 source bundle hash mismatch')

archive = base64.b64decode(encoded, validate=True)
if hashlib.sha256(archive).hexdigest() != EXPECTED_GZIP:
    raise SystemExit('A53 source archive hash mismatch')

src = gzip.decompress(archive)
if hashlib.sha256(src).hexdigest() != EXPECTED_SOURCE:
    raise SystemExit('A53 source hash mismatch')

exec(compile(src, str(Path(__file__)), 'exec'), globals(), globals())

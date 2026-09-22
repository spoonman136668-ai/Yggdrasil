#!/usr/bin/env python3
import base64
import gzip
import hashlib
from pathlib import Path

HERE = Path(__file__).parent
STEM = Path(__file__).stem
PARTS = sorted(HERE.glob(STEM + '.source.part*.b64'))

EXPECTED_PARTS = 7
EXPECTED_B64 = '2ccaa35afbbf97a127b8ce2789c9a589adcb08746cfb409a946db4bdc06ee08b'
EXPECTED_GZIP = 'afff3bb623f846181a37e5936c383b1991b37aa39d756a9b774b1fb52da10bb8'
EXPECTED_SOURCE = '8284fc44fbe2dd965c477ba845f92d44aefa85b802adfe1d672cf144fb45baee'

if len(PARTS) != EXPECTED_PARTS:
    raise SystemExit(f'A51 TTL source part count mismatch: {len(PARTS)}')

encoded = ''.join(''.join(p.read_text().split()) for p in PARTS)
if hashlib.sha256(encoded.encode()).hexdigest() != EXPECTED_B64:
    raise SystemExit('A51 TTL encoded source hash mismatch')

archive = base64.b64decode(encoded, validate=True)
if hashlib.sha256(archive).hexdigest() != EXPECTED_GZIP:
    raise SystemExit('A51 TTL source archive hash mismatch')

src = gzip.decompress(archive)
got = hashlib.sha256(src).hexdigest()
if got != EXPECTED_SOURCE:
    raise SystemExit(f'A51 TTL source hash mismatch: {got}')

exec(compile(src, str(Path(__file__)), 'exec'), globals(), globals())

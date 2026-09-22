#!/usr/bin/env python3
import base64
import gzip
import hashlib
from pathlib import Path

HERE = Path(__file__).parent
STEM = Path(__file__).stem
PARTS = sorted(HERE.glob(STEM + '.source.part*.b64'))

EXPECTED_PARTS = 7
EXPECTED_B64 = '49dba6fdeed19093684c97a78e6690fdec2276229bcdd649f76e0554c16f2892'
EXPECTED_GZIP = 'cbb20b48b21e6a6f7d2b47c5347ce4431d65c3202df0a8daa230472b805f2699'
EXPECTED_SOURCE = 'f1c2cfbd707621b18db101ea9a41f2264841acee10abcc5b80e4239c50ae60e1'
EXPECTED_SOURCE_BYTES = 92868

if len(PARTS) != EXPECTED_PARTS:
    raise SystemExit(f'A52 source part count mismatch: {len(PARTS)}')

encoded = ''.join(''.join(p.read_text().split()) for p in PARTS)
if hashlib.sha256(encoded.encode()).hexdigest() != EXPECTED_B64:
    raise SystemExit('A52 source bundle hash mismatch')

archive = base64.b64decode(encoded, validate=True)
if hashlib.sha256(archive).hexdigest() != EXPECTED_GZIP:
    raise SystemExit('A52 source archive hash mismatch')

src = gzip.decompress(archive)
if len(src) != EXPECTED_SOURCE_BYTES:
    raise SystemExit(f'A52 source byte count mismatch: {len(src)}')

got = hashlib.sha256(src).hexdigest()
if got != EXPECTED_SOURCE:
    raise SystemExit(f'A52 source hash mismatch: {got}')

exec(compile(src, str(Path(__file__)), 'exec'), globals(), globals())

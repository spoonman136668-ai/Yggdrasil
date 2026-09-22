#!/usr/bin/env python3
import base64
import gzip
import hashlib
from pathlib import Path

HERE = Path(__file__).parent
STEM = Path(__file__).stem
PARTS = sorted(HERE.glob(STEM + '.source.part*.b64'))

if len(PARTS) != 6:
    raise SystemExit(f'A46 source part count mismatch: {len(PARTS)}')

EXPECTED_B64 = 'b6edfab88e74753d5d32c113ccee30941ce3421f9a15dc38664d25e214479a5b'
EXPECTED_GZIP = '4e0d2b5ded1f71f55cf3e94652d52224c3bae10bfe9e308a6e101de44f4037f3'
EXPECTED_SOURCE = 'efee5637a1ba709b5299199489f02988517abc49392788b72ea25b295119fcec'

encoded = ''.join(''.join(p.read_text().split()) for p in PARTS)

got_b64 = hashlib.sha256(encoded.encode()).hexdigest()
if got_b64 != EXPECTED_B64:
    raise SystemExit(f'A46 source bundle hash mismatch: {got_b64}')

archive = base64.b64decode(encoded, validate=True)

got_gzip = hashlib.sha256(archive).hexdigest()
if got_gzip != EXPECTED_GZIP:
    raise SystemExit(f'A46 source archive hash mismatch: {got_gzip}')

src = gzip.decompress(archive)

got_source = hashlib.sha256(src).hexdigest()
if got_source != EXPECTED_SOURCE:
    raise SystemExit(f'A46 source hash mismatch: {got_source}')

exec(compile(src, str(Path(__file__)), 'exec'), globals(), globals())

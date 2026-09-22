#!/usr/bin/env python3
import base64
import gzip
import hashlib
from pathlib import Path

HERE = Path(__file__).parent
STEM = Path(__file__).stem
PARTS = sorted(HERE.glob(STEM + '.source.part*.b64'))

if len(PARTS) != 7:
    raise SystemExit(f'A47 source part count mismatch: {len(PARTS)}')

EXPECTED_B64 = '0adcbe11709f1c2ef733766ddfda96d77b865fe9430186123b7d5b7cdb631edc'
EXPECTED_GZIP = 'f92f632cc5f4ab9a04cefacb69a8d8b982d67e7bfb704bdd1c5e3dd0c33aee3b'
EXPECTED_SOURCE = '645b1d8b8417702fce62a6268b9ba97dd41aba21e8cb9f48ccf683f32fc6d468'

encoded = ''.join(''.join(p.read_text().split()) for p in PARTS)

got_b64 = hashlib.sha256(encoded.encode()).hexdigest()
if got_b64 != EXPECTED_B64:
    raise SystemExit(f'A47 source bundle hash mismatch: {got_b64}')

archive = base64.b64decode(encoded, validate=True)

got_gzip = hashlib.sha256(archive).hexdigest()
if got_gzip != EXPECTED_GZIP:
    raise SystemExit(f'A47 source archive hash mismatch: {got_gzip}')

src = gzip.decompress(archive)

got_source = hashlib.sha256(src).hexdigest()
if got_source != EXPECTED_SOURCE:
    raise SystemExit(f'A47 source hash mismatch: {got_source}')

exec(compile(src, str(Path(__file__)), 'exec'), globals(), globals())

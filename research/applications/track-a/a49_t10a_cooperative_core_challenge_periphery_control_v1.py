#!/usr/bin/env python3
import base64
import gzip
import hashlib
from pathlib import Path

HERE = Path(__file__).parent
STEM = Path(__file__).stem
PARTS = sorted(HERE.glob(STEM + '.source.part*.b64'))

if len(PARTS) != 7:
    raise SystemExit(f'A49 source part count mismatch: {len(PARTS)}')

EXPECTED_B64 = 'b2b006c1307788435d023d291c455f4b0c2c634e4f0332ac828c8c06d02fa702'
EXPECTED_GZIP = '76b428f85e1bb54887c4d27eff2e21e56ae409d534da724b28cedeb8d6fd2844'
EXPECTED_SOURCE = '2f605a412bdedf9a66607cf7c544be8c26e10d751f4e85557e17a9afd3b9f569'

encoded = ''.join(''.join(p.read_text().split()) for p in PARTS)
got_b64 = hashlib.sha256(encoded.encode()).hexdigest()
if got_b64 != EXPECTED_B64:
    raise SystemExit(f'A49 source bundle hash mismatch: {got_b64}')

archive = base64.b64decode(encoded, validate=True)
got_gzip = hashlib.sha256(archive).hexdigest()
if got_gzip != EXPECTED_GZIP:
    raise SystemExit(f'A49 source archive hash mismatch: {got_gzip}')

src = gzip.decompress(archive)
got_source = hashlib.sha256(src).hexdigest()
if got_source != EXPECTED_SOURCE:
    raise SystemExit(f'A49 source hash mismatch: {got_source}')

exec(compile(src, str(Path(__file__)), 'exec'), globals(), globals())

#!/usr/bin/env python3
import hashlib
from pathlib import Path

HERE = Path(__file__).parent
STEM = Path(__file__).stem
SOURCE = HERE / (STEM + '.source.py')

EXPECTED_SOURCE_BYTES = 92419
EXPECTED_SOURCE = 'dd19ce7c9b5745087e28b7be965da83f45a876c732e8e1991d123dcf21604656'

src = SOURCE.read_bytes()
if len(src) != EXPECTED_SOURCE_BYTES:
    raise SystemExit(f'A53 repaired source byte-count mismatch: {len(src)}')
if hashlib.sha256(src).hexdigest() != EXPECTED_SOURCE:
    raise SystemExit('A53 repaired source hash mismatch')

exec(compile(src, str(Path(__file__)), 'exec'), globals(), globals())

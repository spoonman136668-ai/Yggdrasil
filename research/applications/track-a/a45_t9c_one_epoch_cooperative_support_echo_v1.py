#!/usr/bin/env python3
import base64,gzip,hashlib
from pathlib import Path

HERE=Path(__file__).parent
STEM=Path(__file__).stem
PARTS=sorted(HERE.glob(STEM+'.payload.part*.b64'))

if len(PARTS)!=6:
    raise SystemExit(f'A45 payload part count mismatch: {len(PARTS)}')

EXPECTED_B64='ac8705be7cf1c1aac580a6474c97d6732ca1e627d5915616cc7d71ec1f840975'
EXPECTED_GZIP='09486353c0ac9fecae8d5572f764e5c3f8b3fd07cff5bb314fa5d325d5991cf6'
EXPECTED_SOURCE='fa444b98128857dcd7790d83e328b242c6069de980aa14828c21b8e45af6e240'

encoded=''.join(''.join(p.read_text().split()) for p in PARTS)
got_b64=hashlib.sha256(encoded.encode()).hexdigest()
if got_b64!=EXPECTED_B64:
    raise SystemExit(f'A45 base64 payload hash mismatch: {got_b64}')

gz=base64.b64decode(encoded,validate=True)
got_gzip=hashlib.sha256(gz).hexdigest()
if got_gzip!=EXPECTED_GZIP:
    raise SystemExit(f'A45 gzip payload hash mismatch: {got_gzip}')

src=gzip.decompress(gz)
got_source=hashlib.sha256(src).hexdigest()
if got_source!=EXPECTED_SOURCE:
    raise SystemExit(f'A45 source hash mismatch: {got_source}')

exec(compile(src,str(Path(__file__)),'exec'),globals(),globals())

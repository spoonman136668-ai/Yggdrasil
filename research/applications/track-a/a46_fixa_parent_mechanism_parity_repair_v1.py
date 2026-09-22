#!/usr/bin/env python3
import base64
import gzip
import hashlib
from pathlib import Path

HERE = Path(__file__).parent
BASE_STEM = 'a46_t9d_cooperative_confirmed_refractory_reentry_v1'
PARTS = sorted(HERE.glob(BASE_STEM + '.source.part*.b64'))

if len(PARTS) != 6:
    raise SystemExit(f'A46-FIXA source part count mismatch: {len(PARTS)}')

EXPECTED_B64 = 'b6edfab88e74753d5d32c113ccee30941ce3421f9a15dc38664d25e214479a5b'
EXPECTED_GZIP = '4e0d2b5ded1f71f55cf3e94652d52224c3bae10bfe9e308a6e101de44f4037f3'
EXPECTED_F46 = 'efee5637a1ba709b5299199489f02988517abc49392788b72ea25b295119fcec'
EXPECTED_F46A = '53d643ca7c1b17b9368abd60cae1666de7698dd3530795845250d2481767c885'

encoded = ''.join(''.join(p.read_text().split()) for p in PARTS)
if hashlib.sha256(encoded.encode()).hexdigest() != EXPECTED_B64:
    raise SystemExit('A46-FIXA source bundle hash mismatch')

archive = base64.b64decode(encoded, validate=True)
if hashlib.sha256(archive).hexdigest() != EXPECTED_GZIP:
    raise SystemExit('A46-FIXA source archive hash mismatch')

src = gzip.decompress(archive)
if hashlib.sha256(src).hexdigest() != EXPECTED_F46:
    raise SystemExit('A46-FIXA F46 source hash mismatch')

replacements = [
    (
        b"            elif kind=='ECHO_PHASE' and mode=='CHALLENGE':\n",
        b"            elif kind in ('ECHO_PHASE','G5_REENTRY') and mode=='CHALLENGE':\n",
    ),
    (
        b"            echo_specific=max(0.0, qcoop-q_raw) if kind in ('ECHO_MARGIN','ECHO_PHASE') else 0.0\n",
        b"            echo_specific=max(0.0, qcoop-q_raw) if kind in ('ECHO_MARGIN','ECHO_PHASE','G5_REENTRY') else 0.0\n",
    ),
    (
        b"            q_c_support=support_margin_field(states,bpre,lc_now,ls_now,i,'C',gated=(kind in ('PHASE_SWITCH','ECHO_PHASE')))\n",
        b"            q_c_support=support_margin_field(states,bpre,lc_now,ls_now,i,'C',gated=(kind in ('PHASE_SWITCH','ECHO_PHASE','G5_REENTRY')))\n",
    ),
    (
        b"            q_s_support=support_margin_field(states,bpre,lc_now,ls_now,i,'S',gated=(kind in ('PHASE_SWITCH','ECHO_PHASE')))\n",
        b"            q_s_support=support_margin_field(states,bpre,lc_now,ls_now,i,'S',gated=(kind in ('PHASE_SWITCH','ECHO_PHASE','G5_REENTRY')))\n",
    ),
    (
        b"            if kind in ('PHASE_SWITCH','ECHO_PHASE'):\n",
        b"            if kind in ('PHASE_SWITCH','ECHO_PHASE','G5_REENTRY'):\n",
    ),
]

for old, new in replacements:
    count = src.count(old)
    if count != 1:
        raise SystemExit(f'A46-FIXA repair target count mismatch: {count}')
    src = src.replace(old, new)

got = hashlib.sha256(src).hexdigest()
if got != EXPECTED_F46A:
    raise SystemExit(f'A46-FIXA repaired source hash mismatch: {got}')

exec(compile(src, str(Path(__file__)), 'exec'), globals(), globals())

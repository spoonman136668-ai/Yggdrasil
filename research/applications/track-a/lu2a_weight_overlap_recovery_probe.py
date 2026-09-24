#!/usr/bin/env python3
import base64, hashlib, json, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
EXPECTED_B64_LEN=74556
EXPECTED_B64_SHA='b9803bdfdd8dfc69c4a1f9d205f0f92083dc1c29ee0c08b98d15a3c45edb95d3'
EXPECTED_RAW_LEN=55917
EXPECTED_RAW_SHA='b1bc60b16ad9262cf1cb3e661084f55fd87ef809be0a46d7692e58e628c20023'

regs=[(HERE/f'lu2a_lu1e_canonical_weights.chunk0{i}.b64').read_text(encoding='ascii').strip() for i in range(4)]
A=''.join(regs)
S0=(HERE/'lu2a_lu1e_canonical_weights_small.chunk00.b64').read_text(encoding='ascii').strip()
S1=(HERE/'lu2a_lu1e_canonical_weights_small.chunk01.b64').read_text(encoding='ascii').strip()
need=EXPECTED_B64_LEN-len(A)
expected_overlap=len(S1)-need

def longest_suffix_prefix(a,b):
    n=min(len(a),len(b))
    for k in range(n,0,-1):
        if a[-k:]==b[:k]:
            return k
    return 0

ov=longest_suffix_prefix(A,S1)
candidate=A+S1[ov:]
row={
  'A_chars':len(A),'S0_chars':len(S0),'S1_chars':len(S1),
  'missing_chars':need,'expected_overlap':expected_overlap,'actual_overlap':ov,
  'overlap_exact_expected':ov==expected_overlap,
  'S0_position_in_A':A.find(S0),
  'candidate_chars':len(candidate),
  'candidate_b64_sha256':hashlib.sha256(candidate.encode('ascii')).hexdigest(),
}
if len(candidate)==EXPECTED_B64_LEN:
    raw=base64.b64decode(candidate,validate=True)
    row.update({
      'raw_bytes':len(raw),
      'raw_sha256':hashlib.sha256(raw).hexdigest(),
      'canonical':(
        hashlib.sha256(candidate.encode('ascii')).hexdigest()==EXPECTED_B64_SHA and
        len(raw)==EXPECTED_RAW_LEN and
        hashlib.sha256(raw).hexdigest()==EXPECTED_RAW_SHA
      )
    })
else:
    row['canonical']=False
if row['canonical']:
    tail=S1[ov:]
    row['recovered_tail_chars']=len(tail)
    row['recovered_tail_sha256']=hashlib.sha256(tail.encode('ascii')).hexdigest()
    row['recovered_tail']=tail
Path(sys.argv[1]).write_text(json.dumps(row,sort_keys=True,separators=(',',':')),encoding='utf-8')
if not row['canonical']:
    raise SystemExit('historical overlap reconstruction did not match canonical frozen weights')

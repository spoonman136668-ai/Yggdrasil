#!/usr/bin/env python3
import base64, hashlib, itertools, json, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
EXPECTED_B64_LEN=74556
EXPECTED_B64_SHA='b9803bdfdd8dfc69c4a1f9d205f0f92083dc1c29ee0c08b98d15a3c45edb95d3'
EXPECTED_RAW_LEN=55917
EXPECTED_RAW_SHA='b1bc60b16ad9262cf1cb3e661084f55fd87ef809be0a46d7692e58e628c20023'

def read(name):
    return (HERE/name).read_text(encoding='ascii').strip()

regs=[read(f'lu2a_lu1e_canonical_weights.chunk0{i}.b64') for i in range(4)]
small=[read('lu2a_lu1e_canonical_weights_small.chunk00.b64'),read('lu2a_lu1e_canonical_weights_small.chunk01.b64')]
A=''.join(regs); S=''.join(small)

def overlap(a,b):
    n=min(len(a),len(b))
    for k in range(n,0,-1):
        if a[-k:]==b[:k]: return k
    return 0

candidates={}
ov_as=overlap(A,S); ov_sa=overlap(S,A)
candidates['A_plus_S_overlap']=A+S[ov_as:]
candidates['S_plus_A_overlap']=S+A[ov_sa:]
need=EXPECTED_B64_LEN-len(A)
if 0<=need<=len(S):
    candidates['A_plus_S_tail']=A+S[-need:]
    candidates['A_plus_S_prefix']=A+S[:need]
need2=EXPECTED_B64_LEN-len(S)
if 0<=need2<=len(A):
    candidates['S_plus_A_tail']=S+A[-need2:]
    candidates['S_plus_A_prefix']=S+A[:need2]

out={'lengths':{'A':len(A),'S':len(S),'expected':EXPECTED_B64_LEN},
     'overlap':{'A_suffix_S_prefix':ov_as,'S_suffix_A_prefix':ov_sa},
     'small_in_A':[x in A for x in small],
     'A_in_S':A in S,
     'candidates':{}}
for name,enc in candidates.items():
    row={'len':len(enc),'b64_sha256':hashlib.sha256(enc.encode('ascii')).hexdigest()}
    if len(enc)==EXPECTED_B64_LEN:
        try:
            raw=base64.b64decode(enc,validate=True)
            row.update({'raw_len':len(raw),'raw_sha256':hashlib.sha256(raw).hexdigest(),
                        'canonical':len(raw)==EXPECTED_RAW_LEN and hashlib.sha256(raw).hexdigest()==EXPECTED_RAW_SHA and row['b64_sha256']==EXPECTED_B64_SHA})
        except Exception as e:
            row['decode_error']=repr(e)
    out['candidates'][name]=row

# If exact overlap reconstruction works, emit only the missing tail for a fifth canonical chunk.
winner=None
for name,row in out['candidates'].items():
    if row.get('canonical'):
        winner=name; break
out['winner']=winner
if winner=='A_plus_S_overlap':
    tail=S[ov_as:]
elif winner=='A_plus_S_tail':
    tail=S[-(EXPECTED_B64_LEN-len(A)):]
else:
    tail=None
if tail is not None:
    out['recovered_tail']={'chars':len(tail),'sha256':hashlib.sha256(tail.encode('ascii')).hexdigest(),'content':tail}
Path(sys.argv[1]).write_text(json.dumps(out,sort_keys=True,separators=(',',':')),encoding='utf-8')

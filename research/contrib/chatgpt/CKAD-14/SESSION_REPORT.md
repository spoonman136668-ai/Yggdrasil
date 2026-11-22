# CKAD14 — bounded sparse weight repair

SPARSE_NATIVE_REPAIR_DEVELOPMENT_SUPPORTED

This is a conventional mixed-integer training algorithm programming existing
native binary polynomial weights. It is not native superiority over the solver.
Each attempt uses384 existing fitting observations;128 calibration outcomes
are inspected only after fitting. The solver gets no degree/family label.
Only optimal, exactly checked weights with zero fitting/calibration error may
be adopted. Every failed/limited attempt remains preserved separately.

| Seed | Slot | Arm | Solver status | Eligible | Correct | Wrong | Abstained |
|---|---:|---|---:|---|---:|---:|---:|
| 101 | 12 | REAL | 0 | True | 1536 | 0 | 0 |
| 101 | 12 | SHUFFLED | 2 | False | 0 | 0 | 1536 |
| 101 | 13 | REAL | 0 | True | 1536 | 0 | 0 |
| 101 | 13 | SHUFFLED | 2 | False | 0 | 0 | 1536 |
| 202 | 12 | REAL | 0 | True | 1536 | 0 | 0 |
| 202 | 12 | SHUFFLED | 2 | False | 0 | 0 | 1536 |
| 202 | 13 | REAL | 0 | True | 1536 | 0 | 0 |
| 202 | 13 | SHUFFLED | 2 | False | 0 | 0 | 1536 |
| 303 | 12 | REAL | 0 | True | 1536 | 0 | 0 |
| 303 | 12 | SHUFFLED | 2 | False | 0 | 0 | 1536 |
| 303 | 13 | REAL | 0 | True | 1536 | 0 | 0 |
| 303 | 13 | SHUFFLED | 2 | False | 0 | 0 | 1536 |

Frozen gates: {'coverage': True, 'real_admission': True, 'retention': True, 'shuffled_denied': True, 'wrong': True}
Hard-query totals: {'abstained': 0, 'correct': 9216, 'incorrect': 0, 'questions': 9216}
Adopted repairs: 6/6.
All previous source constraints, stored property bytes, event history and
previously answered readouts are preserved. Failed repairs leave the entire
parent unchanged. The old CKAD13 states/results remain untouched.

The strongest conventional sparse program is the training compiler itself,
so no claim of superiority over it is possible. CKAD13 CART and independent
exact-hierarchy controls reuse the identical512 observed-input information.
No additional source outcome, simulator action, virgin seed, historical scan,
accepted-ref update, new controller or scheduler was performed.

This does not establish real-world causality, broad transfer, shared-weight
lifelong learning, autonomous discovery, or general intelligence.
Whole campaign Linux 41.439264s / Windows 45.578000s.
Solver cost, bounds and node counts remain in the platform-specific results.
A timeout is a failure of this bounded method, not a successful repair.
Runtime numeric readout and cold restoration require no SciPy solver import.

Source SHA: c7926726935e4ed5d2bb98835c3c9ede0394d39f
Prereg SHA: 736f6ccc08c9e688861bcb174752ac53eb8f9f6c
Stable result SHA256: 7cad1568a73f670eb008fb4afa84a2787a38926d06704877c7998ec16ea3c04e
Reproduce: `python -B research/contrib/chatgpt/CKAD-14/campaign.py --output-directory /tmp/ckad14`.
Independent audit: `python -B research/contrib/chatgpt/CKAD-14/independent_audit.py`.
Mandatory exact-final Linux/Windows root/NKR05 regression and independent raw/G29
qualification follow seal; completed CI/PR receipts determine engineering status.
SCIENTIFIC_PASS=false. DEPLOYMENT NONE. DRAFT/UNMERGED.

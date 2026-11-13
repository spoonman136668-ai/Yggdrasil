# WSP-58 — Early-budget active causal intervention frontier

## Prospective custody
- Frozen protocol committed **before implementation or outcomes**: `abe73363e03e1fd7dfd8815ae6a443e63041176` (`prereg.json`).
- Parent WSP57 source and constraint learner: `2f9e20406626fd6c06a14c8d9c3229e2f3b86076` (draft PR #948). WSP57's missed +10pp threshold is preserved as a negative, not retuned.
- 12 fresh `SELFTEST` worlds use seeds 2401–2412 in a separate WSP58 source SHA256 domain; same finite permutation **source distribution** as WSP57, **not** independent external physics.
- Evaluator-only `source.py` contains the hidden operation tables. Learners cannot import or read it, and never receive any uncharged query outcome.

## Matched-information design
- Active and uniformly random policies both reuse the **unchanged** WSP57 `SparsePermutationWriter` inference algorithm.
- Each arm receives 12 identical charged unary observations (only inputs 0/2/4 per operation), then 24 additional source-returned physical consequences for its own selected pair actions.
- Freeze checkpoints after **0, 4, 8, 12, 16, 24** pair interventions. At each checkpoint compare both arms on the **same common unqueried** queries; never score them on actions observed by either arm.
- **Primary gate fixed at 8 pair actions** (20 total charged actions/arm). Require active exact accuracy at least 35%, active-minus-random gain at least 10 percentage points, no confidently wrong predictions by either policy at that checkpoint, 12 complete worlds and cold restore parity. All other checkpoints are diagnostic and cannot rescue a missed primary gate.
- Report candidate counts, action ledger hashes, wall/CPU time, entropy selection overhead, memory including raw evidence, cold snapshot parity and tamper rejection.

## Limitations
- This tests whether *choosing informative experiences* helps early knowledge acquisition under a strong finite-permutation prior. It does not prove the method invents physical laws, learns natural language, outperforms independently trained neural or exhaustive symbolic controls, or approaches AGI.
- Whole-process compute includes entropy-selection overhead, which random selection avoids. Coverage gains cannot be described as efficiency wins without comparing this cost.
- Protected DEV/PRIMARY first use, merge, promotion, deployment, independent research-loop integration and scheduled jobs remain excluded. Reuse GitHub's existing qualified runners only.
- Focused Linux/Windows SELFTEST and mandatory full final regression plus G29 source atlas are independently tracked; a negative scientific/SELFTEST result can still have passing engineering checks.

## Reproduce the frozen SELFTEST
```sh
python -m unittest discover -s research/contrib/chatgpt/WSP-58 -p 'test_*.py' -v
```

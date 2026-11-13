# WSP-68 — Direct neural weight-space learning without symbolic compilation

## Immutable prospective record
- Preregistration committed **before new experimental source, learner and test code**, SHA `cc76e2a26585ae91fb1d925e0bb22bad0a2873d2`, file `prereg.json`.
- Parent [WSP67 draft PR #959](https://github.com/spoonman136668-ai/Yggdrasil/pull/959), exact source `d1e4ece8700973ae9a6302e1b7c5ef72d2fdb6bb`. Prior result: 405/512 physical predictions, 97 unseen, zero confident errors, Stage B neural weights changed in 7/8 worlds, no forgetting; **independent symbolic control tied**, 8/8 gradient baseline convergence criteria failed. This positive exploratory result is *not* independent neural superiority and remains unchanged.
- WSP67's neural matrix generator compiled a known, source-aligned symbolic hypothesis family into ReLU logic circuits. This successor instead **edits actual neural readout weights after each charged physical experience**, without any symbolic rule enumeration or source-specific conditional logic in the learner.

## New source worlds and learning
- Twelve new SELFTEST-only worlds, seeds **4201–4212**: four XOR/parity-conditional sources, four three-input AND-gated sources, four mixed parity/negation/conjunction with coupled output effects. Unknown shuffled sensor and action roles. These are **synthetic binary sources**, deliberately including effects outside WSP67's one-conjunction-per-output hypothesis grammar.
- One source-blind seed-hashed random policy supplies all learning arms the **same 96 charged consecutive physical actions** from the single zero-state start, with **Stage A after 48** and Stage B after another 48. No training resets, arbitrary physical source queries, heldout labels or private physics access.
- The neural architecture is **eight inputs (four visible bits + four public action one-hots), 32 fixed source-independent random ReLU neurons, 8 skip connections and bias, four continuous output neurons**. This produces a 41-dimensional learned neural readout. A deterministic seed `68182026` fixes the hidden feature weights identically in every world. Hidden-layer features are NOT adapted during the test.
- The readout starts at zero and is **directly modified by one rank-one Sherman–Morrison/recursive-ridge edit per observed action consequence**. Lambda = 0.5; covariance starts at `2I`. No gradients, no source-derived rule compiler, no symbolic candidates or memory lookup at neural inference.
- At inference the cold-restored network uses its learned real-valued neural output matrices and a numeric learned inverse-covariance confidence screen. It abstains if any sensor output margin to 0.5 is below **0.27** or learned feature leverage exceeds **2.0**; raw forced predictions are reported separately. These confidence conditions are heuristic and carry **no mathematical guarantee of safety**.
- Serialize only fixed hidden feature weights, directly edited output weights and covariance; **no physical ledger or symbolic table** is needed to predict. Cold restoration, numerical parameter changes, changed/nonzero coefficients, and previous correct/confident case retention are audited.

## The matched independent controls
- **Independently optimized conventional supervised neural readout**: `independent_batch.py` implements the *same* frozen random feature architecture independently, trains the output weights by exact regularized normal equations using **Cholesky**, and reports objective stationarity `|| (lambda I + XᵀX)W − XᵀY ||∞`. It must attain residual ≤1e-7; the online direct editor must match its weights within 2e-6. This is a **fully converged FIXED-FEATURE neural readout**, not an end-to-end trained MLP. It is expected to tie in numerical optimum, so parity would verify engineering correctness, not superior intelligence.
- **Exact same-history observation memory** from WSP67, for actual test state/action lookups and two-action tasks.
- **Independent fully fitted depth-bounded binary decision tree** from WSP64, given the same 96 charged observations. It may generalize more or less accurately and may make unsafe confident guesses.
- Frozen WSP67 prior symbolic hypothesis compiler run as an **out-of-class rejection diagnostic**, never used to build WSP68 weights or to overstate relative superiority.
- No trained end-to-end neural MLP is yet scientifically qualified. WSP67's previous SGD baseline failed its convergence requirement and is **not evidence that online editing beats trained neural networks**. This important baseline deficiency remains open.

## Frozen test and objective
- Exhaustive 12 × 16 visible states × 4 actions = **768 physical consequences**, explicitly distinguishing charged-and-seen state/actions from **genuinely unseen** input/action pairs.
- Separately 12 × 32 = **384 independently evaluator-selected two-action compositions**, scoring whether both sequential neural predictions were confident and the final physical consequence exactly matched source.
- The frozen prospective `SELFTEST_SIGNAL` requires **>=40 correct confident truly unseen physical predictions**, **>=160 confident correct all-domain**, **>=25 more than exact same-history memory**, **<=16 wrong-confident physical predictions**, **>=96/384 exact confident two-action compositions**, **>=90% retention** of Stage A previously confident and correct physical cases, nonzero actual neural parameter changes in **>=10/12 worlds**, all 12 cold matrix-only restore/tamper checks, and independent batch ridge optimum/parity within frozen numerical tolerances.
- Miss *any* gate: preserve `SELFTEST_NEGATIVE_OR_INCONCLUSIVE`; do not tune the confidence cutoff, source, feature bank, seeds or thresholds after looking at results. The independent symbolic and decision-tree controls' accuracy must still be reported.
- Runtime/CPU, full matrix and covariance bytes, every cold hash, source/composition SHA256 and charged action ledger SHA256 recorded; parity between Linux and Windows required for frozen scientific counts.

## Boundaries
- This is an **explicit fixed-feature representation**. There is no automatically discovered hidden layer, symbolic/language knowledge, unknown-world exploration advantage, open-world general intelligence or independent SCIENTIFIC_PASS. Direct weight updates may be mathematically equivalent to batch supervised training on the same feature architecture, which is a stringent parity check rather than a novel superiority proof.
- SELFTEST only. No protected DEV/PRIMARY scientific first-use, merge, promotion, deployment, scheduled task, official FORGE/Yggdrasil loop modification, runner change, paid API or new controller.

## Reproduce
```sh
python -m unittest discover -s research/contrib/chatgpt/WSP-68 -p 'test_*.py' -v
```

The exact-source focused Linux/Windows suite, source-only generated G29 and full inherited two-platform regression must all finish before claiming final engineering qualification.
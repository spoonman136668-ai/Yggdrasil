# DG1-HC04 — uncertainty-aware causal microprogram version spaces

**Purpose:** Address HC03's out-of-family 128 confidently wrong predictions
by keeping several small causal hypotheses alive until physical evidence
eliminates the alternatives. This is **non-token, no-gradient, source-only DEV**.
It is neither an AGI proof nor evidence that the model has learned a general
program grammar.

**Frozen preregistration:** `d7a8199d92b7b6a8d84e0b689aa9455e6528a545`.
**Source parent:** HC03 exact accepted-engineering draft
`f26efd4c01a3344f12ba2ec9bf8582aa25b99dfa`.
The predecessor's source, frozen evaluation, negative results, and PR #964
remain unchanged. The native main runtime and parallel WSP editing are untouched.

## Unconventional mechanism

Each of two bounded hypothesis cells contains four local action-program masks
over the four fixed forms
`effect = left_bit XOR right_bit XOR (own_bit & slope) XOR offset`.
`slope` and `offset` are learned by elimination from the real physical
transition `(before, action, after)`, not from task labels. A conflicting
observation can create a second cell or reactivate a previously compatible one.
When viable programs predict different outcomes, the model explicitly declines
to predict. Its 32 **logical mask bits** exclude runtime bookkeeping/heap;
actual memory/time are recorded separately. Program grammar and the four-bit
physical state are *pre-specified*, not discovered.

## Exact frozen DEV challenges

* Four parity A→B→A worlds 22101–22104, 16+8+1 contiguous actions each,
  25 total. **DEV pass only if 0 confidently wrong and at least 16 correct of
  64 state/action predictions per seed**, cold restore exact.
* Four *own-bit-dependent* static worlds 22105–22108, 16 contiguous actions
  each. **DEV pass only if 0 confidently wrong and at least 32 correct of 64
  predictions per seed**, cold restore exact. HC03's own-bit negative is the
  known mechanistic target, not a discovery claim.
* Four **AND-neighbor** worlds 22109–22112 deliberately outside the fixed
  hypothesis class. All confident errors are preserved as safety failures,
  with no post-result reclassification.
* All predictions are audited *after* physically acquired public actions
  using evaluator-only 16 states × four actions. No learner sees hidden signs,
  true world labels, counterfactual oracle calls, heldout answers, or phase IDs.
  Abstentions are charged as uncovered predictions.

Controls include unchanged HC03 with the *same charged observations*, a
single-bank same-grammar learner, two-bank no-reactivation ablation,
same-ledger exact lookup, an ungated always-choose-one hypothesis control, and
a conventionally named implementation of precisely the same version-space
algorithm. Ties with the conventional method mean **no superiority**.

Reproduce from the repository root:

```sh
python -m unittest discover -s research/contrib/chatgpt/dg1-hc04-20261113 -p "test_*.py" -v
python research/contrib/chatgpt/dg1-hc04-20261113/eval_dev.py
python -m unittest discover -s tests -p "test_*.py" -v
python scripts/build_code_atlas.py --check-if-present
```

Exact-source G29 atlas and final dual-platform regression are mandatory.
A convincing *mechanistic DEV* result is not SCIENTIFIC_PASS. No adoption into
Yggdrasil's actual runtime unless a separately frozen, independently qualified
original/unfamiliar-world comparison against a genuinely strong conventional
control finds retained advantage at matched compute, information and actions.
No controller/scheduler, paid API, protected first-use, or merge permission is
exercised here.

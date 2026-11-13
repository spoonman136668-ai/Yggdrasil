# DG1-HC03 — contradiction-triggered causal-program society

## Hypothesis

Could Yggdrasil learn and later *reactivate* an executable causal microprogram
from public action consequences, without needing explicit task-boundary labels
or gradient descent? In this initial source-only DEV experiment, two bounded
hypothesis cells differentiate when the active cell's learned causal prediction
is contradicted and subsequently reactivate a previously acquired compatible
cell. A cell remembers **four signed local action programs**, not a global
lookup table of individual state/action experiences.

**Source parent:** Yggdrasil `main` at
`5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`.
**Frozen preregistration:** `4858a5269c2e8ec3a4ff4fb3b7f63f576acf0f8d`
committed before implementation or evaluation.
**Prior:** DG1-MC01 #958 INVALID_DEV, DG1-NCM02 #961 engineering-qualified
but scientific superiority unverified. The WSP weight-editing line #954
is independent and untouched.

## Mechanism

A program is one bit per action expressing a **provided** structural hypothesis:
`flip(action_bit) = left_bit XOR right_bit XOR learned_sign[action]`.
An actual public physical transition identifies a sign for that action.
A contradiction with the active cell's previous sign differentiates a new cell
(if there is capacity) or reactivates a compatible retained cell. The learner
never receives the phase label, hidden sign table, task type, seed or source
oracle. All learning is from a contiguous charged action sequence.

**Important limitations:** The ring topology, affected bit and XOR form are
*hardcoded priors*. The model does not invent these variables, discover causal
graph topology or autonomously build a general program grammar. There are
two banks, four action programs per bank, fixed 16 logical rule bits, and a
bounded integrity-authenticated checkpoint. Actual Python heap/compute cost
is measured separately. No novel general intelligence is claimed.

## Frozen evaluation

- Eight fixed in-family seeds 12101–12108.
- A=16, B=8, return-to-A=1 public action, without a state reset, state
  teleport, model-label input or hidden dataset reading. B is the explicit
  complement of all four of A's sign bits.
- After the 25th public action, evaluator-only exhaustive 16x4 physical
  transition audit; no training or oracle feedback on evaluation queries.
- Controls: single bank reinitialized on contradiction; two banks with
  reactivation disabled; exact last-seen state/action table on same physical
  ledger; unfair two-bank conventional symbolic upper bound supplied with
  the source's regime labels. An equal-capacity symbolic switch detector
  could implement the same algorithm; this study makes no superiority claim
  over that legitimate control.
- Four distinct out-of-family negative seeds 12109–12112 with an additional
  *own-state-bit* dependence excluded from the learner's XOR context prior.
  Confidently wrong physical predictions are explicitly counted, not hidden.
- Frozen DEV_SIGNAL criterion: all eight return-A worlds >=60/64 exact,
  zero confident in-family errors, exact checkpoint restoration and >=1
  reactivation, and mean candidate exact accuracy at least 0.40 greater than
  the same-prior single-bank reset. Any failed criterion is a DEV negative.
  **Even a DEV_SIGNAL is not SCIENTIFIC_PASS.**

## Local reproduction

From the experiment directory:

```sh
python -m unittest discover -s . -p 'test_*.py' -v
python eval_dev.py > result.json
```

GitHub Actions additionally runs the same source-only tests, original native
cell regressions, inherited full regression and the exact-SHA G29 source atlas
on both Windows and Ubuntu. Until those checks pass on the *final candidate
SHA* and stronger matched two-expert conventional comparators and genuinely
novel worlds are independently run, this is isolated developmental research.

**No main merge, no original runtime change, no protected scientific first-use,
no paid APIs, no controller/runner/scheduler changes, no owner acceptance,
no weight-editing mutation.**

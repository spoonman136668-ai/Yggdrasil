# WSP-84 — Construct an unknown three-input causal operator in weights

**Developer-only; PR #982 remains draft and unmerged.** This extends
WSP-83's finite two-atom XOR composition to a source which cannot be
represented by any two-atom XOR from the old library.

## Prospective frozen custody

The new source, learner, training control, tests and outcomes were NOT
present when the researcher preregistered the protocol in standalone
commit \`5f6cef2e6d39f14cb411c2b046557fb6415fe776\`, Git blob
\`5da5a2409842e7cbce27468b2b44a5de1b907607\`.
That commit's parent is the qualified WSP-83 SHA
\`e75acd73e203dafc571a0aaec24d9775e9afe03d\`.
The original registered WSP-80 scientific seeds 5601–5616,
source and thresholds remain untouched and unconsumed.

## Source and mechanism

\`source.py\` models four distinct **unregistered** development worlds:
10011, 10012 hidden three-input causal-operator families; 10013, 10014
memoryless controls. The private rule combines three unknown 3-of-6
action-membership signals from the current action and last two
historical actions. The source's private operator and output target
are NOT available to any learner or control. Every world has exactly
one physically paid 384-action continuous no-reset session, 1,536 total.

The numeric learner receives a generic collection of **60 candidate
balanced three-out-of-six input partition atoms** (20 masks for each of
three action-history positions), but **is not given the private Boolean
operator**. It constructs the complete truth table of a compact
support of 0..3 candidate inputs from the 384 public observation
residuals and requires *every* relevant truth-table cell to have been
physically observed. Unidentifiable functions do not gain invented
truth values; compatible alternative programs abstain if they disagree.
The learned truth table and masks become numerical ReLU minterm
weights, compiled and cold-restored for inference without history
search or evaluator access.

Strong controls: independent exact-expressivity symbolic operator
learner (separate code, expected tie), original *unmodified* WSP-83
two-XOR numeric compiler, fixed action-toggle control, exact paid
lookup, and a genuine **25→64 ReLU→6 sigmoid conventional Adam**
history-aware neural network. The Adam baseline inherits 3
restarts and at most 6000 gradient steps/restart from the prior
qualified WSP-82 training implementation, uses the same 384
physically paid rows and must report convergence honestly.

Unit tests use synthetic **parity and majority** sources unrelated
to the frozen four-world cohort to verify that the learner induces
different input truth tables instead of hardcoding an operator.
The actual four-world experiment runs once on pinned exact-source
CI in Ubuntu/Windows, scoring 43 fixed past-action contexts × 64
visible states × 6 actions × 4 worlds = **66,048 private evaluator
queries after all source-blind predictions have been SHA256-frozen**.
A descriptive, zero-shot cross-world transfer arm is preserved
without a pass threshold so a transfer failure cannot be hidden.

## Interpretation and authority

Even if all development thresholds pass, this is **bounded Boolean
truth-table induction**, not unconstrained invention of new sensors,
operators or architectures. The researcher supplied input
partition candidates, a three-variable table representation, and a
ReLU compiler. A tie against the independent symbolic solver cannot
prove neural weight programming has greater intelligence.
No general intelligence/AGI, open-domain transfer, language ability,
long-term retention or scientific acceptance is claimed.

No protected first-use, merge, controller/runtime/official-loop
changes, deployment, paid API, scheduled task, new runner, or user
Library artifact is authorized. Negative outcomes and qualified
cross-platform logs stay in GitHub.

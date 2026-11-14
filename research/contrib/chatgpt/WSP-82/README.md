# WSP-82 — New temporal causal feature induction (DEVELOPMENT ONLY)

**Objective:** Falsify the earlier WSP81 finite 31-mechanism success on
a different causal grammar. Current weight-programming work must learn a
previously unseen temporal relationship rather than reuse its specific
two-mode trigger/offset hypothesis library.

## Frozen protocol and admission

\`prereg.json\` was committed first at
\`4bff9a0d576e04d8123a902545680d2b78e176da\` with Git blob
\`4c16e604593f6c1c556512327942e0626ff3ddfb\`, before the new
source, learner, comparison and results. The four seeds 9701–9704
are entirely unregistered. The WSP80 5601–5616 protected scientific
cohort is NOT used or authorized. Existing WSP79/80/81 sources and
research baselines are preserved unchanged.

Source rule is separate and evaluator private. A public state/action pair
can differ depending on whether the immediately preceding TWO actions
were equal. The generic learner does **not** contain the private rule,
secret offset, or WSP81's 31-member hypothesis class.

## Development mechanisms and fair controls

- \`source.py\`: no-reset physically paid simulator (384 continuous actions
  per world) with new history-dependent rule and memoryless negatives.
- \`temporal_weights.py\`: source-blind numerical weight compiler. It
  constructs a general bank of lagged Boolean predicates and ReLU gates,
  selects minimum-complexity features that explain PAID public residuals,
  writes 0/1 weights, and cold restores. No online gradients used.
- \`independent_symbolic.py\`: separately implemented equally expressive
  symbolic solver with the same generic feature basis. An exact tie
  is expected and must be reported.
- \`history_adam.py\`: a *genuine* conventional fully learned MLP with
  25 inputs including 2 preceding action one-hots and an equality flag,
  32 hidden ReLU units, 6 sigmoid outputs. It inherits exact 3-restart
  Adam optimizer and 6000-step ceiling from unchanged WSP77
  \`fully_trained_mlp6.py\` (blob
  \`90bca703948c71e482892d2be830682201342368\`).
  Nonconvergence is reported explicitly.
- \`experiment.py\`: same 384 physical actions for all learners/world,
  original WSP81 mechanism rejection, paid history memorizer, simple
  memoryless control, all forced/native neural readouts, frozen
  SHA256-bound 1536 public state/action/history predictions per world
  BEFORE evaluator-private truth. The same complete source and model
  results must reproduce on Ubuntu/Windows.
- \`test_temporal.py\`: zero-cohort synthetic fixtures, model cold
  parity, no-paid/overbudget and tamper refusal, original WSP81
  incompatibility, source-custody and frozen-negative tests.
- Two workflows: dual-OS developer tests and exact-commit
  one-shot frozen developer experiment, all GitHub logs only.

## Boundaries

The public sensor state remains only 6 bits and the rule family was
designed by the researcher. Although the source law is NOT one of
WSP81's hand-enumerated hypotheses, the learner's generic basis includes
lagged equality and action conjunctions as possible building blocks.
Therefore the experiment tests bounded **feature induction**, not
true open-ended invention of unknown feature primitives or AGI.
It does not qualify unfamiliar-world transfer, broad skills, autonomous
research or learned language. A recurrent neural baseline may converge;
only compare its measured results and training status. No scientific
SELFTEST source/first-use, owner controller, scheduling, merge or
deployment is authorized.

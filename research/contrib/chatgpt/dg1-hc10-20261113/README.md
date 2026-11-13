# DG1-HC10 — Can physical probes identify which retained causal world is active?

## Scope and preregistration

This is an external, source-only Yggdrasil mechanism falsification. Frozen
preregistration `3781294c45a9e0e271afcfa036bc2afe8577ad27` precedes all
HC10 implementation or outcomes. The exact parent is engineering-qualified
HC09 draft PR #976 at `5913b9904f361f17216d931361baedeae5f65548`.

HC09 could learn affine and predefined nonlinear-majority causal programs,
but its two banks did **not** solve unlabeled A→B→A changes (68/512 final
correct, 32 confidently wrong, 412 abstentions). HC10 leaves that learned
model and context update **exactly unchanged** and asks whether physically
informative actions alone make its stored contexts identifiable.

## Frozen mechanism and conventional comparisons

A pure new policy reads each existing HC09 bank's public-facing causal-rule
version-space mask. When two banks exist, it chooses a physically executable
mechanism action that maximizes the absolute difference between their
predicted probabilities of a changed bit. If no action at the current state
can distinguish the banks, it can spend one **actually charged**
`do(flip public bit j)` to visit a state with maximal potential
interbank disagreement. If one bank exists or no distinction can be made,
it falls back to HC09's unchanged within-bank action selection.

The conventional comparator uses HC09's **separately written**
`ConventionalContextModel`, with exactly the same two 40-rule-per-action
banks and fixed **320 logical mask bits**. Its separately implemented action
choice scores Jensen–Shannon divergence of the two possible outcome
distributions. It has identical physical action, budget, memory and input
access. Equivalent performance counts as an ordinary conventional tie, not
a novel intelligence advantage.

Further controls: unmodified HC09 bank selector, equal-capacity no-bank-
reactivation ablation, smaller 160-bit single bank and fixed-schedule
physical interventions. Models see **only real public state/action/next
state**; neither evaluator labels nor phase boundaries are exposed.

## Frozen environments and success criteria

Three disjoint cohorts of eight new synthetic worlds each:

- A→B→A seeds **81001–81008**: 16 A, 16 hidden B, eight return-to-A
  physical steps = **40 charged steps** per model (maximum eight forced
  flips). Evaluator-only 64 possible state/action audits at step 16, 32
  and 40; **no audit answers become model training**. The preregistered
  final-A success criterion is at least **160 correct/512**, at least
  **64 correct/512 above original HC09**, and **zero confident errors**.
- Stable three-bit majority **81009–81016**: 48 charged steps per model,
  maximum eight forced flips; need ≥384/512 correct, zero wrong-confident
  to avoid degrading earlier useful fit.
- Outside-the-grammar cubic **81017–81024**: 48 charged steps, eight
  flip cap. Count *all* confidently wrong predictions. Any such error
  is negative source evidence, even if other cohorts improve.

Each source starts at physical state `seed%16`. A causal action
actually executes the hidden physics and charges one physical step;
an external bit flip also charges one but yields **no causal model update**.
All controllers follow independent uninterrupted trajectories.
No free simulator oracle, arbitrary-state training visit, hidden phase
label, model API, tokenization or gradient training.

Accuracy is **correct / confidently wrong / abstained** on 16 states ×4
actions, with a separate never-trained-state/action subset. Trace the
physical action receipts, bank switches, cold checkpoint identity,
actual wall time/peak heap, and conventional equal-capacity comparison.
Action count equality is **not** whole-process compute equality.

## Boundaries and reproduction

The rule grammar and synthetic data are hand-specified. Passing HC10 DEV
would not demonstrate general intelligence, spontaneous rule discovery,
real-world transfer, safe context handling, or superiority to conventional
hidden-state models. A failed return-to-A criterion is a retained
**scientific negative**, not an infrastructure failure.

```sh
python -m unittest discover -s research/contrib/chatgpt/dg1-hc10-20261113 -p 'test_*.py' -v
python research/contrib/chatgpt/dg1-hc10-20261113/eval_dev.py
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/build_code_atlas.py --check-if-present
```

Qualification must cover both Linux and Windows at the **final exact
source SHA** and regenerated source-pinned G29 atlas. Remain on an
isolated draft research branch: no native model integration, Yggdrasil
`main`, FORGE controller, scheduler, protected original science,
paid APIs or independent WSP weight-programming edits.

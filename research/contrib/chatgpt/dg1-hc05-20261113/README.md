# DG1-HC05 — counterfactual intervention value, without oracle access

A source-only Yggdrasil substrate successor testing whether **choosing informative
physical actions**, rather than just reacting to contradictions, can make
bounded causal programs more efficient. This is *not* native runtime
integration or a declaration of scientific success.

**Preregistration:** `d856b93ecf3428c89662e476eb070b78a62f1dbd`,
committed before implementation/evaluation. Parent is HC04's exact final
`aa212b993b00fa752b7f12dbc9eb9384ce9d8a2e`, whose **MIXED_DEV**,
parity retention failure and 72 out-of-class confident errors remain immutable.
The mechanism does not repair HC04's lost A/B/A memory; HC05 tests stationary
causal identification and probe choice.

## Mechanism and falsifiable prediction

Four public binary sites; four physical actions. Each action may follow any
of six fixed local causal formulas: two-neighbor parity, parity plus own bit,
or neighbor AND, each with one unknown XOR sign. The learner tracks a fixed
6-bit surviving-hypothesis mask per action, for **24 logical hypothesis bits**.
Each *real* public action and observed consequence eliminates incompatible
rules. When remaining hypotheses disagree on a hypothetical outcome, the
learner abstains. No learning occurs during readout or planning.

The unusual element is a two-step *belief-space intervention planner*.
For each currently possible first action, it computes its expected information
gain using only its **own hypothesis masks**, then computes the expected
best information gain of one hypothetical subsequent action under the
resulting posterior and possible public next state. This second action
is **never physically executed for free**; at the next time step a new
real intervention is selected and charged. The policy commits exactly
12 physical actions per seed.

## Frozen comparisons

- **Stationary mixed laws:** 8 previously unused source-only seeds
  31001–31008, with independent law families/signs per action.
- **Routing test:** 4 seeds 31009–31012, identical sampling protocol, to
  test whether two-step lookahead outperforms one-step greedy.
- **Deliberate negative:** 4 seeds 31013–31016 with majority-of-three-bit
  physics outside the hypothesis class.
- Each controller starts in the identical physical state and receives
  **12 charged physical interventions**. Their histories may differ naturally,
  and their ledger hashes/costs are recorded. No arbitrary-state training
  requests, resets, counterfactual training, evaluator oracle access, or
  world labels are permitted.
- Comparators: one-step information-gain greedy, round-robin, seeded random,
  and an algorithmically equivalent conventional symbolic two-step planner.
  The conventional planner is expected to **tie**; this is not proof that
  the method beats established active learning.
- After learning, evaluator-only exhaustive 16x4 next-state tests are run.
  Correct, confidently wrong, abstained, and unseen-history results all
  count separately. Timing, tracemalloc and checkpoint bytes are reported.

The frozen development gate requires the lookahead candidate to have zero
in-grammar confidently wrong outcomes and exceed the stronger of greedy and
round-robin by **at least 4/64 mean exact physical predictions** on the
stationary seeds, and beat greedy by at least **2/64** on routing seeds.
Out-of-grammar errors remain explicit failures. No threshold or seed changes
after running. Even a passing synthetic DEV is not `SCIENTIFIC_PASS`.

## Reproduce in the checked-out source tree

```sh
python -m unittest discover -s research/contrib/chatgpt/dg1-hc05-20261113 -p 'test_*.py' -v
python research/contrib/chatgpt/dg1-hc05-20261113/eval_dev.py
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/build_code_atlas.py --check-if-present
```

A final qualification requires exact-SHA source-atlas regeneration,
cross-platform focused tests, inherited regression and cold restore.
Any model benefit requires further **independent physical worlds, matched
conventional controls and full action + planning compute accounting** before
considering native-model promotion. No accepted-ref/controller/scheduler
changes, no paid API, no protected first use, and no edits to the separate WSP
weight-programming line.

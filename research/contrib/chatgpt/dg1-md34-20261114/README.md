# DG1-MD34 — Partial-Observation Consequential Causal Routes

**Purpose:** Make the causal task genuinely harder *before* adding another
unconventional learning rule to Yggdrasil. This is a separate, research-only
**physics benchmark**, not a model, training result, native Yggdrasil update,
or official scientific first-use.

## What changed from MD32

MD32's strong hand-coded reference could solve every episode simply by
paying two probes, reading both complete intermediate mechanism outputs,
and choosing the right final action. Its apparent reward gap to the
privileged oracle mostly measured the cost of those probes, rather than
unfamiliar causal reasoning.

MD34 deliberately removes that shortcut. It gives an agent three
**irreversible physical decisions** and at most **one diagnostic for the
entire episode**. A diagnostic costs 0.09 reward and returns **one
binary bit**, never the full four-way answer. The agent must choose a
context-specific precursor; select one of two consequential causal
routes; and choose the correct final outcome among four alternatives.
The right answer depends on a hidden encoder, a route-specific
intermediate mechanism and a hidden decoder. Decoder structure may
change without an announcement after the route is committed.

Every four successive episodes share the same hidden causal law and
structural-change status but vary the required precursor context.
Only repeated paid action consequences permit building knowledge about
the law. No source graph, seed, offset, rewire flag, latent state,
counterfactual answer, or terminal target can enter a public policy.

## Immutable design before implementation

- Source parent: `ba1ba1fc56a42e41913e6ecfaf2ab1f68de2642c`,
  the fully qualified, but scientifically unverified, MD33 conventional
  control study ([PR #1042](https://github.com/spoonman136668-ai/Yggdrasil/pull/1042)).
- **Preregistration-only commit `665bd80646ae675d32f2a875dde72387be226d2d`**
  precedes MD34 simulator source, tests, and any fixture scores.
- Six frozen causal families: relay/fork/collider reserved for later
  training; braid/inhibitor/crossbridge for unfamiliar structural
  transfer. Each has distinct encoder, paired route laws and decoder.
  Route 1 changes every intermediate state and costs 0.03 more.
- Only fixture seeds **15000–15095** are legal for MD34's current
  simulator. They cover 24 hidden-law blocks × four contexts, each
  counterfactually evaluated stable and rewired: 192 physical worlds.
  This is NOT an official MD34 train/DEV/cold/registered dataset.
- The frozen `prereg.json` contains the model-free reference policies,
  physical intervention costs, split and source conditions,
  go/no-go classification and scientific first-use restrictions.

## Falsifiable physics-only qualification

| Reference policy | Frozen expected mean net reward | Goal success |
|---|---:|---:|
| Privileged physics oracle | **+0.940** | 100% |
| Public one-paid-bit terminal-parity policy | +0.100 | 50% |
| Public no-probe fixed-action policy | −0.185 | 25% |

The oracle is not a legal learner because the harness supplies hidden
graph/offset/change to its scoring function. The public one-bit policy
pays an actual physical terminal intervention and receives only the
parity of the unknown correct action; even then, it must guess between
two remaining outcomes. Its 50% goal ceiling is a property of this
frozen simple policy and balanced fixture, **not** a mathematical upper
bound on a trained persistent learner. Learning the three causal
mechanisms across episodes might improve both accuracy and efficiency.

The negative-control suite demands that every stable/rewire pair remain
identical in all public observations **until** a paid parity
intervention, which must then distinguish the changed law; that
both irreversible route choices genuinely lead to different hidden
outcomes; and that no free extra probe, incorrect phase action or
illegal official/previous research seed is accepted.

These are task-identifiability **preflight** results only. Even if all
physics tests pass, the task may still be too small, structurally
degenerate or learnable by trivial conventional methods.

## Next scientific requirement

Before trying a native tokenless Yggdrasil causal learner, freeze
new unconsumed synthetic train/DEV/transfer/cold allocations and fully
train independent strong Bayesian causal planners, recurrent world
models and model-based RL controls. Match physical action budgets,
observation information and whole-process compute, measure goal
success/diagnostic cost/retention/unfamiliar transfer, and test whether
a trained control approaches the 0.94 physics oracle.

An independently trained conventional control within **0.05**
of the oracle on separate unseen transfer and cold evaluation
classifies this task `TRIVIAL_FOR_NOVEL_GAIN`; stop rather than spend
on another unconventional mechanism. Engineering success never
implies SCIENTIFIC_PASS, AGI or autonomous research integration.

## Reproduce synthetic physics-only preflight

```sh
python -m unittest discover -s research/contrib/chatgpt/dg1-md34-20261114 -p 'test_*.py' -v
python research/contrib/chatgpt/dg1-md34-20261114/partial_routes.py
```

CI must verify 54 inherited Yggdrasil tests plus all 55 frozen MD30–MD33
focused tests and MD34's own ten negative controls on Windows/Linux,
byte-exact cross-platform physical receipts, and a derived G29 source
atlas pinned to the preceding exact task commit. No official scientific
cohorts, merges, weights, accepted refs, controllers, scheduled tasks,
runner changes or cross-project integrations are authorized by this
contribution.

## Verified fixture-only result — November 14, 2026

**ENGINEERING/TASK PHYSICS PASS. SCIENCE/LEARNING UNVERIFIED.**

The exact preregistered physics matched all its prespecified bounds:
**192 physically charged fixture worlds**, 96 stable/rewired
counterfactual pairs, six causal families, 24 four-context hidden-law
blocks. Both irreversible route choices change the downstream
intermediate state and required four-way terminal result, and paired
stable/rewired worlds expose identical public observations until an
actual paid terminal-parity diagnostic.

| Frozen reference | Mean net reward | Goal success |
|---|---:|---:|
| Privileged knowing-the-law oracle | **+0.940** | 100% |
| Public one-bit physical probe (only one allowed) | +0.100 | 50% |
| Blind no-probe terminal guess | −0.185 | 25% |

Oracle minus one-paid-bit reference: **+0.840**. Oracle minus blind:
**+1.125**. This is stronger task-level *information scarcity* than
the saturated two-probe MD32 fixture. Nevertheless it is not a proven
learner advantage: the two public reference policies are fixed,
and the privileged oracle has illegal information for a real agent.
A persistent, trained conventional learner **may** close this gap.

On exact candidate `7c5837c1e3e07ba315499072f2cd51170222e5cf`,
[MD34 qualification](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43626079864)
passed Windows and Linux **119/119 tests each**: 54 inherited, 32
MD30, seven MD31, eight MD32, eight MD33 and 10 new MD34. All
public physical trace and net reward receipts matched byte-for-byte
across operating systems; independent
[G29 source atlas](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43626191075)
also passed Windows and Linux.

The frozen source/benchmark identity, physical SHA-256 and exact
reproduction artifacts are preserved in `result.json` and
`provenance.json` and in those GitHub Actions runs.
**No trained Yggdrasil/native model was executed and none of the
official training/DEV/cold/registered cohorts was opened.**
The scientific go/no-go remains conditional on *independently fitted
strong conventional controls* with matched information, real
physical action costs, compute and independent cold/transfer cohorts.
No merge, owner/runner/controller, accepted-ref or deployment action.

The unrelated CKB proxy-fanout workflow remains a separate
infrastructure failure, not MD34 science.

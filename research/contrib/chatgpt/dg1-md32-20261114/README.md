# DG1-MD32 — Compositional Causal Relay v1

**Scope: independent task-and-physics preflight, not a new learner.**
This is a research-only successor to [DG1-MD31 PR #1038](https://github.com/spoonman136668-ai/Yggdrasil/pull/1038),
which failed scientific development qualification and remains frozen.
Yggdrasil's independent non-transformer, non-token north star and
native model are unchanged.

## Plain-English objective

We first need a causal environment that cannot be solved by blindly
repeating an action, that contains genuinely different causal laws, and
that rewards making **physically charged interventions** to learn what
those laws do. This task links two hidden mechanisms:

1. A required precursor action enters an **encoder** and latches an
   intermediate causal signal. No free intermediate or reward label is
   shown after that irreversible action.
2. A terminal action has to match the output of a **decoder** applied to
   that latent signal. In half the counterfactual fixture worlds,
   the decoder has changed *after* the first action without announcement.

A physical encoder probe reveals one intermediate signal for the current
precursor, and a separate decoder probe at that signal reveals the
correct terminal actuation. Each probe costs 0.08 reward and consumes an
actual `World.step`. Without an intervention, the final choice remains
ambiguous. Every four consecutive episodes share the same law, but each
requires a different precursor context. This creates a route to test
persistent compositional causal knowledge rather than action repetition.

The six fixed, distinct encoder/decoder mechanism families are
**relay, fork and collider** (future train) and **braid, inhibitor and
crossbridge** (future unfamiliar transfer). Each has four hidden
decoder-output offsets. Several mechanisms are nonbijective; the
pairwise law hashes and exact formulas are frozen in the preregistration.
Law/seed/offset/change and the latent signal are hidden from policies.

## Task-first provenance

- MD31 original qualified parent:
  `aedbe74d2b31ead5a0517ce3aa827df9e64abda9`.
- **Preregistration-only commit BEFORE simulator or results:**
  `e8c6fd109941b91ae0829df1113de078fa986dda`.
- Fixture-only seeds **9100–9195**, 24 blocks × four contexts =
  96 fixture episodes, each evaluated once both stable and rewired
  for 192 synthetic physics episodes. These are **not** official cohorts.
- All future train/DEV/cold/registered ranges, and all previous
  MD30/MD31 science cohorts, are inaccessible to this source.
- `compositional_relay.py` is an independent environment and its
  untrained reference checks; `test_compositional_relay.py` checks
  source split, no hidden leaks, physical action costs, repeated-law
  blocks and identifiability. Neither implements a new agent or learns
  weights.

### Physics benchmarks, not learner improvements

The preregistered oracle, blind and physical reference policies are:

| Policy | Expected mean reward | Information |
|---|---:|---|
| Privileged correct-action oracle | +0.960 | Hidden law (upper bound only) |
| Fixed terminal actuator 0 | −0.165 | No probes, 25% success |
| Public two-probe physical reference | +0.800 | Two separately charged mechanism interventions |

The difference oracle versus blind is expected to be **+1.125** per
episode, proving that the task has causal informational stakes. The
physical two-probe policy exactly recovers both links for a cost, so
**it may be a very strong reference and potentially saturate the task**.
The remaining +0.160 between the physics upper bound and this strong
hand-built reference is an efficiency opportunity, **not** proof any
trainable learner has sufficient headroom.

**Next scientific decision:** implement and fully train the strongest
conventional adaptive Bayesian, recurrent and model-based RL controls
on legally separated unconsumed data with matched action, information,
compute and budget. If they approach the oracle within 0.05, classify
the task *TRIVIAL_FOR_NOVEL_GAIN* and STOP; do not spend on another
unconventional learning rule or tune after an observed holdout.

## Reproduce task construction (never official science)

```sh
python -m unittest discover -s research/contrib/chatgpt/dg1-md32-20261114 -p 'test_*.py' -v
python research/contrib/chatgpt/dg1-md32-20261114/compositional_relay.py
```

The source-pinned two-platform workflow also requires the full 54
inherited tests, all 32 original MD30 tests, seven frozen MD31 focused
tests, eight new MD32 focused tests, byte-identical public physical
receipts, and the separately generated G29 atlas on both operating
systems. **Engineering PASS never implies scientific improvement or
authorization to merge, promote, touch native weights or first-use.**

# Yggdrasil 2 — Causal Contract Ecology (CCE)

**Status:** isolated, experimental, nonpromotable research branch.
**Scope:** a candidate rebuild of Yggdrasil's *learner*, not replacement of the
repository, accepted evidence, official controller, or autonomous research loop.

- Parent exact main SHA: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`
- First preregistration commit: `985a402c69360556b7eaa2c2691c9c72d4b1d787`
- Research lineage: compare, do not rewrite, the preexisting structural-plasticity
  and functional-regeneration contracts under `research/architecture/`.
- **No AGI claim; no scientific gain; no source first-use or deployment authority.**

## Architectural thesis

A cell is a revisable, evidence-backed **causal contract**, not an encoded
object label or a unit that magically knows a correct relationship. Contracts
must learn from public action-consequence records, track uncertainty, compete
against simpler explanations, survive cold storage, and eventually compose
into mechanisms for previously unseen tasks. A local distributed graph and
developmental structural decisions remain **goals**, not verified properties
of this tiny first implementation.

The intended sequence is:

1. **CCE-01: predictive-contract arbitration.** In a deliberately small binary
   action environment, learn pooled and singleton-feature action-conditional
   hypotheses online. Permit one irreversible structural split only if its
   *prequential* evidence overcomes a preregistered complexity hurdle and each
   action/feature bin has support. Verify negative-control restraint, a strong
   full-context predictor, serialized state integrity and explicit bytes.
2. **CCE-02: interventional identity binding (proposed only).** Several
   perceptually aliased sources; cells should bind an identity only when active
   interventions reveal persistent distinguishable action-consequence patterns.
   Compare against oracle-free clustering, HMM and active-system-identification
   controls. Separate identifiability failures from model failures.
3. **CCE-03: mechanism compression with behavioral witnesses (proposed only).**
   Replace frequent traces with compact executable contracts, but retain
   counterexamples and reconstruct exact prespecified predictions after cold
   restart. Compare archival costs and retained **function**, not just bytes.
4. **CCE-04: causal composition and inheritance (proposed only).** Build a
   multistep predictive mechanism by composing two previously learned
   contract families, without access to original histories, then ablate
   inheritance. Frozen unseen interventions, withheld compositional combinations,
   interference and matching training/compute are mandatory.
5. **CCE-05: locally proposed growth, merge and repair (proposed only).**
   No centralized access to all environment state for structural choices.
   Fixed maximum slots, neighbors-only messages, explicit complexity price,
   safe rollback and lesion-derived functional recovery.

The combination, *not* the individual ingredients, is the unverified
research proposal. Prior work on dynamic causal graphs, mechanistic world
models, cellular computation and local learning constrains this program;
we do not assert that the combination is unprecedented.

## CCE-01 exact mechanics

The core receives only `((public_bit0, public_bit1), action, observed_outcome)`.
Actions in the synthetic environment are randomized by the environment's
sealed generator; this supports comparison of action-conditioned effects,
but **does not establish causal identification from uncontrolled observations**.

Three models are maintained: a pooled action/outcome Bernoulli table and
one candidate for each publicly observable feature. A candidate can replace
the pooled predictor only after 48 examples, coverage of >=6 examples in all
four (feature, action) cells, and a prequential Brier improvement at least
`max(2.0, 0.01*N)`. The choice is one-way. The bound is 2 features and
one selected split; there is no dynamic graph or free-form ontology.

A separate full-context two-feature table is the stronger competing control.
All models see identical training observations and compute predictions before
updating their own local counts. Neither a ground-truth feature index nor
the positive/null world label is passed to learner code.

## Run engineering tests (does not consume primary experiment)

From the repository root:

```powershell
python -m unittest discover -s research/contrib/chatgpt/y2-cce01 -p test_cce01.py -v
```

The primary frozen synthetic run is distinct from unit tests:

```powershell
python research/contrib/chatgpt/y2-cce01/run_cce01.py --output research/contrib/chatgpt/y2-cce01/result.json
```

**First-use rule:** execute that primary command only after the prereg is
committed and the candidate implementation and controls are frozen. Do not
rerun with changed seeds, code, thresholds, or budgets after seeing scores.
Capture the exact candidate Git SHA/tree, Python platform, evaluator code
identity, source hashes, and command alongside the result. Local scripts
must never launch an official Windows runner, queue job or scheduler.

## What counts as progress?

A unit-test pass establishes engineering behavior only. A good synthetic
result is **development evidence**, not SCIENTIFIC_PASS. A genuine advancement
requires a separate, source-admitted native Yggdrasil experiment, a fully
trained strongest control, unfamiliar causal transfer, cold retention after
interference, independent reproduction and owner qualification. Preserve
negative results.

## Explicit isolation

- No edits to `main`, accepted research state, checkpoints, `.ice`, controllers,
  runners, live interfaces, broker connections, or other architecture families.
- No model API / paid service. Stdlib Python only.
- No growing the system without a matched compaction mechanism and hard
  resident/active/communication budgets.
- No claim of locally **selected** structure: the CCE-01 arbiter is centralized
  and is an intentionally disclosed limitation to remove or beat later.
- Any implementation change after a primary run requires a **new** frozen
  experiment ID, not silent repair of CCE-01.

## Relevant foundations

- Native original: `research/architecture/structural-plasticity.ice` and
  `research/architecture/functional-regeneration.ice` at the pinned parent.
- Public causal count comparator:
  `yggdrasil/public_causal_cells.py` at the pinned parent.
- Existing independent research contribution contract: `CONTRIBUTING_RESEARCH.md`.
- External context (not native proof):
  - Dynamic causal graph learning: https://proceedings.mlr.press/v323/orujlu26a.html
  - Mechanism-centric world models: https://arxiv.org/abs/2607.12474
  - Neural cellular reasoning: https://arxiv.org/abs/2609.36126

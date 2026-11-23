# Y2-CCE06 CAL source and comparator engineering

This folder is a **draft calibration source implementation**, not a completed
calibration study, CCE-06 learner, stronger-control suite, native Yggdrasil
integration, or protected scientific result.

## Source boundary

- `calibration_worlds.py` is evaluator-only. It has two distinct positive causal
  graph templates, action-null and intervention-identifiable observational alias
  negative controls. It emits ONLY public two-bit (observation, action,
  next-observation) records. Source-side hidden dynamics and oracle diagnostic
  must never be imported into candidate or comparator code.
- `calibration_plan.json` fixes the calibration families, seeds, split sizes and
  action costs. Train and cal-eval use deterministic **independently keyed RNG
  streams**, not disjoint theoretical source families.
- Calibration-sized generation is blocked without matching code/plan SHA-256 and
  source-commit fields in a caller-provided lock. This **does not** constitute
  independent custody. No lock or calibration datasets are committed here;
  protected PRIMARY is not implemented or generated.
- Evaluator-generator fixtures are restricted to seed 997 (<=32 events).
  Standalone public fixture RNGs are not registered CAL or PRIMARY sources.
- `calibration_controls.py` contains a full-context public suffix table and an
  EM-fitted action-conditioned HMM. HMM needs >=3 TRAIN-only restarts per
  dimension 2..8, train-only dimensional selection, proper convergence checks
  and a matched evaluation runner before it can count as a **fully fitted**
  comparator.

- `calibration_psr.py` learns 12 observable action-observation operators; a
  finite predictive state is updated recurrently at inference without a
  suffix lookup. `calibration_psr_selection.py` chooses test-basis width,
  context depth and ridge strength using TRAIN only. This is an operator
  model control, not proof of identifiable hidden-state recovery.
- `calibration_active_bayes.py` uses public Dirichlet action-response
  posteriors, priced interventions and expected Bayesian parameter
  information gain. `choose()` is paired with a real public
  `update()` witness. Off-policy evaluation against unrelated logged
  actions is forbidden: a source-custodied cost/accuracy frontier remains
  unmeasured.
- `calibration_decision_bayes.py` is a separate myopic value-of-information
  baseline. It scores each public state/action using the expected reduction
  in posterior predictive Brier risk, weighted by that context's empirical
  TRAIN frequency. Online posterior updates never change the frozen TRAIN
  weights. This is more directly aligned to terminal prediction risk than
  parameter information gain, but only approximates the fixed audit
  distribution and does not plan multi-step downstream state changes.

- `calibration_recurrent.py` is a compact, fully trainable tanh recurrent
  network using truncated backpropagation through time and Adam. `calibration_recurrent_selection.py`
  selects capacity and learning rate on chronological public TRAIN-only data,
  then refits on all TRAIN. Max epochs and non-activated early stop are
  reported honestly; a fixture-only fit is **not** a fully qualified strongest
  recurrent comparator or a causal-learning gain.

- `calibration_policy_frontier.py` is a **DEV-only on-policy evaluator
  interface**: it calls each policy's selected `env.step(action)`, supplies
  only its actual public action/outcome witness, and scores all frozen
  posteriors against a shared terminal public audit. It includes hard
  paid-probe budgets, simple no-action/alternating references, per-seed
  receipts and a descriptive cost/Brier Pareto view. Its local fixture
  hashes reject exact TRAIN/audit duplication, **not** source overlap,
  independent custody or oracle contamination outside the public schema.
  Its output is never a scientific GO/NO-GO or the strongest-policy frontier.

## Current gaps / strict stop

- No CCE06 split/merge candidate or learned relations. A trainable
  recurrent neural estimator, learned-operator PSR comparator and costed
  Bayesian policies (information-gain and decision-focused) exist as isolated
  engineering controls, but have **not** completed strong TRAIN-only
  source-custodied selection, cross-platform full
  regression or qualified strongest-comparator comparison. No interactive
  source-custodied cost/accuracy Pareto frontier (DEV fixtures only).
- No committed independent-source lock, evaluator, data manifests or independent
  custody receipt. No CAL-EVAL materialized and **no primary first-use**.
- No physical-world evidence, learning gain, accepted promotion, deployment or
  reviewer authority.
- This code adds Python research files; the pre-existing G29 generated atlas may
  require its **approved source-pinned generator** before full CI passes. Never
  hand-edit `.ice` or bypass atlas checks.
- For exact next gate: finish the remaining genuine strong controls + training
  convergence checks + source-custody lock, verify identifiability, freeze
  evaluator and execute TRAIN-only control selection. Only then consider CAL
  scoring and separately governed PRIMARY preregistration.

## Fixtures only

```bash
cd research/contrib/chatgpt/y2-cce06
python -m unittest -v test_calibration test_calibration_fit_selection
python -m unittest -v test_calibration_psr test_calibration_psr_selection test_calibration_active_bayes
python -m unittest -v test_calibration_recurrent
python -m unittest -v test_calibration_policy_frontier
python -m unittest -v test_calibration_decision_bayes test_calibration_decision_frontier
```

Fixture tests never use the frozen experimental seed list and cannot validate
the scientific headroom or OOD-transfer hypotheses.
